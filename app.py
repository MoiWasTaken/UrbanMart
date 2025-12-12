# app.py - UrbanMart Retail Insights Dashboard (Enhanced Version)
# Professional Investor-Ready Dashboard with Improved Visibility & New Features

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ========================================
# PAGE CONFIGURATION
# ========================================
st.set_page_config(
    page_title="UrbanMart Retail Insights",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CUSTOM CSS FOR PROFESSIONAL STYLING
# ========================================
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    h1 {
        color: #1a1a1a;
        font-weight: 700;
        padding-bottom: 10px;
    }
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 30px;
        padding: 10px 0;
        border-bottom: 3px solid #3498db;
    }
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin: 20px 0;
    }
    .recommendation-box {
        background-color: #fff3cd;
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ========================================
# DATA LOADING & PROCESSING
# ========================================
@st.cache_data
def load_and_process_data():
    """Load and process the UrbanMart sales data"""
    try:
        # Load CSV
        df = pd.read_csv('urbanmart_sales.csv')
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Create derived fields
        df['line_revenue'] = df['quantity'] * df['unit_price'] - df['discount_applied']
        
        # Extract month, quarter, and day of week
        df['month'] = df['date'].dt.to_period('M').astype(str)
        df['quarter'] = df['date'].dt.to_period('Q').astype(str)
        df['day_of_week'] = df['date'].dt.day_name()
        
        # Category profit margins
        margin_map = {
            'Beverages': 0.30,
            'Snacks': 0.25,
            'Personal Care': 0.40,
            'Dairy': 0.20,
            'Bakery': 0.20
        }
        
        df['profit_margin'] = df['product_category'].map(margin_map)
        df['estimated_profit'] = df['line_revenue'] * df['profit_margin']
        
        return df
    
    except FileNotFoundError:
        st.error("❌ Error: urbanmart_sales.csv not found. Please ensure the file is in the same directory.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

# Load data
df_original = load_and_process_data()

# ========================================
# SIDEBAR - FILTERS
# ========================================
st.sidebar.image("https://via.placeholder.com/300x80/2c3e50/ffffff?text=UrbanMart+Analytics", use_container_width=True)
st.sidebar.title("🎯 Dashboard Filters")
st.sidebar.markdown("---")

# Date Range Filter
st.sidebar.subheader("📅 Date Range")
min_date = df_original['date'].min().date()
max_date = df_original['date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle single date selection
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

# Store Location Filter
st.sidebar.subheader("🏪 Store Location")
all_locations = sorted(df_original['store_location'].unique().tolist())
selected_locations = st.sidebar.multiselect(
    "Select Locations",
    options=all_locations,
    default=all_locations
)

# Channel Filter
st.sidebar.subheader("🛒 Sales Channel")
selected_channel = st.sidebar.selectbox(
    "Select Channel",
    options=['All', 'In-store', 'Online']
)

# Product Category Filter
st.sidebar.subheader("📦 Product Category")
all_categories = sorted(df_original['product_category'].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=all_categories,
    default=all_categories
)

# Customer Segment Filter
st.sidebar.subheader("👥 Customer Segment")
all_segments = sorted(df_original['customer_segment'].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Select Segments",
    options=all_segments,
    default=all_segments
)

# Discount Range Filter
st.sidebar.subheader("💰 Discount Range")
min_discount = float(df_original['discount_applied'].min())
max_discount = float(df_original['discount_applied'].max())
discount_range = st.sidebar.slider(
    "Discount Applied ($)",
    min_value=min_discount,
    max_value=max_discount,
    value=(min_discount, max_discount)
)

# Quantity Range Filter
st.sidebar.subheader("📊 Quantity Range")
min_qty = int(df_original['quantity'].min())
max_qty = int(df_original['quantity'].max())
quantity_range = st.sidebar.slider(
    "Quantity Purchased",
    min_value=min_qty,
    max_value=max_qty,
    value=(min_qty, max_qty)
)

# High-Value Customer Filter
st.sidebar.subheader("⭐ High-Value Customers")
high_value_threshold = st.sidebar.number_input(
    "Minimum Customer Revenue ($)",
    min_value=0,
    max_value=1000,
    value=100,
    step=10
)
show_high_value_only = st.sidebar.checkbox("Show Only High-Value Customers")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use filters to drill down into specific segments and time periods.")

# ========================================
# APPLY FILTERS
# ========================================
df = df_original.copy()

# Apply date filter
df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# Apply location filter
if selected_locations:
    df = df[df['store_location'].isin(selected_locations)]

# Apply channel filter
if selected_channel != 'All':
    df = df[df['channel'] == selected_channel]

# Apply category filter
if selected_categories:
    df = df[df['product_category'].isin(selected_categories)]

# Apply segment filter
if selected_segments:
    df = df[df['customer_segment'].isin(selected_segments)]

# Apply discount filter
df = df[(df['discount_applied'] >= discount_range[0]) & (df['discount_applied'] <= discount_range[1])]

# Apply quantity filter
df = df[(df['quantity'] >= quantity_range[0]) & (df['quantity'] <= quantity_range[1])]

# Apply high-value customer filter
if show_high_value_only:
    customer_revenue = df.groupby('customer_id')['line_revenue'].sum()
    high_value_customers = customer_revenue[customer_revenue >= high_value_threshold].index
    df = df[df['customer_id'].isin(high_value_customers)]

# ========================================
# MAIN DASHBOARD
# ========================================
st.title("🏪 UrbanMart Retail Insights Dashboard")
st.markdown("### Professional Analytics for Strategic Decision Making")
st.markdown("---")

# Check if data is available after filtering
if len(df) == 0:
    st.warning("⚠️ No data available for the selected filters. Please adjust your filter criteria.")
    st.stop()

# ========================================
# SECTION A - EXECUTIVE KPIs (ENHANCED)
# ========================================
st.header("📊 Executive Summary")

# Calculate KPIs
total_revenue = df['line_revenue'].sum()
total_transactions = df['transaction_id'].nunique()
total_bills = df['bill_id'].nunique()
unique_customers = df['customer_id'].nunique()

# Average Order Value
avg_order_value = total_revenue / total_bills if total_bills > 0 else 0

# Average Customer Value (NEW)
avg_customer_value = total_revenue / unique_customers if unique_customers > 0 else 0

# Calculate monthly growth
monthly_revenue = df.groupby('month')['line_revenue'].sum().sort_index()
if len(monthly_revenue) >= 2:
    current_month_rev = monthly_revenue.iloc[-1]
    previous_month_rev = monthly_revenue.iloc[-2]
    monthly_growth = ((current_month_rev - previous_month_rev) / previous_month_rev * 100) if previous_month_rev > 0 else 0
else:
    monthly_growth = 0

# Calculate repeat purchase rate
customer_orders = df.groupby('customer_id')['bill_id'].nunique()
repeat_customers = (customer_orders > 1).sum()
total_customers = customer_orders.count()
repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0

# High-Value Customers Count
customer_revenue = df.groupby('customer_id')['line_revenue'].sum()
high_value_count = (customer_revenue >= high_value_threshold).sum()

# Display KPIs in two rows
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💵 Total Revenue",
        value=f"${total_revenue:,.2f}",
        delta=None
    )

with col2:
    st.metric(
        label="🛍️ Average Order Value (AOV)",
        value=f"${avg_order_value:.2f}",
        delta=None
    )

with col3:
    st.metric(
        label="👤 Average Customer Value (ACV)",
        value=f"${avg_customer_value:.2f}",
        delta=None,
        help="Total Revenue / Number of Unique Customers"
    )

col4, col5, col6 = st.columns(3)

with col4:
    growth_color = "normal" if monthly_growth >= 0 else "inverse"
    st.metric(
        label="📈 Monthly Revenue Growth",
        value=f"{monthly_growth:.1f}%",
        delta=f"{monthly_growth:.1f}%",
        delta_color=growth_color
    )

with col5:
    st.metric(
        label="🔄 Repeat Purchase Rate",
        value=f"{repeat_rate:.1f}%",
        delta=None
    )

with col6:
    st.metric(
        label="⭐ High-Value Customers",
        value=f"{high_value_count:,}",
        delta=None,
        help=f"Customers with revenue ≥ ${high_value_threshold}"
    )

st.markdown("---")

# ========================================
# SECTION B - STORE PERFORMANCE (BLUES)
# ========================================
st.header("🏪 Store Performance Analysis")

col1, col2 = st.columns([2, 1])

with col1:
    # Revenue by Store - Horizontal Bar Chart with BLUE palette
    revenue_by_store = df.groupby('store_location')['line_revenue'].sum().sort_values(ascending=True)
    
    fig_store = go.Figure(go.Bar(
        x=revenue_by_store.values,
        y=revenue_by_store.index,
        orientation='h',
        marker=dict(
            color=revenue_by_store.values,
            colorscale='Blues',
            showscale=False,
            line=dict(color='#08519c', width=1)
        ),
        text=[f'${x:,.0f}' for x in revenue_by_store.values],
        textposition='outside',
        textfont=dict(size=14, color='#000000', family='Arial Black')
    ))
    
    fig_store.update_layout(
        title=dict(text="Revenue by Store Location", font=dict(size=18, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Revenue ($)", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Store Location", font=dict(size=14, color='#000000')),
        height=400,
        showlegend=False,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        xaxis=dict(gridcolor='#dee2e6', showgrid=True),
        yaxis=dict(gridcolor='#dee2e6')
    )
    
    st.plotly_chart(fig_store, use_container_width=True)

with col2:
    # Store Leaderboard Table
    st.subheader("🏆 Store Leaderboard")
    
    store_stats = df.groupby('store_location').agg({
        'line_revenue': 'sum',
        'bill_id': 'nunique',
        'transaction_id': 'count'
    }).round(2)
    
    store_stats.columns = ['Revenue', 'Orders', 'Items']
    store_stats['AOV'] = (store_stats['Revenue'] / store_stats['Orders']).round(2)
    store_stats = store_stats.sort_values('Revenue', ascending=False)
    store_stats['Revenue'] = store_stats['Revenue'].apply(lambda x: f'${x:,.2f}')
    store_stats['AOV'] = store_stats['AOV'].apply(lambda x: f'${x:,.2f}')
    
    st.dataframe(store_stats, use_container_width=True)

# AOV by Store with BLUE palette
st.subheader("📊 Average Order Value by Store")
aov_by_store = df.groupby('store_location').agg({
    'line_revenue': 'sum',
    'bill_id': 'nunique'
})
aov_by_store['AOV'] = aov_by_store['line_revenue'] / aov_by_store['bill_id']
aov_by_store = aov_by_store.sort_values('AOV', ascending=False)

fig_aov = px.bar(
    aov_by_store,
    x=aov_by_store.index,
    y='AOV',
    color='AOV',
    color_continuous_scale='Blues',
    text='AOV'
)

fig_aov.update_traces(
    texttemplate='$%{text:.2f}', 
    textposition='outside',
    textfont=dict(size=14, color='#000000', family='Arial Black'),
    marker=dict(line=dict(color='#08519c', width=1))
)

fig_aov.update_layout(
    title=dict(text="Average Order Value by Store", font=dict(size=18, color='#000000', family='Arial Black')),
    xaxis_title=dict(text="Store Location", font=dict(size=14, color='#000000')),
    yaxis_title=dict(text="Average Order Value ($)", font=dict(size=14, color='#000000')),
    showlegend=False,
    height=400,
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    font=dict(color='#000000', size=12),
    xaxis=dict(gridcolor='#dee2e6'),
    yaxis=dict(gridcolor='#dee2e6', showgrid=True)
)

st.plotly_chart(fig_aov, use_container_width=True)

st.markdown("---")

# ========================================
# SECTION C - CUSTOMER INSIGHTS (GREENS)
# ========================================
st.header("👥 Customer Insights")

col1, col2 = st.columns([1, 2])

with col1:
    # Revenue by Customer Segment - Pie Chart with GREEN palette
    revenue_by_segment = df.groupby('customer_segment')['line_revenue'].sum()
    
    fig_segment = go.Figure(data=[go.Pie(
        labels=revenue_by_segment.index,
        values=revenue_by_segment.values,
        hole=0.4,
        marker=dict(colors=['#006d2c', '#31a354', '#74c476'], line=dict(color='#000000', width=2)),
        textinfo='label+percent+value',
        textfont=dict(size=14, color='#000000', family='Arial Black'),
        texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}'
    )])
    
    fig_segment.update_layout(
        title=dict(text="Revenue Distribution by Customer Segment", font=dict(size=18, color='#000000', family='Arial Black')),
        height=400,
        showlegend=True,
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        legend=dict(font=dict(size=12, color='#000000'))
    )
    
    st.plotly_chart(fig_segment, use_container_width=True)
    
    # Loyal Customer KPI
    loyal_customers = df[df['customer_segment'] == 'Loyal']['customer_id'].nunique()
    st.metric(
        label="⭐ Loyal Customers",
        value=f"{loyal_customers:,}",
        delta=None
    )

with col2:
    # Top 10 Customers Table
    st.subheader("🌟 Top 10 High-Value Customers")
    
    customer_stats = df.groupby('customer_id').agg({
        'line_revenue': 'sum',
        'bill_id': 'nunique',
        'customer_segment': 'first'
    }).round(2)
    
    customer_stats.columns = ['Total Revenue', 'Order Count', 'Segment']
    customer_stats = customer_stats.sort_values('Total Revenue', ascending=False).head(10)
    customer_stats['Total Revenue'] = customer_stats['Total Revenue'].apply(lambda x: f'${x:,.2f}')
    customer_stats.index.name = 'Customer ID'
    
    st.dataframe(customer_stats, use_container_width=True, height=400)

st.markdown("---")

# ========================================
# SECTION D - CATEGORY & PROFITABILITY (PURPLES)
# ========================================
st.header("📦 Category & Profitability Analysis")

col1, col2 = st.columns(2)

with col1:
    # Revenue by Category with PURPLE palette
    revenue_by_category = df.groupby('product_category')['line_revenue'].sum().sort_values(ascending=False)
    
    fig_category = px.bar(
        revenue_by_category,
        x=revenue_by_category.index,
        y=revenue_by_category.values,
        color=revenue_by_category.values,
        color_continuous_scale='Purples',
        text=revenue_by_category.values
    )
    
    fig_category.update_traces(
        texttemplate='$%{text:,.0f}', 
        textposition='outside',
        textfont=dict(size=14, color='#000000', family='Arial Black'),
        marker=dict(line=dict(color='#4a148c', width=1))
    )
    
    fig_category.update_layout(
        title=dict(text="Revenue by Product Category", font=dict(size=18, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Category", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Revenue ($)", font=dict(size=14, color='#000000')),
        showlegend=False,
        height=400,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        xaxis=dict(gridcolor='#dee2e6'),
        yaxis=dict(gridcolor='#dee2e6', showgrid=True)
    )
    
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    # Profit by Category with PURPLE palette
    profit_by_category = df.groupby('product_category')['estimated_profit'].sum().sort_values(ascending=False)
    
    fig_profit = px.bar(
        profit_by_category,
        x=profit_by_category.index,
        y=profit_by_category.values,
        color=profit_by_category.values,
        color_continuous_scale='Purples',
        text=profit_by_category.values
    )
    
    fig_profit.update_traces(
        texttemplate='$%{text:,.0f}', 
        textposition='outside',
        textfont=dict(size=14, color='#000000', family='Arial Black'),
        marker=dict(line=dict(color='#4a148c', width=1))
    )
    
    fig_profit.update_layout(
        title=dict(text="Estimated Profit by Category", font=dict(size=18, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Category", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Profit ($)", font=dict(size=14, color='#000000')),
        showlegend=False,
        height=400,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        xaxis=dict(gridcolor='#dee2e6'),
        yaxis=dict(gridcolor='#dee2e6', showgrid=True)
    )
    
    st.plotly_chart(fig_profit, use_container_width=True)

# Pareto Chart - Top Products with PURPLE palette
st.subheader("📊 Product Revenue Concentration (Pareto Analysis)")

product_revenue = df.groupby('product_name')['line_revenue'].sum().sort_values(ascending=False)
product_revenue_cumsum = product_revenue.cumsum()
product_revenue_pct = (product_revenue_cumsum / product_revenue.sum() * 100)

fig_pareto = go.Figure()

# Bar chart for revenue
fig_pareto.add_trace(go.Bar(
    x=product_revenue.head(20).index,
    y=product_revenue.head(20).values,
    name='Revenue',
    marker=dict(color='#6a1b9a', line=dict(color='#4a148c', width=1)),
    yaxis='y',
    text=[f'${x:,.0f}' for x in product_revenue.head(20).values],
    textposition='outside',
    textfont=dict(size=12, color='#000000', family='Arial Black')
))

# Line chart for cumulative percentage
fig_pareto.add_trace(go.Scatter(
    x=product_revenue_pct.head(20).index,
    y=product_revenue_pct.head(20).values,
    name='Cumulative %',
    marker=dict(color='#ff6f00', size=8),
    line=dict(color='#ff6f00', width=3),
    yaxis='y2',
    mode='lines+markers',
    text=[f'{x:.1f}%' for x in product_revenue_pct.head(20).values],
    textposition='top center',
    textfont=dict(size=11, color='#000000', family='Arial Black')
))

fig_pareto.update_layout(
    title=dict(text="Top 20 Products - Revenue & Cumulative Percentage", font=dict(size=18, color='#000000', family='Arial Black')),
    xaxis_title=dict(text="Product Name", font=dict(size=14, color='#000000')),
    yaxis=dict(title="Revenue ($)", side='left', gridcolor='#dee2e6', showgrid=True, titlefont=dict(size=14, color='#000000')),
    yaxis2=dict(title="Cumulative %", side='right', overlaying='y', range=[0, 100], gridcolor='#dee2e6', titlefont=dict(size=14, color='#000000')),
    height=500,
    hovermode='x unified',
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    font=dict(color='#000000', size=12),
    legend=dict(font=dict(size=12, color='#000000'))
)

st.plotly_chart(fig_pareto, use_container_width=True)

st.markdown("---")

# ========================================
# SECTION E - CHANNEL MIX (ORANGES)
# ========================================
st.header("🛒 Sales Channel Analysis")

col1, col2 = st.columns([2, 1])

with col1:
    # Revenue by Channel - Stacked Bar with ORANGE palette
    channel_revenue = df.groupby(['month', 'channel'])['line_revenue'].sum().reset_index()
    
    fig_channel = px.bar(
        channel_revenue,
        x='month',
        y='line_revenue',
        color='channel',
        title="Revenue by Channel Over Time",
        color_discrete_map={'In-store': '#e65100', 'Online': '#ff9800'},
        text='line_revenue',
        barmode='group'
    )
    
    fig_channel.update_traces(
        texttemplate='$%{text:,.0f}', 
        textposition='outside',
        textfont=dict(size=12, color='#000000', family='Arial Black'),
        marker=dict(line=dict(color='#000000', width=1))
    )
    
    fig_channel.update_layout(
        title=dict(text="Revenue by Channel Over Time", font=dict(size=18, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Month", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Revenue ($)", font=dict(size=14, color='#000000')),
        height=400,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        xaxis=dict(gridcolor='#dee2e6'),
        yaxis=dict(gridcolor='#dee2e6', showgrid=True),
        legend=dict(title="Channel", font=dict(size=12, color='#000000'))
    )
    
    st.plotly_chart(fig_channel, use_container_width=True)

with col2:
    # Channel Mix KPIs
    st.subheader("📊 Channel Distribution")
    
    total_channel_revenue = df.groupby('channel')['line_revenue'].sum()
    online_revenue = total_channel_revenue.get('Online', 0)
    instore_revenue = total_channel_revenue.get('In-store', 0)
    total_rev = total_channel_revenue.sum()
    
    online_pct = (online_revenue / total_rev * 100) if total_rev > 0 else 0
    instore_pct = (instore_revenue / total_rev * 100) if total_rev > 0 else 0
    
    st.metric(
        label="🌐 Online Revenue %",
        value=f"{online_pct:.1f}%",
        delta=None
    )
    
    st.metric(
        label="🏪 In-Store Revenue %",
        value=f"{instore_pct:.1f}%",
        delta=None
    )
    
    st.metric(
        label="💰 Online Revenue",
        value=f"${online_revenue:,.2f}",
        delta=None
    )
    
    st.metric(
        label="💰 In-Store Revenue",
        value=f"${instore_revenue:,.2f}",
        delta=None
    )

st.markdown("---")

# ========================================
# SECTION F - QUARTERLY PERFORMANCE (TEALS) - NEW
# ========================================
st.header("📅 Quarterly Business Performance")

# Calculate quarterly metrics
quarterly_data = df.groupby('quarter').agg({
    'line_revenue': 'sum',
    'customer_id': 'nunique',
    'bill_id': 'nunique'
}).reset_index()

quarterly_data.columns = ['Quarter', 'Revenue', 'Customers', 'Orders']
quarterly_data['AOV'] = quarterly_data['Revenue'] / quarterly_data['Orders']
quarterly_data = quarterly_data.sort_values('Quarter')

# Calculate QoQ growth
if len(quarterly_data) >= 2:
    current_q_rev = quarterly_data['Revenue'].iloc[-1]
    previous_q_rev = quarterly_data['Revenue'].iloc[-2]
    qoq_growth = ((current_q_rev - previous_q_rev) / previous_q_rev * 100) if previous_q_rev > 0 else 0
else:
    qoq_growth = 0

# Display Quarterly KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Current Quarter Revenue",
        value=f"${quarterly_data['Revenue'].iloc[-1]:,.2f}" if len(quarterly_data) > 0 else "$0.00",
        delta=None
    )

with col2:
    qoq_color = "normal" if qoq_growth >= 0 else "inverse"
    st.metric(
        label="📈 Quarter-over-Quarter Growth",
        value=f"{qoq_growth:.1f}%",
        delta=f"{qoq_growth:.1f}%",
        delta_color=qoq_color
    )

with col3:
    st.metric(
        label="👥 Current Quarter Customers",
        value=f"{quarterly_data['Customers'].iloc[-1]:,}" if len(quarterly_data) > 0 else "0",
        delta=None
    )

with col4:
    st.metric(
        label="🛍️ Current Quarter AOV",
        value=f"${quarterly_data['AOV'].iloc[-1]:,.2f}" if len(quarterly_data) > 0 else "$0.00",
        delta=None
    )

# Quarterly Revenue Chart with TEAL palette
col1, col2 = st.columns(2)

with col1:
    fig_quarterly_rev = px.bar(
        quarterly_data,
        x='Quarter',
        y='Revenue',
        color='Revenue',
        color_continuous_scale='Teal',
        text='Revenue',
        title="Quarterly Revenue Trend"
    )
    
    fig_quarterly_rev.update_traces(
        texttemplate='$%{text:,.0f}', 
        textposition='outside',
        textfont=dict(size=14, color='#000000', family='Arial Black'),
        marker=dict(line=dict(color='#004d40', width=1))
    )
    
    fig_quarterly_rev.update_layout(
        title=dict(text="Quarterly Revenue Trend", font=dict(size=18, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Quarter", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Revenue ($)", font=dict(size=14, color='#000000')),
        showlegend=False,
        height=400,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        xaxis=dict(gridcolor='#dee2e6'),
        yaxis=dict(gridcolor='#dee2e6', showgrid=True)
    )
    
    st.plotly_chart(fig_quarterly_rev, use_container_width=True)

with col2:
    # Quarterly Customer Count with TEAL palette
    fig_quarterly_cust = px.line(
        quarterly_data,
        x='Quarter',
        y='Customers',
        markers=True,
        title="Quarterly Customer Count"
    )
    
    fig_quarterly_cust.update_traces(
        line=dict(color='#00796b', width=3),
        marker=dict(size=10, color='#004d40', line=dict(color='#000000', width=2)),
        text=quarterly_data['Customers'],
        textposition='top center',
        textfont=dict(size=14, color='#000000', family='Arial Black')
    )
    
    fig_quarterly_cust.update_layout(
        title=dict(text="Quarterly Customer Count", font=dict(size=18, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Quarter", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Number of Customers", font=dict(size=14, color='#000000')),
        height=400,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        xaxis=dict(gridcolor='#dee2e6'),
        yaxis=dict(gridcolor='#dee2e6', showgrid=True)
    )
    
    st.plotly_chart(fig_quarterly_cust, use_container_width=True)

st.markdown("---")

# ========================================
# SECTION G - OPERATIONAL INSIGHTS
# ========================================
st.header("⚙️ Operational Insights")

col1, col2 = st.columns(2)

with col1:
    # Heatmap: Revenue by Day of Week x Store
    st.subheader("🔥 Revenue Heatmap: Day × Store")
    
    # Define day order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    heatmap_data = df.groupby(['day_of_week', 'store_location'])['line_revenue'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='store_location', values='line_revenue').fillna(0)
    
    # Reindex to ensure correct day order
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='Reds',
        text=heatmap_pivot.values,
        texttemplate='$%{text:,.0f}',
        textfont=dict(size=11, color='#000000', family='Arial Black'),
        colorbar=dict(title="Revenue ($)", titlefont=dict(color='#000000'))
    ))
    
    fig_heatmap.update_layout(
        title=dict(text="Revenue Heatmap: Day × Store", font=dict(size=16, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Store Location", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Day of Week", font=dict(size=14, color='#000000')),
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12)
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col2:
    # Quantity Distribution
    st.subheader("📦 Quantity Distribution")
    
    fig_qty = px.histogram(
        df,
        x='quantity',
        nbins=20,
        color_discrete_sequence=['#d32f2f'],
        title="Distribution of Purchase Quantities"
    )
    
    fig_qty.update_traces(
        marker=dict(line=dict(color='#000000', width=1)),
        textfont=dict(size=12, color='#000000')
    )
    
    fig_qty.update_layout(
        title=dict(text="Distribution of Purchase Quantities", font=dict(size=16, color='#000000', family='Arial Black')),
        xaxis_title=dict(text="Quantity", font=dict(size=14, color='#000000')),
        yaxis_title=dict(text="Frequency", font=dict(size=14, color='#000000')),
        height=400,
        showlegend=False,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        font=dict(color='#000000', size=12),
        xaxis=dict(gridcolor='#dee2e6'),
        yaxis=dict(gridcolor='#dee2e6', showgrid=True)
    )
    
    st.plotly_chart(fig_qty, use_container_width=True)

st.markdown("---")

# ========================================
# SECTION H - INSIGHTS & RECOMMENDATIONS (NEW)
# ========================================
st.header("🧠 Insights & Recommendations to Boost Performance")

# Calculate insights
best_store = revenue_by_store.idxmax()
best_store_revenue = revenue_by_store.max()

best_category = revenue_by_category.idxmax()
best_category_revenue = revenue_by_category.max()

# Channel efficiency
channel_aov = df.groupby('channel').agg({
    'line_revenue': 'sum',
    'bill_id': 'nunique'
})
channel_aov['AOV'] = channel_aov['line_revenue'] / channel_aov['bill_id']
best_channel = channel_aov['AOV'].idxmax()
best_channel_aov = channel_aov['AOV'].max()

# Best customer segment
segment_value = df.groupby('customer_segment').agg({
    'line_revenue': 'sum',
    'customer_id': 'nunique'
})
segment_value['ACV'] = segment_value['line_revenue'] / segment_value['customer_id']
best_segment = segment_value['ACV'].idxmax()
best_segment_acv = segment_value['ACV'].max()

# Display Insights
st.markdown(f"""
<div class="insight-box">
<h3>📊 Key Performance Insights</h3>

<p><strong>🏆 Best Performing Store:</strong> <span style="color: #0066cc; font-weight: bold;">{best_store}</span> generated <strong>${best_store_revenue:,.2f}</strong> in revenue. This location shows strong customer demand and should be considered for expansion or replication of successful strategies.</p>

<p><strong>📦 Top Revenue Category:</strong> <span style="color: #6a1b9a; font-weight: bold;">{best_category}</span> contributed <strong>${best_category_revenue:,.2f}</strong> in revenue. This category demonstrates high market demand and profitability potential.</p>

<p><strong>🛒 Most Efficient Channel:</strong> <span style="color: #e65100; font-weight: bold;">{best_channel}</span> has the highest Average Order Value of <strong>${best_channel_aov:.2f}</strong>, indicating better basket composition and customer purchasing behavior.</p>

<p><strong>👥 Highest Value Segment:</strong> <span style="color: #006d2c; font-weight: bold;">{best_segment}</span> customers have an Average Customer Value of <strong>${best_segment_acv:.2f}</strong>, making them the most valuable segment to retain and grow.</p>
</div>
""", unsafe_allow_html=True)

# Strategic Recommendations
st.markdown(f"""
<div class="recommendation-box">
<h3>💡 Strategic Recommendations</h3>

<ol style="font-size: 15px; line-height: 1.8;">
    <li><strong>Expand Digital Marketing for Loyal Customers:</strong> Increase targeted promotions and personalized offers for {best_segment} customers through email campaigns and app notifications to boost repeat purchases by 15-20%.</li>
    
    <li><strong>Strengthen {best_channel} Channel Operations:</strong> Since {best_channel} shows the highest AOV (${best_channel_aov:.2f}), invest in improving this channel's user experience, delivery speed, and product availability to capture more high-value transactions.</li>
    
    <li><strong>Promote High-Margin Categories:</strong> Focus marketing efforts on {best_category} and Personal Care products (40% margin) through in-store displays, bundle offers, and cross-selling strategies to maximize profitability.</li>
    
    <li><strong>Optimize Discount Strategy:</strong> Analyze discount effectiveness by category and segment. Reduce discounts on high-demand, high-margin products while maintaining strategic promotions for customer acquisition in underperforming segments.</li>
    
    <li><strong>Replicate {best_store} Success Model:</strong> Conduct a detailed analysis of {best_store}'s operations, product mix, staffing, and customer service practices. Implement best practices across other locations, particularly in underperforming stores, to drive overall revenue growth of 10-15%.</li>
</ol>

<p style="margin-top: 20px; font-weight: bold; color: #d32f2f;">⚡ Priority Action: Focus on retaining and growing the {best_segment} customer base while expanding the {best_channel} channel infrastructure for maximum ROI.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ========================================
# SECTION I - RAW DATA PREVIEW
# ========================================
st.header("📄 Raw Data Preview")
st.subheader("Filtered Transaction Data (First 30 Rows)")

# Display columns to show
display_columns = [
    'transaction_id', 'date', 'store_location', 'customer_segment',
    'product_category', 'product_name', 'quantity', 'unit_price',
    'discount_applied', 'line_revenue', 'channel', 'payment_method'
]

st.dataframe(
    df[display_columns].head(30).style.format({
        'unit_price': '${:.2f}',
        'discount_applied': '${:.2f}',
        'line_revenue': '${:.2f}'
    }),
    use_container_width=True,
    height=400
)

# Download button for filtered data
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name=f'urbanmart_filtered_data_{datetime.now().strftime("%Y%m%d")}.csv',
    mime='text/csv',
)

st.markdown("---")

# ========================================
# FOOTER
# ========================================
st.markdown("""
    <div style='text-align: center; color: #2c3e50; padding: 20px; background-color: #ecf0f1; border-radius: 10px;'>
        <p style='font-size: 18px; font-weight: bold;'>🏪 <strong>UrbanMart Retail Insights Dashboard</strong></p>
        <p style='font-size: 14px;'>Built with Python & Streamlit | Data-Driven Retail Analytics</p>
        <p style='font-size: 12px; color: #7f8c8d;'>© 2025 UrbanMart Analytics Team | Version 2.0 Enhanced</p>
    </div>
""", unsafe_allow_html=True)