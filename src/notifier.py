import os
import json
import logging
import requests
from typing import Optional

logger = logging.getLogger("fb_automation")

TELEGRAM_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "telegram_config.json")

class TelegramNotifier:
    """Sends real-time execution alerts, token expiry warnings, and audit reports to Telegram."""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None, enabled: bool = True):
        # Load from config file if available
        file_token = None
        file_chat_id = None
        if os.path.exists(TELEGRAM_CONFIG_PATH):
            try:
                with open(TELEGRAM_CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    file_token = cfg.get("bot_token")
                    file_chat_id = cfg.get("chat_id")
            except Exception:
                pass

        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN") or file_token or "8739252005:AAFWEjL7Nt7b2G0vVM3IMCV4ojsvUbI1hp4"
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID") or file_chat_id
        self.enabled = bool(enabled and self.bot_token)

    def set_chat_id(self, chat_id: str):
        self.chat_id = str(chat_id)
        os.makedirs(os.path.dirname(TELEGRAM_CONFIG_PATH), exist_ok=True)
        with open(TELEGRAM_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"bot_token": self.bot_token, "chat_id": self.chat_id}, f, indent=2)
        logger.info(f"Saved Telegram chat_id: {self.chat_id}")

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.enabled or not self.chat_id:
            logger.warning("TelegramNotifier: Missing chat_id or disabled")
            return False
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        try:
            r = requests.post(url, json=payload, timeout=10)
            return r.ok
        except Exception as e:
            logger.warning(f"Telegram notification delivery failed: {e}")
            return False

    def send_alert(self, title: str, details: str, severity: str = "warning"):
        icon = "🚨" if severity == "error" else ("⚠️" if severity == "warning" else "ℹ️")
        msg = f"<b>{icon} FB AUTOMATION ALERT: {title}</b>\n\n{details}"
        self.send_message(msg)

    def send_token_expiry_alert(self, account_name: str, page_name: str, error_msg: str):
        msg = (
            f"🚨 <b>CRITICAL: FACEBOOK TOKEN EXPIRED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Account:</b> {account_name}\n"
            f"📄 <b>Page:</b> {page_name}\n"
            f"❌ <b>Error:</b> <code>{error_msg}</code>\n\n"
            f"👉 <i>Open your Mobile Dashboard to paste a new token!</i>"
        )
        self.send_message(msg)

    def send_stock_alert(self, page_name: str, count: int):
        msg = (
            f"⚠️ <b>DRIVE STOCK ALERT: VIDEOS RUNNING LOW</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 <b>Page:</b> {page_name}\n"
            f"📦 <b>Remaining Videos:</b> <b>{count}</b>\n\n"
            f"👉 <i>Please add fresh reels to the Google Drive folder!</i>"
        )
        self.send_message(msg)

    def send_run_summary(self, slot_name: str, total: int, success: int, failed: int, details: str = ""):
        icon = "✅" if failed == 0 else "⚠️"
        msg = (
            f"{icon} <b>FB AUTOMATION UPLOAD SUMMARY</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ <b>Slot:</b> {slot_name}\n"
            f"📊 <b>Total Processed:</b> {total}\n"
            f"✅ <b>Successful:</b> {success}\n"
            f"❌ <b>Failed:</b> {failed}\n"
        )
        if details:
            msg += f"\n📝 <b>Details:</b>\n{details}"
        self.send_message(msg)


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
