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

Obs.: Todas as rotas (exceto `POST /auth/login`) exigem `Authorization: Bearer <token>`.

## Orçamentos (metadados)

- `GET /orcamentos` lista orçamentos
- `POST /orcamentos` cria orçamento (cliente, arquiteto, ambiente?)
- `GET /orcamentos/{id}` obtém orçamento
- `PATCH /orcamentos/{id}` atualiza (cliente/arquiteto/ambiente/status)
- `DELETE /orcamentos/{id}` remove

## Orçamento (itens)

- `GET /orcamento/{session_id}` lista itens por vista
- `PUT /orcamento/{session_id}/editar-item/{item_id}` edita item
- `DELETE /orcamento/{session_id}/remover/{item_id}` remove item
