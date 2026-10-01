import sys
import os
import json
import threading
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DOCS_DIR = os.path.join(BASE_DIR, "docs")

# Global audit job state
audit_lock = threading.Lock()
audit_job = {
    "status": "idle", # "idle", "running", "completed", "error"
    "current_account": None,
    "current_page": None,
    "progress_current": 0,
    "progress_total": 0,
    "message": "Ready",
    "last_completed_at": None,
    "error_message": None
}

def run_audit_worker(account_id=None, page_id=None):
    global audit_job
    with audit_lock:
        audit_job["status"] = "running"
        audit_job["message"] = f"Starting live audit for {account_id or 'fleet'}..."
        audit_job["progress_current"] = 0
        audit_job["progress_total"] = 0
        audit_job["error_message"] = None

    try:
        from scripts.real_facebook_monetization_engine import audit_account_fleet, load_master_data
        master = load_master_data()
        
        target_accounts = [account_id] if account_id else [a["account_id"] for a in master.get("accounts", [])]
        
        if page_id:
            audit_job["progress_total"] = 1
        else:
            total_p = sum(len(a.get("pages", [])) for a in master.get("accounts", []) if not account_id or a["account_id"] == account_id)
            audit_job["progress_total"] = total_p

        def on_progress(idx, total, pname, pid):
            with audit_lock:
                audit_job["current_page"] = pname
                audit_job["progress_current"] = idx
                audit_job["message"] = f"Reading Facebook screen for {pname} ({idx}/{total})..."

        for acc in target_accounts:
            with audit_lock:
                audit_job["current_account"] = acc
                audit_job["message"] = f"Auditing account {acc} on Facebook..."
            audit_account_fleet(acc, target_page_id=page_id, progress_callback=on_progress)

        with audit_lock:
            audit_job["status"] = "completed"
            audit_job["message"] = f"Live Facebook audit successfully finished!"
            audit_job["last_completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    except Exception as e:
        with audit_lock:
            audit_job["status"] = "error"
            audit_job["error_message"] = str(e)
            audit_job["message"] = f"Audit encountered an error: {e}"

class RealAuditHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/audit-status":
            with audit_lock:
                resp = json.dumps(audit_job).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return
        
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/audit-live":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                body = json.loads(post_data)
            except Exception:
                body = {}

            target_acc = body.get("account_id")
            target_pid = body.get("page_id")

            with audit_lock:
                if audit_job["status"] == "running":
                    err_resp = json.dumps({"error": "An audit is already running!", "job": audit_job}).encode("utf-8")
                    self.send_response(409)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(err_resp)))
                    self.end_headers()
                    self.wfile.write(err_resp)
                    return

            # Start worker in background
            t = threading.Thread(target=run_audit_worker, args=(target_acc, target_pid), daemon=True)
            t.start()

            resp = json.dumps({"status": "started", "message": f"Real audit launched for {target_acc or 'fleet'}!"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        self.send_response(404)
        self.end_headers()

def main():
    port = 8089
    server = HTTPServer(("0.0.0.0", port), RealAuditHTTPHandler)
    print(f"==================================================")
    print(f"🚀 RAJ FB PRO • REAL AUDIT SERVER RUNNING ON PORT {port}")
    print(f"Serving docs directory: {DOCS_DIR}")
    print(f"API endpoints: POST /api/audit-live | GET /api/audit-status")
    print(f"==================================================")
    server.serve_forever()

if __name__ == "__main__":
    main()
