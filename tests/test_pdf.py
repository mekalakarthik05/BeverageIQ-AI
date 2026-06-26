import pytest
from utils.pdf_generator import generate_enterprise_pdf

def test_pdf_generation_bytes():
    pdf_bytes = generate_enterprise_pdf(
        title="Test Report",
        subtitle="Testing PDF Engine",
        date_str="2026-07-03",
        kpis=[("Test KPI", "100")]
    )
    
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b'%PDF-') # Verify PDF header signature
