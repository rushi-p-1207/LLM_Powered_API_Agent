class Retriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve(self, query, k=3):
        retriever = self.vectorstore.db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        docs = retriever.invoke(query)
        return "\n\n".join(doc.page_content for doc in docs)
