# SyntaxHub 🚀

**SyntaxHub** is an AI-powered code analysis, snippet management, and RAG (Retrieval-Augmented Generation) workspace platform. It detects outdated patterns in your Java, React, JavaScript, and Python code against official documentation using ChromaDB vector search and Pollinations AI (free, no API key needed).

> 🌐 **Live Demo**: [https://syntax-hub.vercel.app](https://syntax-hub.vercel.app)

---

## 📁 Project Structure

```
Syntax_Hub-main/
├── client/          # Next.js 16 + React 19 Frontend        → Port 3000
├── server/          # Node.js + Express + MongoDB Backend    → Port 5000
├── services/        # Python FastAPI + ChromaDB AI Service  → Port 8000
├── dev.js           # Orchestrator: starts all 3 servers at once
├── package.json     # Root scripts (npm run dev)
└── docker-compose.yml
```

---

## ✅ Prerequisites

Before running, make sure you have these installed:

| Tool | Version | Download |
|------|---------|----------|
| **Node.js** | 18+ | https://nodejs.org |
| **Python** | 3.10+ | https://python.org |
| **MongoDB** | Community 7+ | https://www.mongodb.com/try/download/community |
| **Git** | any | https://git-scm.com |

> **MongoDB** must be running locally on `mongodb://localhost:27017` before starting the project.

---

## 🚀 How to Run Locally (VS Code)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/SamikshaPharakate/SyantaxHub.git
cd SyantaxHub
```

### Step 2 — Install All Dependencies

```bash
npm run install:all
```

This installs:
- Node.js packages for `client/` (Next.js)
- Node.js packages for `server/` (Express)
- Python packages for `services/` (FastAPI, ChromaDB, sentence-transformers)

> ⚠️ If Python venv fails on Windows, manually run:
> ```bash
> cd services
> python -m venv .venv
> .venv\Scripts\pip install -r requirements.txt
> cd ..
> ```

### Step 3 — Configure Environment Variables

Copy the example env file:
```bash
copy .env.example .env
```

Edit `.env` and set at minimum:
```env
MONGO_URI=mongodb://localhost:27017/syntaxhub
JWT_SECRET=syntaxhub_secret_key_2024
```

> 💡 **AI works without any API keys!** The chatbot uses Pollinations AI (free, no key needed).  
> Optionally add `OPENROUTER_API_KEY` in `services/.env` for premium LLM results.

### Step 4 — Start MongoDB

Make sure MongoDB is running:
```bash
# Windows (if installed as service, it auto-starts)
# Or start manually:
mongod --dbpath "C:\data\db"
```

### Step 5 — Run All Servers at Once

```bash
npm run dev
```

This starts **all 3 servers simultaneously**:

| Server | URL | Description |
|--------|-----|-------------|
| 🌐 Next.js Frontend | http://localhost:3000 | Main app UI |
| ⚙️ Express Backend | http://localhost:5000 | REST API + Auth + MongoDB |
| 🤖 Python AI Service | http://localhost:8000 | ChromaDB RAG + AI analysis |
| 📖 AI Swagger Docs | http://localhost:8000/docs | API documentation |

### Step 6 — Open the App

Open your browser and go to:
```
http://localhost:3000
```

---

## 🔧 Individual Server Commands

If you want to run servers separately (3 separate terminals):

```bash
# Terminal 1 — Frontend (Next.js)
npm run dev:client

# Terminal 2 — Backend (Express + MongoDB)
npm run dev:server

# Terminal 3 — AI Service (Python FastAPI)
npm run dev:services
```

---

## 🌍 Deployment

### Frontend — Vercel (Free)

The Next.js client is deployed on Vercel:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from the client directory
cd client
vercel --prod
```

Or deploy via **Vercel Dashboard**:
1. Go to https://vercel.com/new
2. Import your GitHub repo: `SamikshaPharakate/SyantaxHub`
3. Set **Root Directory** → `client`
4. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL` = your Express backend URL
   - `NEXT_PUBLIC_AI_SERVICE_URL` = your Python service URL
5. Click **Deploy**

### Backend — Render.com (Free)

Deploy the Express server on [Render](https://render.com):

1. New → **Web Service** → Connect your GitHub repo
2. **Root Directory**: `server`
3. **Build Command**: `npm install`
4. **Start Command**: `node src/server.js`
5. Add Environment Variables:
   - `MONGO_URI` = your MongoDB Atlas connection string
   - `JWT_SECRET` = your secret key
   - `AI_SERVICE_URL` = your Python service URL on Render

### Python AI Service — Render.com (Free)

1. New → **Web Service** → Connect your GitHub repo
2. **Root Directory**: `services`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python main.py`

### Database — MongoDB Atlas (Free)

1. Go to https://cloud.mongodb.com
2. Create a free cluster
3. Get your connection string:
   ```
   mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/syntaxhub
   ```
4. Add it as `MONGO_URI` in Render environment variables

---

## 🐳 Docker (All-in-One)

Run everything including MongoDB with Docker:

```bash
docker-compose up --build
```

---

## 🤖 AI Features (No API Key Needed!)

SyntaxHub uses a **3-tier AI fallback chain**:

1. 🥇 **Express Backend → Python FastAPI + ChromaDB RAG** (best, uses vector docs)
2. 🥈 **Direct Python AI Microservice** (FastAPI fallback)
3. 🥉 **Pollinations.ai free LLM** (browser-direct, **always works**, zero API key)

This means the **AI Chat and Code Analysis work even without any paid API keys**.

---

## 🧪 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | Node.js, Express.js, MongoDB, Mongoose, JWT |
| AI Service | Python, FastAPI, ChromaDB, sentence-transformers |
| AI/LLM | Pollinations AI (free), OpenRouter, Google Gemini |
| Vector DB | ChromaDB (persistent local storage) |
| Deployment | Vercel (frontend), Render (backend + AI) |

---

## 📬 Support

If you run into issues:
- Check that **MongoDB is running** before starting servers
- Check the terminal for error messages
- The AI chat works even if backend servers are down (uses Pollinations.ai directly)

---

*Built with ❤️ — SyntaxHub AI-Powered Code Intelligence Platform*
