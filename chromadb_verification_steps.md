# Step 1 — Go to Backend Folder

Open CMD and run:

```
cd "C:\Raval Aakash\intership-task\RAG-code\backend"
```

---

# Step 2 — Activate Virtual Environment

```
venv\Scripts\activate
```

Expected:

```
(venv) C:\Raval Aakash\intership-task\RAG-code\backend>
```

---

# Step 3 — Verify ChromaDB Installation

```
pip show chromadb
```

Expected:

```
Name: chromadb
Version: 1.5.9
```

---

# Step 4 — Start Python

```
python
```

Expected:

```
>>>
```

---

# Step 5 — Import ChromaDB

```
import chromadb
```

If there is no error, ChromaDB is successfully imported.

---

# Step 6 — Connect to Local ChromaDB

Our database path is:

```
./chroma_db
```

Run:

```
client = chromadb.PersistentClient(path="./chroma_db")
```

---

# Step 7 — Check Collections

```
print(client.list_collections())
```

Expected:

```
[Collection(name=rag_documents)]
```

---

# Step 8 — Get the Collection

Our collection name is:

```
rag_documents
```

Run:

```
collection = client.get_collection("rag_documents")
```

---

# Step 9 — Check Total Chunks

```
print(collection.count())
```

Example:

```
97
```

This means the collection contains 97 stored records/chunks.

---

# Step 10 — Get Documents, Metadata and Embeddings

```
data = collection.get(
    include=["documents", "metadatas", "embeddings"]
)
```

The returned data contains:

```
data
├── ids
├── documents
├── metadatas
└── embeddings
```

---

# Step 11 — View Metadata

To view metadata of the first record:

```
print(data["metadatas"][0])
```

Example:

```
{'source': 'example.pdf', 'page': 1}
```

---

# Step 12 — View Embedding

To view the first record's embedding:

```
print(data["embeddings"][0])
```

Example:

```
[0.0342, -0.1287, 0.0561, ...]
```
