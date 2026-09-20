import json
from datetime import timedelta
from pathlib import Path
from db import get_db

def main():
    db = get_db()

    # The 30-day window is measured from the most recent order in the collection, not from
    # today's clock: the dataset is a fixed snapshot, so anchoring on "now" would return
    # nothing once the snapshot ages. Against live data the two are the same thing.
    latest = db["orders"].find_one(sort=[("createdAt", -1)])
    if not latest:
        print("[]")
        return
    end_date = latest["createdAt"]
    start_date = end_date - timedelta(days=30)
    print(f"window: {start_date:%Y-%m-%d} .. {end_date:%Y-%m-%d}\n")

    pipeline = [
        {"$match": {"createdAt": {"$gte": start_date}}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "qtySold": {"$sum": "$items.qty"}
        }},
        {"$lookup": {
            "from": "products",
            "localField": "_id",
            "foreignField": "_id",
            "as": "product"
        }},
        {"$unwind": "$product"},
        {"$project": {
            "_id": 0,
            "qtySold": 1,
            "sku": "$product.sku",
            "name": "$product.name"
        }},
        {"$sort": {"qtySold": -1, "sku": 1}},
        {"$limit": 5}
    ]

    results = list(db["orders"].aggregate(pipeline))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    out = Path("out/top_k_sales_last_30d_top5.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"נשמר: {out.resolve()}")

if __name__ == "__main__":
    main()
