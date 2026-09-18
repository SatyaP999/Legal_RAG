import pickle
from pathlib import Path
from variables import PDF_PATH, MD_PATH
from vectorstore import get_vectorstore
from langchain_classic.indexes import SQLRecordManager, index as ls_index

from document_parser import chunk_md_with_fixed_chunk_size, chunk_md
STRATEGY = {
    "header_only": chunk_md,
    "header_then_recursive": chunk_md_with_fixed_chunk_size
}

CHUNKS_DIR = Path("./chunk_store")
CHUNKS_DIR.mkdir(exist_ok=True)

def index_pipeline(
        pdf_path: Path,
        md_path: Path
):
    for collection_name, fn_name in STRATEGY.items():
        chunks, chunk_ids = fn_name(md_path=md_path, pdf_path=pdf_path)
        vectorstore = get_vectorstore(
            collection_name=collection_name
        )
        record_manager = SQLRecordManager(
            f"chroma/{collection_name}",
            db_url="sqlite:///record_manager.sqlite"
        )
        record_manager.create_schema()
        result = ls_index(
            chunks, record_manager=record_manager,
            vector_store=vectorstore,
            cleanup="full",
            source_id_key="doc_id"
        )
        print(f"[{collection_name}] {result}")
        count = vectorstore._collection.count()

        assert count == len(chunks), f"[{collection_name}] mismatch: {count} {len(chunks)}"

        chunks_path = CHUNKS_DIR / f"{collection_name}.pkl"
        with open(chunks_path, "wb") as f:
            pickle.dump(chunks, f)
        print(f"[{collection_name}] saved {len(chunks)} chunks to {chunks_path}")

if __name__ == "__main__":
    index_pipeline(
        pdf_path=PDF_PATH,
        md_path=MD_PATH
    )
