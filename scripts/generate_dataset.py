import os
import sys
import pandas as pd
import numpy as np
import random
from pathlib import Path

# Add project root to path so we can import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR, NUM_PRODUCTS, NUM_STORES, WEEKS_OF_SALES

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_products():
    print("Generating Products...")
    brands = ['AquaFlow', 'FizzyPop', 'NatureNectar', 'BrewMaster']
    categories = ['Carbonated', 'Juice', 'Water', 'Energy']
    
    products_data = []
    for i in range(1, NUM_PRODUCTS + 1):
        brand = random.choice(brands)
        cat = random.choice(categories)
        sub_cat = f"{cat} - {random.choice(['Diet', 'Regular', 'Premium'])}"
        
        products_data.append({
            'product_id': f"P{i:03d}",
            'product_name': f"{brand} {cat} {i}",
            'brand': brand,
            'category': cat,
            'sub_category': sub_cat,
            'unit_price': round(random.uniform(1.5, 5.0), 2),
            'pack_size_ml': random.choice([330, 500, 1000, 1500])
        })
    return pd.DataFrame(products_data)

def generate_stores():
    print("Generating Stores...")
    regions = ['North', 'South', 'East', 'West']
    formats = ['Supermarket', 'Convenience', 'Hypermarket']
    
    stores_data = []
    for i in range(1, NUM_STORES + 1):
        region = random.choice(regions)
        store_format = random.choice(formats)
        city = f"City_{region}_{i}"
        
        stores_data.append({
            'store_id': f"S{i:03d}",
            'store_name': f"Store {i} - {city}",
            'city': city,
            'region': region,
            'store_format': store_format
        })
    return pd.DataFrame(stores_data)

def generate_sales_and_inventory(products_df, stores_df):
    print("Generating Sales and Inventory...")
    weeks = list(range(1, WEEKS_OF_SALES + 1))
    
    promo_types = ['Price Cut', 'Bundle', 'BOGO', 'Display', 'No Promotion']
    promo_weights = [0.1, 0.05, 0.05, 0.1, 0.7] # 70% of the time, no promotion
    
    sales_data = []
    inventory_data = []
    
    for week in weeks:
        for _, store in stores_df.iterrows():
            for _, product in products_df.iterrows():
                
                # Baseline weekly sales
                base_sales = np.random.normal(loc=50, scale=15)
                
                # Promotions
                promo_type = np.random.choice(promo_types, p=promo_weights)
                promotion_flag = 1 if promo_type != 'No Promotion' else 0
                
                discount_pct = 0.0
                sales_multiplier = 1.0
                
                if promo_type == 'Price Cut':
                    discount_pct = 0.2
                    sales_multiplier = 1.5
                elif promo_type == 'Bundle':
                    discount_pct = 0.15
                    sales_multiplier = 1.3
                elif promo_type == 'BOGO':
                    discount_pct = 0.5
                    sales_multiplier = 2.0
                elif promo_type == 'Display':
                    discount_pct = 0.0
                    sales_multiplier = 1.2
                    
                units_sold = int(max(0, base_sales * sales_multiplier))
                
                # Add some noise based on region or format if desired
                if store['store_format'] == 'Hypermarket':
                    units_sold = int(units_sold * 1.5)
                
                unit_price = product['unit_price']
                actual_price = unit_price * (1 - discount_pct)
                revenue = round(units_sold * actual_price, 2)
                
                sales_data.append({
                    'week': week,
                    'product_id': product['product_id'],
                    'store_id': store['store_id'],
                    'units_sold': units_sold,
                    'revenue': revenue,
                    'promotion_flag': promotion_flag,
                    'promotion_type': promo_type,
                    'discount_pct': discount_pct
                })
                
                # Inventory simulation
                # Simple logic: we try to maintain 2 weeks of cover
                target_inventory = int(units_sold * 2.5)
                opening_stock = max(0, target_inventory - int(np.random.normal(10, 5))) 
                units_received = max(0, units_sold + (target_inventory - opening_stock))
                
                # Cap the units sold to what we actually have + received
                available_stock = opening_stock + units_received
                if units_sold > available_stock:
                    units_sold = available_stock
                    sales_data[-1]['units_sold'] = units_sold
                    sales_data[-1]['revenue'] = round(units_sold * actual_price, 2)
                    
                closing_stock = available_stock - units_sold
                stockout_flag = 1 if closing_stock == 0 else 0
                
                inventory_data.append({
                    'week': week,
                    'store_id': store['store_id'],
                    'product_id': product['product_id'],
                    'opening_stock': opening_stock,
                    'units_received': units_received,
                    'units_sold': units_sold,
                    'closing_stock': closing_stock,
                    'stockout_flag': stockout_flag
                })
                
    return pd.DataFrame(sales_data), pd.DataFrame(inventory_data)

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    products_df = generate_products()
    stores_df = generate_stores()
    sales_df, inventory_df = generate_sales_and_inventory(products_df, stores_df)
    
    products_df.to_csv(DATA_DIR / "products.csv", index=False)
    stores_df.to_csv(DATA_DIR / "stores.csv", index=False)
    sales_df.to_csv(DATA_DIR / "sales.csv", index=False)
    inventory_df.to_csv(DATA_DIR / "inventory.csv", index=False)
    
    print(f"Data generation complete! Saved to {DATA_DIR}")

if __name__ == "__main__":
    main()
