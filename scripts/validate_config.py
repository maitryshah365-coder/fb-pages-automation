import sys
import os
import yaml

def validate_config(config_path: str = "config.yaml") -> bool:
    if not os.path.exists(config_path):
        print(f"ERROR: Configuration file not found: {config_path}")
        return False

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            print(f"ERROR: Invalid YAML syntax: {e}")
            return False

    pages = data.get("pages", [])
    if not pages:
        print("ERROR: No pages configured in 'pages' section.")
        return False

    seen_names = set()
    seen_ids = set()

    for idx, p in enumerate(pages):
        name = p.get("name")
        page_id = p.get("page_id")
        folder_id = p.get("drive_folder_id")

        if not name:
            print(f"ERROR: Page #{idx + 1} missing 'name'.")
            return False
        if name in seen_names:
            print(f"ERROR: Duplicate page name '{name}'.")
            return False
        seen_names.add(name)

        if not page_id:
            print(f"ERROR: Page '{name}' missing 'page_id'.")
            return False
        if page_id != "REPLACE_WITH_FB_PAGE_ID" and page_id in seen_ids:
            print(f"ERROR: Duplicate page_id '{page_id}'.")
            return False
        seen_ids.add(page_id)

        if not folder_id:
            print(f"ERROR: Page '{name}' missing 'drive_folder_id'.")
            return False

    print(f"SUCCESS: Configuration file '{config_path}' validated ({len(pages)} pages found).")
    return True

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    if not validate_config(path):
        sys.exit(1)
