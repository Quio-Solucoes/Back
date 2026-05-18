# Back
Backend da SaaS de geração de orçamento.

## Rodando com FastAPI

```bash
uvicorn app.main:app --reload --port 5001
```

## Auth

- `POST /usuarios` (nome, email, telefone, senha)
- `POST /auth/login` (email, senha) -> `access_token`
- `GET /auth/me` (Authorization: Bearer <token>)
