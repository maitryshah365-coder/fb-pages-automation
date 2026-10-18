import requests

urls = [
    'https://maitryshah365-coder.github.io/fb-pages-automation/',
    'https://maitryshah365-coder.github.io/fb-pages-automation/data/pages_data.json',
    'https://maitryshah365-coder.github.io/fb-pages-automation/data/latest_run_summary.json',
    'https://maitryshah365-coder.github.io/fb-pages-automation/data/upload_history.json',
    'https://raw.githubusercontent.com/maitryshah365-coder/fb-pages-automation/main/docs/data/pages_data.json'
]
for u in urls:
    try:
        r = requests.head(u, timeout=10)
        size = r.headers.get("content-length", "unknown")
        print(f"{r.status_code} | {size} bytes | {u}")
    except Exception as e:
        print(f"ERR | {e} | {u}")
