from pydantic import BaseModel
from typing import List
from enum import Enum

class LLMChoice(str, Enum):
    LLAMA2_70B = "llama2-70b"
    GPT_OSS_120B = "gpt-oss-120b"
    GEMMA_7B = "gemma-7b"
    LLAMA3_70B = "llama3-70b"

class RAGVariant(str, Enum):
    VANILLA = "vanilla"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    HYBRID = "hybrid"

class ChatMessage(BaseModel):
    message: str
    is_user: bool
    timestamp: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage]
    llm_choice: LLMChoice
    rag_variant: RAGVariant
    use_internet_search: bool = False

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    processing_time: float

class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    chunks_processed: int

class ConfigUpdate(BaseModel):
    llm_choice: LLMChoice
    rag_variant: RAGVariant
    use_internet_search: bool