import urllib.request
import re

# 2. Fix RGBA issues in stitch_custom.css
with open('app/static/css/stitch_custom.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace dark background rgba (17, 28, 45 is #111C2D, surface-container-low in dark mode)
def replace_surface_container_low(match):
    opacity = float(match.group(1))
    return f"color-mix(in srgb, var(--color-surface-container-low) {int(opacity*100)}%, transparent)"
css = re.sub(r'rgba\(\s*17\s*,\s*28\s*,\s*45\s*,\s*([\d\.]+)\s*\)', replace_surface_container_low, css)

# Replace borders using white/black to adapt based on outline colors
def replace_border_colors(match):
    opacity = float(match.group(2))
    return f"color-mix(in srgb, var(--color-outline-variant) {int(opacity*100)}%, transparent)"
css = re.sub(r'rgba\(\s*(255|0)\s*,\s*\1\s*,\s*\1\s*,\s*([\d\.]+)\s*\)', replace_border_colors, css)

# Replace primary glow colors
def replace_primary_glow(match):
    opacity = float(match.group(1))
    return f"color-mix(in srgb, var(--color-primary) {int(opacity*100)}%, transparent)"
css = re.sub(r'rgba\(\s*59\s*,\s*130\s*,\s*246\s*,\s*([\d\.]+)\s*\)', replace_primary_glow, css)

# Also fix background colors if any were missed
css = css.replace('#111C2D', 'var(--color-surface-container-low)')
css = css.replace('#263143', 'var(--color-surface-container-highest)')
css = css.replace('#08111F', 'var(--color-background)')

with open('app/static/css/stitch_custom.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Fixed RGBA hardcoding in CSS!")
