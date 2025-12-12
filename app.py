"""
app.py

UrbanMart Sales Dashboard – Python + Streamlit

Features:
- Sidebar filters (date range, store, channel, category)
- KPIs (revenue, transactions, avg revenue, unique customers)
- Revenue by category & store
- Daily revenue trend
- Top products and top customers
- Uses synthetic dataset urbanmart_sales.csv
"""

import streamlit as st
import pandas as pd
import numpy as np


FILE_PATH = "urbanmart_sales.csv"


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Load the CSV, ensure correct dtypes, and engineer features needed for the dashboard.
    """
    df = pd.read_csv(file_path)

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Basic type safety
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)
    df["discount_applied"] = df["discount_applied"].astype(float)

    # Feature engineering
    df["line_revenue"] = df["quantity"] * df["unit_price"] - df["discount_applied"]
    df["day_of_week"] = df["date"].dt.day_name()

    # Transaction-level approximation (optional)
    # average revenue per transaction could also be computed at bill_id level
    return df


def filter_data(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    store_locations=None,
    channel=None,
    categories=None,
) -> pd.DataFrame:
    """
    Apply filters step by step and return filtered DataFrame.
    This mirrors the function the assignment described.
    """
    filtered = df.copy()

    if start_date is not None:
        filtered = filtered[filtered["date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered = filtered[filtered["date"] <= pd.to_datetime(end_date)]
    if store_locations:
        filtered = filtered[filtered["store_location"].isin(store_locations)]
    if channel and channel != "All":
        filtered = filtered[filtered["channel"] == channel]
    if categories and len(categories) > 0:
        filtered = filtered[filtered["product_category"].isin(categories)]

    return filtered


def render_kpis(df_filtered: pd.DataFrame):
    """
    Show key metrics at the top of the dashboard.
    """
    total_revenue = df_filtered["line_revenue"].sum()
    total_transactions = df_filtered["bill_id"].nunique()
    avg_revenue_per_txn = (
        total_revenue / total_transactions if total_transactions > 0 else 0
    )
    unique_customers = df_filtered["customer_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"{total_revenue:,.2f}")
    col2.metric("Total Transactions", f"{total_transactions}")
    col3.metric("Avg Revenue / Transaction", f"{avg_revenue_per_txn:,.2f}")
    col4.metric("Unique Customers", f"{unique_customers}")


def render_revenue_by_category(df_filtered: pd.DataFrame):
    """
    Bar chart: Revenue by product category.
    """
    st.subheader("Revenue by Product Category")
    if df_filtered.empty:
        st.info("No data for selected filters.")
        return

    rev_by_cat = (
        df_filtered.groupby("product_category")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
    )
    st.bar_chart(rev_by_cat.set_index("product_category")["line_revenue"])


def render_revenue_by_store(df_filtered: pd.DataFrame):
    """
    Bar chart: Revenue by store location.
    """
    st.subheader("Revenue by Store Location")
    if df_filtered.empty:
        st.info("No data for selected filters.")
        return

    rev_by_store = (
        df_filtered.groupby("store_location")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("line_revenue", ascending=False)
    )
    st.bar_chart(rev_by_store.set_index("store_location")["line_revenue"])


def render_daily_trend(df_filtered: pd.DataFrame):
    """
    Line chart: Daily revenue trend.
    """
    st.subheader("Daily Revenue Trend")
    if df_filtered.empty:
        st.info("No data for selected filters.")
        return

    daily_rev = (
        df_filtered.groupby("date")["line_revenue"]
        .sum()
        .reset_index()
        .sort_values("date")
    ).set_index("date")

    st.line_chart(daily_rev["line_revenue"])


def render_top_entities(df_filtered: pd.DataFrame):
    """
    Tables for top 5 products and top 5 customers.
    """
    st.subheader("Top 5 Products by Revenue")
    if df_filtered.empty:
        st.info("No data for selected filters.")
    else:
        top_products = (
            df_filtered.groupby(["product_id", "product_name"])["line_revenue"]
            .sum()
            .reset_index()
            .sort_values("line_revenue", ascending=False)
            .head(5)
        )
        st.dataframe(top_products)

    st.subheader("Top 5 Customers by Revenue")
    if df_filtered.empty:
        st.info("No data for selected filters.")
    else:
        top_customers = (
            df_filtered.groupby(["customer_id"])["line_revenue"]
            .sum()
            .reset_index()
            .sort_values("line_revenue", ascending=False)
            .head(5)
        )
        st.dataframe(top_customers)


def main():
    st.set_page_config(
        page_title="UrbanMart Sales Dashboard",
        page_icon="🛒",
        layout="wide",
    )

    st.title("UrbanMart Sales Dashboard")
    st.caption("Built by MAIB students using Python & Streamlit")

    # Load data
    df = load_data(FILE_PATH)

    # Sidebar filters
    st.sidebar.header("Filters")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    store_locations = st.sidebar.multiselect(
        "Store locations",
        options=sorted(df["store_location"].unique().tolist()),
        default=sorted(df["store_location"].unique().tolist()),
    )

    channel = st.sidebar.selectbox(
        "Channel",
        options=["All"] + sorted(df["channel"].unique().tolist()),
        index=0,
    )

    product_categories = st.sidebar.multiselect(
        "Product categories (optional)",
        options=sorted(df["product_category"].unique().tolist()),
    )

    # Apply filters
    df_filtered = filter_data(
        df,
        start_date=start_date,
        end_date=end_date,
        store_locations=store_locations,
        channel=channel,
        categories=product_categories,
    )

    # Layout: KPIs on top
    st.markdown("### Key Metrics")
    render_kpis(df_filtered)

    # Two-column layout for category/store views
    col_left, col_right = st.columns(2)
    with col_left:
        render_revenue_by_category(df_filtered)
    with col_right:
        render_revenue_by_store(df_filtered)

    # Daily trend full width
    render_daily_trend(df_filtered)

    # Top products/customers
    render_top_entities(df_filtered)

    # Raw data sample
    st.markdown("### Sample Raw Data (Filtered)")
    st.dataframe(df_filtered.head(20))


if __name__ == "__main__":
    main()