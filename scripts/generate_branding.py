import os
import sys
import base64
from PIL import Image, ImageDraw, ImageFont

def get_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

def process_branding():
    assets_dir = "assets"
    source_logo = os.path.join(assets_dir, "logo.png")
    
    if not os.path.exists(source_logo):
        print(f"Error: Master logo not found at {source_logo}")
        sys.exit(1)
        
    print(f"Processing master logo: {source_logo}")
    img = Image.open(source_logo).convert("RGBA")
    w, h = img.size
    
    # --- 1. Master Logo Transparency ---
    data = img.getdata()
    transparent_data = []
    # Strict lum-keying to preserve glowing pixels
    for item in data:
        r, g, b, a = item
        if r < 12 and g < 12 and b < 20:
            transparent_data.append((0, 0, 0, 0))
        else:
            transparent_data.append(item)
            
    transparent_img = Image.new("RGBA", img.size)
    transparent_img.putdata(transparent_data)
    
    # 2048x2048 Master Logo
    logo_2048 = transparent_img.resize((2048, 2048), Image.Resampling.LANCZOS)
    logo_2048.save(os.path.join(assets_dir, "logo.png"), "PNG")
    logo_2048.save(os.path.join(assets_dir, "logo_dark.png"), "PNG")
    logo_2048.save(os.path.join(assets_dir, "logo_light.png"), "PNG")
    print("Generated 2048x2048 transparent master logos (logo.png, logo_dark.png, logo_light.png)")

    # --- 2. Icon Cropping (Favicon / App Icon) ---
    # The logo has the icon in the center top. We crop a tight square around it.
    icon_box = (int(w*0.08), int(h*0.05), int(w*0.92), int(h*0.75))
    icon_img = transparent_img.crop(icon_box)
    
    # Make perfect square
    iw, ih = icon_img.size
    dim = max(iw, ih)
    square_icon = Image.new("RGBA", (dim, dim), (0,0,0,0))
    square_icon.paste(icon_img, ((dim - iw) // 2, (dim - ih) // 2))
    
    app_icon = square_icon.resize((1024, 1024), Image.Resampling.LANCZOS)
    app_icon.save(os.path.join(assets_dir, "app_icon.png"), "PNG")
    print("Generated app_icon.png (1024x1024)")
    
    favicon_png = square_icon.resize((512, 512), Image.Resampling.LANCZOS)
    favicon_png.save(os.path.join(assets_dir, "favicon.png"), "PNG")
    print("Generated favicon.png (512x512)")
    
    favicon_png.save(os.path.join(assets_dir, "favicon.ico"), format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Generated favicon.ico (multi-resolution 16px to 256px)")
    
    # --- 3. Sidebar Lockup (1400x400) ---
    sidebar_w, sidebar_h = 1400, 400
    sidebar_logo = Image.new("RGBA", (sidebar_w, sidebar_h), (0,0,0,0))
    draw_sb = ImageDraw.Draw(sidebar_logo)
    
    # Icon on the left
    icon_360 = square_icon.resize((360, 360), Image.Resampling.LANCZOS)
    sidebar_logo.paste(icon_360, (20, 20))
    
    # Typography
    font_sb_title = get_font("segoeuib.ttf", 160)
    font_sb_sub = get_font("segoeui.ttf", 60)
    
    draw_sb.text((420, 70), "BeverageIQ", font=font_sb_title, fill="#F8FAFC")
    draw_sb.text((425, 260), "Enterprise AI FMCG Analytics Platform", font=font_sb_sub, fill="#7C5CFC")
    
    sidebar_logo.save(os.path.join(assets_dir, "sidebar_logo.png"), "PNG")
    print("Generated sidebar_logo.png (1400x400 lockup)")
    
    # --- 4. Social Preview (1280x640) ---
    social_w, social_h = 1280, 640
    social_img = Image.new("RGBA", (social_w, social_h), "#0B1020")
    draw_soc = ImageDraw.Draw(social_img)
    
    # Glow/Gradient background effect
    draw_soc.ellipse((-200, -200, 600, 600), fill="#120c29")
    draw_soc.ellipse((800, 200, 1600, 1000), fill="#0f172a")
    
    # Icon
    icon_500 = square_icon.resize((480, 480), Image.Resampling.LANCZOS)
    social_img.paste(icon_500, (60, 80), icon_500)
    
    font_soc_title = get_font("segoeuib.ttf", 110)
    font_soc_sub = get_font("segoeui.ttf", 45)
    font_soc_chip = get_font("segoeuib.ttf", 24)
    
    draw_soc.text((560, 140), "BeverageIQ", font=font_soc_title, fill="#F8FAFC")
    draw_soc.text((565, 290), "Enterprise AI FMCG", font=font_soc_sub, fill="#2DD4BF")
    draw_soc.text((565, 360), "Analytics Platform", font=font_soc_sub, fill="#7C5CFC")
    
    # Feature Chips
    chips = ["🤖 AI Powered", "⚡ Real-Time Analytics", "📊 Executive Reports", "🛡️ Zero Hallucination"]
    cx, cy = 565, 480
    for chip in chips:
        # Measure text using getbbox
        bbox = font_soc_chip.getbbox(chip)
        cw = bbox[2] - bbox[0] + 40
        ch = bbox[3] - bbox[1] + 20
        draw_soc.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=10, fill="#161B2E", outline="#7C5CFC", width=2)
        draw_soc.text((cx+20, cy+6), chip, font=font_soc_chip, fill="#F8FAFC")
        cx += cw + 25

    social_img.save(os.path.join(assets_dir, "social_preview.png"), "PNG")
    print("Generated social_preview.png (1280x640 SaaS Hero)")
    
    # --- 5. Base64 SVGs ---
    def create_svg(png_path, svg_path):
        with open(png_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        tmp = Image.open(png_path)
        sw, sh = tmp.size
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sw} {sh}" width="{sw}" height="{sh}">
  <image href="data:image/png;base64,{encoded}" width="{sw}" height="{sh}" />
</svg>'''
        with open(svg_path, "w") as f:
            f.write(svg_content)
            
    create_svg(os.path.join(assets_dir, "logo.png"), os.path.join(assets_dir, "logo.svg"))
    create_svg(os.path.join(assets_dir, "favicon.png"), os.path.join(assets_dir, "favicon.svg"))
    print("Generated logo.svg and favicon.svg (Base64 embedded)")

if __name__ == "__main__":
    process_branding()
