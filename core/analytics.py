import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import execute_query_to_df
from core.sql_generator import generate_sql

def run_analytics(intent: str, entities: dict) -> dict:
    """
    Executes the SQL query and performs Pandas-based calculations based on the intent.
    Returns a dictionary with result summaries and the processed DataFrame.
    """
    sql, params = generate_sql(intent, entities)
    df = execute_query_to_df(sql, params)
    
    if df.empty:
        return {"status": "error", "message": "No data found for the given query."}
        
    result = {
        "status": "success",
        "intent": intent,
        "raw_rows": len(df),
        "data": None,
        "summary": ""
    }
    
    limit = entities.get("limit", 5) # Default limit to 5 if not specified
    
    try:
        if intent == "sales" or intent == "revenue":
            total_revenue = df['revenue'].sum()
            total_units = df['units_sold'].sum()
            result['summary'] = f"Total Revenue: ${total_revenue:,.2f} | Total Units Sold: {total_units:,}"
            cat_df = df.groupby('category')[['revenue', 'units_sold']].sum().reset_index()
            result['data'] = cat_df
            
        elif intent == "promotion":
            promo_df = df.groupby('promotion_type')[['revenue', 'units_sold']].sum().reset_index()
            promo_yes = df[df['promotion_flag'] == 1]['revenue'].sum()
            promo_no = df[df['promotion_flag'] == 0]['revenue'].sum()
            result['summary'] = f"Revenue with Promotions: ${promo_yes:,.2f} | Revenue without Promotions: ${promo_no:,.2f}"
            result['data'] = promo_df
            
        elif intent == "top_products":
            top_df = df.groupby('product_name')['revenue'].sum().reset_index().sort_values(by='revenue', ascending=False).head(limit)
            top_product = top_df.iloc[0] if not top_df.empty else None
            if top_product is not None:
                result['summary'] = f"Top Product: {top_product['product_name']} (${top_product['revenue']:,.2f})"
            result['data'] = top_df
            
        elif intent == "bottom_products":
            bottom_df = df.groupby('product_name')['revenue'].sum().reset_index().sort_values(by='revenue', ascending=True).head(limit)
            bottom_product = bottom_df.iloc[0] if not bottom_df.empty else None
            if bottom_product is not None:
                result['summary'] = f"Bottom Product: {bottom_product['product_name']} (${bottom_product['revenue']:,.2f})"
            result['data'] = bottom_df
            
        elif intent == "inventory" or intent == "stockout":
            total_stockouts = df['stockout_flag'].sum()
            stockout_rate = (total_stockouts / len(df)) * 100
            result['summary'] = f"Total Stockout Incidents: {total_stockouts} | Stockout Rate: {stockout_rate:.2f}%"
            inv_df = df.groupby('region')['stockout_flag'].sum().reset_index()
            result['data'] = inv_df
            
        elif intent == "trend":
            trend_df = df.groupby('week')['revenue'].sum().reset_index()
            start_rev = trend_df['revenue'].iloc[0]
            end_rev = trend_df['revenue'].iloc[-1]
            growth = ((end_rev - start_rev) / start_rev * 100) if start_rev else 0
            result['summary'] = f"Revenue Growth (Week 1 to {len(trend_df)}): {growth:.2f}%"
            result['data'] = trend_df
            
        elif intent == "comparison":
            comp_df = df.groupby('region')['revenue'].sum().reset_index().sort_values(by='revenue', ascending=False)
            top_region = comp_df.iloc[0] if not comp_df.empty else None
            result['summary'] = f"Top Region: {top_region['region']} (${top_region['revenue']:,.2f})" if top_region is not None else "Comparison data ready."
            result['data'] = comp_df
            
        else:
            total_revenue = df['revenue'].sum()
            result['summary'] = f"Total Revenue: ${total_revenue:,.2f}"
            result['data'] = df.head(10)
            
    except Exception as e:
        result['status'] = "error"
        result['message'] = f"Error during pandas analytics: {e}"
        
    return result

# ---------------------------------------------------------
# DIRECT DASHBOARD FETCHERS (Enterprise Analytics Pages)
# ---------------------------------------------------------

def get_db_stats():
    from core.database import get_connection
    conn = get_connection()
    try:
        products = pd.read_sql("SELECT COUNT(*) as c FROM products", conn).iloc[0]['c']
        stores = pd.read_sql("SELECT COUNT(*) as c FROM stores", conn).iloc[0]['c']
        sales = pd.read_sql("SELECT COUNT(*) as c FROM sales", conn).iloc[0]['c']
        inventory = pd.read_sql("SELECT COUNT(*) as c FROM inventory", conn).iloc[0]['c']
        
        total_rev = pd.read_sql("SELECT SUM(revenue) as r FROM sales", conn).iloc[0]['r']
        units_sold = pd.read_sql("SELECT SUM(units_sold) as u FROM sales", conn).iloc[0]['u']
        avg_discount = pd.read_sql("SELECT AVG(discount_pct) as d FROM sales WHERE promotion_flag=1", conn).iloc[0]['d'] * 100
        stockouts = pd.read_sql("SELECT SUM(stockout_flag) as s FROM inventory", conn).iloc[0]['s']
        stockout_rate = (stockouts / inventory) * 100 if inventory > 0 else 0
    except Exception:
        products, stores, sales, inventory, total_rev, units_sold, avg_discount, stockout_rate = 0, 0, 0, 0, 0.0, 0, 0.0, 0.0
    finally:
        conn.close()
    return products, stores, sales, inventory, total_rev, units_sold, avg_discount, stockout_rate

