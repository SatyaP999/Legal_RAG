from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "data" / "Legal_data.pdf"
MD_PATH = BASE_DIR / "data" / "legal_data.md"

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


