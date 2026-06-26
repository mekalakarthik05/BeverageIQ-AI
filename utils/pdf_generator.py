import io
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

# Theme Colors (Matching BeverageIQ UI)
BG_COLOR = (0.043, 0.063, 0.125)        # #0B1020
CARD_BG = (0.086, 0.106, 0.184)         # #161B2F
TEXT_PRIMARY = (0.973, 0.980, 0.988)    # #F8FAFC
TEXT_SECONDARY = (0.580, 0.639, 0.722)  # #94A3B8
PURPLE = (0.545, 0.361, 0.965)          # #8B5CF6
TEAL = (0.176, 0.831, 0.749)            # #2DD4BF
DANGER = (0.957, 0.247, 0.369)          # #F43F5E

def set_color(c, rgb_tuple):
    c.setFillColorRGB(*rgb_tuple)

def set_stroke(c, rgb_tuple):
    c.setStrokeColorRGB(*rgb_tuple)

def draw_master_background(c, width, height, title, date_str):
    """Draws the dark master layout including header, footer, and watermark."""
    # Full Dark Background
    set_color(c, BG_COLOR)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Header Bar
    set_color(c, CARD_BG)
    c.rect(0, height - 60, width, 60, fill=1, stroke=0)
    
    # BeverageIQ Branding
    set_color(c, PURPLE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 38, "Beverage")
    set_color(c, TEAL)
    c.drawString(130, height - 38, "IQ")
    
    # Title & Date
    set_color(c, TEXT_SECONDARY)
    c.setFont("Helvetica", 12)
    c.drawString(165, height - 38, f"|   {title}")
    
    c.setFont("Helvetica", 10)
    c.drawString(width - 120, height - 35, date_str)
    
    # Diagonal CONFIDENTIAL Watermark
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(45)
    c.setFont("Helvetica-Bold", 80)
    c.setFillColorRGB(1, 1, 1, alpha=0.03)
    c.drawCentredString(0, 0, "CONFIDENTIAL")
    c.restoreState()
    
    # Footer
    set_color(c, TEXT_SECONDARY)
    c.setFont("Helvetica", 9)
    c.drawString(40, 20, "BeverageIQ Enterprise Analytics - Internal Executive Report")
    c.drawString(width - 60, 20, f"Page {c.getPageNumber()}")

def is_risk_kpi(label):
    lbl = label.lower()
    risk_keywords = ['stockout', 'worst', 'lowest', 'overstock', 'risk']
    for w in risk_keywords:
        if w in lbl: return True
    return False

