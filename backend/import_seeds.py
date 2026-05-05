import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.services.knowledge_service import import_documents
from app.schemas.knowledge import KnowledgeDocumentCreate

SEEDS_DIR = Path(__file__).parent / "seeds"

def load_seed_file(filepath: Path) -> list[KnowledgeDocumentCreate]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [KnowledgeDocumentCreate(**item) for item in data]

def main():
    db = SessionLocal()
    try:
        total_imported = 0
        total_skipped = 0

        for seed_file in SEEDS_DIR.glob("*.json"):
            print(f"Loading {seed_file.name}...")
            documents = load_seed_file(seed_file)
            imported, skipped = import_documents(db, documents)
            total_imported += imported
            total_skipped += skipped
            print(f"  Imported: {imported}, Skipped: {skipped}")

        print(f"\nTotal: Imported {total_imported}, Skipped {total_skipped}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
