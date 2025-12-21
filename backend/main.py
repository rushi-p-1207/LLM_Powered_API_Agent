import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pdf_spider import PDFIngestionEngine
from RAG.chunking import MarkdownChunker
from RAG.vectorstore import VectorStore
from RAG.retriever import Retriever
from RAG.llm import SmartAPILLM

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

    return retriever, llm

def chat_loop(retriever, llm):
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

if __name__ == "__main__":
    retriever, llm = setup_pipeline()
    chat_loop(retriever, llm)
