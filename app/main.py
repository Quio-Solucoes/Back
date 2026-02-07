from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.features.chat.router import router as chat_router
from app.features.conversations.router import router as conversations_router
from app.features.health.router import router as health_router

app = FastAPI(title="Quio Back", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router, tags=["chat"])
app.include_router(health_router, tags=["health"])
app.include_router(conversations_router, tags=["conversations"])


@app.get("/")
def index():
    return {"status": "ok", "message": "Backend FastAPI online"}

