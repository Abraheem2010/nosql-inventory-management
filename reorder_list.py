import json
from pathlib import Path
from db import get_db

def main():
    db = get_db()

    pipeline = [
        {"$group": {
            "_id": "$product_id",
            "stock_on_hand": {"$sum": {
                "$cond": [
                    {"$eq": ["$type", "IN"]},
                    "$qty",
                    {"$multiply": ["$qty", -1]}
                ]
            }}
        }},
        {"$lookup": {
            "from": "products",
            "localField": "_id",
            "foreignField": "_id",
            "as": "product"
        }},
        {"$unwind": "$product"},
        {"$project": {
            "sku": "$product.sku",
            "name": "$product.name",
            "stock_on_hand": 1,
            "reorder_point": "$product.reorder_point",
            "needs_reorder": {"$lt": ["$stock_on_hand", "$product.reorder_point"]},
            "gap": {"$max": [
                {"$subtract": ["$product.reorder_point", "$stock_on_hand"]},
                0
            ]}
        }},
        {"$match": {"needs_reorder": True}},
        {"$sort": {"gap": -1, "sku": 1}},
        {"$project": {
            "_id": 0,
            "sku": 1, "name": 1,
            "stock_on_hand": 1, "reorder_point": 1, "gap": 1
        }}
    ]

    results = list(db["stock_movements"].aggregate(pipeline))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    out = Path("out/reorder_list.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"נשמר: {out.resolve()}")

if __name__ == "__main__":
    main()
