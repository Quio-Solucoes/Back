from __future__ import annotations

import unicodedata

from app.core.models import Componente
from app.core.repositories import buscar_catalogo_componentes, buscar_movel_por_nome
from app.core.services import criar_configuracao_padrao
from app.core.states import ESTADOS
from app.core.utils import gerar_resumo_configuracao, resposta_com_opcoes


def normalizar(txt: str) -> str:
    txt = txt.lower().strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    if txt.endswith("s"):
        txt = txt[:-1]
    return txt


class Conversa:
    def __init__(self):
        self.estado = ESTADOS["INICIO"]
        self.configuracao = None
        self.categoria_selecionada = None


conversas: dict[str, Conversa] = {}
CATALOGO = buscar_catalogo_componentes()


def processar_mensagem(message: str, session_id: str = "default") -> dict:
    if not message:
        return {"response": "Requisição inválida"}, 400

    conversa = conversas.setdefault(session_id, Conversa())

    if conversa.estado == ESTADOS["INICIO"]:
        movel = buscar_movel_por_nome(message)

        if not movel:
            return {
                "response": "? Móvel não encontrado. Tente: Guarda-roupa, Cozinha, Rack...",
            }, 200

        conversa.configuracao = criar_configuracao_padrao(movel)
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return (
            resposta_com_opcoes(
                gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "?? Dimensão"},
                    {"id": "2", "label": "?? Cor"},
                    {"id": "3", "label": "?? Material"},
                    {"id": "4", "label": "?? Componentes"},
                    {"id": "5", "label": "? Confirmar"},
                ],
            ),
            200,
        )

    if conversa.estado == ESTADOS["CONFIGURANDO_MOVEL"]:
        if message == "1":
            conversa.estado = ESTADOS["ALTERAR_DIMENSAO"]
            return (
                {
                    "response": (
                        "?? Digite as dimensões no formato:\n\n"
                        "L x A x P\n\n"
                        "Exemplo:\n"
                        "800 x 700 x 600"
                    )
                },
                200,
            )

        if message == "2":
            conversa.estado = ESTADOS["ESCOLHER_COR"]
            return (
                resposta_com_opcoes(
                    "?? Escolha a cor:",
                    [
                        {"id": "branco", "label": "Branco"},
                        {"id": "preto", "label": "Preto"},
                        {"id": "amadeirado", "label": "Amadeirado"},
                    ],
                ),
                200,
            )

        if message == "3":
            conversa.estado = ESTADOS["ESCOLHER_MATERIAL"]
            return (
                resposta_com_opcoes(
                    "?? Escolha o material:",
                    [
                        {"id": "mdp", "label": "MDP"},
                        {"id": "mdf", "label": "MDF"},
                        {"id": "aluminio", "label": "Alumínio"},
                    ],
                ),
                200,
            )

        if message == "4":
            categorias = sorted(
                {normalizar(c.categoria_funcional) for c in conversa.configuracao.componentes}
            )

            conversa.estado = ESTADOS["ESCOLHER_CATEGORIA_COMPONENTE"]

            return (
                resposta_com_opcoes(
                    "?? Qual componente deseja alterar?",
                    [{"id": c, "label": c.capitalize()} for c in categorias]
                    + [{"id": "0", "label": "? Voltar"}],
                ),
                200,
            )

        if message == "5":
            total = conversa.configuracao.total_geral()
            return (
                {
                    "response": (
                        "? Orçamento finalizado!\n\n"
                        f"Total final: R$ {total:.2f}\n\n"
                        "Obrigado por usar nosso sistema!"
                    )
                },
                200,
            )

    if conversa.estado == ESTADOS["ALTERAR_DIMENSAO"]:
        try:
            partes = message.lower().replace(" ", "").split("x")
            L, A, P = map(float, partes)

            conversa.configuracao.L_mm = L
            conversa.configuracao.A_mm = A
            conversa.configuracao.P_mm = P
            conversa.configuracao.recalcular_preco_por_area()

            conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

            return (
                resposta_com_opcoes(
                    "?? Dimensão atualizada!\n\n"
                    + gerar_resumo_configuracao(conversa.configuracao),
                    [
                        {"id": "1", "label": "?? Dimensão"},
                        {"id": "2", "label": "?? Cor"},
                        {"id": "3", "label": "?? Material"},
                        {"id": "4", "label": "?? Componentes"},
                        {"id": "5", "label": "? Confirmar"},
                    ],
                ),
                200,
            )
        except Exception:
            return {"response": "? Formato inválido. Use: 800 x 700 x 600"}, 200

    if conversa.estado == ESTADOS["ESCOLHER_COR"]:
        conversa.configuracao.cor = message.capitalize()
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return (
            resposta_com_opcoes(
                gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "?? Dimensão"},
                    {"id": "2", "label": "?? Cor"},
                    {"id": "3", "label": "?? Material"},
                    {"id": "4", "label": "?? Componentes"},
                    {"id": "5", "label": "? Confirmar"},
                ],
            ),
            200,
        )

    if conversa.estado == ESTADOS["ESCOLHER_MATERIAL"]:
        conversa.configuracao.material = message.upper()
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return (
            resposta_com_opcoes(
                gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "?? Dimensão"},
                    {"id": "2", "label": "?? Cor"},
                    {"id": "3", "label": "?? Material"},
                    {"id": "4", "label": "?? Componentes"},
                    {"id": "5", "label": "? Confirmar"},
                ],
            ),
            200,
        )

    if conversa.estado == ESTADOS["ESCOLHER_CATEGORIA_COMPONENTE"]:
        if message == "0":
            conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
            return (
                resposta_com_opcoes(
                    "? Voltando ao menu principal...\n\n"
                    + gerar_resumo_configuracao(conversa.configuracao),
                    [
                        {"id": "1", "label": "?? Dimensão"},
                        {"id": "2", "label": "?? Cor"},
                        {"id": "3", "label": "?? Material"},
                        {"id": "4", "label": "?? Componentes"},
                        {"id": "5", "label": "? Confirmar"},
                    ],
                ),
                200,
            )

        categoria = normalizar(message)
        if categoria not in CATALOGO:
            return {"response": "? Categoria inválida. Tente novamente."}, 200

        conversa.categoria_selecionada = categoria
        conversa.estado = ESTADOS["ESCOLHER_COMPONENTE"]

        return (
            resposta_com_opcoes(
                "?? Escolha o novo componente:",
                [
                    {
                        "id": c["id"],
                        "label": f"{c['nome']} (R$ {c['preco_unitario']:.2f})",
                    }
                    for c in CATALOGO[categoria]
                ],
            ),
            200,
        )

    if conversa.estado == ESTADOS["ESCOLHER_COMPONENTE"]:
        categoria = conversa.categoria_selecionada

        opcao = next(
            (c for c in CATALOGO[categoria] if c["id"] == message),
            None,
        )

        if not opcao:
            return {"response": "? Opção inválida. Tente novamente."}, 200

        conversa.configuracao.componentes = [
            c
            for c in conversa.configuracao.componentes
            if normalizar(c.categoria_funcional) != categoria
        ]

        conversa.configuracao.componentes.append(
            Componente(
                nome=opcao["nome"],
                categoria_funcional=categoria,
                quantidade=1,
                preco_unitario=opcao["preco_unitario"],
            )
        )

        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return (
            resposta_com_opcoes(
                "? Componente atualizado!\n\n"
                + gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "?? Dimensão"},
                    {"id": "2", "label": "?? Cor"},
                    {"id": "3", "label": "?? Material"},
                    {"id": "4", "label": "?? Componentes"},
                    {"id": "5", "label": "? Confirmar"},
                ],
            ),
            200,
        )

    return {"response": "? Não entendi. Tente novamente."}, 200

