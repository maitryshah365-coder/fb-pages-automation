import json

def run():
    with open('scripts/inline_bookmarklet.txt', 'r', encoding='utf-8') as f:
        bm_code = f.read().strip()

    raw_js = bm_code
    if raw_js.startswith('javascript:'):
        raw_js = raw_js[len('javascript:'):]

    escaped_bm = json.dumps(bm_code)
    escaped_raw = json.dumps(raw_js)

    replacement = f'''function copyBookmarkletCode() {{
  const code = {escaped_bm};
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(code).then(() => {{
      showToast("📋 100% Inline Bookmarklet Copied! Bookmark URL me paste karein.");
    }}).catch(() => {{
      prompt("Copy this Bookmarklet Code:", code);
    }});
  }} else {{
    prompt("Copy this Bookmarklet Code:", code);
  }}
}}

function copyConsoleScript() {{
  const code = {escaped_raw};
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(code).then(() => {{
      showToast("⚡ Scanner Code Copied! Facebook par F12 dabayein, Console me paste karein aur Enter dabayein!");
    }}).catch(() => {{
      prompt("Copy this Console Code:", code);
    }});
  }} else {{
    prompt("Copy this Console Code:", code);
  }}
}}'''

    target = '''function copyBookmarkletCode() {
  const code = "javascript:(function(){var s=document.createElement('script');s.src='https://maitryshah365-coder.github.io/fb-pages-automation/js/fb_real_scanner.js?v='+Date.now();document.body.appendChild(s);})();";
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(code).then(() => {
      showToast("📋 Bookmarklet Code Copied! Chrome Bookmarks me paste karein.");
    }).catch(() => {
      prompt("Copy this Bookmarklet Code:", code);
    });
  } else {
    prompt("Copy this Bookmarklet Code:", code);
  }
}'''

    for p in ['docs/js/gold_app.js', 'web/js/gold_app.js']:
        with open(p, 'r', encoding='utf-8') as f:
            c = f.read()
        if target in c:
            c = c.replace(target, replacement)
            c = c.replace('window.copyBookmarkletCode = copyBookmarkletCode;', 'window.copyBookmarkletCode = copyBookmarkletCode;\nwindow.copyConsoleScript = copyConsoleScript;')
            with open(p, 'w', encoding='utf-8') as f:
                f.write(c)
            print('Successfully updated', p)
        else:
            print('Target not found in', p)

if __name__ == '__main__':
    run()
