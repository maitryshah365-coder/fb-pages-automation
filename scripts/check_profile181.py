import os
import sqlite3
import json
import shutil
import tempfile

prof_dir = r"C:\Users\Win\AppData\Local\CentBrowser\User Data\Profile 181"

# Check History for Facebook or Developers URLs
h_path = os.path.join(prof_dir, "History")
if os.path.exists(h_path):
    try:
        temp_dir = tempfile.gettempdir()
        temp_h = os.path.join(temp_dir, "temp_h_181.db")
        shutil.copy2(h_path, temp_h)
        conn = sqlite3.connect(temp_h)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT title, url FROM urls WHERE url LIKE '%facebook.com%' AND title != '' ORDER BY last_visit_time DESC LIMIT 100")
        rows = cur.fetchall()
        print("Facebook Titles & URLs:")
        for r in rows:
            print(" -", r[0], "-->", r[1])
        conn.close()
        os.remove(temp_h)
    except Exception as e:
        print("History query error:", e)

# Check Cookies
cookie_path = os.path.join(prof_dir, "Network", "Cookies")
if not os.path.exists(cookie_path):
    cookie_path = os.path.join(prof_dir, "Cookies")

if os.path.exists(cookie_path):
    try:
        temp_c = os.path.join(tempfile.gettempdir(), "temp_c_181.db")
        shutil.copy2(cookie_path, temp_c)
        conn = sqlite3.connect(temp_c)
        cur = conn.cursor()
        cur.execute("SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE '%facebook.com%' AND name = 'c_user'")
        for r in cur.fetchall():
            print("Facebook c_user cookie:", r[0], r[1], r[2])
        conn.close()
        os.remove(temp_c)
    except Exception as e:
        print("Cookie query error:", e)
