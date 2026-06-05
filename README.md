# NoSQL Inventory Management System

A MongoDB-based inventory management system using aggregation pipelines.

## Project Structure

```
pipelines/
├── db.py                          # MongoDB connection
├── inventory_value_ILS.py         # Total inventory value in ILS (₪)
├── inventory_value_by_category.py # Inventory value grouped by category
├── reorder_list.py                # Products that need reordering
└── top_k_sales_last_30d_top5.py   # Top 5 best-selling products
```

## Setup

### 1. Install dependencies
```bash
pip install pymongo python-dotenv
```

### 2. Configure environment
Create a `.env` file in the `pipelines/` folder:
```
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?appName=Cluster0
```

### 3. Run a pipeline
```bash
cd pipelines
python inventory_value_ILS.py
python reorder_list.py
python inventory_value_by_category.py
python top_k_sales_last_30d_top5.py
```

## Database Collections

| Collection | Description |
|---|---|
| `products` | Product catalog with SKU, name, price, category |
| `stock_movements` | IN/OUT stock transactions |
| `orders` | Customer orders with items and quantities |

## Pipeline Outputs

- **inventory_value_ILS** — Total value per product in Israeli Shekel
- **inventory_value_by_category** — Value and units grouped by category  
- **reorder_list** — Products below reorder point, sorted by gap
- **top_k_sales** — Top 5 products by quantity sold
