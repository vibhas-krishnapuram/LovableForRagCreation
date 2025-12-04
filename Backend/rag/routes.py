from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, Form
from config.security import *


from schemas.rag_Models import (
    CreateRAGResponse,
    RagListItem,
    RAGQueryRequest,
)

from rag.service import *

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.post("/create", response_model=CreateRAGResponse)
async def create_RAG_route(RAG_name: str = Form(...),
                    Model: str = Form(...),
                    key: str = Form(...),
                    documents: list[UploadFile] = File(...),
                    current_user_id: str = Depends(get_current_user_token)):
    return_val = await create_RAG(RAG_name, Model, key, documents, current_user_id)
    return return_val


@router.post("/{RAG_id}/query")
async def query_rag_route(
    RAG_id: str,
    request: RAGQueryRequest,
    current_user_id: str = Depends(get_current_user_token),
):
    return_val = await query_rag(RAG_id, request, current_user_id)
    return return_val

@router.post("/{RAG_id}/file_query")
async def file_query_rag_route(
    RAG_id: str,
    query: str = Form(...),
    file: UploadFile = File(None),
    current_user_id: str = Depends(get_current_user_token),
    ):
    return_val = await file_query_rag(RAG_id, query, file, current_user_id)
    return return_val


@router.post("/{RAG_id}/add_docs")
async def add_documents_to_rag_route(
            RAG_id: str,
            new_documents: list[UploadFile] = File(...),
            current_user_id = Depends(get_current_user_token)
):
    return_val = await add_documents_to_rag(RAG_id, new_documents, current_user_id)
    return return_val

@router.get("/list", response_model=list[RagListItem])
def get_all_rag_route(
    current_user_id: str = Depends(get_current_user_token)
    ):
    return_val = get_all_rag(current_user_id)
    return return_val

@router.delete("/delete/{rag_id}", status_code=204)
def delete_rag_route(rag_id: str,
                current_user_id: str = Depends(get_current_user_token)
            ):
    return_val = delete_rag(rag_id, current_user_id)
    return return_val
