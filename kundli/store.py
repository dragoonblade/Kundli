"""Chart context store with TTL. Uses Redis if REDIS_URL is set, else file-based."""
import json
import logging
import os
import tempfile
import time
from datetime import datetime

_CHART_DIR = os.path.join(tempfile.gettempdir(), "kundli_charts")
os.makedirs(_CHART_DIR, exist_ok=True)
_CHART_TTL = 3600  # 1 hour


class ChartStore:
    """TTL cache for chart contexts."""

    def __init__(self):
        self._redis = None
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(redis_url)
                self._redis.ping()
                logging.info("ChartStore: using Redis")
            except (ImportError, ConnectionError, OSError) as e:
                logging.warning(f"ChartStore: Redis unavailable ({e}), falling back to file-based")
                self._redis = None

    def set(self, key, value):
        """Store a chart context with TTL."""
        payload = json.dumps({"data": self._serialize(value)})
        if self._redis:
            self._redis.setex(f"kundli:{key}", _CHART_TTL, payload)
            return
        self._evict()
        path = os.path.join(_CHART_DIR, f"{key}.json")
        with open(path, "w") as f:
            json.dump({"data": self._serialize(value), "ts": time.time()}, f)

    def get(self, key):
        """Retrieve a chart context by key."""
        if self._redis:
            raw = self._redis.get(f"kundli:{key}")
            if not raw:
                return None
            return self._deserialize(json.loads(raw)["data"])
        path = os.path.join(_CHART_DIR, f"{key}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - payload.get("ts", 0) > _CHART_TTL:
            os.remove(path)
            return None
        return self._deserialize(payload["data"])

    def _evict(self):
        now = time.time()
        try:
            entries = sorted(
                ((f, os.path.join(_CHART_DIR, f)) for f in os.listdir(_CHART_DIR) if f.endswith(".json")),
                key=lambda x: os.path.getmtime(x[1]),
            )
        except OSError:
            return
        for name, path in entries:
            try:
                if now - os.path.getmtime(path) > _CHART_TTL:
                    os.remove(path)
            except OSError:
                pass
        remaining = [p for _, p in entries if os.path.exists(p)]
        while len(remaining) > 100:
            try:
                os.remove(remaining.pop(0))
            except OSError:
                pass

    @staticmethod
    def _serialize(ctx):
        """Convert chart context to JSON-safe dict."""
        out = dict(ctx)

        def _ser_period(d):
            s = {**d, "start": d["start"].isoformat(), "end": d["end"].isoformat()}
            if "antardasha" in d:
                s["antardasha"] = [_ser_period(a) for a in d["antardasha"]]
            if "pratyantar" in d:
                s["pratyantar"] = [_ser_period(p) for p in d["pratyantar"]]
            return s

        out["dashas"] = [_ser_period(d) for d in ctx["dashas"]]
        return out

    @staticmethod
    def _deserialize(data):
        """Restore chart context from JSON."""
        def _deser_period(d):
            d["start"] = datetime.fromisoformat(d["start"])
            d["end"] = datetime.fromisoformat(d["end"])
            if "antardasha" in d:
                d["antardasha"] = [_deser_period(a) for a in d["antardasha"]]
            if "pratyantar" in d:
                d["pratyantar"] = [_deser_period(p) for p in d["pratyantar"]]
            return d

        data["dashas"] = [_deser_period(d) for d in data["dashas"]]
        return data
