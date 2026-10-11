import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def audit_drive():
    audit_file = 'data/drive_verified_stock_audit.json'
    folders_file = 'docs/data/drive_folders_audit.json'
    pages_file = 'docs/data/pages_data.json'

    print("==================================================")
    print("GOOGLE DRIVE VIDEO STOCK & INVENTORY AUDIT")
    print("==================================================")

    # 1. Check drive_verified_stock_audit.json if present
    if os.path.exists(audit_file):
        with open(audit_file, 'r', encoding='utf-8') as f:
            d = json.load(f)

        print(f"\n[SOURCE: {audit_file}]")
        print(f"Total Pages Audited: {d.get('total_pages')}")
        print(f"Total Valid Videos (Playable >0 byte): {d.get('total_valid_videos')}")
        print(f"Total 0-byte Wiped / Ghost Files: {d.get('total_zero_byte_wiped')}")

        pages = d.get('pages', {})
        empty_pages = [v for v in pages.values() if v.get('valid_videos_stock', 0) == 0 or v.get('status') == 'EMPTY_STOCK']
        critical_pages = [v for v in pages.values() if 0 < v.get('valid_videos_stock', 0) <= 5]
        low_pages = [v for v in pages.values() if 5 < v.get('valid_videos_stock', 0) <= 15]

        print(f"\nEMPTY STOCK FOLDERS (0 Valid Videos Left): {len(empty_pages)}")
        for p in empty_pages:
            print(f"  🔴 {p.get('name')} | {p.get('account')} | Valid: {p.get('valid_videos_stock', 0)} | Wiped: {p.get('zero_byte_wiped', 0)} | Err: {p.get('error', 'None')}")

        print(f"\nCRITICAL STOCK FOLDERS (1 to 5 Videos Left): {len(critical_pages)}")
        for p in critical_pages:
            print(f"  ⚠️ {p.get('name')} | {p.get('account')} | Valid: {p.get('valid_videos_stock')} | Wiped: {p.get('zero_byte_wiped', 0)}")

        print(f"\nLOW STOCK FOLDERS (6 to 15 Videos Left): {len(low_pages)}")
        for p in low_pages:
            print(f"  🟡 {p.get('name')} | {p.get('account')} | Valid: {p.get('valid_videos_stock')}")

    # 2. Check drive_folders_audit.json
    if os.path.exists(folders_file):
        with open(folders_file, 'r', encoding='utf-8') as f:
            df = json.load(f)

        print(f"\n[SOURCE: {folders_file}]")
        print(f"Total Folders: {len(df)}")
        df_zero = [(k, v) for k, v in df.items() if v.get('video_count', 0) == 0]
        df_crit = [(k, v) for k, v in df.items() if 0 < v.get('video_count', 0) <= 5]
        df_low = [(k, v) for k, v in df.items() if 5 < v.get('video_count', 0) <= 15]

        print(f"Folders with 0 videos: {len(df_zero)}")
        print(f"Folders with 1-5 videos: {len(df_crit)}")
        print(f"Folders with 6-15 videos: {len(df_low)}")
        for k, v in df_low:
            print(f"  🟡 {k} ({v.get('account')}): {v.get('video_count')} videos left")

    # 3. Check pages_data.json
    if os.path.exists(pages_file):
        with open(pages_file, 'r', encoding='utf-8') as f:
            pdf = json.load(f)
        pages_list = pdf.get('pages', [])
        p_zero = [p for p in pages_list if (p.get('drive_videos_count') or 0) == 0]
        p_crit = [p for p in pages_list if 0 < (p.get('drive_videos_count') or 0) <= 5]
        p_low = [p for p in pages_list if 5 < (p.get('drive_videos_count') or 0) <= 15]

        print(f"\n[SOURCE: {pages_file}]")
        print(f"Pages with 0 drive stock: {len(p_zero)}")
        for p in p_zero:
            print(f"  🔴 {p.get('name')} ({p.get('account')}): drive_videos_count = 0, folder_id = {p.get('drive_folder_id')}")
        print(f"Pages with 1-5 drive stock: {len(p_crit)}")
        for p in p_crit:
            print(f"  ⚠️ {p.get('name')} ({p.get('account')}): drive_videos_count = {p.get('drive_videos_count')}")
        print(f"Pages with 6-15 drive stock: {len(p_low)}")
        for p in p_low:
            print(f"  🟡 {p.get('name')} ({p.get('account')}): drive_videos_count = {p.get('drive_videos_count')}")

if __name__ == '__main__':
    audit_drive()
