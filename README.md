# NoSQL Inventory Management

An inventory-analytics toolkit built on **MongoDB aggregation pipelines**. Each script answers one
business question by aggregating stock movements and orders against the product catalogue — and the
repository ships with its dataset, so it runs end to end on a fresh machine.

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
- The same stock valued two ways: at **selling price** (what the shelf is worth) and at **cost**
  (what it ties up in capital) — two questions that give different answers
- Connection handling kept out of the queries (`db.py`), configuration through the environment,
  no credentials in code

## The data

Database `inventory`, seeded from `data/`:

| Collection | Documents | Fields |
|---|---:|---|
| `products` | 32 | `sku`, `name`, `category`, `cost`, `price`, `reorder_point`, `supplier_id` |
| `stock_movements` | 29 | `product_id`, `type` (`IN` / `OUT`), `qty`, `at`, `reason` |
| `orders` | 16 | `customer_id`, `createdAt`, `city`, `items[]` (`product_id`, `qty`, `price`) |

Twelve of the 32 catalogued products have recorded stock movements, so only those carry a stock
figure. Three of them — the Coffee items — have no `price` in the catalogue; their retail value is
reported as `null` rather than silently counted as zero, and they are excluded from the total.
Their `cost` is present, so they do appear in the cost-based view.

## The four questions

### 1. What is the inventory worth? — `inventory_value_ILS.py`

Stock-on-hand × selling price, per product.

| SKU | Product | On hand | Price | Value |
|---|---|---:|---:|---:|
| SKU-TEST-102 | Ergonomic Office Chair | 60 | ₪950 | ₪57,000 |
| SKU-1005 | Bluetooth Headset | 92 | ₪250 | ₪23,000 |
| SKU-TEST-104 | Mechanical Keyboard | 63 | ₪350 | ₪22,050 |
| SKU-TEST-103 | 4K Webcam | 54 | ₪280 | ₪15,120 |
| SKU-1004 | Aluminum Laptop Stand | 56 | ₪150 | ₪8,400 |
| SKU-1003 | HDMI Cable 2m | 298 | ₪25 | ₪7,450 |
| SKU-1001 | Wireless Keyboard | 47 | ₪150 | ₪7,050 |
| SKU-TEST-101 | Portable Power Bank | 29 | ₪180 | ₪5,220 |
| SKU-1002 | USB-C Mouse | 30 | ₪120 | ₪3,600 |
| SKU123 | Espresso 1kg | 210 | — | — |
| SKU777 | Filter 500g | 65 | — | — |
| SKU999 | Old Beans 250g | 60 | — | — |

**Total: ₪148,890**

### 2. Where is the capital tied up? — `inventory_value_by_category.py`

Grouped by category and valued at **cost** this time.

| Category | Units | Value at cost |
|---|---:|---:|
| Electronics | 261 | ₪29,165 |
| Furniture | 60 | ₪27,000 |
| Accessories | 408 | ₪13,400 |
| Coffee | 335 | ₪8,985 |

The two views disagree, which is the point. Accessories hold the most units but little capital;
Furniture is a single product line holding ₪27,000 in 60 units.

### 3. What needs reordering? — `reorder_list.py`

Products whose stock has fallen below their reorder point, sorted by the size of the shortfall.

| SKU | Product | On hand | Reorder point | Gap |
|---|---|---:|---:|---:|
| SKU-1002 | USB-C Mouse | 30 | 40 | 10 |

### 4. What sells best? — `top_k_sales_last_30d_top5.py`

The five products with the highest quantity sold over a 30-day window, from `orders`.

| Product | SKU | Units sold |
|---|---|---:|
| Wireless Keyboard | SKU-1001 | 43 |
| USB-C Mouse | SKU-1002 | 37 |
| Espresso 1kg | SKU123 | 35 |
| Aluminum Laptop Stand | SKU-1004 | 22 |
| Bluetooth Headset | SKU-1005 | 17 |

The window ends at the most recent order in the collection rather than at today's date: the dataset
is a fixed snapshot, so anchoring on the clock would return an empty result once the snapshot ages.
Against a live database the two are the same thing.

Read together with question 3, the USB-C Mouse is both the best seller after the keyboard and the
only product below its reorder point — exactly the pair of facts a purchasing decision needs.

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
