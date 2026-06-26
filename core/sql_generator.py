def generate_sql(intent: str, entities: dict) -> tuple[str, tuple]:
    """
    Generates a parameterized SQL query and its parameters based on intent.
    Returns (sql_query, params_tuple).
    """
    # Base query for sales & products & stores
    base_sales_query = """
        SELECT 
            s.week, s.units_sold, s.revenue, s.promotion_flag, s.promotion_type, s.discount_pct,
            p.product_name, p.brand, p.category, p.sub_category,
            st.store_name, st.region, st.city, st.store_format
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN stores st ON s.store_id = st.store_id
    """
    
    # Base query for inventory & products & stores
    base_inventory_query = """
        SELECT 
            i.week, i.opening_stock, i.units_received, i.units_sold, i.closing_stock, i.stockout_flag,
            p.product_name, p.brand, p.category,
            st.store_name, st.region, st.city
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN stores st ON i.store_id = st.store_id
    """

    where_clauses = []
    params = []
    
    # Apply entity filters if any
    if entities.get("regions"):
        placeholders = ",".join(["?"] * len(entities["regions"]))
        where_clauses.append(f"st.region IN ({placeholders})")
        params.extend(entities["regions"])
        
    if entities.get("categories"):
        placeholders = ",".join(["?"] * len(entities["categories"]))
        where_clauses.append(f"p.category IN ({placeholders})")
        params.extend(entities["categories"])
        
    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)
        
    if intent in ["inventory", "stockout"]:
        sql = base_inventory_query + where_sql
    else:
        sql = base_sales_query + where_sql
        
    return sql, tuple(params)
