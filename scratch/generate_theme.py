import re
import json

html = open('app/templates/base.html', encoding='utf-8').read()
match = re.search(r'tailwind\.config\s*=\s*(\{.*?\});', html, re.DOTALL)
if match:
    config_str = match.group(1)
    # Fix JSON syntax if needed
    config_str = re.sub(r'(\w+):', r'"\1":', config_str)
    try:
        config = eval(config_str.replace('false', 'False').replace('true', 'True'))
        colors = config['theme']['extend']['colors']
        
        dark_vars = []
        light_vars = []
        tailwind_colors = []
        
        for key, hex_val in colors.items():
            var_name = f"--color-{key}"
            tailwind_colors.append(f'"{key}": "var({var_name})"')
            dark_vars.append(f"  {var_name}: {hex_val};")
            
            # Simple heuristic for light mode colors based on the name or dark hex
            # We'll just generate placeholders and adjust them.
            light_vars.append(f"  {var_name}: {hex_val}; /* TODO: light */")
            
        print("/* CSS VARIABLES */")
        print(":root {")
        print("\n".join(light_vars))
        print("}")
        print(".dark {")
        print("\n".join(dark_vars))
        print("}")
        
        print("\n/* TAILWIND COLORS */")
        print(",\n".join(tailwind_colors))
        
    except Exception as e:
        print("Error parsing:", e)
