import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import yaml
from src.drive_client import DriveClient

def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    with open("data/pages_tokens.json", "r", encoding="utf-8") as f:
        tokens = json.load(f)

    token_map = {str(t["id"]): t["name"] for t in tokens}
    client = DriveClient("service_account.json")
    
    audit_data = {}
    
    print(f"Auditing all {len(cfg.get('pages', []))} pages in config.yaml...")
    for p in cfg.get("pages", []):
        pid = str(p.get("page_id"))
        pname = token_map.get(pid, p.get("name"))
        fid = p.get("drive_folder_id")
        
        print(f"Auditing '{pname}' ({fid})...")
        if not fid or "REPLACE" in fid:
            continue
            
        try:
            files = client.list_folder_videos(fid)
            total_size = sum(int(f.get("size", 0) or 0) for f in files) / (1024 * 1024)
            sample_names = [f.get("name") for f in files[:3]]
            
            audit_data[pname] = {
                "folder_id": fid,
                "video_count": len(files),
                "total_size_mb": round(total_size, 2),
                "subfolders_count": 0,
                "sample_videos": sample_names
            }
            print(f"  -> {len(files)} videos found ({round(total_size, 2)} MB)")
        except Exception as e:
            print(f"  -> Error auditing {pname}: {e}")

    out_path = "data/drive_folders_audit.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved full audit to {out_path} with {len(audit_data)} pages!")

if __name__ == "__main__":
    main()
