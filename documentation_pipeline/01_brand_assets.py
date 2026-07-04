import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required. Please install it using: pip install Pillow")
    exit(1)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
BRAND_DIR = ROOT / "docs" / "report_assets" / "branding"
BRAND_DIR.mkdir(parents=True, exist_ok=True)

# Corporate Colors
PRIMARY_BLUE = "#3B82F6"
PRIMARY_GREEN = "#10B981"
DARK_BG = "#0F172A"
LIGHT_BG = "#FFFFFF"

def draw_logo(bg_color=None, transparent=False, size=(800, 800)):
    if transparent:
        img = Image.new("RGBA", size, (255, 255, 255, 0))
    else:
        img = Image.new("RGBA", size, bg_color)
        
    draw = ImageDraw.Draw(img)
    
    # Coordinates for drawing the central lens / Q motif
    cx, cy = size[0] // 2, size[1] // 2
    radius = int(size[0] * 0.35)
    
    # Draw outer ring (Blue)
    draw.arc(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        start=45, end=360, fill=PRIMARY_BLUE, width=int(size[0]*0.1)
    )
    
    # Draw inner AI node (Green)
    inner_r = int(radius * 0.4)
    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        fill=PRIMARY_GREEN
    )
    
    # Draw the 'Q' tail / Circuit line (Green)
    draw.line(
        [cx + inner_r, cy + inner_r, cx + radius + int(size[0]*0.1), cy + radius + int(size[0]*0.1)],
        fill=PRIMARY_GREEN, width=int(size[0]*0.08), joint="curve"
    )
    
    return img

def main():
    print("="*50)
    print("Phase 1: Generating Brand Assets")
    print("="*50)
    
    assets = {
        "logo_transparent.png": draw_logo(transparent=True),
        "logo_dark.png": draw_logo(bg_color=DARK_BG),
        "logo_light.png": draw_logo(bg_color=LIGHT_BG),
        "favicon.png": draw_logo(transparent=True, size=(64, 64)),
        "app_icon.png": draw_logo(bg_color=DARK_BG, size=(512, 512)),
    }
    
    for filename, img in assets.items():
        filepath = BRAND_DIR / filename
        img.save(filepath)
        print(f"[OK] Generated {filename}")
        
    print(f"\nAll brand assets saved to {BRAND_DIR.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
