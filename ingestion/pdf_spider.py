import os
import re
import json
import time
import requests
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance
from urllib.parse import urlparse
from io import BytesIO
from typing import Optional


class PDFIngestionEngine:

    def __init__(self, output_dir="ingested_docs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "LLM-SmartAPI-Agent/1.0"})

#text utilities
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'[ \t]+', ' ', text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    def _ocr_image(self, image: Image.Image) -> str:
        image = image.convert("L")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        return pytesseract.image_to_string(image, config="--psm 6")

#pdf processing
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> list:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = []

        for page_number in range(len(doc)):
            page = doc[page_number]
            text = page.get_text()

            # OCR fallback for scanned pdfs
            if len(text.strip()) < 80:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = self._ocr_image(image)

            cleaned_text = self._clean_text(text)

            if cleaned_text:
                pages.append({
                    "page_number": page_number + 1,
                    "content": cleaned_text
                })

        doc.close()
        return pages

#download
    def download_pdf(self, pdf_url: str) -> Optional[bytes]:
        try:
            response = self.session.get(pdf_url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Failed to download {pdf_url}: {e}")
            return None

#saving output
    def save_as_json(self, source_url: str, pages: list) -> str:
        parsed = urlparse(source_url)
        filename = os.path.basename(parsed.path).replace(".pdf", "")
        filename = re.sub(r"[^\w\-]", "_", filename)

        output_path = os.path.join(self.output_dir, f"{filename}.json")

        payload = {
            "source": source_url,
            "document_type": "pdf",
            "ingested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pages": pages
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"Saved structured document: {output_path}")
        return output_path

#public api
    def ingest_pdf(self, pdf_url: str) -> Optional[str]:
        print(f"Ingesting PDF: {pdf_url}")
        pdf_bytes = self.download_pdf(pdf_url)

        if not pdf_bytes:
            return None

        pages = self.extract_text_from_pdf(pdf_bytes)
        if not pages:
            print("No text extracted")
            return None

        return self.save_as_json(pdf_url, pages)


if __name__ == "__main__":
    engine = PDFIngestionEngine(output_dir="api_docs_ingested")

    engine.ingest_pdf(
        "https://openweathermap.org/themes/openweathermap/assets/docs/Using_OpenWeatherMap_Weather_Tiles_with_Leaflet.pdf"
    )
