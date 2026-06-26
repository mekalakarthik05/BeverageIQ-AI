import pytest
from core.analytics import get_db_stats, get_dashboard_charts_data

def test_get_db_stats():
    stats = get_db_stats()
    assert len(stats) == 8
    
    products, stores, sales, inventory, rev, units, discount, stockout = stats
    assert products > 0
    assert stores > 0
    assert rev > 0

def test_dashboard_charts_data():
    sales_data, promo_data, trend_data, top_data = get_dashboard_charts_data()
    assert sales_data is not None
    assert not sales_data['data'].empty
