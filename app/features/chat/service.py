
from app.features.ambientes.componentes.model import Componente
from app.features.chat.enum_states import ESTADOS
from app.features.chat.configuration_service import criar_configuracao_padrao
from app.features.chat.formatters import gerar_resumo_configuracao, resposta_com_opcoes
from app.features.chat.helpers_tabbles import gerar_tabela_moveis_orcados, normalizar
from app.features.conversations.store import get_or_create_conversa
from app.features.orcamento.catalog.repository import buscar_catalogo_componentes, buscar_movel_por_nome
from app.features.orcamento.pdf.service import salvar_pdf_local

CATALOGO = buscar_catalogo_componentes()

MENU = [
    {"id": "1", "label": "?? Dimensão"},
    {"id": "2", "label": "?? Cor"},
    {"id": "3", "label": "?? Material"},
    {"id": "4", "label": "?? Componentes"},
    {"id": "5", "label": "? Confirmar"},
]


def processar_mensagem(message: str, session_id: str) -> dict:
    conversa = get_or_create_conversa(session_id)

    if conversa.estado == ESTADOS["INICIO"]:
        movel = buscar_movel_por_nome(message)

        if not movel:
            return {"response": "Movel nao encontrado. Tente: Guarda-roupa, Cozinha, Rack..."}

        conversa.configuracao = criar_configuracao_padrao(movel)
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
        return resposta_com_opcoes(gerar_resumo_configuracao(conversa.configuracao), MENU)

    if conversa.estado == ESTADOS["CONFIGURANDO_MOVEL"]:
        if message == "1":
            conversa.estado = ESTADOS["ALTERAR_DIMENSAO"]
            return {"response": "Digite as dimensoes no formato:\nL x A x P\nExemplo: 800 x 700 x 600"}

        if message == "2":
            conversa.estado = ESTADOS["ESCOLHER_COR"]
            return resposta_com_opcoes(
                "Escolha a cor:",
                [
                    {"id": "branco", "label": "Branco"},
                    {"id": "preto", "label": "Preto"},
                    {"id": "amadeirado", "label": "Amadeirado"},
                ],
            )

        if message == "3":
            conversa.estado = ESTADOS["ESCOLHER_MATERIAL"]
            return resposta_com_opcoes(
                "Escolha o material:",
                [
                    {"id": "mdp", "label": "MDP"},
                    {"id": "mdf", "label": "MDF"},
                    {"id": "aluminio", "label": "Aluminio"},
                ],
            )

        if message == "4":
            categorias = sorted({normalizar(c.categoria_funcional) for c in conversa.configuracao.componentes})
            conversa.estado = ESTADOS["ESCOLHER_CATEGORIA_COMPONENTE"]
            return resposta_com_opcoes(
                "Qual componente deseja alterar?",
                [{"id": c, "label": c.capitalize()} for c in categorias] + [{"id": "0", "label": "Voltar"}],
            )

        if message == "5":
            conversa.estado = ESTADOS["CONFIRMANDO_MOVEL"]
            total = conversa.configuracao.total_geral()
            return resposta_com_opcoes(
                f"Movel configurado com sucesso.\n{conversa.configuracao.nome_movel}\nValor: R$ {total:.2f}\nDeseja confirmar este movel no orcamento?",
                [
                    {"id": "sim", "label": "Sim, adicionar ao orcamento"},
                    {"id": "nao", "label": "Nao, continuar editando"},
                ],
            )

    if conversa.estado == ESTADOS["CONFIRMANDO_MOVEL"]:
        if message.lower() == "sim":
            conversa.moveis_orcados.append(conversa.configuracao)
            conversa.configuracao = None
            conversa.estado = ESTADOS["ADICIONAR_MAIS_MOVEIS"]
            qtd_moveis = len(conversa.moveis_orcados)
            return resposta_com_opcoes(
                f"Movel adicionado ao orcamento.\nVoce tem {qtd_moveis} movel(is) no orcamento.\nO que deseja fazer agora?",
                [
                    {"id": "mais", "label": "Orcar mais moveis"},
                    {"id": "revisar", "label": "Revisar orcamento"},
                    {"id": "finalizar", "label": "Finalizar e gerar PDF"},
                ],
            )

        if message.lower() == "nao":
            conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
            return resposta_com_opcoes("Voltando para edicao...\n\n" + gerar_resumo_configuracao(conversa.configuracao), MENU)

    if conversa.estado == ESTADOS["ADICIONAR_MAIS_MOVEIS"]:
        if message.lower() == "mais":
            conversa.estado = ESTADOS["INICIO"]
            return {"response": "Perfeito! Qual movel deseja orcar?\nExemplos: Guarda-roupa, Cozinha, Rack, Estante..."}

        if message.lower() == "revisar":
            conversa.estado = ESTADOS["REVISAO_FINAL"]
            tabela = gerar_tabela_moveis_orcados(conversa.moveis_orcados)
            return resposta_com_opcoes(
                tabela + "\n\nO que deseja fazer?",
                [
                    {"id": "mais", "label": "Adicionar mais moveis"},
                    {"id": "remover", "label": "Remover movel"},
                    {"id": "finalizar", "label": "Finalizar e gerar PDF"},
                ],
            )

        if message.lower() == "finalizar":
            conversa.estado = ESTADOS["REVISAO_FINAL"]
            tabela = gerar_tabela_moveis_orcados(conversa.moveis_orcados)
            return resposta_com_opcoes(
                tabela + "\n\nConfirma a finalizacao do orcamento?",
                [
                    {"id": "confirmar", "label": "Sim, gerar PDF"},
                    {"id": "mais", "label": "Adicionar mais moveis"},
                    {"id": "remover", "label": "Remover movel"},
                ],
            )

    if conversa.estado == ESTADOS["REVISAO_FINAL"]:
        if message.lower() == "mais":
            conversa.estado = ESTADOS["INICIO"]
            return {"response": "Qual movel deseja adicionar ao orcamento?"}

        if message.lower() == "remover":
            if not conversa.moveis_orcados:
                return {"response": "Nao ha moveis para remover."}

            opcoes = [
                {
                    "id": str(idx),
                    "label": f"{idx}. {m.nome_movel} - R$ {m.total_geral():.2f}",
                }
                for idx, m in enumerate(conversa.moveis_orcados, 1)
            ]
            opcoes.append({"id": "0", "label": "Cancelar"})
            return resposta_com_opcoes("Qual movel deseja remover?", opcoes)

        if message.lower() in {"confirmar", "finalizar"}:
            try:
                filename = salvar_pdf_local(conversa.moveis_orcados, session_id)
                conversa.estado = ESTADOS["FINALIZADO"]
                total_final = sum(m.total_geral() for m in conversa.moveis_orcados)
                qtd_moveis = len(conversa.moveis_orcados)
                return {
                    "response": (
                        "Orcamento finalizado com sucesso.\n"
                        f"Total de moveis: {qtd_moveis}\n"
                        f"Valor total: R$ {total_final:.2f}\n"
                        "Seu PDF esta pronto para download."
                    ),
                    "pdf_ready": True,
                    "pdf_filename": filename,
                    "download_url": f"/orcamento/pdf/download/{session_id}",
                }
            except Exception as exc:
                return {"response": f"Erro ao gerar PDF: {exc}"}

        if message.isdigit():
            if message == "0":
                tabela = gerar_tabela_moveis_orcados(conversa.moveis_orcados)
                return resposta_com_opcoes(
                    tabela,
                    [
                        {"id": "mais", "label": "Adicionar mais moveis"},
                        {"id": "remover", "label": "Remover movel"},
                        {"id": "finalizar", "label": "Finalizar e gerar PDF"},
                    ],
                )

            idx = int(message) - 1
            if 0 <= idx < len(conversa.moveis_orcados):
                movel_removido = conversa.moveis_orcados.pop(idx)
                if not conversa.moveis_orcados:
                    conversa.estado = ESTADOS["INICIO"]
                    return {"response": "Movel removido. Nao ha mais moveis no orcamento. Vamos comecar um novo orcamento?"}

                tabela = gerar_tabela_moveis_orcados(conversa.moveis_orcados)
                return resposta_com_opcoes(
                    f"{movel_removido.nome_movel} removido.\n\n{tabela}",
                    [
                        {"id": "mais", "label": "Adicionar mais moveis"},
                        {"id": "remover", "label": "Remover outro movel"},
                        {"id": "finalizar", "label": "Finalizar e gerar PDF"},
                    ],
                )

    if conversa.estado == ESTADOS["ALTERAR_DIMENSAO"]:
        try:
            partes = message.lower().replace(" ", "").split("x")
            largura, altura, profundidade = map(float, partes)
            conversa.configuracao.L_mm = largura
            conversa.configuracao.A_mm = altura
            conversa.configuracao.P_mm = profundidade
            conversa.configuracao.recalcular_preco_por_area()
            conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
            return resposta_com_opcoes("Dimensao atualizada.\n\n" + gerar_resumo_configuracao(conversa.configuracao), MENU)
        except Exception:
            return {"response": "Formato invalido. Use: 800 x 700 x 600"}

    if conversa.estado == ESTADOS["ESCOLHER_COR"]:
        conversa.configuracao.cor = message.capitalize()
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
        return resposta_com_opcoes(gerar_resumo_configuracao(conversa.configuracao), MENU)

    if conversa.estado == ESTADOS["ESCOLHER_MATERIAL"]:
        conversa.configuracao.material = message.upper()
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
        return resposta_com_opcoes(gerar_resumo_configuracao(conversa.configuracao), MENU)

    if conversa.estado == ESTADOS["ESCOLHER_CATEGORIA_COMPONENTE"]:
        if message == "0":
            conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
            return resposta_com_opcoes("Voltando ao menu principal...\n\n" + gerar_resumo_configuracao(conversa.configuracao), MENU)

        categoria = normalizar(message)
        if categoria not in CATALOGO:
            return {"response": "Categoria invalida. Tente novamente."}

        conversa.categoria_selecionada = categoria
        conversa.estado = ESTADOS["ESCOLHER_COMPONENTE"]
        return resposta_com_opcoes(
            "Escolha o novo componente:",
            [
                {"id": c["id"], "label": f"{c['nome']} (R$ {c['preco_unitario']:.2f})"}
                for c in CATALOGO[categoria]
            ],
        )

    if conversa.estado == ESTADOS["ESCOLHER_COMPONENTE"]:
        categoria = conversa.categoria_selecionada
        opcao = next((c for c in CATALOGO[categoria] if c["id"] == message), None)

        if not opcao:
            return {"response": "Opcao invalida. Tente novamente."}

        conversa.configuracao.componentes = [
            c for c in conversa.configuracao.componentes if normalizar(c.categoria_funcional) != categoria
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
        return resposta_com_opcoes("Componente atualizado.\n\n" + gerar_resumo_configuracao(conversa.configuracao), MENU)

    return {"response": "Nao entendi. Tente novamente."}

