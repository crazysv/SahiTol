"""In-memory rate limiter for PIN brute-force protection and abuse prevention."""
import time
import threading
from typing import Dict, List, Tuple


class RateLimiter:
    """Thread-safe sliding-window rate limiter for sensitive authentication endpoints."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 900):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._failures: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def _cleanup(self, now: float, key: str) -> List[float]:
        """Prune timestamps older than window_seconds."""
        cutoff = now - self.window_seconds
        valid = [t for t in self._failures.get(key, []) if t > cutoff]
        if valid:
            self._failures[key] = valid
        else:
            self._failures.pop(key, None)
        return valid

    def is_locked(self, key: str) -> Tuple[bool, int]:
        """Check if key is currently locked out. Returns (is_locked, retry_after_seconds)."""
        now = time.time()
        with self._lock:
            attempts = self._cleanup(now, key)
            if len(attempts) >= self.max_attempts:
                oldest_in_window = attempts[0]
                retry_after = int(oldest_in_window + self.window_seconds - now) + 1
                return True, max(1, retry_after)
            return False, 0

    def record_failure(self, key: str) -> Tuple[int, int]:
        """Record a failed attempt. Returns (current_attempt_count, retry_after_seconds)."""
        now = time.time()
        with self._lock:
            attempts = self._cleanup(now, key)
            attempts.append(now)
            self._failures[key] = attempts
            if len(attempts) >= self.max_attempts:
                oldest_in_window = attempts[0]
                retry_after = int(oldest_in_window + self.window_seconds - now) + 1
                return len(attempts), max(1, retry_after)
            return len(attempts), 0

    def record_success(self, key: str) -> None:
        """Clear failed attempts on successful authentication."""
        with self._lock:
            self._failures.pop(key, None)

    def reset(self) -> None:
        """Reset all tracking records (primarily for testing)."""
        with self._lock:
            self._failures.clear()


# Global limiter instances
phone_limiter = RateLimiter(max_attempts=5, window_seconds=900)  # 5 attempts per 15 min
ip_limiter = RateLimiter(max_attempts=25, window_seconds=900)    # 25 attempts per IP per 15 min
