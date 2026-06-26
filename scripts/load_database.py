import sqlite3
import pandas as pd
import sys
from pathlib import Path

# Add project root to path so we can import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR, DATABASE_PATH

def load_data_to_db():
    print(f"Connecting to database at {DATABASE_PATH}...")
    conn = sqlite3.connect(DATABASE_PATH)
    
    tables = ['products', 'stores', 'sales', 'inventory']
    
    for table in tables:
        csv_file = DATA_DIR / f"{table}.csv"
        if not csv_file.exists():
            print(f"Error: {csv_file} not found. Please run generate_dataset.py first.")
            return
            
        print(f"Loading {table}...")
        df = pd.read_csv(csv_file)
        
        # Write to SQLite
        df.to_sql(table, conn, if_exists='replace', index=False)
        print(f"Loaded {len(df)} rows into {table}.")
        
    print("Creating indexes...")
    cursor = conn.cursor()
    
    # Indexes for Products
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    
    # Indexes for Stores
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stores_region ON stores(region)")
    
    # Indexes for Sales
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_week ON sales(week)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_store_id ON sales(store_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_promo ON sales(promotion_flag)")
    
    # Indexes for Inventory
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_week ON inventory(week)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_store_id ON inventory(store_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_stockout ON inventory(stockout_flag)")
    
    conn.commit()
    conn.close()
    
    print("Database loaded successfully with indexes.")

if __name__ == "__main__":
    load_data_to_db()
