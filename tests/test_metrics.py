"""Tests for translation cache metrics endpoint and counters."""

from __future__ import annotations

import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen

import app
from cache import Cache


def test_translation_cache_stats_hit_and_miss(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_CACHE", "true")
    cache = Cache(str(tmp_path / "cache"))

    assert cache.get_translation_stats() == {"hit_count": 0, "miss_count": 0}

    assert cache.get_translation("missing") is None
    cache.set_translation("hello", "Hello")
    assert cache.get_translation("hello") == "Hello"

    assert cache.get_translation_stats() == {"hit_count": 1, "miss_count": 1}


def test_metrics_endpoint_returns_translation_stats(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_CACHE", "true")
    cache = Cache(str(tmp_path / "cache"))
    cache.get_translation("missing")
    cache.set_translation("hello", "Hello")
    cache.get_translation("hello")
    monkeypatch.setattr(app, "get_cache", lambda: cache)

    server = ThreadingHTTPServer(("127.0.0.1", 0), app._HealthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        with urlopen(f"http://{host}:{port}/metrics", timeout=2) as response:
            assert response.status == 200
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert payload["hit_count"] == 1
    assert payload["miss_count"] == 1


def test_clear_cache_endpoint_deletes_translation_files(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_CACHE", "true")
    cache = Cache(str(tmp_path / "cache"))
    cache.set_translation("hello", "Hello")
    cache.set_translation("world", "World")
    monkeypatch.setattr(app, "get_cache", lambda: cache)

    server = ThreadingHTTPServer(("127.0.0.1", 0), app._HealthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        request = Request(
            f"http://{host}:{port}/clear-cache",
            method="POST",
            data=b"",
        )
        with urlopen(request, timeout=2) as response:
            assert response.status == 200
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert payload["status"] == "ok"
    assert payload["deleted_files"] == 2
    assert not any(cache.translation_dir.glob("*.pkl"))
