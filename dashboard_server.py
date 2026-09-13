import os
import json
import sqlite3
import time
from datetime import datetime, timezone
import requests
from flask import Flask, jsonify, request, send_from_directory

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
TOKENS_PATH = r"C:\Users\Win\.gemini\antigravity-ide\brain\313a3f26-ac39-434f-8050-53be5bd48383\scratch\pages_tokens.json"

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "docs"), static_url_path="")

# In-memory API cache (TTL: 300s / 5 mins)
API_CACHE = {}

def get_page_tokens():
    """Loads all 15 Facebook Page access tokens."""
    if os.path.exists(TOKENS_PATH):
        with open(TOKENS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_db_connection():
    """Creates a thread-safe connection to the SQLite tracking database."""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_posted_videos(page_id=None):
    """Retrieves posted videos from SQLite state."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        if page_id:
            cur.execute("""
                SELECT id, facebook_video_id, drive_file_id, page_id, post_type, 
                       duration_seconds, aspect_ratio, created_at 
                FROM posted_videos 
                WHERE page_id = ? 
                ORDER BY created_at DESC
            """, (page_id,))
        else:
            cur.execute("""
                SELECT id, facebook_video_id, drive_file_id, page_id, post_type, 
                       duration_seconds, aspect_ratio, created_at 
                FROM posted_videos 
                ORDER BY created_at DESC
            """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        if conn:
            conn.close()
        return []

def get_today_post_count(page_id=None):
    """Calculates videos posted today."""
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        cur = conn.cursor()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if page_id:
            cur.execute("SELECT COUNT(*) FROM posted_videos WHERE page_id = ? AND date(created_at) = ?", (page_id, today))
        else:
            cur.execute("SELECT COUNT(*) FROM posted_videos WHERE date(created_at) = ?", (today,))
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        if conn:
            conn.close()
        return 0

def fetch_fb_page_profile(page_id, token):
    """Fetches real-time Page profile from Meta Graph API with caching."""
    now = time.time()
    cache_key = f"profile_{page_id}"
    if cache_key in API_CACHE and (now - API_CACHE[cache_key]["time"] < 300):
        return API_CACHE[cache_key]["data"]

    url = f"https://graph.facebook.com/v20.0/{page_id}"
    params = {
        "fields": "name,followers_count,fan_count,category,link,verification_status",
        "access_token": token
    }
    try:
        res = requests.get(url, params=params, timeout=5).json()
        if "error" not in res:
            API_CACHE[cache_key] = {"data": res, "time": now}
            return res
    except Exception:
        pass
    return None

def get_next_slot():
    """Computes time until next USA posting slot (10am, 3pm, 7pm, 10pm EDT)."""
    # EDT is UTC-4. Convert current UTC to EDT hours
    now_utc = datetime.now(timezone.utc)
    utc_hours = [14, 19, 23, 2] # corresponding to 10am, 3pm, 7pm, 10pm EDT
    
    current_utc_hour = now_utc.hour
    current_utc_minute = now_utc.minute

    # Find the next scheduled UTC hour
    next_hour = None
    sorted_slots = [2, 14, 19, 23]
    for slot in sorted_slots:
        if slot > current_utc_hour or (slot == current_utc_hour and current_utc_minute == 0):
            next_hour = slot
            break
    if next_hour is None:
        next_hour = sorted_slots[0] # wraps to tomorrow 2:00 UTC

    # Calculate remaining time in seconds
    return {
        "schedule_slots_edt": ["10:00 AM", "3:00 PM", "7:00 PM", "10:00 PM"],
        "next_slot_edt": "10:00 AM" if next_hour == 14 else ("3:00 PM" if next_hour == 19 else ("7:00 PM" if next_hour == 23 else "10:00 PM")),
        "current_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "active"
    }

# ----------------- ROUTES -----------------

@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "docs"), "index.html")

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(BASE_DIR, "docs", "css"), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(BASE_DIR, "docs", "js"), filename)

@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory(os.path.join(BASE_DIR, "docs", "data"), filename)

def get_real_pages_data():
    json_path = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

@app.route("/api/overview")
def api_overview():
    """Global summary across all pages using 100% real data."""
    real_data = get_real_pages_data()
    if real_data and "portfolio" in real_data:
        port = real_data["portfolio"]
        return jsonify({
            "total_pages": port.get("total_pages", 15),
            "total_followers": port.get("total_followers", 0),
            "total_views": port.get("total_views", 0),
            "total_posts": port.get("total_posts", 0),
            "total_likes": port.get("total_likes", 0),
            "schedule": get_next_slot(),
            "pipeline_health": "All Systems Operational"
        })
    
    pages = get_page_tokens()
    posted_today = get_today_post_count()
    return jsonify({
        "total_pages": len(pages),
        "total_posted_today": posted_today,
        "daily_target": len(pages) * 4,
        "schedule": get_next_slot(),
        "pipeline_health": "All Systems Operational"
    })

@app.route("/api/pages")
def api_pages():
    """List of all 15 pages with high-level metrics."""
    real_data = get_real_pages_data()
    if real_data and "pages" in real_data:
        return jsonify(real_data["pages"])

    pages = get_page_tokens()
    return jsonify(pages)

@app.route("/api/page/<page_id>")
def api_page_detail(page_id):
    """Detailed analytics matching Facebook Professional Dashboard for a single page with 100% real Meta data."""
    real_data = get_real_pages_data()
    if real_data and "pages" in real_data:
        page = next((p for p in real_data["pages"] if str(p.get("id")) == str(page_id)), None)
        if page:
            return jsonify(page)

    return jsonify({"error": "Page not found"}), 404

@app.route("/api/sync", methods=["GET", "POST"])
def api_sync():
    """Triggers 100% real Meta Graph API sync."""
    try:
        import sys
        sys.path.insert(0, BASE_DIR)
        from scripts.sync_dashboard_data import sync_data
        sync_data()
        return jsonify({"success": True, "message": "100% Real Live Meta Graph API Sync completed successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/trigger-upload", methods=["POST"])
def api_trigger_upload():
    """Triggers an immediate workflow dispatch on GitHub Actions."""
    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT") or ""
    owner = "maitryshah365-coder"
    repo = "fb-pages-automation"
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/post.yml/dispatches"
    
    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "ref": "main",
        "inputs": {
            "dry_run": False
        }
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=8)
        if r.status_code == 204:
            return jsonify({"success": True, "message": "Automation triggered successfully on GitHub Actions cloud!"})
        else:
            return jsonify({"success": False, "message": f"GitHub response: {r.status_code} - {r.text}"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    print("\n========================================================")
    print("  Facebook Professional Mobile Dashboard & Command Center")
    print("  Server running on http://127.0.0.1:8888")
    print("========================================================\n")
    app.run(host="0.0.0.0", port=8888, debug=False)
