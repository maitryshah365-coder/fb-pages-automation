import urllib.parse
import html.parser
import json

def test():
    with open('scripts/inline_bookmarklet.txt', 'r', encoding='utf-8') as f:
        bm = f.read().strip()

    raw_js = bm
    if raw_js.startswith('javascript:'):
        raw_js = raw_js[len('javascript:'):]

    # Clean URL-encode keeping JS structure safe
    # We must encode: " ' < > ` \ and spaces
    encoded_js = urllib.parse.quote(raw_js, safe='();/?:@&=+$,')
    href_value = "javascript:" + encoded_js

    print("Encoded length:", len(href_value))
    print("Contains raw quote:", '"' in href_value)
    print("Contains raw single quote:", "'" in href_value)
    print("Contains raw <:", '<' in href_value)
    print("Contains raw >:", '>' in href_value)

    # Test HTML parsing
    test_html = f'<div class="card"><a href="{href_value}" id="btnDragBookmarklet"><span>⭐ Drag to Bookmarks: <strong>⚡ Scan FB Tools</strong></span></a><button>Copy</button></div>'
    
    class TestParser(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.errors = []
            self.links = []
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                self.links.append(dict(attrs))

    p = TestParser()
    p.feed(test_html)
    print("Parsed successfully!")
    print("Found 'a' tag count:", len(p.links))
    print("Href starts with:", p.links[0]['href'][:40])

if __name__ == '__main__':
    test()
