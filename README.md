# 🧠 RAG PDF Intelligence Studio

A full-stack **Retrieval-Augmented Generation (RAG)** application for question-answering over PDF documents using **LangChain**, **ChromaDB**, **Hugging Face Embeddings**, **Google Gemini**, **FastAPI**, and **React (Vite)**.

---

## 🌟 Key Features

- 📄 Upload, update, delete PDF documents
- ✂️ Auto chunking (Size: 500, Overlap: 50)
- 🔤 HuggingFace `all-MiniLM-L6-v2` embeddings
- 🗄️ Local ChromaDB vector database
- 🔍 Top-K similarity search
- 🤖 Google Gemini LLM answers
- 🎨 Modern React Glassmorphism UI

---

## 📁 Project Structure

```
RAG-code/
├── setup.bat               ← Run this FIRST on new computer (Windows)
├── start_app.bat           ← Run this to START the app (Windows)
├── docker-compose.yml      ← Run with Docker (any OS)
├── backend/
│   ├── main.py             ← FastAPI server
│   ├── requirements.txt    ← Python packages
│   ├── .env.example        ← Copy this to .env and add API key
│   └── app/
│       ├── config.py
│       ├── document_processor.py
│       ├── embeddings.py
│       ├── vector_store.py
│       └── rag_chain.py
└── frontend/
    ├── package.json        ← Node.js packages
    ├── vite.config.js      ← Vite + API proxy config
    └── src/
        ├── App.jsx
        └── components/
```

---

## 🚀 How to Run (3 Methods)

---

### ✅ Method 1: Windows One-Click (Easiest)

> **Prerequisites:** Install [Python 3.10+](https://python.org) and [Node.js 18+](https://nodejs.org) only

**Step 1 — Clone the repo:**
```bash
git clone https://github.com/Codewithakku/RAG.git
cd RAG
```

**Step 2 — Run setup (only ONCE on new computer):**
```
Double-click: setup.bat
```
This will:
- ✅ Check Python & Node.js
- ✅ Create Python virtual environment
- ✅ Install all Python packages (`pip install -r requirements.txt`)
- ✅ Install Node packages (`npm install`)
- ✅ Open `.env` file for you to add API key

**Step 3 — Add your Gemini API Key in `backend/.env`:**
```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```
> Get free API key from: https://aistudio.google.com/

**Step 4 — Start the app:**
```
Double-click: start_app.bat
```
Browser will open automatically at **http://localhost:5173** 🎉

---

### 🐳 Method 2: Docker (Any OS — Windows/Mac/Linux)

> **Prerequisites:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) only

**Step 1 — Clone the repo:**
```bash
git clone https://github.com/Codewithakku/RAG.git
cd RAG
```

**Step 2 — Create `.env` file:**
```bash
cp backend/.env.example backend/.env
# Open backend/.env and add your GOOGLE_API_KEY
```

**Step 3 — Run with Docker:**
```bash
docker-compose up --build
```

Open browser: **http://localhost:5173** 🎉

**Stop the app:**
```bash
docker-compose down
```

---

### 🛠️ Method 3: Manual Setup (Any OS)

**Prerequisites:**
- Python 3.10+
- Node.js 18+
- Google Gemini API Key

**Terminal 1 — Backend:**
```bash
git clone https://github.com/Codewithakku/RAG.git
cd RAG/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# Add your GOOGLE_API_KEY in .env

# Start backend
python main.py
```

**Terminal 2 — Frontend:**
```bash
cd RAG/frontend
npm install
npm run dev
```

Open browser: **http://localhost:5173** 🎉

---

## 📡 API Endpoints

| Method   | Endpoint                  | Description                        |
| :------- | :------------------------ | :--------------------------------- |
| `GET`    | `/api/health`             | Health check & API key status      |
| `GET`    | `/api/documents`          | List all indexed PDFs              |
| `POST`   | `/api/documents/upload`   | Upload & index a PDF               |
| `PUT`    | `/api/documents/{doc_id}` | Update an existing PDF             |
| `DELETE` | `/api/documents/{doc_id}` | Delete a PDF from vector store     |
| `POST`   | `/api/query`              | Ask a question (RAG query)         |

- **API Docs (Swagger):** http://localhost:8000/docs

---

## ⚙️ Environment Variables (`backend/.env`)

| Variable          | Description                          | Default              |
| :---------------- | :----------------------------------- | :------------------- |
| `GOOGLE_API_KEY`  | **Required** — Google Gemini API Key | -                    |
| `GEMINI_MODEL`    | Gemini model to use                  | `gemini-2.0-flash`   |
| `CHROMA_DB_DIR`   | ChromaDB storage path                | `./chroma_db`        |
| `CHUNK_SIZE`      | PDF chunk size (characters)          | `500`                |
| `CHUNK_OVERLAP`   | Chunk overlap                        | `50`                 |
| `TOP_K`           | Number of chunks for similarity search | `3`                |
| `EMBEDDING_MODEL` | HuggingFace embedding model          | `all-MiniLM-L6-v2`  |

---

## 📄 License

MIT License — Free to use for educational and production purposes.
