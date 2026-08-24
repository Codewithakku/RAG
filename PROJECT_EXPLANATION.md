# 🧠 RAG Project — Main Topics Explained

## 🎯 Project Shu Kare? (What does it do?)

**User PDF upload kare → Question puche → AI answer ape**

Simple shabdoma: Tu koi pan PDF document upload kari shake, pachhi tene lagta koi pan prashna puche, to system PDF mathi relevant information shodi ne Google Gemini AI thi intelligent answer ape.

---

## 🏗️ Architecture — Kevi rite kaam kare?

```
PDF Upload
    ↓
Text Extract (pypdf)
    ↓
Chunks banavo (LangChain Text Splitter)
    ↓
Vectors banavo (HuggingFace Embeddings)
    ↓
ChromaDB ma store karo
    ↓
User Question aave
    ↓
Question ne pan Vector banavo
    ↓
ChromaDB ma similar chunks shodo (Similarity Search)
    ↓
Gemini LLM ne context + question apo
    ↓
Final Answer!
```

---

## 📚 Main Topics — Ek Ek Samjiye

---

### 1️⃣ RAG (Retrieval-Augmented Generation)

**Shu che?**
AI ne direct train karvane badle, pehla relevant documents mathi information retrieve (shodo) karo, pachhi AI thi answer generate karo.

**Problem jo RAG na hoy:**

- Gemini ne tara PDF ni khabar nathi
- Direct puchho to hallucination (bakwas answer) aave

**RAG thi:**

- Pehla PDF mathi relevant text shodo
- Pachhi te text + question Gemini ne do
- Gemini accurate, grounded answer ape

**Real-life example:**

> Tu puche: _"PDF ma chunking kevi rite kaam kare?"_
> RAG: PDF mathi top-3 relevant paragraphs shode → Gemini ne do → Gemini correct answer ape ✅

---

### 2️⃣ LangChain

**Shu che?**
Ek Python framework jo badha AI components ne ek saathe connect kare.

**Apda project ma shu kare?**
| Component | Kaam |
|---|---|
| `PyPDFLoader` | PDF mathi text kadhe |
| `RecursiveCharacterTextSplitter` | Text ne 500 char na chunks ma kape |
| `ChatGoogleGenerativeAI` | Gemini LLM ne connect kare |
| `RAG Chain` | Retrieve + Generate pipeline banave |

**Analogy:**
LangChain = **Supervisor** jo badha tools ne manage kare (PDF reader, Vector DB, LLM badha ek chain ma joday)

---

### 3️⃣ ChromaDB

**Shu che?**
Local Vector Database — tara computer par j save thay, koi cloud nahi.

**Shu store kare?**
Text chunks ne **vectors (numbers)** ma convert kari store kare.

**Example:**

> "Chunking is the process of splitting text"
> → [0.23, -0.45, 0.67, 0.12, ...] (384 numbers!)
> → ChromaDB ma save

**Similarity Search kevi rite kare?**

- User question → vector banavo
- ChromaDB ma badha vectors saathe compare karo
- Sabse "similar" (close) vectors return kare
- Te = most relevant text chunks!

**Analogy:**
ChromaDB = **Smart Library** jo books content understand kari indexed rakhe. Tu koi concept puchhe to similar books instantly shodi kade.

---

### 4️⃣ HuggingFace Embeddings (`all-MiniLM-L6-v2`)

**Shu che?**
Ek AI model jo **text ne numbers (vectors) ma convert** kare.

**Apda project ma:**

- Model: `all-MiniLM-L6-v2`
- Output: 384 numbers per sentence
- Locally run thay (no internet needed after download)

**Kevo kaam kare?**

| Text                 | Vector (simplified)                 |
| -------------------- | ----------------------------------- |
| "cat sits on mat"    | [0.2, 0.8, -0.1, ...]               |
| "kitten on carpet"   | [0.19, 0.79, -0.09, ...] ← similar! |
| "python programming" | [0.9, -0.3, 0.5, ...] ← different!  |

