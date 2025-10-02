from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from ..config import settings
from typing import List, Optional

class VectorStoreService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Create index if doesn't exist
        if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
            print("Creating Pinecone index")
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=384,  # all-MiniLM-L6-v2 dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        self.vector_store = PineconeVectorStore(
            index=pc.Index(settings.PINECONE_INDEX_NAME),
            embedding=self.embeddings
        )
        
        self._documents: List[Document] = []
    
    async def add_documents(self, documents: List[Document]) -> int:
        try:
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Use LangChain's Pinecone integration
            self.vector_store.add_texts(texts, metadatas)
            
            self._documents.extend(documents)
            
            return len(documents)
        except Exception as e:
            print(f"Error adding documents: {e}")
            return 0
    
    async def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        semantic_retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        sem_docs = semantic_retriever.get_relevant_documents(query)
        return sem_docs
    
    async def hybrid_search(self, query: str, k: int = 2) -> List[Document]:
        """
        Hybrid RAG retrieval:
        - semantic retriever from the vector store (Pinecone)
        - BM25 keyword retriever over the in-memory documents
        - combined via EnsembleRetriever (weights adjustable)
        Returns a list of Documents (de-duplicated).
        """
        
        if not self._documents:
            # nothing to search for BM25; fallback to pure semantic
            return await self.similarity_search(query, k=k)

        # create a semantic retriever from the vector store
        semantic_retriever = self.vector_store.as_retriever(search_kwargs={"k": k})

        # build BM25 retriever from in-memory documents
        bm25_retriever = BM25Retriever.from_documents(self._documents, k=k)

        try:
            # ensemble the two retrievers. adjust weights as needed.
            ensemble = EnsembleRetriever(retrievers=[semantic_retriever, bm25_retriever],
                                         weights=[0.7, 0.3])
            # common method name for retrievers in LangChain
            hybrid_results = ensemble.get_relevant_documents(query)
            
        except Exception as e:
            # Robust fallback: do both separately and merge results
            print(f"EnsembleRetriever failed, falling back to manual merge: {e}")
            sem_docs = semantic_retriever.get_relevant_documents(query)
            bm25_docs = bm25_retriever.get_relevant_documents(query)

            # merge while preserving order and removing duplicates (by content+metadata)
            seen = set()
            hybrid_results = []
            for doc in sem_docs + bm25_docs:
                key = (doc.page_content, tuple(sorted((doc.metadata or {}).items())))
                if key not in seen:
                    seen.add(key)
                    hybrid_results.append(doc)

            # limit results to k
            hybrid_results = hybrid_results[:k*2]

        return hybrid_results

vector_store_service = VectorStoreService()