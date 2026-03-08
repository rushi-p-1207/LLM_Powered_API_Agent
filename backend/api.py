import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ingestion.pdf_spider import PDFIngestionEngine
from RAG.chunking import MarkdownChunker
from RAG.vectorstore import VectorStore
from RAG.retriever import Retriever
from RAG.llm import SmartAPILLM
from backend.sandbox_client import SandboxClient

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="SmartAPI Agent", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global pipeline state ──────────────────────────────────────────────────────
retriever: Optional[Retriever] = None
llm: Optional[SmartAPILLM] = None
sandbox: Optional[SandboxClient] = None
store: Optional[VectorStore] = None
ingested_docs: List[dict] = []          # [{url, name}]

executor = ThreadPoolExecutor(max_workers=4)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global retriever, llm, sandbox, store
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _init_pipeline)

def _init_pipeline():
    global retriever, llm, sandbox, store
    print("Initialising pipeline...")
    store   = VectorStore(collection_name="openweather")
    retriever = Retriever(store)
    llm     = SmartAPILLM()
    sandbox = SandboxClient()
    print("Pipeline ready.")

# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_code(text: str) -> Optional[str]:
    match = re.search(r"```(python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(2).strip()
    return None

def _ingest_blocking(url: str) -> str:
    """Download → chunk → add to vector store. Returns doc name."""
    ingestor = PDFIngestionEngine(output_dir="api_docs_ingested")
    pdf_path = ingestor.ingest_pdf(url)
    if not pdf_path:
        raise RuntimeError("PDF ingestion failed – could not download or parse the PDF.")
    chunker = MarkdownChunker()
    chunks = chunker.chunk_json(json_path=pdf_path)
    if not chunks:
        raise RuntimeError("No text chunks extracted from the PDF.")
    store.add_chunks(chunks)
    return os.path.basename(pdf_path)

def _chat_blocking(query: str) -> dict:
    context = retriever.retrieve(query)
    if not context:
        return {
            "answer": "Sorry, no relevant information was found in the ingested documentation.",
            "code": None
        }
    answer = llm.generate_answer(context=context, query=query)
    code   = extract_code(answer)
    return {"answer": answer, "code": code}

def _execute_blocking(code: str) -> dict:
    result = sandbox.execute_code(code)
    if result.startswith("Error:") or result.startswith("Sandbox execution failed"):
        return {"error": result}
    return {"output": result}

# ── Request / Response models ─────────────────────────────────────────────────
class IngestRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    query: str

class ExecuteRequest(BaseModel):
    code: str

# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "pipeline_ready": retriever is not None,
        "ingested_count": len(ingested_docs),
    }

@app.get("/documents")
async def list_documents():
    return {"documents": ingested_docs}

@app.post("/ingest")
async def ingest(req: IngestRequest):
    if store is None:
        raise HTTPException(503, "Pipeline not ready yet.")
    try:
        loop = asyncio.get_event_loop()
        name = await loop.run_in_executor(executor, _ingest_blocking, req.url)
        entry = {"url": req.url, "name": name}
        # avoid duplicates
        if not any(d["url"] == req.url for d in ingested_docs):
            ingested_docs.append(entry)
        return {"message": f"Ingested '{name}' successfully.", "document": entry}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/chat")
async def chat(req: ChatRequest):
    if retriever is None or llm is None:
        raise HTTPException(503, "Pipeline not ready yet.")
    if not req.query.strip():
        raise HTTPException(400, "Query must not be empty.")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _chat_blocking, req.query)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/execute")
async def execute(req: ExecuteRequest):
    if sandbox is None:
        raise HTTPException(503, "Pipeline not ready yet.")
    if not req.code.strip():
        raise HTTPException(400, "Code must not be empty.")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _execute_blocking, req.code)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
