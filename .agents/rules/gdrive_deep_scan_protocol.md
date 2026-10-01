# MANDATORY GOOGLE DRIVE DEEP SCANNING & ACCURATE SYNC PROTOCOL

Whenever onboarding any new Facebook ID or scanning any Google Drive link/folder:

## 1. NEVER DO SHALLOW / SINGLE-PAGE SCANS
- Google Drive API limits single responses to `pageSize`. 
- **STRICT PROHIBITION:** NEVER execute a single query without a `nextPageToken` pagination loop.
- **STRICT PROHIBITION:** NEVER cap at 100. Folders often contain 200, 500, 1000+ reels.

## 2. MANDATORY DEEP RECURSIVE SCAN SPECIFICATION
Every scan script MUST implement:
1. **Full Pagination Loop:**
   ```python
   pageSize = 1000
   while True:
       res = service.files().list(
           q=query,
           pageSize=1000,
           fields="nextPageToken, files(id, name, mimeType, size, createdTime)",
           pageToken=page_token,
           supportsAllDrives=True,
           includeItemsFromAllDrives=True
       ).execute()
       items.extend(res.get('files', []))
       page_token = res.get('nextPageToken')
       if not page_token:
           break
   ```
2. **Recursive Nested Subfolder Discovery:**
   - Always check if subfolders contain child folders.
   - Recurse into all nested folders to catch all video stock.
3. **Dual Video Detection:**
   - Check `mimeType contains 'video/'`
   - Check file extensions: `.mp4`, `.mov`, `.mkv`, `.webm`, `.avi`, `.m4v`, `.3gp`.
4. **Detailed Metrics Output:**
   - Exact reel count per folder.
   - Total file size in MB/GB.
   - Sample filenames for verification.

## 3. MASTER FLEET SYNCHRONIZATION
Immediately after deep scanning:
1. Save raw deep scan results to `data/<account>_drive_folders.json`.
2. Update permanent pages config `data/usa_account<N>_<owner>_permanent_pages.json`.
3. Update `data/drive_folders_audit.json` & `docs/data/drive_folders_audit.json`.
4. Update `docs/data/pages_data.json` & `web/data/pages_data.json` with exact counts.
5. Update `data/master_fleet_monetization.json` (and `docs/`, `web/`).
6. Update hero stock counter badges in `web/index.html` & `docs/index.html`.
7. Update device health diagnostic files and push to GitHub so runners and dashboard reflect 100% exact real counts.
