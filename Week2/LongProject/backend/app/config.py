import os
from pydantic_settings import BaseSettings
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    
    # Model Configurations
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    GROQ_MODELS: Dict[str, str] = {
        "llama2-70b": "llama2-70b-4096",
        "gpt-oss-120b": "openai/gpt-oss-120b",
        "gemma-7b": "gemma-7b-it",
        "llama3-70b": "llama-3.3-70b-versatile"
    }
    
    # Vector Database
    PINECONE_INDEX_NAME: str = "multimodal-rag"
    
    # RAG Config
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 80
    
    class Config:
        env_file = ".env"

settings = Settings()