import re
import colorsys

def hex_to_hsl(hex_code):
    hex_code = hex_code.lstrip('#')
    if len(hex_code) == 3:
        hex_code = "".join([c*2 for c in hex_code])
    r, g, b = tuple(int(hex_code[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)

def hsl_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

def generate_light_color(hex_code):
    try:
        h, l, s = hex_to_hsl(hex_code)
        # Invert lightness: If it's dark (l < 0.5), make it light (1.0 - l)
        # but keep it within bounds (0.05 to 0.95)
        # Also reduce saturation slightly for light mode to look cleaner
        new_l = 1.0 - l
        if new_l > 0.95: new_l = 0.95
        if new_l < 0.1: new_l = 0.1
        
        # Exceptions for primary/accents
        if s > 0.5 and 0.4 < l < 0.6:
            # Leave saturated mid-tones (blues/greens) alone
            new_l = l
            
        new_s = max(0, s - 0.1)
        return hsl_to_hex(h, new_l, new_s)
    except:
        return hex_code

html = open('app/templates/base.html', encoding='utf-8').read()

# Extract colors dict
color_match = re.search(r'"colors":\s*\{([^}]+)\}', html)
if not color_match:
    print("Could not find colors dict")
    exit(1)

colors_body = color_match.group(1)
color_pairs = re.findall(r'"([^"]+)":\s*"([^"]+)"', colors_body)

dark_css = []
light_css = []
new_tailwind_colors = []

for name, hex_code in color_pairs:
    if hex_code.startswith('#'):
        var_name = f"--color-{name}"
        dark_css.append(f"            {var_name}: {hex_code};")
        light_hex = generate_light_color(hex_code)
        
        # Manual overrides for better aesthetics
        if name == "background" or name == "surface" or name == "surface-dim":
            light_hex = "#f8fafc"
        elif name == "surface-container-highest" or name == "surface-variant":
            light_hex = "#e2e8f0"
        elif name == "surface-container-low" or name == "surface-container":
            light_hex = "#f1f5f9"
        elif name.startswith("on-surface") or name == "on-background":
            light_hex = "#0f172a"
        elif name == "outline-variant" or name == "outline":
            light_hex = "#cbd5e1"
            
        light_css.append(f"            {var_name}: {light_hex};")
        new_tailwind_colors.append(f'                      "{name}": "var({var_name})"')
    else:
        new_tailwind_colors.append(f'                      "{name}": "{hex_code}"')

style_block = f"""
    <style>
        :root {{
{chr(10).join(light_css)}
        }}
        .dark {{
{chr(10).join(dark_css)}
        }}
    </style>
"""

# Replace colors in Tailwind config
new_colors_body = ",\n".join(new_tailwind_colors)
html = html[:color_match.start(1)] + "\n" + new_colors_body + "\n                    " + html[color_match.end(1):]

# Inject style block into head
html = html.replace('</head>', style_block + '</head>')

open('app/templates/base.html', 'w', encoding='utf-8').write(html)
print("Successfully injected CSS variables for Light/Dark mode!")
