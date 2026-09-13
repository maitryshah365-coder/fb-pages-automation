import logging
import requests
from typing import Optional

logger = logging.getLogger("fb_automation")


class DiscordNotifier:
    """Sends execution alerts to Discord Webhook."""

    def __init__(self, webhook_url: Optional[str] = None, enabled: bool = False):
        self.webhook_url = webhook_url
        self.enabled = bool(enabled and webhook_url)

    def send_success(self, page_name: str, video_title: str, post_id: str, post_type: str = "reel"):
        if not self.enabled:
            return
        content = (
            f"✅ **Facebook Automation Post Succeeded**\n"
            f"**Page:** {page_name}\n"
            f"**Type:** {post_type.upper()}\n"
            f"**Video:** {video_title}\n"
            f"**Post ID:** `{post_id}`"
        )
        self._post_webhook({"content": content})

    def send_failure(self, page_name: str, video_title: Optional[str], error_message: str):
        if not self.enabled:
            return
        v_info = f"**Video:** {video_title}\n" if video_title else ""
        content = (
            f"❌ **Facebook Automation Post Failed**\n"
            f"**Page:** {page_name}\n"
            f"{v_info}"
            f"**Error:** ```{error_message}```"
        )
        self._post_webhook({"content": content})

    def _post_webhook(self, payload: dict):
        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            logger.warning(f"Failed to deliver Discord notification: {e}")
