from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


class ResumeParseError(RuntimeError):
    """Raised when resume PDF extraction fails."""


class ResumeParser:
    def extract_text(self, pdf_bytes: bytes) -> str:
        if not pdf_bytes:
            raise ResumeParseError("Uploaded resume PDF is empty.")

        try:
            reader = PdfReader(BytesIO(pdf_bytes))
        except Exception as exc:  # pragma: no cover - parser-specific failures
            raise ResumeParseError("Could not open the uploaded PDF.") from exc

        pages: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())

        text = "\n\n".join(pages).strip()
        if not text:
            raise ResumeParseError(
                "Could not extract text from the uploaded PDF. The file may be scanned or image-only."
            )

        return text
