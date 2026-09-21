import re
import json

def main():
    with open('scripts/inline_bookmarklet.txt', 'r', encoding='utf-8') as f:
        bm_code = f.read().strip()

    print(f"Loaded inline bookmarklet: {len(bm_code)} characters")

    # 1. Update HTML files
    for html_path in ['docs/index.html', 'web/index.html']:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = r'<a href="javascript:[^"]+"\s+class="mz-btn-bookmarklet"[^>]*>[\s\S]*?</a>'
        new_link = f'''<a href="{bm_code}" 
               class="mz-btn-bookmarklet" 
               id="btnDragBookmarklet"
               title="Drag this button directly to your Chrome Bookmarks bar (Ctrl+Shift+B)"
               style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; font-weight: 800; font-size: 13px; padding: 8px 16px; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 15px rgba(37,99,235,0.4); cursor: grab; border: 1px solid rgba(147,197,253,0.3);">
              <span>⚡ Scan FB Tools</span>
            </a>'''

        new_content = re.sub(pattern, lambda m: new_link, content)
        if new_content != content:
            print(f"Successfully replaced link in {html_path}")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            print(f"FAILED to match pattern in {html_path}")

    # 2. Update gold_app.js files (copyBookmarkletCode function)
    raw_js = bm_code
    if raw_js.startswith("javascript:"):
        raw_js = raw_js[len("javascript:"):]

    js_escaped = json.dumps(raw_js)

    for js_path in ['docs/js/gold_app.js', 'web/js/gold_app.js']:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

        copy_fn_pattern = r'function copyBookmarkletCode\(\)\s*\{[\s\S]*?showToast\([^\)]+\);\s*\}\)\.catch\([^\)]+\);\s*\}\s*else\s*\{[\s\S]*?\}\s*\}'
        new_copy_fn = f'''function copyBookmarkletCode() {{
  const code = {js_escaped};
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(code).then(() => {{
      showToast("📋 Real Scanner Code Copied! Facebook par F12 Console me paste karein ya Bookmark URL me dalein.");
    }}).catch(() => {{
      prompt("Copy this Scanner Code:", code);
    }});
  }} else {{
    prompt("Copy this Scanner Code:", code);
  }}
}}'''

        new_js_content = re.sub(copy_fn_pattern, lambda m: new_copy_fn, js_content)
        if new_js_content != js_content:
            print(f"Successfully updated copyBookmarkletCode in {js_path}")
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(new_js_content)
        else:
            print(f"FAILED to match copyBookmarkletCode pattern in {js_path}")

if __name__ == '__main__':
    main()