def generate_enterprise_pdf(title, subtitle, date_str, kpis=None, insights=None, charts=None):
    """Generates a majestic multi-page, dark-themed executive PDF using ReportLab."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # ==========================================
    # PAGE 1: COVER PAGE
    # ==========================================
    set_color(c, BG_COLOR)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Graphic Accents
    set_color(c, PURPLE)
    c.rect(40, 0, 10, height, fill=1, stroke=0)
    set_color(c, TEAL)
    c.rect(50, 0, 4, height, fill=1, stroke=0)
    
    # Center Branding
    set_color(c, PURPLE)
    c.setFont("Helvetica-Bold", 72)
    c.drawString(80, height/2 + 80, "Beverage")
    set_color(c, TEAL)
    c.drawString(400, height/2 + 80, "IQ")
    
    set_color(c, TEXT_PRIMARY)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(80, height/2 + 10, title)
    
    c.setFont("Helvetica", 18)
    set_color(c, TEXT_SECONDARY)
    c.drawString(80, height/2 - 30, subtitle)
    
    c.setFont("Helvetica", 14)
    set_color(c, TEXT_SECONDARY)
    c.drawString(80, height/2 - 120, f"Date Generated: {date_str}")
    c.drawString(80, height/2 - 140, "Confidential Enterprise Analytics Report")
    
    c.showPage()
    
    # ==========================================
    # PAGE 2: EXECUTIVE SUMMARY & KPIs
    # ==========================================
    if kpis:
        draw_master_background(c, width, height, title, date_str)
        y_pos = height - 120
        
        set_color(c, TEXT_PRIMARY)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(40, y_pos, "Business Health & KPIs")
        y_pos -= 20
        
        set_color(c, TEXT_SECONDARY)
        c.setFont("Helvetica", 12)
        c.drawString(40, y_pos, "High-level metrics identifying current business posture.")
        y_pos -= 50
        
        card_w = (width - 100) / 2
        card_h = 75
        x_start = 40
        x_curr = x_start
        
        for idx, (k_label, k_val) in enumerate(kpis):
            if y_pos < 120:
                c.showPage()
                draw_master_background(c, width, height, title, date_str)
                y_pos = height - 120
                
            is_risk = is_risk_kpi(k_label)
            
            # Card BG
            set_color(c, CARD_BG)
            set_stroke(c, CARD_BG)
            c.roundRect(x_curr, y_pos - card_h, card_w, card_h, 8, fill=1, stroke=0)
            
            # Accent Stripe (Danger Red or Brand Purple)
            accent_color = DANGER if is_risk else PURPLE
            set_color(c, accent_color)
            c.roundRect(x_curr, y_pos - card_h, 8, card_h, 8, fill=1, stroke=0)
            
            # Label
            set_color(c, DANGER if is_risk else TEXT_SECONDARY)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_curr + 25, y_pos - 25, str(k_label).upper())
            
            # Value
            set_color(c, TEXT_PRIMARY)
            c.setFont("Helvetica-Bold", 22)
            c.drawString(x_curr + 25, y_pos - 55, str(k_val))
            
            x_curr += card_w + 20
            if (idx + 1) % 2 == 0:
                x_curr = x_start
                y_pos -= (card_h + 20)
                
        c.showPage()
        
    # ==========================================
    # PAGE 3: VISUAL ANALYTICS
    # ==========================================
    if charts:
        draw_master_background(c, width, height, title, date_str)
        y_pos = height - 120
        
        set_color(c, TEXT_PRIMARY)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(40, y_pos, "Visual Analytics")
        y_pos -= 20
        
        set_color(c, TEXT_SECONDARY)
        c.setFont("Helvetica", 12)
        c.drawString(40, y_pos, "High-resolution telemetry exported natively from the dashboard.")
        y_pos -= 50
        
        for idx, fig in enumerate(charts):
            if fig is None: continue
            
            img_height = 280
            if y_pos < img_height + 60:
                c.showPage()
                draw_master_background(c, width, height, title, date_str)
                y_pos = height - 120
                
            try:
                # High-res retina export
                img_bytes = fig.to_image(format="png", width=1200, height=700, scale=2)
                img = ImageReader(io.BytesIO(img_bytes))
                img_width = 520
                
                # Chart Background Container to blend nicely
                set_color(c, CARD_BG)
                c.roundRect(40, y_pos - img_height - 10, img_width + 10, img_height + 20, 10, fill=1, stroke=0)
                
                c.drawImage(img, 45, y_pos - img_height, width=img_width, height=img_height, preserveAspectRatio=True)
                
                y_pos -= (img_height + 40)
            except Exception as e:
                # Fail-safe
                set_color(c, CARD_BG)
                c.roundRect(40, y_pos - img_height - 10, 530, img_height + 20, 10, fill=1, stroke=0)
                set_color(c, DANGER)
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(width/2, y_pos - (img_height/2), "[ Chart Unavailable / Missing Dependencies ]")
                print(f"Chart export failed dynamically: {e}")
                y_pos -= (img_height + 40)
                
        c.showPage()
        
    # ==========================================
    # PAGE 4: BUSINESS INSIGHTS
    # ==========================================
    if insights:
        draw_master_background(c, width, height, title, date_str)
        y_pos = height - 120
        
        set_color(c, TEXT_PRIMARY)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(40, y_pos, "Business Insights & Actions")
        y_pos -= 20
        
        set_color(c, TEXT_SECONDARY)
        c.setFont("Helvetica", 12)
        c.drawString(40, y_pos, "AI-driven analysis and recommended business actions.")
        y_pos -= 50
        
        for ins in insights:
            if y_pos < 120:
                c.showPage()
                draw_master_background(c, width, height, title, date_str)
                y_pos = height - 120
                
            is_rec = str(ins).startswith("RECOMMENDATION:")
            card_h = 60
            
            # Card Background
            if is_rec:
                c.setFillColorRGB(0.176, 0.831, 0.749, alpha=0.1) # Transparent Teal
                set_stroke(c, TEAL)
            else:
                set_color(c, CARD_BG)
                set_stroke(c, CARD_BG)
                
            c.roundRect(40, y_pos - card_h, width - 80, card_h, 8, fill=1, stroke=1)
            
            # Icon / Prefix
            if is_rec:
                set_color(c, TEAL)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(60, y_pos - 25, "TARGET ACTION")
                set_color(c, TEXT_PRIMARY)
                c.setFont("Helvetica-Bold", 12)
                text_to_draw = str(ins).replace("RECOMMENDATION:", "").strip()
            else:
                set_color(c, PURPLE)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(60, y_pos - 25, "INSIGHT")
                set_color(c, TEXT_PRIMARY)
                c.setFont("Helvetica", 12)
                text_to_draw = str(ins).replace("Summary: ", "").strip()
                
            # Truncate text nicely for PDF
            text_to_draw = text_to_draw[:110] + ("..." if len(text_to_draw)>110 else "")
            c.drawString(60, y_pos - 45, text_to_draw)
            
            y_pos -= (card_h + 20)
            
        c.showPage()
        
    # ==========================================
    # PAGE 5: APPENDIX
    # ==========================================
    draw_master_background(c, width, height, title, date_str)
    y_pos = height - 120
    
    set_color(c, TEXT_PRIMARY)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, y_pos, "Appendix & Methodology")
    y_pos -= 50
    
    set_color(c, TEXT_SECONDARY)
    c.setFont("Helvetica", 12)
    
    paras = [
        "This report was generated autonomously by the BeverageIQ Enterprise Analytics Engine.",
        "Data was sourced directly from the production SQLite data warehouse and analyzed via Pandas.",
        "Visualizations are powered by Plotly and rendered at high-resolution using Kaleido.",
        "Any natural language insights were generated using local Ollama LLM deployments",
        "running at strict zero-temperature to eliminate hallucination vectors.",
        "",
        "CONFIDENTIALITY NOTICE:",
        "This document contains proprietary financial and inventory telemetry.",
        "It is intended solely for the use of authorized executive personnel."
    ]
    
    for p in paras:
        if p.startswith("CONFIDENTIALITY"):
            y_pos -= 30
            set_color(c, DANGER)
            c.setFont("Helvetica-Bold", 12)
        elif p.startswith("This document"):
            set_color(c, TEXT_SECONDARY)
            c.setFont("Helvetica", 12)
            
        c.drawString(40, y_pos, p)
        y_pos -= 20
        
    set_color(c, PURPLE)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, 100, "BeverageIQ")
    set_color(c, TEAL)
    c.drawString(155, 100, "AI Engineering")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
