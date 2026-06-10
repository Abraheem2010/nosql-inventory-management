# NoSQL Inventory Management

A small inventory-analytics toolkit built on **MongoDB aggregation pipelines**.
Each script answers one business question by aggregating stock movements and orders.

## What it demonstrates

- MongoDB **aggregation pipelines** (`$group`, `$lookup`, `$unwind`, `$cond`, `$project`, `$match`, `$sort`, `$limit`)
- Derived metrics: stock-on-hand, inventory value, and reorder gaps
- DB connection kept separate from the queries (`db.py`)
- Environment-based configuration via `.env` — no hard-coded credentials

## Project structure

```
.
├── db.py                          # MongoDB connection (reads MONGO_URI from .env)
├── inventory_value_ILS.py         # Inventory value per product, in ILS (₪)
├── inventory_value_by_category.py # Inventory value & units grouped by category
├── reorder_list.py                # Products below their reorder point, sorted by gap
└── top_k_sales_last_30d_top5.py   # Top 5 best-selling products by quantity
```

Each script prints its result as JSON and also writes it to `out/<name>.json`.

## Database: `inventory`

| Collection | Description |
|---|---|
| `products` | Catalog: SKU, name, price, category, reorder_point |
| `stock_movements` | IN/OUT stock transactions (`type`, `qty`, `product_id`) |
| `orders` | Customer orders with `items` (product_id, qty) and `createdAt` |

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root:
   ```
   MONGO_URI=mongodb+srv://<user>:<password>@<cluster>/?appName=Cluster0
   ```
3. Run any script:
   ```bash
   python inventory_value_ILS.py
   python inventory_value_by_category.py
   python reorder_list.py
   python top_k_sales_last_30d_top5.py
   ```

## Pipelines

- **inventory_value_ILS** — stock-on-hand × price per product, sorted by total value.
- **inventory_value_by_category** — value and units grouped by category.
- **reorder_list** — products whose stock is below `reorder_point`, sorted by the shortfall.
- **top_k_sales** — the five products with the highest quantity sold.
