"""
Load the sample dataset in data/ into MongoDB so the aggregation scripts can run.

Each JSON file in data/ becomes a collection of the same name. The files are MongoDB
Extended JSON exports, so ObjectIds and dates are parsed back into real BSON types —
otherwise $lookup would compare an ObjectId against a string and silently return nothing.

Existing collections are replaced.

Run:  python seed_db.py
"""

from pathlib import Path

from bson.json_util import loads

from db import get_db

DATA = Path(__file__).parent / "data"


def main():
    db = get_db()
    files = sorted(DATA.glob("*.json"))
    if not files:
        raise SystemExit(f"No JSON files found in {DATA}")

    for path in files:
        collection = path.stem
        docs = loads(path.read_text(encoding="utf-8"))
        if not isinstance(docs, list):
            docs = [docs]
        db[collection].drop()
        db[collection].insert_many(docs)
        print(f"{collection:<18} {len(docs):>4} documents loaded")

    print(f"\nDatabase '{db.name}' ready. Collections: {sorted(db.list_collection_names())}")


if __name__ == "__main__":
    main()
