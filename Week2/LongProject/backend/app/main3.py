from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Any, Dict, Optional
import uuid
import os
import time
from pathlib import Path

# Import your existing modules
from .models.models import *
from .services.rag_service import rag_service
from .services.document_processor import document_processor
from .services.vector_store import vector_store_service
from .utils.observability import setup_observability

app = FastAPI(title="Multi-Modal RAG Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup observability
tracer = setup_observability()

# Global store for uploaded documents
UPLOADED_DOCUMENTS = set()
DOCUMENT_METADATA = {}

def normalize_conversation_history(history: List[Any]) -> List[Dict[str, Any]]:
    """Convert conversation history to consistent dictionary format"""
    normalized = []
    for msg in history:
        if isinstance(msg, dict):
            normalized.append({
                "message": msg.get("message", str(msg)),
                "is_user": msg.get("is_user", False),
                "timestamp": msg.get("timestamp", "")
            })
        else:
            normalized.append({
                "message": getattr(msg, "message", str(msg)),
                "is_user": getattr(msg, "is_user", False),
                "timestamp": getattr(msg, "timestamp", "")
            })
    return normalized

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(f"🔍 Received chat request - Message: {request.message}, LLM: {request.llm_choice}, RAG: {request.rag_variant}")
    
    start_time = time.time()
    
    try:
        formatted_history = normalize_conversation_history(request.conversation_history)
        
        print(f"📝 Formatted history: {len(formatted_history)} messages")
        
        # Use all uploaded documents as context (no need to specify file path)
        if request.rag_variant == RAGVariant.VANILLA:
            response, sources = await rag_service.vanilla_rag(
                request.message, 
                formatted_history,
                request.llm_choice.value,
                request.use_internet_search
            )
        elif request.rag_variant == RAGVariant.KNOWLEDGE_GRAPH:
            response, sources = await rag_service.knowledge_graph_rag(
                request.message,
                formatted_history,
                request.llm_choice.value,
                request.use_internet_search
            )
        elif request.rag_variant == RAGVariant.HYBRID:
            response, sources = await rag_service.hybrid_rag(
                request.message,
                formatted_history,
                request.llm_choice.value,
                request.use_internet_search
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid RAG variant")
        
        processing_time = time.time() - start_time
        
        print(f"✅ Response generated: {len(response)} chars, {len(sources)} sources, {processing_time:.2f}s")
        
        return ChatResponse(
            response=response,
            sources=sources,
            processing_time=processing_time
        )
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

# New direct chat endpoint - uses ALL uploaded documents automatically
@app.post("/direct-chat")
async def direct_chat(
    message: str = Query(..., description="Your message to the AI"),
    llm: str = Query("llama2-70b", description="LLM to use", choices=["llama2-70b", "gpt-oss-120b", "gemma-7b", "llama3-70b"]),
    rag: str = Query("vanilla", description="RAG variant to use", choices=["vanilla", "knowledge_graph", "hybrid"]),
    use_internet: bool = Query(False, description="Enable internet search")
    # No file_path parameter needed - uses all uploaded documents
):
    """Direct chat endpoint that uses ALL previously uploaded documents"""
    try:
        # Prepare request data
        request_data = {
            "message": message,
            "conversation_history": [],
            "llm_choice": llm,
            "rag_variant": rag,
            "use_internet_search": use_internet
        }
        
        # Create ChatRequest object
        chat_request = ChatRequest(**request_data)
        
        # Call chat logic directly
        start_time = time.time()
        formatted_history = normalize_conversation_history(chat_request.conversation_history)
        
        if rag == "vanilla":
            response, sources = await rag_service.vanilla_rag(
                message, 
                formatted_history,
                llm,
                use_internet
            )
        elif rag == "knowledge_graph":
            response, sources = await rag_service.knowledge_graph_rag(
                message,
                formatted_history,
                llm,
                use_internet
            )
        elif rag == "hybrid":
            response, sources = await rag_service.hybrid_rag(
                message,
                formatted_history,
                llm,
                use_internet
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid RAG variant")
        
        processing_time = time.time() - start_time
        
        return {
            "response": response,
            "sources": sources,
            "processing_time": processing_time,
            "llm_used": llm,
            "rag_used": rag,
            "internet_search": use_internet,
            "available_documents": len(UPLOADED_DOCUMENTS)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Direct chat error: {str(e)}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload document via file upload - stores it for future chats"""
    try:
        os.makedirs("uploads", exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        file_path = f"uploads/{uuid.uuid4()}.{file_extension}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        documents = await document_processor.process_document(file_path, file.filename)
        chunks_processed = await vector_store_service.add_documents(documents)
        
        if chunks_processed == 0:
            last_err = getattr(vector_store_service, "get_last_init_error", lambda: None)()
            raise HTTPException(status_code=500, detail=f"Failed to ingest document; chunks_processed=0; last_error={last_err}")

        # Store document info for future reference
        document_id = str(uuid.uuid4())
        UPLOADED_DOCUMENTS.add(document_id)
        DOCUMENT_METADATA[document_id] = {
            "file_name": file.filename,
            "file_type": file_extension,
            "upload_time": time.time(),
            "chunks_processed": chunks_processed
        }
        
        os.remove(file_path)
        
        return DocumentUploadResponse(
            message="Document processed successfully and stored for future chats",
            document_id=document_id,
            chunks_processed=chunks_processed
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New direct upload endpoint with file path
@app.post("/direct-upload")
async def direct_upload(file_path: str = Query(..., description="Full path to the document file")):
    """Direct upload endpoint using file path - stores it for future chats"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        file_name = os.path.basename(file_path)
        file_extension = file_name.split('.')[-1].lower()
        
        # Check if file type is supported
        supported_types = ["txt", "pdf", "docx", "jpg", "jpeg", "png"]
        if file_extension not in supported_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}. Supported types: {', '.join(supported_types)}")
        
        # Create uploads directory if not exists
        os.makedirs("uploads", exist_ok=True)
        
        # Copy file to uploads directory
        temp_file_path = f"uploads/{uuid.uuid4()}.{file_extension}"
        import shutil
        shutil.copy2(file_path, temp_file_path)
        
        # Process document
        documents = await document_processor.process_document(temp_file_path, file_name)
        chunks_processed = await vector_store_service.add_documents(documents)
        
        # Store document info
        document_id = str(uuid.uuid4())
        UPLOADED_DOCUMENTS.add(document_id)
        DOCUMENT_METADATA[document_id] = {
            "file_name": file_name,
            "file_type": file_extension,
            "upload_time": time.time(),
            "chunks_processed": chunks_processed,
            "original_path": file_path
        }
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": "Document uploaded successfully and stored for future chats",
            "file_name": file_name,
            "chunks_processed": chunks_processed,
            "document_id": document_id,
            "available_documents_count": len(UPLOADED_DOCUMENTS)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint to list uploaded documents
@app.get("/documents")
async def list_documents():
    """List all uploaded documents available for chatting"""
    return {
        "total_documents": len(UPLOADED_DOCUMENTS),
        "documents": [
            {
                "document_id": doc_id,
                **metadata
            }
            for doc_id, metadata in DOCUMENT_METADATA.items()
        ]
    }

# New endpoint to clear uploaded documents
@app.delete("/documents")
async def clear_documents():
    """Clear all uploaded documents (reset the knowledge base)"""
    global UPLOADED_DOCUMENTS, DOCUMENT_METADATA
    count = len(UPLOADED_DOCUMENTS)
    UPLOADED_DOCUMENTS.clear()
    DOCUMENT_METADATA.clear()
    
    # You might also want to clear the vector store
    # await vector_store_service.clear_documents()
    
    return {
        "message": f"All documents cleared successfully",
        "documents_removed": count
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Multi-Modal RAG Chatbot",
        "documents_available": len(UPLOADED_DOCUMENTS)
    }

@app.get("/")
async def root():
    return {
        "message": "Multi-Modal RAG Chatbot API",
        "endpoints": {
            "POST /chat": "Chat with the AI (JSON body)",
            "POST /direct-chat": "Direct chat using ALL uploaded documents",
            "POST /upload": "Upload document via file upload",
            "POST /direct-upload": "Upload document via file path", 
            "GET /documents": "List all uploaded documents",
            "DELETE /documents": "Clear all uploaded documents",
            "GET /health": "Basic health check",
            "GET /": "This information page"
        },
        "available_llms": ["llama2-70b", "gpt-oss-120b", "gemma-7b", "llama3-70b"],
        "available_rag_variants": ["vanilla", "knowledge_graph", "hybrid"],
        "supported_file_types": ["txt", "pdf", "docx", "jpg", "jpeg", "png"],
        "current_documents_count": len(UPLOADED_DOCUMENTS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    

#    How to run
#    uvicorn app.main3:app --host 0.0.0.0 --port 8000
                                                                                                    
#    $ curl -X POST "http://localhost:8000/direct-chat?message=What%20is%20Machine%20Learning?&llm=llama3-70b&rag=vanilla&use_internet=true"
#    $ curl -X POST "http://localhost:8000/direct-upload?file_path=C:\Users\DEVANSH\Downloads\mmbert-1-9.pdf"
#    $ curl http://localhost:8000/documents
#    $ curl -X POST "http://localhost:8000/direct-chat?message=What%20is%20Annealed%20Language%20Learning%20in%20mmbert?&llm=gpt-oss-120b&rag=vanilla&use_internet=true"
#    $ curl -X DELETE http://localhost:8000/documents

