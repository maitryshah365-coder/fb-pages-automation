"""
Profile Session & Storage State Manager
Handles isolated sandbox profiles on disk, session persistence, and metadata.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")


class ProfileSessionManager:
    """Manages persistent browser profiles and authentication states."""

    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.profile_dir = os.path.join(PROFILES_DIR, profile_id)
        os.makedirs(self.profile_dir, exist_ok=True)
        self.meta_file = os.path.join(self.profile_dir, "profile_meta.json")
        self.pages_file = os.path.join(self.profile_dir, "pages.json")

    def save_metadata(self, meta: Dict[str, Any]) -> None:
        """Saves profile hardware, telemetry and status metadata."""
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    def load_metadata(self) -> Dict[str, Any]:
        """Loads profile metadata if exists."""
        if os.path.exists(self.meta_file):
            with open(self.meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_pages(self, pages: List[Dict[str, Any]]) -> None:
        """Saves discovered Facebook pages for this profile."""
        payload = {
            "synced_at": datetime.now(timezone.utc).isoformat(),
            "profile_id": self.profile_id,
            "pages_count": len(pages),
            "pages": pages
        }
        with open(self.pages_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def load_pages(self) -> List[Dict[str, Any]]:
        """Loads synced pages for this profile."""
        if os.path.exists(self.pages_file):
            with open(self.pages_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("pages", [])
        return []

    def get_user_data_dir(self) -> str:
        """Returns the isolated Chromium user data directory."""
        user_data_path = os.path.join(self.profile_dir, "chrome_user_data")
        os.makedirs(user_data_path, exist_ok=True)
        return user_data_path
