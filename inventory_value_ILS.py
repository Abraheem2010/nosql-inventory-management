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
            "_id": 0,
            "sku": "$product.sku",
            "name": "$product.name",
            "stock_on_hand": 1,
            "price_ils": "$product.price",
            "total_value_ils": {
                "$multiply": ["$stock_on_hand", "$product.price"]
            }
        }},
        {"$sort": {"total_value_ils": -1}}
    ]

    results = list(db["stock_movements"].aggregate(pipeline))

    total = sum(r.get("total_value_ils") or 0 for r in results)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nסה\"כ שווי מלאי: ₪{total:,.2f}")

    out = Path("out/inventory_value_ILS.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"נשמר: {out.resolve()}")


if __name__ == "__main__":
    main()
