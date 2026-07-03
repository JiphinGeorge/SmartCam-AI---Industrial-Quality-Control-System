import os
import ast
import json
import re

ROOT = "app"
ROUTES_DIR = os.path.join(ROOT, "routes")
TEMPLATES_DIR = os.path.join(ROOT, "templates")
STATIC_DIR = os.path.join(ROOT, "static")

audit = {
    "api_endpoints": [],
    "duplicate_routes": [],
    "unused_templates": [],
    "unused_css": [],
    "unused_js": [],
    "unused_images": []
}

def analyze_routes():
    routes_found = set()
    used_templates = set()
    for file in os.listdir(ROUTES_DIR):
        if not file.endswith('.py'): continue
        filepath = os.path.join(ROUTES_DIR, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract routes: @bp.route('/path')
            routes = re.findall(r"@\w+\.route\(['\"](.*?)['\"]", content)
            for r in routes:
                if r in routes_found:
                    audit["duplicate_routes"].append(r)
                routes_found.add(r)
                if r.startswith('/api'):
                    audit["api_endpoints"].append(r)
            
            # Extract templates
            templates = re.findall(r"render_template\(['\"](.*?)['\"]", content)
            for t in templates:
                used_templates.add(t)
                
    return used_templates

def analyze_templates(used_templates):
    all_templates = set()
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for f in files:
            if f.endswith('.html'):
                # Get path relative to templates dir
                rel_path = os.path.relpath(os.path.join(root, f), TEMPLATES_DIR).replace('\\', '/')
                all_templates.add(rel_path)
                
    # Also base templates might be extended, not directly rendered
    for t in list(all_templates):
        with open(os.path.join(TEMPLATES_DIR, t), 'r', encoding='utf-8') as f:
            content = f.read()
            extended = re.findall(r"{% extends ['\"](.*?)['\"]", content)
            for e in extended:
                used_templates.add(e)
                
    audit["unused_templates"] = list(all_templates - used_templates)

def analyze_static():
    # Just a simple check for CSS/JS presence in templates
    all_css = []
    all_js = []
    all_img = []
    
    for root, _, files in os.walk(STATIC_DIR):
        for f in files:
            path = os.path.relpath(os.path.join(root, f), STATIC_DIR).replace('\\', '/')
            if f.endswith('.css'): all_css.append(path)
            elif f.endswith('.js'): all_js.append(path)
            elif f.endswith(('.png', '.jpg', '.svg', '.jpeg')): all_img.append(path)
            
    # Read all templates
    template_contents = ""
    for root, _, files in os.walk(TEMPLATES_DIR):
        for f in files:
            if f.endswith('.html'):
                with open(os.path.join(root, f), 'r', encoding='utf-8') as fh:
                    template_contents += fh.read()
                    
    # Read all JS
    js_contents = ""
    for js in all_js:
        with open(os.path.join(STATIC_DIR, js), 'r', encoding='utf-8') as fh:
            js_contents += fh.read()
            
    combined = template_contents + js_contents
    
    for css in all_css:
        if css.split('/')[-1] not in template_contents:
            audit["unused_css"].append(css)
            
    for js in all_js:
        if js.split('/')[-1] not in template_contents:
            audit["unused_js"].append(js)
            
    for img in all_img:
        img_name = img.split('/')[-1]
        if img_name not in combined and img_name != "avatar.jpg":
            audit["unused_images"].append(img)

def main():
    used_templates = analyze_routes()
    analyze_templates(used_templates)
    analyze_static()
    
    with open('QA_AUDIT.json', 'w') as f:
        json.dump(audit, f, indent=4)
        
    print("[*] Codebase Audit complete. Saved to QA_AUDIT.json")

if __name__ == "__main__":
    main()
