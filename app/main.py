from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.features.chat.router import router as chat_router
from app.features.chat.voz.router import router as chat_voice_router
from app.features.conversations.router import router as conversations_router
from app.features.health.router import router as health_router
from app.features.orcamento.router import router as orcamento_router
from app.features.system.router import router as system_router
from app.config.settings import CORS_ALLOW_ALL, CORS_ORIGINS


def create_app() -> FastAPI:
    application = FastAPI(title="Quio Solucoes API", version="1.0.0")

    if CORS_ALLOW_ALL:
        application.add_middleware(
            CORSMiddleware,
            allow_origin_regex=".*",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.include_router(chat_router)
    application.include_router(chat_voice_router)
    application.include_router(orcamento_router)
    application.include_router(system_router)
    application.include_router(conversations_router)
    application.include_router(health_router)

    return application


app = create_app()
