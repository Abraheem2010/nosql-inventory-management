# NoSQL Inventory Management

An inventory-analytics toolkit built on **MongoDB aggregation pipelines**. Each script answers one
business question by aggregating stock movements against the product catalogue — and the repository
ships with its dataset, so it runs end to end on a fresh machine.

## Quick start

```bash
pip install -r requirements.txt
python seed_db.py      # loads data/ into a local MongoDB
python inventory_value_ILS.py
```

`db.py` connects to `mongodb://localhost:27017` by default. To use a cluster instead, create a
`.env` file with `MONGO_URI=mongodb+srv://<user>:<password>@<cluster>/`.

## What it demonstrates

- MongoDB **aggregation pipelines**: `$group`, `$lookup`, `$unwind`, `$cond`, `$project`, `$match`, `$sort`, `$round`
- Stock-on-hand derived from an **event log** rather than stored as a field — `IN` movements add,
  `OUT` movements subtract, through a `$cond` inside `$group`
- Joining collections with `$lookup` on `ObjectId` keys
- The same stock figure valued two ways: at **selling price** (what the shelf is worth to the
  customer) and at **cost** (what it ties up in capital)
- Connection handling kept out of the queries (`db.py`), configuration through the environment,
  no credentials in code

## The data

Database `inventory`, seeded from `data/`:

| Collection | Documents | Fields |
|---|---:|---|
| `products` | 32 | `sku`, `name`, `category`, `cost`, `price`, `reorder_point`, `supplier_id` |
| `stock_movements` | 14 | `product_id`, `type` (`IN` / `OUT`), `qty`, `at`, `reason` |
| `orders` | 16 | `customer_id`, `createdAt`, `city`, `items[]` (`product_id`, `qty`, `price`) |

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

### 2. Where is the capital tied up? — `inventory_value_by_category.py`

Grouped by category, valued at **cost** this time.

| Category | Units | Value |
|---|---:|---:|
| Electronics | 127 | ₪10,700 |
| Accessories | 384 | ₪4,400 |

Accessories hold three times the units but a fraction of the capital — a different answer from
question 1, and the reason both views are worth having.

### 3. What needs reordering? — `reorder_list.py`

Products below their reorder point, sorted by the size of the shortfall.

| SKU | Product | On hand | Reorder point | Gap |
|---|---|---:|---:|---:|
| SKU-1005 | Bluetooth Headset | 20 | 30 | 10 |
| SKU-1004 | Aluminum Laptop Stand | 8 | 15 | 7 |

### 4. What sells best? — `top_k_sales_last_30d_top5.py`

The five products with the highest quantity sold over a 30-day window, from `orders`.

| Product | SKU | Units sold |
|---|---|---:|
| Wireless Keyboard | SKU-1001 | 43 |
| USB-C Mouse | SKU-1002 | 37 |
| Espresso 1kg | SKU123 | 35 |
| Aluminum Laptop Stand | SKU-1004 | 22 |
| Bluetooth Headset | SKU-1005 | 17 |

The window ends at the most recent order in the collection rather than at today's date: the
dataset is a fixed snapshot, so anchoring on the clock would return an empty result once the
snapshot ages. Against a live database the two are the same thing.

Every script prints its result as JSON and writes it to `out/<name>.json`; the files committed under
`out/` are the output of an actual run.

## Project structure

```
.
├── data/                          # the dataset (MongoDB Extended JSON)
├── out/                           # results of a real run
├── db.py                          # connection: MONGO_URI, or local by default
├── seed_db.py                     # loads data/ into MongoDB
├── inventory_value_ILS.py         # question 1
├── inventory_value_by_category.py # question 2
├── reorder_list.py                # question 3
└── top_k_sales_last_30d_top5.py   # question 4
```
