import os
from langchain_community.vectorstores import Chroma
from .embeddings import get_embedding_model


class VectorStore:
    def __init__(self, collection_name="api_docs"):
        os.makedirs("vector_store", exist_ok=True)

        self.db = Chroma(
            collection_name=collection_name,
            embedding_function=get_embedding_model(),
            persist_directory=f"vector_store/{collection_name}"
        )

    def add_chunks(self, chunks):
        texts = [chunk["content"] for chunk in chunks]
        metadatas = [{"source": chunk["source"]} for chunk in chunks]

        self.db.add_texts(texts=texts, metadatas=metadatas)
        self.db.persist()
