import asyncio
from playwright.async_api import async_playwright
import os
import fitz  # PyMuPDF
import sys

# Ensure backend imports work for PDF generation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_generator import generate_enterprise_pdf

async def capture():
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Force 1920x1080
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        print("Connecting to Streamlit...")
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await page.wait_for_timeout(4000) # Let it warm up
        
        pages = [
            ("🏠 Executive Dashboard", "dashboard.png"),
            ("💬 Analytics Chat", "analytics_chat.png"),
            ("📊 Sales Analytics", "sales.png"),
            ("🎯 Promotion Analytics", "promotion.png"),
            ("📦 Inventory Analytics", "inventory.png"),
            ("🌟 Product Analytics", "products.png"),
            ("🌍 Regional Analytics", "regional.png"),
            ("📈 Trend Analytics", "trends.png"),
            ("🗄️ Data Explorer", "explorer.png"),
            ("⚙️ System Status", "system_status.png")
        ]
        
        for name, file in pages:
            print(f"Navigating to {file}...")
            try:
                # Find the radio label
                loc = page.locator(f'label:has-text("{name}")').first
                if await loc.count() > 0:
                    await loc.click()
                else:
                    await page.locator(f'text="{name}"').first.click()
                    
                # Wait for any spinner to disappear
                await page.wait_for_timeout(3000)
                
                # Special logic for chat page
                if "chat" in file:
                    print("Clicking 'Best Promotion'...")
                    try:
                        await page.locator('button:has-text("🏆 Best Promotion")').first.click()
                        print("Waiting for AI Analysis Result...")
                        # Wait specifically for the LLM output header to appear, giving it up to 120s
                        await page.wait_for_selector('text="AI Analysis Result"', state="visible", timeout=120000)
                        # Wait for charts to animate/render
                        await page.wait_for_timeout(5000)
                    except Exception as ce:
                        print(f"Chat interaction failed: {ce}")
                
                await page.screenshot(path=f"screenshots/{file}", full_page=True)
                print(f"Captured {file}")
            except Exception as e:
                print(f"Failed to capture {name}: {e}")
                
        await browser.close()
        
    print("Generating High-Res PDF sample...")
    try:
        pdf_bytes = generate_enterprise_pdf(
            title="Executive Dashboard",
            subtitle="Automated PDF Export",
            date_str="2026-07-04",
            kpis=[("Total Revenue", "$1,000,000")]
        )
        doc = fitz.open("pdf", pdf_bytes)
        page = doc[0] # First page
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3)) # High res (3x scaling)
        pix.save("screenshots/pdf_sample.png")
        print("Captured pdf_sample.png")
    except Exception as e:
        print(f"Failed to generate pdf sample: {e}")
        
    print("Done capturing all screenshots.")

if __name__ == "__main__":
    asyncio.run(capture())
