# UrbanMart Sales Dashboard – Python & Streamlit Mini Project

## Project overview

This project implements a **Retail Insights Dashboard** for **UrbanMart**, a mid-sized retail chain operating in a metropolitan city. The dashboard is built using **Python**, **pandas**, and **Streamlit**, and visualizes synthetic but realistic daily transaction data.

The goal is to allow management to quickly understand:

- Which product categories are performing well  
- How sales vary across stores and days  
- Which customers are most valuable  

---

## Files in this project

- `urbanmart_sales.csv`  
  Synthetic dataset of UrbanMart transaction-level sales.

- `app.py`  
  Streamlit application that builds the interactive sales dashboard.

- `generate_urbanmart_data.py`  
  Script used to generate the synthetic dataset (not required to run the dashboard once the CSV exists).

---

## Dataset description

Each row in `urbanmart_sales.csv` represents **one transaction line** (one product in one bill).

**Columns:**

- `transaction_id`: Unique ID for each bill line (e.g., `TXN-2025-00001`)
- `bill_id`: Bill number (one bill can have multiple products)
- `date`: Transaction date (`YYYY-MM-DD`)
- `store_id`: Store identifier (e.g., `S1`, `S2`)
- `store_location`: Store location (e.g., `Downtown`, `Uptown`, `Suburban`, `City Center`)
- `customer_id`: Unique customer ID (e.g., `C001`)
- `customer_segment`: One of `Regular`, `New`, `Loyal`
- `product_id`: Product code (e.g., `P101`)
- `product_category`: `Beverages`, `Snacks`, `Personal Care`, or `Household`
- `product_name`: Human-readable product name
- `quantity`: Units purchased
- `unit_price`: Price per unit
- `payment_method`: `Cash`, `Credit Card`, or `UPI`
- `discount_applied`: Discount amount in currency units
- `channel`: `In-store` or `Online`

In the dashboard, a new column is engineered:

- `line_revenue = quantity * unit_price - discount_applied`
- `day_of_week = day name derived from date`

---

## How to run the dashboard

### 1. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate