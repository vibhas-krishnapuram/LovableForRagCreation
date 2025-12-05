export interface User {
  user_id: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CreateUserRequest {
  username: string;
  password: string;
}

export interface CreateUserResponse {
  Action: string;
  user_id: string;
}

export interface RagListItem {
  rag_id: string;
  rag_name: string;
  model: string;
}

export interface CreateRAGResponse {
  RAG_id: string;
}

export interface RAGQueryRequest {
  query: string;
}

export interface RAGQueryResponse {
  response: string;
  model_used?: string;
  RAG_name?: string;
  documents_retrieved?: number;
  performance?: {
    retrieval_time: string;
    llm_time: string;
    total_time: string;
  };
  uploaded_doc_included?: boolean;
}