**Analogy:**
Embedding model = **Translator** jo human language ne math language ma badlav kare jene computer compare kari shake.

---

### 5️⃣ Google Gemini (LLM)

**Shu che?**
Google nu powerful AI language model — ChatGPT jaisa pan Google nu.

**Apda project ma:**

- Model: `gemini-2.0-flash`
- Kaam: RAG thi mela relevant chunks + user question laine final answer generate kare
- API key thi access thay (free tier available)

**RAG without Gemini vs with Gemini:**

| Without RAG                   | With RAG                     |
| ----------------------------- | ---------------------------- |
| Gemini ne PDF ni khabar nathi | Context (chunks) apiye chiye |
| Hallucination thay            | Accurate, grounded answers   |
| Generic answers               | PDF-specific answers         |

---

### 6️⃣ FastAPI (Backend)

**Shu che?**
Python web framework — REST API banave jo frontend saathe baat kare.

**Apda project na endpoints:**
| Endpoint | Kaam |
|---|---|
| `POST /api/documents/upload` | PDF upload karo |
| `GET /api/documents` | Badha PDFs list karo |
| `DELETE /api/documents/{id}` | PDF delete karo |
| `POST /api/query` | Question pucho, answer melo |
| `GET /api/health` | Server chalu che ke nahi check karo |

**Analogy:**
FastAPI = **Receptionist** jo frontend ni requests receive kare ne backend services ne forward kare.

---

### 7️⃣ React + Vite (Frontend)

**Shu che?**

- **React**: UI banava nu JavaScript library (Facebook nu)
- **Vite**: React app fast run karvanu tool

**Apda project na components:**
| Component | Kaam |
|---|---|
| `Header.jsx` | App nu top bar, settings button |
| `DocumentManager.jsx` | PDF upload, list, delete UI |
| `QueryConsole.jsx` | Question type karo, answer dekho |
| `SettingsModal.jsx` | API key, model select karo |

**Frontend → Backend Connection:**
Vite proxy use kare — `/api/...` automatically `localhost:8000` par jaay.

---

### 8️⃣ Chunking (Text Splitting)

**Shu che?**
PDF no badho text ek saath process na thay, eTle chhota-chhota pieces (chunks) ma kapi nakho.

**Apda project ma settings:**

- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters (consecutive chunks ma common text hoy jeThi context na tute)

**Example:**

```
Original: "LangChain is a framework... [2000 chars]"

Chunk 1: "LangChain is a framework for..." [500 chars]
Chunk 2: "...for building AI apps..." [500 chars]  ← 50 chars overlap
Chunk 3: "...AI apps with LLMs..." [500 chars]
```

---

## 🔄 Complete Flow — Ek Vaar Badhu Saathe

```
👤 User: PDF upload kare
    ↓
📄 pypdf: Text extract kare
    ↓
✂️ LangChain Splitter: 500-char chunks banave
    ↓
🔢 HuggingFace Model: Chunks → 384-dim vectors
    ↓
🗄️ ChromaDB: Vectors store kare (locally)

---

👤 User: Question type kare
    ↓
🔢 HuggingFace Model: Question → vector
    ↓
🗄️ ChromaDB: Top-3 similar chunks shode
    ↓
📝 LangChain: Prompt banave (context + question)
    ↓
🤖 Gemini API: Answer generate kare
    ↓
⚡ FastAPI: Response frontend ne mokle
    ↓
🖥️ React UI: Answer display kare
```

---

## 📊 Technology Stack Summary

| Layer            | Technology                   | Version    |
| ---------------- | ---------------------------- | ---------- |
| Frontend         | React + Vite                 | 18.x / 5.x |
| Backend          | FastAPI + Uvicorn            | 0.109+     |
| AI Orchestration | LangChain                    | 0.2+       |
| Vector DB        | ChromaDB                     | 0.4+       |
| Embeddings       | HuggingFace all-MiniLM-L6-v2 | -          |
| LLM              | Google Gemini 2.0 Flash      | -          |
| PDF Processing   | pypdf + PyPDFLoader          | 4.0+       |
