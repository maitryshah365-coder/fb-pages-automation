import re
import urllib.parse
import subprocess

with open('docs/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'id="btnDragBookmarklet"[^>]*href="([^"]+)"', c)
if not m:
    m = re.search(r'href="([^"]+)"[^>]*id="btnDragBookmarklet"', c)

if m:
    href = m.group(1)
    print("Href starts with:", href[:40])
    raw = urllib.parse.unquote(href[len("javascript:"):])
    with open('scripts/extracted_bm.js', 'w', encoding='utf-8') as out:
        out.write(raw)
    
    r = subprocess.run(['node', '-c', 'scripts/extracted_bm.js'], capture_output=True, text=True)
    print("Node check exit code:", r.returncode)
    if r.stdout:
        print("STDOUT:", r.stdout)
    if r.stderr:
        print("STDERR:", r.stderr)
else:
    print("Bookmarklet not found in HTML!")
