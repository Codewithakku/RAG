# 🧠 RAG PDF Intelligence Studio

A full-stack **Retrieval-Augmented Generation (RAG)** application for question-answering over PDF documents using **LangChain**, **ChromaDB**, **Hugging Face Embeddings (`all-MiniLM-L6-v2`)**, **Google Gemini (`gemini-3.6-flash`)**, **FastAPI**, and a **React (Vite)** Glassmorphism UI.

---

## 🌟 Key Features & Specifications

- 📄 **PDF Processing**: Upload, update, delete, and list PDF documents (`PyPDFLoader` + `pypdf` fallback).
- ✂️ **Recursive Chunking**: Configured with `Chunk Size = 500` characters and `Chunk Overlap = 50` characters.
- 🔤 **Dense Vector Embeddings**: Hugging Face `all-MiniLM-L6-v2` embedding model (384-dimensional vector space).
- 🗄️ **Local Vector Database**: Persistent local ChromaDB database stored in `./backend/chroma_db`.
- 🔍 **Similarity Search**: Top `K = 3` context chunk retrieval using cosine vector similarity.
- 🤖 **Google Gemini LLM**: Context-grounded response generation using `gemini-3.6-flash` via `ChatGoogleGenerativeAI`.
- 🎨 **Modern React UI**: Built with Vite, Tailwind/Glassmorphism dark theme, document manager, query console, and settings modal.

---

## 📁 Repository Structure

```
RAG-code/
├── README.md                 # Setup guide and instructions for running on any machine
├── .gitignore                # Git ignore rules for node_modules, venv, and local db
├── create_sample_pdf.py      # Utility script to generate a sample testing PDF file
├── backend/
│   ├── main.py               # FastAPI REST API endpoints
│   ├── requirements.txt      # Python backend dependencies
│   ├── .env.example          # Sample environment configuration
│   └── app/
│       ├── config.py         # App configuration settings
│       ├── document_processor.py # PDF Loading & Recursive Character Splitting (500/50)
│       ├── embeddings.py     # Hugging Face all-MiniLM-L6-v2 embeddings
│       ├── vector_store.py   # ChromaDB Vector Store & Document Management
│       └── rag_chain.py      # Gemini LLM + Simple RAG Prompt Pipeline
└── frontend/
    ├── package.json          # React & Vite dependencies
    ├── vite.config.js        # Vite config with backend API proxy
    ├── index.html            # Main HTML file
    └── src/
        ├── index.css         # Modern glassmorphic theme styling
        ├── App.jsx           # Main React layout
        └── components/
            ├── Header.jsx          # Specs badges & settings trigger
            ├── DocumentManager.jsx # PDF Upload, Update, Delete & List
            ├── QueryConsole.jsx    # Question input, Top K selector & Gemini Answer
            └── SettingsModal.jsx   # Gemini API Key & Model Configuration
```

---

## 💻 Step-by-Step Setup Guide (Running on a Second Computer)

Follow these step-by-step instructions to set up and run this application on any computer.

### Prerequisites

- **Git**
- **Python** (version 3.10 or higher)
- **Node.js** (version 18 or higher)
- **Google Gemini API Key** ([Get your API key from Google AI Studio](https://aistudio.google.com/))

---

### Step 1: Clone the Repository

Open your terminal or command prompt and clone the repository:

```bash
git clone https://github.com/Codewithakku/RAG.git
cd RAG
```

---

### Step 2: Set Up Python Backend

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Create a Python Virtual Environment**:
   - **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Python Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the `backend/` directory by copying `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Open `.env` and add your Google Gemini API Key:

   ```env
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-3.6-flash
   CHROMA_DB_DIR=./chroma_db
   CHUNK_SIZE=500
   CHUNK_OVERLAP=50
   TOP_K=3
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

5. **Start the FastAPI Backend Server**:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```
   _The backend will start running on `http://localhost:8000`._

---

### Step 3: Set Up React Frontend

1. **Open a new terminal window** and navigate to the `frontend/` directory:

   ```bash
   cd RAG/frontend
   ```

2. **Install Node Dependencies**:

   ```bash
   npm install
   ```

3. **Start the Vite Frontend Development Server**:
   ```bash
   npm run dev
   ```
   _The frontend will start running on `http://localhost:5173`._

---

### Step 4: Open and Test the Application

1. Open your browser and navigate to **[http://localhost:5173](http://localhost:5173)**.
2. In the **Document Storage Manager** panel on the left, upload any PDF document (or run `python create_sample_pdf.py` in the root folder to generate `sample_rag_guide.pdf`).
3. In the **RAG Query Console** on the right, type your question (e.g. _"What is the chunk size?"_) and click **Ask Gemini**.
4. The system will perform Similarity Search (Top K = 3) on ChromaDB, inject the context into `gemini-3.6-flash`, and return a context-grounded response alongside matching source chunks!

---

## 📡 API Endpoints Summary

| Method   | Endpoint                  | Description                                                                       |
| :------- | :------------------------ | :-------------------------------------------------------------------------------- |
| `GET`    | `/api/health`             | Health status and API key configuration check                                     |
| `GET`    | `/api/documents`          | List indexed PDF documents and chunk counts in ChromaDB                           |
| `POST`   | `/api/documents/upload`   | Upload PDF file -> chunk (500/50) -> embed (`all-MiniLM-L6-v2`) -> store ChromaDB |
| `PUT`    | `/api/documents/{doc_id}` | Re-upload PDF -> update document chunks in ChromaDB                               |
| `DELETE` | `/api/documents/{doc_id}` | Delete document and chunks from ChromaDB                                          |
| `POST`   | `/api/query`              | Retrieve Top K (3) context chunks -> run Gemini LLM -> return answer & sources    |

---

## 📄 License

MIT License. Free to use and modify for educational and production purposes.
