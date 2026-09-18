import os
import json
import yaml
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PageConfig:
    page_id: str
    name: str
    drive_folder_id: str
    enabled: bool = True
    daily_limit: int = 2
    title_mode: str = "filename"  # "filename" or "fixed"
    fixed_title: str = ""
    description_footer: str = ""
    default_hashtags: List[str] = field(default_factory=list)
    page_access_token: str = ""
    display_name: str = ""

    @property
    def token_env_var(self) -> str:
        """Returns standard environment variable name for this Page's Access Token."""
        safe_name = self.name.upper().replace("-", "_").replace(" ", "_")
        return f"FB_TOKEN_{safe_name}"

    def get_access_token(self) -> Optional[str]:
        """Resolves Page Access Token from configuration, environment or token file."""
        # 0. Direct token from page configuration
        if self.page_access_token:
            return self.page_access_token.strip()

        # 1. Check Page-specific environment variable e.g. FB_TOKEN_PAGE_1
        token = os.environ.get(self.token_env_var)
        if token:
            return token.strip()

        # 2. Check general FB_PAGE_ACCESS_TOKEN fallback
        token = os.environ.get("FB_PAGE_ACCESS_TOKEN")
        if token:
            return token.strip()

        # 3. Check local file if running in local development mode
        token_file = f"{self.name}.token"
        if os.path.exists(token_file):
            with open(token_file, "r", encoding="utf-8") as f:
                return f.read().strip()

        # 4. Check pages_tokens.json and verified pages files locally
        token_candidates = [
            "data/pages_tokens.json",
            "data/account2_verified_pages.json",
            "data/uk_account1_binjal_permanent_pages.json",
            "data/uk_account1_binjal_pages.json",
            "data/uk_account2_chanda_permanent_pages.json",
            "data/uk_account2_chanda_pages.json",
            "data/uk_account3_mahi_permanent_pages.json",
            "data/uk_account3_mahi_pages.json",
            "scratch/pages_tokens.json",
            r"C:\Users\Win\.gemini\antigravity-ide\brain\313a3f26-ac39-434f-8050-53be5bd48383\scratch\pages_tokens.json"
        ]
        for tf in token_candidates:
            if os.path.exists(tf):
                try:
                    with open(tf, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                        pages_list = raw.get("pages", []) if isinstance(raw, dict) else raw
                        for p in pages_list:
                            pid = str(p.get("id") or p.get("page_id") or "")
                            tok = p.get("access_token") or p.get("page_access_token") or ""
                            normalized_name = (
                                str(self.name)
                                .replace("uk3_page_", "")
                                .replace("uk2_page_", "")
                                .replace("uk1_page_", "")
                                .replace("page_", "")
                            )
                            if pid == str(self.page_id) or str(p.get("index")) == normalized_name:
                                if tok:
                                    return tok.strip()
                except Exception:
                    pass

        return None


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay_seconds: int = 5
    max_delay_seconds: int = 60


@dataclass
class NotificationConfig:
    discord_enabled: bool = False
    discord_webhook_url: str = ""


@dataclass
class AppConfig:
    page_group: str
    ai_disclosure_status: str
    database_path: str
    retry: RetryConfig
    notifications: NotificationConfig
    pages: List[PageConfig]
    delete_after_post: bool = True

    def get_page_by_name(self, name: str) -> Optional[PageConfig]:
        for p in self.pages:
            if p.name.lower() == name.lower():
                return p
        return None

    def get_page_by_id(self, page_id: str) -> Optional[PageConfig]:
        for p in self.pages:
            if p.page_id == page_id:
                return p
        return None


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """Loads and validates application configuration from YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    page_group = data.get("page_group", "personal_fb_id_1")
    ai_disclosure_status = data.get("ai_disclosure_status", "pending_determination")
    db_path = data.get("database", {}).get("path", "data/posted_videos.db")

    retry_data = data.get("retry", {})
    retry = RetryConfig(
        max_attempts=int(retry_data.get("max_attempts", 3)),
        base_delay_seconds=int(retry_data.get("base_delay_seconds", 5)),
        max_delay_seconds=int(retry_data.get("max_delay_seconds", 60))
    )

    notif_data = data.get("notifications", {})
    discord_url = (
        os.environ.get("DISCORD_WEBHOOK_URL") or
        notif_data.get("discord_webhook_url", "")
    )
    notifications = NotificationConfig(
        discord_enabled=bool(notif_data.get("discord_enabled", False)) or bool(os.environ.get("DISCORD_WEBHOOK_URL")),
        discord_webhook_url=discord_url
    )

    pages = []
    raw_pages = data.get("pages", [])
    for p in raw_pages:
        page = PageConfig(
            page_id=str(p.get("page_id", "")),
            name=str(p.get("name", "")),
            drive_folder_id=str(p.get("drive_folder_id", "")),
            enabled=bool(p.get("enabled", True)),
            daily_limit=int(p.get("daily_limit", 2)),
            title_mode=str(p.get("title_mode", "filename")),
            fixed_title=str(p.get("fixed_title", "")),
            description_footer=str(p.get("description_footer", "")),
            default_hashtags=p.get("default_hashtags", []) or [],
            page_access_token=str(p.get("page_access_token", "")),
            display_name=str(p.get("display_name", ""))
        )
        pages.append(page)

    delete_after_post = bool(data.get("delete_after_post", True))

    return AppConfig(
        page_group=page_group,
        ai_disclosure_status=ai_disclosure_status,
        database_path=db_path,
        retry=retry,
        notifications=notifications,
        pages=pages,
        delete_after_post=delete_after_post
    )
