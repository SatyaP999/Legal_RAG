import hashlib
from datetime import datetime
import pymupdf
import pymupdf4llm
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)
from variables import (
    PDF_PATH, MD_PATH, CHUNK_OVERLAP, CHUNK_SIZE
)


def get_pdf_hash(pdf_path: Path):
    with open(pdf_path, "rb") as f:
        file_content = f.read()

    return hashlib.sha256(file_content).hexdigest()


def convert_pdf_md(pdf_path: Path):
    if not str(pdf_path).endswith(".pdf"):
        raise ValueError("Invalid file type, this function only accepts .pdf files.")
    try:
        md = pymupdf4llm.to_markdown(pdf_path)
        # print(md)
        with open("data/legal_data.md", "w", encoding='utf-8') as f:
            f.write(md)
    except FileNotFoundError:
        print(f"Error: The file at location '{pdf_path}' cannnot be found.")
    except PermissionError:
        print(f"Error: Permission denied. Check your read/write access for these paths.")
    except Exception as e:
        print(f"An unexpected error occurred during conversion: {e}")

def create_doc_chunking(
        md_path: Path,
        pdf_path: Path
):
    if not str(md_path).endswith(".md"):
            raise ValueError("Invalid file type, this function only accepts .md files.")
    try:
        file_hash = get_pdf_hash(pdf_path=pdf_path)
        metadata = {
            "source_file": "Legal_data.pdf",
            "doc_id": "doc_123",
            "ingestion_date": datetime.utcnow().isoformat(),
            "doc_version": file_hash
        }

        loader = TextLoader(md_path, encoding='utf-8')
        markdown_content = loader.load()[0].page_content
        headers_to_split_on = [
            ("#", "H1"),
            ("##", "H2"),
            ("###", "H3"),
            ("####", "H4"),
        ]
        return (headers_to_split_on, markdown_content, metadata)
    except FileNotFoundError:
        print(f"Error: The file at location '{md_path}' cannnot be found.")
    except PermissionError:
        print(f"Error: Permission denied. Check your read/write access for these paths.")

def make_chunk_id(
        doc_id: str,
        chunk_index: int,
        text: str
) -> str:
    content_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
    return f"{doc_id}::{chunk_index}::{content_hash}"

def chunk_md(
   md_path: Path,
   pdf_path: Path
):
    
    headers_to_split, markdown_content, metadata = create_doc_chunking(
        md_path=md_path,
        pdf_path=pdf_path
    )
    chunks = []
    chunk_ids = []
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split)
    md_chunks = markdown_splitter.split_text(markdown_content)

    for index, chunk in enumerate(md_chunks):
        updated_metadata = {
            **metadata,
            **chunk.metadata,
            "chunk_index": index
        }
        c_id = make_chunk_id(
            doc_id=metadata["doc_id"],
            chunk_index=index,
            text=chunk.page_content
        )
        chunk.metadata = updated_metadata
        chunks.append(chunk)
        chunk_ids.append(c_id)

    assert len(chunks) == len(chunk_ids) == len(md_chunks), f"Mismatch: {len(chunks)}, {len(chunk_ids)}, {len(md_chunks)}"
    return chunks, chunk_ids


def chunk_md_with_fixed_chunk_size(
    md_path: Path,
    pdf_path: Path
) -> list[Document]:
    
    chunks = []
    chunk_ids = []
    headers_to_split, markdown_content, metadata = create_doc_chunking(
        md_path=md_path,
        pdf_path=pdf_path
    )
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split,
    )
    md_chunks = markdown_splitter.split_text(markdown_content)

    for chunk in md_chunks:
        chunk.metadata = {
            **metadata,
            **chunk.metadata
        }

    text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
    )
    final_chunks = text_splitter.split_documents(md_chunks)

    for index, chunk in enumerate(final_chunks):
        chunk.metadata["chunk_index"] = index
        c_id = make_chunk_id(
            doc_id=metadata["doc_id"],
            chunk_index=index,
            text=chunk.page_content
        )
        chunk.metadata["chunk_id"] = c_id
        chunk_ids.append(c_id)

    assert len(final_chunks) == len(chunk_ids)
    return final_chunks, chunk_ids


