import io
import os
from pathlib import Path

from app.core.exceptions import AppException


ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE = 5 * 1024 * 1024


class FileParseError(AppException):
    def __init__(self, message: str):
        super().__init__(status_code=422, detail=message)


def validate_file(filename: str, content: bytes) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileParseError(f"不支持的文件格式: {ext}，仅支持 PDF 和 DOCX")
    if len(content) > MAX_FILE_SIZE:
        raise FileParseError(f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)")
    if ext == ".pdf":
        if content[:4] != b"%PDF":
            raise FileParseError("文件内容不是有效的 PDF 格式")
    elif ext == ".docx":
        if content[:2] != b"PK":
            raise FileParseError("文件内容不是有效的 DOCX 格式")


def parse_pdf(content: bytes) -> str:
    import pdfplumber

    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            return "\n\n".join(pages)
    except Exception as exc:
        raise FileParseError(f"PDF 解析失败: {exc}") from exc


def parse_docx(content: bytes) -> str:
    from docx import Document

    try:
        doc = Document(io.BytesIO(content))
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        return "\n\n".join(paragraphs)
    except Exception as exc:
        raise FileParseError(f"DOCX 解析失败: {exc}") from exc


def parse_upload(filename: str, content: bytes) -> str:
    validate_file(filename, content)

    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(content)
    elif ext == ".docx":
        return parse_docx(content)

    raise FileParseError(f"不支持的文件格式: {ext}")
