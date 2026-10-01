import os
import json

BASE_DIR = r"E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")

accounts = sorted(os.listdir(PROFILES_DIR))
print(f"Checking cookies for {len(accounts)} accounts in data/profiles/:\n")

for acc in accounts:
    acc_dir = os.path.join(PROFILES_DIR, acc)
    ck_file = os.path.join(acc_dir, "cookies.json")
    pages_file = os.path.join(acc_dir, "pages.json")
    meta_file = os.path.join(acc_dir, "profile_meta.json")

    has_ck = os.path.exists(ck_file)
    ck_size = os.path.getsize(ck_file) if has_ck else 0
    has_pages = os.path.exists(pages_file)
    pages_count = 0
    if has_pages:
        try:
            p_data = json.load(open(pages_file, encoding='utf-8'))
            pages_count = len(p_data) if isinstance(p_data, list) else len(p_data.get('pages', []))
        except:
            pass

    c_user = None
    xs = None
    if has_ck and ck_size > 50:
        try:
            cks = json.load(open(ck_file, encoding='utf-8'))
            for c in cks:
                if c.get('name') == 'c_user':
                    c_user = c.get('value')
                elif c.get('name') == 'xs':
                    xs = c.get('value')
        except:
            pass

    print(f"[{acc}]")
    print(f"   • Cookies: {'YES (' + str(ck_size) + ' bytes)' if has_ck else 'MISSING'}")
    print(f"   • c_user (FB UID): {c_user}")
    print(f"   • xs token: {'Valid length' if xs and len(xs) > 10 else 'Missing/Invalid'}")
    print(f"   • Pages assigned: {pages_count}")
    print()
