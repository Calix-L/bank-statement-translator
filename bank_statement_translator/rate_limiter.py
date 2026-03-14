"""Rate limiter for API calls."""

from __future__ import annotations

import time
from collections import deque
from threading import Lock


class RateLimiter:
    """Token bucket rate limiter for API calls."""
    
    def __init__(self, max_calls: int, time_window: float):
        """Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self.lock = Lock()
    
    def __call__(self, func):
        """Decorator to rate limit function calls."""
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                
                # Remove old calls outside the time window
                while self.calls and self.calls[0] < now - self.time_window:
                    self.calls.popleft()
                
                # Check if we need to wait
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.time_window - (now - self.calls[0])
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        # Clean up again after sleeping
                        now = time.time()
                        while self.calls and self.calls[0] < now - self.time_window:
                            self.calls.popleft()
                
                # Record this call
                self.calls.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def wait(self) -> None:
        """Wait if rate limit is reached."""
        with self.lock:
            now = time.time()
            
            # Remove old calls
            while self.calls and self.calls[0] < now - self.time_window:
                self.calls.popleft()
            
            # Wait if needed
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)


# Pre-configured rate limiters
# Zhipu API: typically 60 calls/minute for free tier
zhipu_limiter = RateLimiter(max_calls=60, time_window=60)

# Baidu OCR: typically 500 calls/day, so be more conservative
ocr_limiter = RateLimiter(max_calls=10, time_window=60)