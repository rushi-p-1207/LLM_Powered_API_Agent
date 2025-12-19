from io import BytesIO
from typing import List, Dict
from docling.document_converter import DocumentConverter
from docling.datamodel.document import DocumentStream
from langchain_text_splitters import RecursiveCharacterTextSplitter


class MarkdownChunker:
    """
    Converts PDF documents into structured Markdown and
    splits them into semantically meaningful chunks
    for embedding and retrieval.
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100
    ):
        self.converter = DocumentConverter()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.separators = [
            "\n```",
            "\n###### ", "\n##### ", "\n#### ", "\n### ", "\n## ", "\n# ",
            "\nHTTP Method:",
            "\nEndpoint:",
            "\nURL:",
            "\nParameters:",
            "\nRequest Parameters:",
            "\nResponse:",
            "\nJSON Response:",
            "\nStatus Codes:",
            "\nError Codes:",
            "\nExample:",
            "\nDescription:",
            "\n- ", "\n* ", "\n+ ",
            "\n1. ",
            "\n|", "\n:-",
            "\n> ",
            "\n\n",
            "\n",
            " "
        ]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators
        )

    def chunk_pdf(
        self,
        pdf_bytes: bytes,
        document_name: str
    ) -> List[Dict]:
        """
        Converts PDF bytes into markdown chunks.

        Returns a list of dictionaries:
        {
            "chunk_id": int,
            "content": str,
            "source": str
        }
        """

        pdf_stream = BytesIO(pdf_bytes)

        document = DocumentStream(
            name=document_name,
            stream=pdf_stream
        )

        result = self.converter.convert(document)
        markdown_text = result.document.export_to_markdown()

        chunks = self.splitter.split_text(markdown_text)

        return [
            {
                "chunk_id": idx,
                "content": chunk,
                "source": document_name
            }
            for idx, chunk in enumerate(chunks)
        ]