def get_dashboard_charts_data():
    sales_data = run_analytics("sales", {"limit": 5})
    promo_data = run_analytics("promotion", {"limit": 5})
    trend_data = run_analytics("trend", {"limit": 5})
    top_data = run_analytics("top_products", {"limit": 5})
    
    return sales_data, promo_data, trend_data, top_data


def get_base_sales_df() -> pd.DataFrame:
    sql = """
        SELECT s.week, s.units_sold, s.revenue, s.promotion_flag, s.promotion_type, s.discount_pct,
               p.product_name, p.brand, p.category, p.sub_category,
               st.store_name, st.region, st.city, st.store_format
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN stores st ON s.store_id = st.store_id
    """
    return execute_query_to_df(sql)

def get_base_inventory_df() -> pd.DataFrame:
    sql = """
        SELECT i.week, i.opening_stock, i.units_received, i.units_sold, i.closing_stock, i.stockout_flag,
               p.product_name, p.brand, p.category,
               st.store_name, st.region, st.city
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN stores st ON i.store_id = st.store_id
    """
    return execute_query_to_df(sql)

def get_sales_analytics():
    df = get_base_sales_df()
    return {
        'total_rev': df['revenue'].sum(),
        'units_sold': df['units_sold'].sum(),
        'avg_rev': df['revenue'].mean(),
        'growth': ((df.groupby('week')['revenue'].sum().iloc[-1] / df.groupby('week')['revenue'].sum().iloc[0]) - 1) * 100,
        'trend_weekly': df.groupby('week')['revenue'].sum().reset_index(),
        'top_products': df.groupby('product_name')['revenue'].sum().reset_index().sort_values('revenue', ascending=False).head(10),
        'by_brand': df.groupby('brand')['revenue'].sum().reset_index(),
        'by_category': df.groupby('category')['revenue'].sum().reset_index(),
        'by_region': df.groupby('region')['revenue'].sum().reset_index()
    }

def get_promotion_analytics():
    df = get_base_sales_df()
    promo_df = df[df['promotion_flag'] == 1]
    return {
        'promo_rev': promo_df['revenue'].sum(),
        'coverage': (len(promo_df) / len(df)) * 100,
        'avg_discount': promo_df['discount_pct'].mean() * 100,
        'by_type': df.groupby('promotion_type')['revenue'].sum().reset_index(),
        'discount_vs_rev': promo_df.groupby('discount_pct')['revenue'].mean().reset_index()
    }

def get_inventory_analytics():
    df = get_base_inventory_df()
    current_week = df['week'].max()
    curr_df = df[df['week'] == current_week]
    stockouts = curr_df[curr_df['stockout_flag'] == 1]
    low_stock = curr_df[(curr_df['closing_stock'] > 0) & (curr_df['closing_stock'] < 20)]
    overstock = curr_df[curr_df['closing_stock'] > 200]
    return {
        'current_inv': curr_df['closing_stock'].sum(),
        'stockout_prods': len(stockouts),
        'low_stock_prods': len(low_stock),
        'overstock_prods': len(overstock),
        'health': pd.DataFrame([{'status': 'Stockout', 'count': len(stockouts)}, {'status': 'Low Stock', 'count': len(low_stock)}, {'status': 'Healthy/Overstock', 'count': len(curr_df) - len(stockouts) - len(low_stock)}]),
        'trend': df.groupby('week')['stockout_flag'].sum().reset_index(),
        'by_region': df.groupby('region')['closing_stock'].sum().reset_index(),
        'near_stockout': low_stock[['product_name', 'store_name', 'closing_stock']].sort_values('closing_stock').head(10)
    }

def get_product_analytics():
    df = get_base_sales_df()
    prod_rev = df.groupby('product_name')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
    return {
        'top_prod': prod_rev.iloc[0]['product_name'],
        'bottom_prod': prod_rev.iloc[-1]['product_name'],
        'top_rev': prod_rev.iloc[0]['revenue'],
        'by_product': prod_rev.head(15),
        'by_category': df.groupby('category')['revenue'].sum().reset_index(),
        'by_brand': df.groupby('brand')['revenue'].sum().reset_index()
    }

def get_regional_analytics():
    df = get_base_sales_df()
    reg_rev = df.groupby('region')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
    return {
        'best_reg': reg_rev.iloc[0]['region'],
        'worst_reg': reg_rev.iloc[-1]['region'],
        'best_rev': reg_rev.iloc[0]['revenue'],
        'worst_rev': reg_rev.iloc[-1]['revenue'],
        'units_reg': df.groupby('region')['units_sold'].sum().reset_index(),
        'by_region': reg_rev,
        'trend_reg': df.groupby(['week', 'region'])['revenue'].sum().reset_index()
    }

def get_trend_analytics():
    df = get_base_sales_df()
    weekly = df.groupby('week')['revenue'].sum().reset_index()
    return {
        'weekly': weekly,
        'promo_trend': df.groupby(['week', 'promotion_type'])['revenue'].sum().reset_index(),
        'growth': ((weekly['revenue'].iloc[-1] / weekly['revenue'].iloc[0]) - 1) * 100
    }
