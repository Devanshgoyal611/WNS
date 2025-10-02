from typing import List, Tuple, Dict, Optional
from .vector_store import vector_store_service
from .internet_search import internet_search_service
from .llm_service import llm_service
import networkx as nx
from langchain.schema import Document

class RAGService:
    def __init__(self):
        self.knowledge_graph = nx.Graph()

    # ---------- Public RAG entry points ----------
    async def vanilla_rag( self, query: str, conversation_history: List, llm_choice: str, use_internet: bool = False) -> Tuple[str, List[str]]:
        """
        Simple semantic-only retrieval + optional internet context.
        """
        semantic_docs = await self._get_semantic_docs(query, k=4)
        internet_results = await self._get_internet_results(query, use_internet, web_k=3)

        context = self._build_context(
            mode="vanilla", documents=semantic_docs, internet_results=internet_results
        )

        prompt = self._compose_prompt(context, conversation_history, query, style="comprehensive")
        response = await llm_service.generate_response_groq(prompt, llm_choice, conversation_history)
        sources = self._extract_sources(semantic_docs)

        return response, sources

    async def knowledge_graph_rag(
        self,
        query: str,
        conversation_history: List,
        llm_choice: str,
        use_internet: bool = False,
    ) -> Tuple[str, List[str]]:
        """
        Builds a simple KG from retrieved docs, extracts key entities and uses KG context.
        """
        docs = await self._get_semantic_docs(query, k=5)
        # Build KG from docs
        self._build_knowledge_graph(docs, query)

        entities = self._extract_key_entities(docs, query)
        kg_context = self._build_knowledge_graph_context(docs, entities)

        internet_results = await self._get_internet_results(query, use_internet, web_k=3)
        if internet_results:
            kg_context += self._format_internet_results(internet_results)

        prompt = self._compose_prompt(kg_context, conversation_history, query, style="kg_reasoning")
        response = await llm_service.generate_response_groq(prompt, llm_choice, conversation_history)
        sources = self._extract_sources(docs)

        return response, sources

    async def hybrid_rag(
        self,
        query: str,
        conversation_history: List,
        llm_choice: str,
        use_internet: bool = False,
    ) -> Tuple[str, List[str]]:
        """
        Combines semantic and hybrid (semantic+BM25) retrieval and optional web/arXiv results.
        """
        semantic_docs = await self._get_semantic_docs(query, k=3)
        hybrid_docs = await vector_store_service.hybrid_search(query, k=3)

        # Merge and deduplicate documents preserving order: semantic first, then hybrid
        merged_docs = self._merge_unique_docs(semantic_docs, hybrid_docs)

        internet_results = await self._get_internet_results(query, use_internet, web_k=3, arxiv_k=2)

        context = self._build_context(mode="hybrid", documents=merged_docs, internet_results=internet_results)
        prompt = self._compose_prompt(context, conversation_history, query, style="synthesise")
        response = await llm_service.generate_response_groq(prompt, llm_choice, conversation_history)
        sources = self._extract_sources(merged_docs)

        return response, sources

    # ---------- Internal helpers (DRY) ----------
    async def _get_semantic_docs(self, query: str, k: int = 4) -> List[Document]:
        try:
            return await vector_store_service.similarity_search(query, k=k)
        except Exception:
            # graceful fallback: return empty list on error
            return []

    async def _get_internet_results(
        self, query: str, use_internet: bool, web_k: int = 3, arxiv_k: int = 0
    ) -> List[Dict]:
        if not use_internet:
            return []

        results: List[Dict] = []
        try:
            web_results = await internet_search_service.search_web(query, web_k)
            results.extend(web_results or [])
        except Exception:
            # ignore web fetch errors but continue
            pass

        if arxiv_k > 0:
            try:
                arxiv_results = await internet_search_service.search_arxiv(query, arxiv_k)
                if arxiv_results:
                    results.extend(arxiv_results)
            except Exception:
                pass

        return results

    def _merge_unique_docs(self, *doc_lists: List[Document]) -> List[Document]:
        """Merge multiple lists of Document while preserving order and de-duplicating by (content, source)."""
        seen = set()
        merged: List[Document] = []
        for docs in doc_lists:
            for d in docs or []:
                source = (d.metadata or {}).get("source", "")
                key = (d.page_content.strip(), source)
                if key not in seen:
                    seen.add(key)
                    merged.append(d)
        return merged

    def _extract_sources(self, docs: List[Document]) -> List[str]:
        return [
            (doc.metadata or {}).get("source", "Unknown")
            for doc in docs
        ]

    def _build_context(self, mode: str, documents: List[Document], internet_results: Optional[List[Dict]] = None) -> str:
        """
        Generic context builder for different modes (vanilla/hybrid/knowledge graph)
        """
        internet_results = internet_results or []
        ctx_lines = []

        if mode in ("vanilla", "hybrid", "kg"):
            if documents:
                ctx_lines.append(f"Retrieved Documents ({len(documents)}):")
                for i, doc in enumerate(documents, start=1):
                    src = (doc.metadata or {}).get("source", "Unknown")
                    ctx_lines.append(f"Document {i} (Source: {src}):\n{doc.page_content}\n")
            else:
                ctx_lines.append("No documents retrieved from the vector store.\n")

        if internet_results:
            ctx_lines.append("Internet Results:")
            for i, r in enumerate(internet_results, start=1):
                title = r.get("title", "No title")
                desc = r.get("description", r.get("summary", "No description"))
                src = r.get("link", r.get("url", "Unknown"))
                ctx_lines.append(f"[Web {i}] {title} (Source: {src})\n{desc}\n")

        return "\n".join(ctx_lines)

    def _compose_prompt(self, context: str, conversation_history: List, query: str, style: str = "comprehensive") -> str:
        """
        Compose the final prompt sent to the LLM. 'style' controls slight instruction wording.
        """
        style_instruction = {
            "comprehensive": "Please provide a comprehensive answer citing given sources only. If the query is unrelated to the context, politely indicate that you don't have the information.",
            "kg_reasoning": "Using knowledge graph reasoning, analyze relationships and provide an insightful answer citing sources. If the query is unrelated to the context, politely indicate that you don't have the information.",
            "synthesise": "Synthesize information from all available sources and highlight key insights with citations. If the query is unrelated to the context, politely indicate that you don't have the information.",
        }.get(style, "Please answer the user's question using the provided context and cite sources.")

        history_text = self._format_history(conversation_history)

        prompt = (
            f"Context:\n{context}\n\n"
            f"Conversation History:\n{history_text}\n\n"
            f"User Question: {query}\n\n"
            f"{style_instruction}"
        )
        return prompt

    def _format_history(self, conversation_history: List) -> str:
        """
        Formats the last few messages in conversation_history. Handles simple objects/dicts.
        Expects elements that either have attributes `.is_user` and `.message` or are dict-like:
        {'is_user': True|False, 'message': '...'}
        """
        if not conversation_history:
            return "(no prior messages)"

        lines = []
        for msg in conversation_history[-5:]:
            try:
                is_user = msg.get("is_user") if isinstance(msg, dict) else msg.is_user
                text = msg.get("message") if isinstance(msg, dict) else msg.message
    
                # fallback to dict-style
                if is_user is None:
                    is_user = msg.get("is_user", False) if isinstance(msg, dict) else False
                if text is None:
                    text = msg.get("message", "") if isinstance(msg, dict) else str(msg)
                role = "User" if is_user else "Assistant"
                lines.append(f"{role}: {text}")
            except Exception:
                lines.append(str(msg))
        return "\n".join(lines)

    # ---------- Knowledge graph helpers ----------
    def _build_knowledge_graph(self, documents: List[Document], query: str):
        # Simplified KG construction; clears previous graph and adds query node + doc nodes
        self.knowledge_graph.clear()
        self.knowledge_graph.add_node("query", type="query", content=query)
        for i, doc in enumerate(documents):
            doc_id = f"doc_{i}"
            snippet = (doc.page_content or "")[:200]
            self.knowledge_graph.add_node(doc_id, type="document", content=snippet)
            self.knowledge_graph.add_edge("query", doc_id, weight=1.0)

    def _extract_key_entities(self, documents: List[Document], query: str) -> List[str]:
        """
        Simple entity extraction fallback: collect capitalised words longer than 5 chars.
        Replace with NER in production.
        """
        entities = set()
        text = (query or "") + " " + " ".join([(d.page_content or "") for d in documents])
        for token in text.split():
            if len(token) > 5 and token[0].isupper():
                entities.add(token.strip(".,;:()[]"))
        return list(entities)[:10]

    def _build_knowledge_graph_context(self, documents: List[Document], entities: List[str]) -> str:
        ctx = "Knowledge Graph Context:\n"
        if entities:
            ctx += f"Key Entities: {', '.join(entities)}\n\n"
        ctx += "Relevant Documents:\n"
        for i, doc in enumerate(documents, start=1):
            src = (doc.metadata or {}).get("source", "Unknown")
            ctx += f"Document {i} (Source: {src}):\n{doc.page_content}\n\n"
        return ctx

    def _format_internet_results(self, internet_results: List[Dict]) -> str:
        if not internet_results:
            return ""
        return self._build_context(mode="internet", documents=[], internet_results=internet_results)

# Create a module-level instance if you want the singleton pattern as before
rag_service = RAGService()
