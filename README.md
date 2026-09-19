# NoSQL Inventory Management

An inventory-analytics toolkit built on **MongoDB aggregation pipelines**. Each script answers one
business question by aggregating stock movements and orders — and the repository ships with the
sample dataset, so it runs end to end on a fresh machine.

## Quick start

```bash
pip install -r requirements.txt
python seed_db.py      # loads data/ into a local MongoDB
python inventory_value_ILS.py
```

`db.py` connects to `mongodb://localhost:27017` by default. To use a cluster instead, create a
`.env` file with `MONGO_URI=mongodb+srv://<user>:<password>@<cluster>/`.

## What it demonstrates

- MongoDB **aggregation pipelines**: `$group`, `$lookup`, `$unwind`, `$cond`, `$project`, `$match`, `$sort`, `$limit`, `$round`
- Stock-on-hand derived from an **event log** rather than stored as a field — `IN` movements add,
  `OUT` movements subtract, through a `$cond` inside `$group`
- Joining collections with `$lookup` on `ObjectId` keys
- Connection handling kept out of the queries (`db.py`), configuration through the environment, no credentials in code

## The data

Database `inventory`, seeded from `data/`:

| Collection | Documents | Fields |
|---|---:|---|
| `products` | 5 | `sku`, `name`, `category`, `cost`, `price`, `reorder_point`, `supplier_id` |
| `stock_movements` | 14 | `product_id`, `type` (`IN` / `OUT`), `qty`, `at`, `reason` |
| `orders` | — | `items[]` (`product_id`, `qty`), `createdAt` — see note below |

## The four questions

### 1. What is the inventory worth? — `inventory_value_ILS.py`

Stock-on-hand × selling price, per product.

| SKU | Product | On hand | Price | Value |
|---|---|---:|---:|---:|
| SKU-1003 | HDMI Cable 2m | 376 | ₪25 | ₪9,400 |
| SKU-1002 | USB-C Mouse | 60 | ₪120 | ₪7,200 |
| SKU-1001 | Wireless Keyboard | 47 | ₪150 | ₪7,050 |
| SKU-1005 | Bluetooth Headset | 20 | ₪250 | ₪5,000 |
| SKU-1004 | Aluminum Laptop Stand | 8 | ₪150 | ₪1,200 |

**Total: ₪29,850**

### 2. Where is the value tied up? — `inventory_value_by_category.py`

Grouped by category, valued at **cost** rather than price.

| Category | Units | Value |
|---|---:|---:|
| Electronics | 127 | ₪10,700 |
| Accessories | 384 | ₪4,400 |

Accessories hold three times the units but a fraction of the capital.

### 3. What needs reordering? — `reorder_list.py`

Products below their reorder point, sorted by the size of the shortfall.

| SKU | Product | On hand | Reorder point | Gap |
|---|---|---:|---:|---:|
| SKU-1005 | Bluetooth Headset | 20 | 30 | 10 |
| SKU-1004 | Aluminum Laptop Stand | 8 | 15 | 7 |

### 4. What sells best? — `top_k_sales_last_30d_top5.py`

The five products with the highest quantity sold in the last 30 days, from the `orders` collection.

> The `orders` export is not included in this repository yet, so this script currently returns an
> empty list against the sample data. The pipeline itself is complete.

Every script prints its result as JSON and writes it to `out/<name>.json`; the committed files under
`out/` are the output of an actual run.

## Project structure

```
.
├── data/                          # sample dataset (MongoDB Extended JSON)
├── out/                           # results of a real run
├── db.py                          # connection: MONGO_URI, or local by default
├── seed_db.py                     # loads data/ into MongoDB
├── inventory_value_ILS.py         # question 1
├── inventory_value_by_category.py # question 2
├── reorder_list.py                # question 3
└── top_k_sales_last_30d_top5.py   # question 4
```
