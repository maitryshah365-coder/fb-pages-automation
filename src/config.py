import os
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

    @property
    def token_env_var(self) -> str:
        """Returns standard environment variable name for this Page's Access Token."""
        safe_name = self.name.upper().replace("-", "_").replace(" ", "_")
        return f"FB_TOKEN_{safe_name}"

    def get_access_token(self) -> Optional[str]:
        """Resolves Page Access Token from environment or token file."""
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
            default_hashtags=p.get("default_hashtags", []) or []
        )
        pages.append(page)

    return AppConfig(
        page_group=page_group,
        ai_disclosure_status=ai_disclosure_status,
        database_path=db_path,
        retry=retry,
        notifications=notifications,
        pages=pages
    )
