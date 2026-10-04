"""
Production entry point for Render.

Render injects PORT. Bind on 0.0.0.0 and that port.
Local default remains 8000 when PORT is unset.
"""

import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
