"""
Vercel entrypoint (automatic detection).

Vercel's Python runtime looks for a FastAPI `app` instance in one of a few
default filenames at the project root: app.py, index.py, server.py,
main.py, wsgi.py, or asgi.py. The real app lives in app/main.py (one level
down), so this file just re-exports it under a name Vercel finds
automatically -- no pyproject.toml config needed at all.
"""
from app.main import app  # noqa: F401  (re-exported for Vercel's detection)
