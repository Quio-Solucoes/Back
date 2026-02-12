from app.features.conversations.store import reset_conversa


def resetar_conversa(session_id: str) -> dict:
    if reset_conversa(session_id):
        return {"response": "Conversa resetada com sucesso!"}
    return {"response": "Conversa nao encontrada."}
