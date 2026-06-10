import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from db import get_db

def main():
    db = get_db()

    start_date = datetime.now(timezone.utc) - timedelta(days=30)

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
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"נשמר: {out.resolve()}")

if __name__ == "__main__":
    main()
