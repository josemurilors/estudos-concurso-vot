import time
import threading

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def consume(self, tokens=1):
        with self.lock:
            self.refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class MemoryRateLimiter:
    def __init__(self):
        self._buckets = {}
        self._lock = threading.Lock()

    def get_bucket(self, key, rate=5/60, capacity=5):
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(rate, capacity)
            return self._buckets[key]

    def check(self, key, tokens=1):
        bucket = self.get_bucket(key)
        return bucket.consume(tokens)
