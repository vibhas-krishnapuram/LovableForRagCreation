# RAG Creator API

**A tool to spin up custom RAG (Retrieval-Augmented Generation) API endpoints for your AI solutions—no code required.**

RAG Creator lets you upload documents and instantly create AI-powered question-answering APIs. Perfect for building internal tools, knowledge bases, or integrating AI into your applications.

---

## Vision

The end goal is to provide a complete platform where users can:
- Upload their documents (PDFs, Word docs, text files)
- Instantly create RAG API endpoints
- Query their documents using AI (Claude, GPT-4, etc.)
- Integrate these endpoints into their own apps and internal tools
- Manage multiple RAG instances from a simple dashboard
- Use it as a no-code RAG solution or as an API service

---

## Current Status

### What's Working Now
- **User Authentication** - JWT-based login/signup system
- **Document Upload** - Support for PDFs, DOCX, TXT files
- **RAG Creation** - Create RAG instances with uploaded documents
- **Vector Storage** - ChromaDB integration for semantic search
- **Multi-Model Support** - Claude (AWS Bedrock) and GPT-4 (OpenAI)
- **Query API** - REST endpoints to query your documents
- **User Isolation** - Each user's RAG instances are private
- **File Query** - Upload additional documents during queries
- **Web Frontend** - Modern React dashboard for managing RAG instances

### Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Tailwind CSS
- **Database**: SQLite + SQLAlchemy
- **Vector DB**: ChromaDB
- **Embeddings**: AWS Bedrock (Titan) or OpenAI
- **LLMs**: Claude 3 Sonnet, GPT-4 Mini
- **Auth**: JWT tokens

---

## In Progress

- **Code Refactoring** - Organizing into modular structure (services, routes, models)
- **Performance Optimization** - Caching embeddings and DB connections
- **API Documentation** - Comprehensive usage guide and examples

---

## Roadmap / TODO

### Backend Improvements
- Support for more file formats (CSV, Excel, Markdown)
- Implement rate limiting
- Add conversation history/memory
- Support for custom embedding models
- Streaming responses for long answers
- Document update/refresh functionality
- Multi-language support

### Frontend (Completed ✅)
- ✅ Web dashboard for managing RAGs
- ✅ Drag-and-drop file uploads
- ✅ Real-time query interface
- ✅ Document management
- ✅ User authentication UI

### Frontend (Future)
- API key management UI
- Usage analytics and monitoring
- Enhanced query history
- Export/import RAG configurations

### DevOps
- Docker containerization
- CI/CD pipeline
- Production deployment guide
- Monitoring and logging setup

---

## Current Architecture

```
User Authentication (JWT)
    ↓
Document Upload → Text Extraction → Chunking → Embeddings
    ↓
ChromaDB Storage (Vector Database)
    ↓
Query → Retrieve Relevant Chunks → LLM Processing → Response
```

---

## Current Project Structure

```
RAG_creator/
├── Backend/
│   ├── main.py             # Main FastAPI application
│   ├── auth/               # Authentication routes and services
│   ├── rag/                # RAG routes and services
│   ├── db/                 # Database models and CRUD operations
│   ├── config/             # Configuration (CORS, security)
│   ├── schemas/            # Pydantic models
│   └── utils/              # Utilities (file processing, RAG operations)
├── Frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts (Auth)
│   │   ├── services/       # API service layer
│   │   └── types/          # TypeScript types
│   └── package.json        # Frontend dependencies
├── RAG_MAKER.db           # SQLite database
├── rag_data/              # User uploaded documents
└── chroma_data/           # Vector database storage
```

## Quick Start

### Backend Setup

1. Navigate to the Backend directory
2. Install Python dependencies
3. Set up environment variables (`.env` file)
4. Run the FastAPI server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to the Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend at `http://localhost:8000`.

---

## Contributing

This is an active development project. Contributions, ideas, and feedback are welcome!

---

## Notes

- Currently optimized for development/testing
- Moving toward production-ready architecture
- Performance improvements being implemented (caching, connection pooling)
