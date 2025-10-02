import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer

def setup_observability():
    if os.getenv('LANGSMITH_API_KEY'):
        client = Client()
        tracer = LangChainTracer()
        return tracer
    return None

def log_rag_operation(operation: str, query: str, documents_retrieved: int, response_time: float):
    # Simple logging for observability
    print(f"RAG Operation: {operation}")
    print(f"Query: {query}")
    print(f"Documents Retrieved: {documents_retrieved}")
    print(f"Response Time: {response_time:.2f}s")