from pydantic import BaseModel

# Pydantic for RAG_ID 
class CreateRAGResponse(BaseModel):
    RAG_id: str


class RAGQueryRequest(BaseModel):
    query: str


class RagListItem(BaseModel):
    rag_id: str
    rag_name: str 
    model: str 
