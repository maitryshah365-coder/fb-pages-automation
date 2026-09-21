import urllib.parse
import json
import re
import html.parser

def main():
    # 1. Load the raw inline JS
    with open('scripts/inline_bookmarklet.txt', 'r', encoding='utf-8') as f:
        bm = f.read().strip()

    raw_js = bm
    if raw_js.startswith('javascript:'):
        raw_js = raw_js[len('javascript:'):]

    # 2. URL-encode keeping safe characters: () ; / ? : @ & = + $ ,
    # This guarantees zero double-quotes, zero single-quotes, zero < and >
    encoded_js = urllib.parse.quote(raw_js, safe='();/?:@&=+$,')
    href_value = "javascript:" + encoded_js

    print(f"Generated safe encoded bookmarklet: {len(href_value)} chars")

    # 3. Update HTML files
    for html_path in ['docs/index.html', 'web/index.html']:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the anchor
        # Match <a ... id="btnDragBookmarklet" ...>...</a>
        pattern = r'<a\s+href="[^"]*"\s+class="mz-btn-bookmarklet"\s+id="btnDragBookmarklet"[^>]*>[\s\S]*?</a>'
        
        new_anchor = f'''<a href="{href_value}" 
               class="mz-btn-bookmarklet" 
               id="btnDragBookmarklet"
               title="Drag this button directly to your Chrome Bookmarks bar (Ctrl+Shift+B)"
               style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; font-weight: 800; font-size: 12px; padding: 8px 14px; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 15px rgba(37,99,235,0.4); cursor: grab; border: 1px solid rgba(147,197,253,0.3);">
              <span>⭐ Drag to Bookmarks: <strong>⚡ Scan FB Tools</strong></span>
            </a>'''

        new_content = re.sub(pattern, lambda m: new_anchor, content)
        
        # Bump version to v=8.9.7
        new_content = re.sub(r'js/gold_app\.js\?v=[\d\.]+', 'js/gold_app.js?v=8.9.7', new_content)

        # Validate with HTML parser
        class Validator(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.found_anchor = False
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    d = dict(attrs)
                    if d.get('id') == 'btnDragBookmarklet':
                        self.found_anchor = True

        v = Validator()
        v.feed(new_content)
        if not v.found_anchor:
            raise Exception(f"Validation failed for {html_path}: anchor not found in parsed HTML!")

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully updated and validated {html_path}")

    # 4. Update gold_app.js
    escaped_code = json.dumps(href_value)
    copy_fn_replacement = f'''function copyBookmarkletCode() {{
  const code = {escaped_code};
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(code).then(() => {{
      showToast("📋 Bookmarklet Code Copied! Chrome Bookmarks me paste karein.");
    }}).catch(() => {{
      prompt("Copy this Bookmarklet Code:", code);
    }});
  }} else {{
    prompt("Copy this Bookmarklet Code:", code);
  }}
}}'''

    for js_path in ['docs/js/gold_app.js', 'web/js/gold_app.js']:
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()

        copy_fn_pattern = r'function copyBookmarkletCode\(\)\s*\{[\s\S]*?showToast\([^\)]+\);\s*\}\)\.catch\([^\)]+\);\s*\}\s*else\s*\{[\s\S]*?\}\s*\}'
        new_js = re.sub(copy_fn_pattern, lambda m: copy_fn_replacement, js)

        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(new_js)
        print(f"Successfully updated copyBookmarkletCode in {js_path}")

if __name__ == '__main__':
    main()
