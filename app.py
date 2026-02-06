from app.main import app

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("ðŸš€ Servidor Flask iniciado!")
    print("ðŸ“ Rodando em: http://localhost:5001")
    print("ðŸ’¬ Endpoint do chat: http://localhost:5001/chat")
    print("ðŸ¥ Health check: http://localhost:5001/health")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)

