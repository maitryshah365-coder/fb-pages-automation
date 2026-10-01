import http.server
import socketserver
import threading
import time
from playwright.sync_api import sync_playwright

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

PORT = 9991
handler = lambda *args: QuietHandler(*args, directory="docs")
httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
print(f"Server started on 127.0.0.1:{PORT}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    url = f"http://127.0.0.1:{PORT}/index.html"
    print("Navigating to:", url)
    page.goto(url, wait_until="networkidle", timeout=15000)
    time.sleep(3)
    page.screenshot(path="temp_verified_dashboard.png")

    btn = page.locator('text="Monetization Hub"').first
    if btn.count() > 0:
        btn.click()
        time.sleep(2)
        page.screenshot(path="temp_verified_monetization_hub.png")

    browser.close()

httpd.shutdown()
print("SUCCESS! Both screenshots captured!")
