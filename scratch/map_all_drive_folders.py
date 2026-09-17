import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import yaml
from src.drive_client import DriveClient

def main():
    target_id = "1IL8OAUOfOZpisnHiGV0cKeO6x7O_UYRS"
    client = DriveClient("service_account.json")
    
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    with open("data/pages_tokens.json", "r", encoding="utf-8") as f:
        tokens = json.load(f)
        
    pages_token_map = {p["name"].lower().replace(" ", "").replace("_", ""): p for p in tokens}
    cfg_pages = cfg.get("pages", [])

    print("Fetching folders inside parent 'Usa Ids GITHUB'...")
    query = f"'{target_id}' in parents and trashed = false"
    results = client.service.files().list(
        q=query,
        fields="files(id, name, mimeType)",
        pageSize=100,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    
    drive_folders = results.get("files", [])
    print(f"Found {len(drive_folders)} folders in Google Drive:\n")
    
    mapping = {}
    for df in drive_folders:
        dname = df.get("name")
        did = df.get("id")
        clean_name = dname.lower().replace(" ", "").replace("_", "")
        mapping[clean_name] = (dname, did)
        print(f"  * Folder: {dname:<25} | ID: {did}")

    print("\nMatching with config.yaml pages:")
    for p in cfg_pages:
        p_name = p.get("name")
        # find matching token for real name
        pid = str(p.get("page_id"))
        real_name = p_name
        for t in tokens:
            if str(t.get("id")) == pid:
                real_name = t.get("name")
                break
        
        clean_real = real_name.lower().replace(" ", "").replace("_", "")
        old_fid = p.get("drive_folder_id")
        matched = mapping.get(clean_real)
        
        print(f"\nPage: {real_name} ({p_name}) | ID: {pid}")
        print(f"  Current Config Folder ID: {old_fid}")
        if matched:
            print(f"  -> MATCHED Drive Folder: {matched[0]} | New ID: {matched[1]}")
        else:
            print(f"  -> NO EXACT MATCH! (Check clean_name: {clean_real})")

if __name__ == "__main__":
    main()
