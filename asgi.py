import uvicorn

from service import create_app

if __name__ == "__main__":
    uvicorn.run(
        "asgi:create_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=True,
        use_colors=True,
        proxy_headers=True
    )
