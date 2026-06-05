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
            "category": "$product.category",
            "value": {"$multiply": ["$stock_on_hand", "$product.cost"]},
            "units": "$stock_on_hand"
        }},
        {"$group": {
            "_id": "$category",
            "totalUnits": {"$sum": "$units"},
            "totalValue": {"$sum": "$value"}
        }},
        {"$project": {
            "_id": 0,
            "category": "$_id",
            "totalUnits": 1,
            "totalValue": {"$round": ["$totalValue", 2]}
        }},
        {"$sort": {"category": 1}}
    ]

    results = list(db["stock_movements"].aggregate(pipeline))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    out = Path("out/inventory_value_by_category.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"נשמר: {out.resolve()}")

if __name__ == "__main__":
    main()
