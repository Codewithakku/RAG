import os

def create_simple_pdf(filename="sample_rag_guide.pdf"):
    """Generates a sample PDF document for testing the RAG application."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Sample RAG Architecture & AI Guide")
        
        c.setFont("Helvetica", 11)
        text_lines = [
            "1. Introduction to Retrieval-Augmented Generation (RAG)",
            "Retrieval-Augmented Generation (RAG) combines dense vector search with large language models.",
            "Instead of relying solely on pre-trained parametric knowledge, RAG retrieves contextually relevant",
            "document passages from a vector database like ChromaDB.",
            "",
            "2. Document Processing and Chunking Strategy",
            "In this implementation plan, PDF documents are processed using LangChain's PyPDFLoader.",
            "The raw text is divided into manageable chunks using RecursiveCharacterTextSplitter.",
            "The configured Chunk Size is exactly 500 characters, with a Chunk Overlap of 50 characters.",
            "Chunking ensures that semantic meaning is preserved across document boundaries.",
            "",
            "3. Vector Embeddings with Hugging Face",
            "The text chunks are transformed into dense vector embeddings using Hugging Face.",
            "The selected embedding model is all-MiniLM-L6-v2, which maps text into a 384-dimensional vector space.",
            "These embeddings are stored locally inside a persistent ChromaDB database folder.",
            "",
            "4. Similarity Search and Top K Retrieval",
            "When a user submits a natural language question, the system computes the question embedding.",
            "ChromaDB performs a similarity search to retrieve the Top K = 3 most relevant document chunks.",
            "These 3 context chunks are supplied directly to the prompt template.",
            "",
            "5. Google Gemini LLM Integration",
            "The retrieved context and user question are formatted into a simple context-based prompt.",
            "Google Gemini (configurable model e.g. gemini-2.0-flash) generates a precise answer.",
            "If the answer cannot be found in the retrieved context, Gemini states that the context is insufficient."
        ]
        
        y = height - 90
        for line in text_lines:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
            c.drawString(50, y, line)
            y -= 18
            
        c.save()
        print(f"Successfully generated ReportLab PDF: {filename}")
        return True
    except ImportError:
        # Fallback to fpdf or basic PDF binary builder if reportlab is not installed
        pass

    # Fallback basic PDF generator using standard library string stream
    pdf_content = (
        "%PDF-1.4\n"
        "1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        "2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        "3 0 obj <</Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R>> endobj\n"
        "4 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        "5 0 obj <</Length 650>> stream\n"
        "BT /F1 16 Tf 50 740 Td (Sample RAG System & AI Guide) Tj ET\n"
        "BT /F1 10 Tf 50 710 Td (1. Retrieval-Augmented Generation Overview) Tj ET\n"
        "BT /F1 10 Tf 50 690 Td (RAG enables Large Language Models to answer questions grounded in PDF documents.) Tj ET\n"
        "BT /F1 10 Tf 50 670 Td (2. Document Chunking Parameters) Tj ET\n"
        "BT /F1 10 Tf 50 650 Td (Documents are loaded via PyPDFLoader and split with RecursiveCharacterTextSplitter.) Tj ET\n"
        "BT /F1 10 Tf 50 630 Td (Chunk Size is 500 characters and Chunk Overlap is 50 characters.) Tj ET\n"
        "BT /F1 10 Tf 50 610 Td (3. Hugging Face Embeddings & ChromaDB) Tj ET\n"
        "BT /F1 10 Tf 50 590 Td (Text chunks are embedded using all-MiniLM-L6-v2 into 384-dimensional vectors.) Tj ET\n"
        "BT /F1 10 Tf 50 570 Td (ChromaDB persists vector data locally in ./chroma_db directory.) Tj ET\n"
        "BT /F1 10 Tf 50 550 Td (4. Retrieval Top K and Google Gemini Answer) Tj ET\n"
        "BT /F1 10 Tf 50 530 Td (Similarity search retrieves Top K = 3 matching context chunks for Google Gemini LLM.) Tj ET\n"
        "endstream\n"
        "endobj\n"
        "xref\n"
        "0 6\n"
        "0000000000 65535 f \n"
        "0000000009 00000 n \n"
        "0000000062 00000 n \n"
        "0000000117 00000 n \n"
        "0000000242 00000 n \n"
        "0000000315 00000 n \n"
        "trailer <</Size 6 /Root 1 0 R>>\n"
        "startxref\n"
        "1020\n"
        "%%EOF\n"
    )
    with open(filename, "wb") as f:
        f.write(pdf_content.encode("latin-1"))
    print(f"Successfully generated sample PDF: {filename}")
    return True

if __name__ == "__main__":
    create_simple_pdf()
