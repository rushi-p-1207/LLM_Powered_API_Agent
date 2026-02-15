import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pdf_spider import PDFIngestionEngine
from RAG.chunking import MarkdownChunker
from RAG.vectorstore import VectorStore
from RAG.retriever import Retriever
from RAG.llm import SmartAPILLM

from backend.sandbox_client import SandboxClient
import re

PDF_URL = "https://openweathermap.org/themes/openweathermap/assets/docs/Using_OpenWeatherMap_Weather_Tiles_with_Leaflet.pdf"

def setup_pipeline():
    #ingest pdf
    print("Ingesting PDF...")
    ingestor = PDFIngestionEngine(output_dir="api_docs_ingested")
    pdf_path = ingestor.ingest_pdf(PDF_URL)

    if not pdf_path:
        raise RuntimeError("PDF ingestion failed")

    #chunking
    print("Chunking PDF...")
    chunker = MarkdownChunker()
    chunks = chunker.chunk_json(json_path=pdf_path)

    if not chunks:
        raise RuntimeError("No chunks generated from PDF")

    #vectorstore
    print("Creating vector store...")
    store = VectorStore(collection_name="openweather")
    store.add_chunks(chunks)

    #retriver
    retriever = Retriever(store)

    #llm
    llm = SmartAPILLM()

    #sandbox
    sandbox = SandboxClient()

    return retriever, llm, sandbox

def extract_code(text):
    # Regex to find code blocks, optionally with 'python' language specifier
    match = re.search(r"```(python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(2).strip()
    return None

def chat_loop(retriever, llm, sandbox):
    print("\n===== Welcome to SmartAPI Chat =====")
    print("Type 'exit' to quit.\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ["exit", "quit"]:
            print("Exiting chat. Goodbye!")
            break

        # Retrieve context from vector store
        context = retriever.retrieve(user_query)

        if not context:
            print("LLM: Sorry, no relevant information found in the documentation.\n")
            continue

        # Generate LLM response
        answer = llm.generate_answer(context=context, query=user_query)
        print(f"\nLLM:\n{answer}\n")

        # Check for code execution
        code_to_execute = extract_code(answer)
        if code_to_execute:
            print("\n[Code Detected]")
            print(f"---\n{code_to_execute}\n---")
            run_choice = input("Do you want to execute this code? (y/n): ").lower()
            
            if run_choice == 'y':
                print("\nExecuting in Sandbox...")
                result = sandbox.execute_code(code_to_execute)
                print(f"Sandbox Output:\n{result}\n")
            else:
                print("Skipping execution.\n")

if __name__ == "__main__":
    retriever, llm, sandbox = setup_pipeline()
    chat_loop(retriever, llm, sandbox)
