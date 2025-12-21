class Retriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve(self, query: str, k: int = 3) -> str:
        retriever = self.vectorstore.db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

        docs = retriever.invoke(query)

        if not docs:
            return ""

        return "\n\n".join(
            f"[SOURCE: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )
