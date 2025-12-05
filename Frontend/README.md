# RAG Creator Frontend

A modern React frontend for the RAG Creator application, built with TypeScript, Vite, and Tailwind CSS.

## Features

- **User Authentication**: Login and signup with JWT token management
- **Dashboard**: View and manage all your RAG instances
- **Create RAG**: Upload documents and create new RAG instances
- **Query Interface**: Ask questions about your documents with AI-powered responses
- **Document Management**: Add additional documents to existing RAG instances
- **Modern UI**: Beautiful, responsive design with Tailwind CSS

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

1. Navigate to the Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional):
```bash
VITE_API_URL=http://localhost:8000
```

If you don't create a `.env` file, the app will default to `http://localhost:8000`.

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### Build

Build for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
Frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── CreateRAG.tsx
│   │   ├── QueryRAG.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/         # React contexts
│   │   └── AuthContext.tsx
│   ├── services/         # API services
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html            # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Usage

1. **Sign Up/Login**: Create an account or login with existing credentials
2. **Create RAG**: Upload documents (PDF, DOCX, TXT) and create a RAG instance
3. **Query**: Ask questions about your documents and get AI-powered answers
4. **Manage**: View, add documents to, or delete your RAG instances

## API Integration

The frontend communicates with the FastAPI backend at the configured API URL. All API calls include JWT authentication tokens automatically.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

