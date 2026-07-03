import re

with open('app/static/css/stitch_custom.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace hardcoded hex colors that I can identify
replacements = [
    (r'#08111F|#081424', 'var(--color-background)'),
    (r'#040e1f', 'var(--color-surface-container-lowest)'),
    (r'#2a3547', 'var(--color-surface-variant)'),
    (r'#45474c', 'var(--color-outline-variant)'),
    (r'#d8e3fb', 'var(--color-on-surface)'),
    (r'#111C2D', 'var(--color-surface-container-low)'),
    (r'#263143', 'var(--color-surface-container-highest)')
]

for old, new in replacements:
    css = re.sub(old, new, css, flags=re.IGNORECASE)

with open('app/static/css/stitch_custom.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Replaced hex colors with variables!")
