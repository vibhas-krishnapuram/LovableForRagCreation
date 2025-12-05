/// <reference types="vite/client" />
import axios from 'axios';
import type {
  LoginRequest,
  LoginResponse,
  CreateUserRequest,
  CreateUserResponse,
  RagListItem,
  CreateRAGResponse,
  RAGQueryResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data);
    return response.data;
  },

  createUser: async (data: CreateUserRequest): Promise<CreateUserResponse> => {
    const response = await api.post<CreateUserResponse>('/auth/create_user', data);
    return response.data;
  },
};

export const ragAPI = {
  create: async (
    ragName: string,
    model: string,
    key: string,
    documents: File[]
  ): Promise<CreateRAGResponse> => {
    const formData = new FormData();
    formData.append('RAG_name', ragName);
    formData.append('Model', model);
    formData.append('key', key);
    documents.forEach((doc) => {
      formData.append('documents', doc);
    });

    const response = await api.post<CreateRAGResponse>('/rag/create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (): Promise<RagListItem[]> => {
    const response = await api.get<RagListItem[]>('/rag/list');
    return response.data;
  },

  query: async (ragId: string, query: string): Promise<RAGQueryResponse> => {
    const response = await api.post<RAGQueryResponse>(
      `/rag/${ragId}/query`,
      { query }
    );
    return response.data;
  },

  fileQuery: async (
    ragId: string,
    query: string,
    file?: File
  ): Promise<RAGQueryResponse> => {
    const formData = new FormData();
    formData.append('query', query);
    if (file) {
      formData.append('file', file);
    }

    const response = await api.post<RAGQueryResponse>(
      `/rag/${ragId}/file_query`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  addDocs: async (ragId: string, documents: File[]): Promise<void> => {
    const formData = new FormData();
    documents.forEach((doc) => {
      formData.append('new_documents', doc);
    });

    await api.post(`/rag/${ragId}/add_docs`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  delete: async (ragId: string): Promise<void> => {
    await api.delete(`/rag/delete/${ragId}`);
  },
};

export default api;

