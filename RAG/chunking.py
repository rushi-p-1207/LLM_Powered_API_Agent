from io import BytesIO
from typing import List, Dict
from docling.document_converter import DocumentConverter
from docling.datamodel.document import DocumentStream
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import os


class MarkdownChunker:
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
        """Chunk a PDF given as bytes."""
        pdf_stream = BytesIO(pdf_bytes)

        document = DocumentStream(
            name=document_name,
            stream=pdf_stream
        )

        result = self.converter.convert(document)
        markdown_text = result.document.export_to_markdown()

        return self._split_markdown(markdown_text, document_name)

    def chunk_json(
        self,
        json_path: str
    ) -> List[Dict]:
        """Chunk an already ingested JSON document."""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"{json_path} does not exist!")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pages = data.get("pages", [])
        if not pages:
            return []

       
        markdown_text = "\n\n".join(page["content"] for page in pages)
        document_name = os.path.basename(json_path)

        return self._split_markdown(markdown_text, document_name)

    def _split_markdown(self, markdown_text: str, document_name: str) -> List[Dict]:
        chunks = self.splitter.split_text(markdown_text)
        return [
            {
                "chunk_id": idx,
                "content": chunk,
                "source": document_name
            }
            for idx, chunk in enumerate(chunks)
        ]
