# SyntaxHub 🚀

**SyntaxHub** is an AI-powered code analysis, snippet management, and RAG (Retrieval-Augmented Generation) workspace platform.

---

## 📁 Repository Structure

```
syntax-hub/
├── client/          # Next.js 16 + React 19 Frontend (Port 3000)
├── server/          # Node.js + Express + MongoDB Backend API (Port 5000)
└── services/        # Python FastAPI AI / RAG / LLM / ChromaDB Service (Port 8000)
```

### 1. `client/` (Frontend)
- **Framework**: Next.js 16 (App Router), React 19, TypeScript
- **Styling**: Tailwind CSS v4, Lucide Icons, Base UI / Shadcn
- **API Helpers**: Integrated `client/lib/api.ts` connecting to Backend & AI services.

### 2. `server/` (Backend API)
- **Framework**: Node.js & Express.js
- **Database**: MongoDB via Mongoose ORM
- **Features**:
  - Authentication (JWT login/register)
  - Code Snippets & Project Management
  - AI Proxy Controller forwarding requests to Python AI Service

### 3. `services/` (AI & RAG Microservice)
- **Framework**: Python 3.10+ & FastAPI
- **Vector DB**: ChromaDB (`chromadb`) persistent vector storage
- **AI/LLM Stack**: Google Gemini / OpenAI / Ollama integration, Code Embeddings (`sentence-transformers`), RAG Engine

---

## ⚡ Quick Start (Local Development)

### Prerequisites
- Node.js 18+ & pnpm / npm
- Python 3.10+ & `pip`
- MongoDB running locally on `mongodb://localhost:27017` (or Docker)

### Installation & Launch

1. **Install dependencies for all services**:
   ```bash
   npm run install:all
   ```

2. **Configure environment variables**:
   - Copy `.env.example` to `.env` in `server/` and `services/`
   - Set `GEMINI_API_KEY` or `OPENAI_API_KEY` in `services/.env`

3. **Run services concurrently**:
   ```bash
   # Run Frontend (Next.js)
   npm run dev:client

   # Run Backend (Express API)
   npm run dev:server

   # Run AI Microservice (FastAPI)
   npm run dev:services
   ```

---

## 🐳 Docker Deployment

Run all services including MongoDB and ChromaDB using Docker Compose:
```bash
docker-compose up --build
```
- **Client**: `http://localhost:3000`
- **Server API**: `http://localhost:5000/api`
- **AI Service Docs (Swagger)**: `http://localhost:8000/docs`
