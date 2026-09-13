import time
import random
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger("fb_automation")


class PermanentError(Exception):
    """Raised when an error cannot be resolved by retrying (e.g., auth failure, invalid file)."""
    pass


class RetryableError(Exception):
    """Raised when an operation encounters a transient failure (e.g., network timeout, rate limit)."""
    pass


def retry_with_backoff(
    action: Callable[[], Any],
    max_attempts: int = 3,
    base_delay: float = 5.0,
    max_delay: float = 60.0,
    action_name: str = "Operation"
) -> Any:
    """
    Executes an action with exponential backoff and jitter.
    Permanent errors fail immediately; transient errors are retried up to max_attempts.
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            return action()
        except PermanentError as pe:
            logger.error(f"[{action_name}] Permanent error encountered, will not retry: {pe}")
            raise
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                logger.error(f"[{action_name}] All {max_attempts} attempts failed. Last error: {e}")
                raise

            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            # Add jitter (+- 20%)
            jitter = random.uniform(0.8, 1.2) * delay
            logger.warning(
                f"[{action_name}] Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {jitter:.1f}s..."
            )
            time.sleep(jitter)
