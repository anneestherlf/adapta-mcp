"""Observability helpers: logging configuration and simple in-memory metrics.

This module keeps dependencies minimal (no Prometheus client) and exposes a
small metrics dictionary that the FastAPI app can return at `/metrics`.
"""
import logging
import threading
import time
from typing import Dict

# Basic logging configuration for the Gateway
def configure_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger()
    if logger.handlers:
        # Avoid reconfiguring if already configured
        return

    handler = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(level)


# Simple thread-safe in-memory metrics
_metrics_lock = threading.Lock()
_metrics: Dict[str, float] = {
    "requests_total": 0,
    "requests_success": 0,
    "requests_error": 0,
    "last_request_latency_ms": 0.0,
}


def incr(metric: str, value: float = 1.0) -> None:
    with _metrics_lock:
        _metrics[metric] = _metrics.get(metric, 0.0) + value


def set_metric(metric: str, value: float) -> None:
    with _metrics_lock:
        _metrics[metric] = value


def get_metrics() -> Dict[str, float]:
    with _metrics_lock:
        return dict(_metrics)


def time_block(metric_name_latency: str):
    """Context manager to measure a block and set latency metric (ms)."""

    class TimerCtx:
        def __enter__(self):
            self._start = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc, tb):
            elapsed = (time.perf_counter() - self._start) * 1000.0
            set_metric(metric_name_latency, elapsed)

    return TimerCtx()
