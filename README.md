# LLM-Powered SmartAPI Agent

An AI-powered assistant that ingests API documentation PDFs, answers questions using RAG (Retrieval-Augmented Generation), and executes generated code in a sandboxed environment.



## Quick Start

Open **three separate terminal windows** and run the following commands in order:

### 1. Sandbox (port 9000)

```bash
export PATH="/opt/anaconda3/envs/smartapi/bin:$PATH"
cd sandbox
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

### 2. Backend API (port 8000)

```bash
export PATH="/opt/anaconda3/envs/smartapi/bin:$PATH"
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

> On startup the backend initialises the RAG pipeline (vector store, embeddings, LLM). This takes ~10 seconds. Wait for `Pipeline ready.` in the logs.

### 3. Frontend (port 5173)

```bash
export PATH="/opt/anaconda3/envs/smartapi/bin:$PATH"
cd frontend
npx vite --host 0.0.0.0 --port 5173
```

Then open **http://localhost:5173** in your browser.

## Usage

1. **Ingest a PDF** — In the left sidebar, paste any PDF URL and click **Ingest Document**
2. **Ask questions** — Type a question in the chat panel about the ingested documentation
3. **Run code** — If the LLM generates code, it auto-populates in the Monaco editor on the right. Edit it if needed, then click **RUN** (or press `⌘+Enter`)
4. **View output** — Sandbox results appear in the Terminal Output panel below the editor


## Project Structure

```
├── backend/
│   ├── api.py              # FastAPI server (main backend)
│   ├── main.py             # Original CLI chat loop
│   └── sandbox_client.py   # HTTP client for the sandbox
├── frontend/
│   ├── src/
│   │   ├── api.ts          # Typed API client
│   │   ├── App.tsx         # Main 3-panel layout
│   │   └── components/     # TopNav, LeftSidebar, ChatPanel, RightPanel
│   └── ...
├── sandbox/
│   ├── app.py              # FastAPI sandbox server
│   └── sandbox_service.py  # Code execution engine
├── RAG/
│   ├── chunking.py         # PDF → text chunks
│   ├── vectorstore.py      # ChromaDB vector store
│   ├── retriever.py        # Similarity search
│   ├── llm.py              # HuggingFace DeepSeek LLM
│   └── embeddings.py       # Sentence transformer embeddings
├── ingestion/
│   └── pdf_spider.py       # PDF download + OCR extraction
├── server.ts               # Deno proxy (legacy)
└── .env                    # API tokens
```
