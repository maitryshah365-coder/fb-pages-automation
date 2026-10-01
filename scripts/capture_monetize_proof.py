import http.server
import socketserver
import threading
import time
from playwright.sync_api import sync_playwright

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

PORT = 9995
httpd = socketserver.TCPServer(("127.0.0.1", PORT), lambda *args: QuietHandler(*args, directory="docs"))
threading.Thread(target=httpd.serve_forever, daemon=True).start()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle")
    time.sleep(2)
    page.evaluate("switchMainView('meta_tools_hub')")
    time.sleep(2)
    page.screenshot(path="temp_verified_monetization_hub.png")
    browser.close()

httpd.shutdown()
print("Monetization Hub screenshot captured successfully!")
