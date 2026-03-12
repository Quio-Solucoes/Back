from fastapi import HTTPException


from app.features.chat.enum_states import ESTADOS
from app.features.chat.helpers_tabbles import normalizar
from app.features.conversations.store import get_conversa
from app.features.empresas.memberships.enums import MembershipRole
from app.features.orcamento.ambientes.componentes.model import Componente
from app.features.orcamento.catalogo.catalogo_repository import buscar_catalogo_componentes
from app.features.orcamento.pricing import calcular_total_movel, requires_owner_admin_for_descontos


CATALOGO = buscar_catalogo_componentes()


def obter_orcamento(
    session_id: str,
    desconto_cliente_pct: float = 0.0,
    taxa_arquiteto_pct: float = 0.0,
    user_role: MembershipRole | None = None,
    lucro_liquido_pct: float = 0.0,
    consultor_pct: float | None = None,
) -> dict:
    conversa = get_conversa(session_id)

    if not conversa:
        return {"moveis": [], "total": 0, "finalizado": False}

    if requires_owner_admin_for_descontos(desconto_cliente_pct, taxa_arquiteto_pct, user_role or MembershipRole.COLABORADOR):
        raise HTTPException(status_code=403, detail="Desconto/taxa acima de 2% requer OWNER ou ADMIN")

    moveis = []
    total_geral = 0.0

    for idx, config in enumerate(conversa.moveis_orcados):
        componentes = [
            {
                "nome": c.nome,
                "categoria": c.categoria_funcional,
                "quantidade": c.quantidade,
                "preco": c.preco_unitario,
                "subtotal": c.total(),
            }
            for c in config.componentes
        ]

        base_total = config.total_geral()
        total_movel = calcular_total_movel(
            base_total=base_total,
            lucro_liquido_pct=lucro_liquido_pct,
            desconto_cliente_pct=desconto_cliente_pct,
            comissao_arquiteto_pct=taxa_arquiteto_pct,
            consultor_pct=consultor_pct if consultor_pct is not None else 0.04,
        )
        total_geral += total_movel

        moveis.append(
            {
                "id": idx,
                "nome": config.nome_movel,
                "dimensoes": f"{int(config.L_mm)}x{int(config.A_mm)}x{int(config.P_mm)} mm",
                "material": config.material,
                "cor": config.cor,
                "total": total_movel,
                "componentes": componentes,
            }
        )

    return {"moveis": moveis, "total": total_geral, "finalizado": conversa.estado == ESTADOS["FINALIZADO"]}


def remover_movel(session_id: str, movel_id: int) -> dict:
    conversa = get_conversa(session_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    if movel_id < 0 or movel_id >= len(conversa.moveis_orcados):
        raise HTTPException(status_code=400, detail="Movel invalido")

    conversa.moveis_orcados.pop(movel_id)
    return {"success": True}


def editar_componente(session_id: str, movel_id: int, componente_id: int) -> dict:
    conversa = get_conversa(session_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    if movel_id < 0 or movel_id >= len(conversa.moveis_orcados):
        raise HTTPException(status_code=400, detail="Movel invalido")

    movel = conversa.moveis_orcados[movel_id]

    if componente_id < 0 or componente_id >= len(movel.componentes):
        raise HTTPException(status_code=400, detail="Componente invalido")

    componente = movel.componentes[componente_id]
    categoria = normalizar(componente.categoria_funcional)

    if categoria not in CATALOGO:
        raise HTTPException(status_code=400, detail="Categoria nao encontrada no catalogo")

    return {"categoria": categoria, "opcoes": CATALOGO[categoria]}


def atualizar_componente(session_id: str, movel_id: int, componente_id: int, opcao_id: str) -> dict:
    conversa = get_conversa(session_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    if movel_id < 0 or movel_id >= len(conversa.moveis_orcados):
        raise HTTPException(status_code=400, detail="Movel invalido")

    movel = conversa.moveis_orcados[movel_id]

    if componente_id < 0 or componente_id >= len(movel.componentes):
        raise HTTPException(status_code=400, detail="Componente invalido")

    componente_antigo = movel.componentes[componente_id]
    categoria = normalizar(componente_antigo.categoria_funcional)

    opcoes = CATALOGO.get(categoria, [])
    nova_opcao = next((o for o in opcoes if str(o["id"]) == opcao_id), None)

    if not nova_opcao:
        raise HTTPException(status_code=400, detail="Opcao invalida")

    movel.componentes.pop(componente_id)
    movel.componentes.insert(
        componente_id,
        Componente(
            nome=nova_opcao["nome"],
            categoria_funcional=categoria,
            quantidade=componente_antigo.quantidade,
            preco_unitario=nova_opcao["preco_unitario"],
        ),
    )

    return {"success": True}


def editar_dimensao(session_id: str, movel_id: int, largura: float, altura: float, profundidade: float) -> dict:
    conversa = get_conversa(session_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    if movel_id < 0 or movel_id >= len(conversa.moveis_orcados):
        raise HTTPException(status_code=400, detail="Movel invalido")

    movel = conversa.moveis_orcados[movel_id]
    movel.L_mm = largura
    movel.A_mm = altura
    movel.P_mm = profundidade
    movel.recalcular_preco_por_area()

    return {"success": True}


def status_orcamento(session_id: str) -> dict:
    conversa = get_conversa(session_id)

    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    return {
        "estado": conversa.estado,
        "qtd_moveis": len(conversa.moveis_orcados),
        "total": sum(m.total_geral() for m in conversa.moveis_orcados) if conversa.moveis_orcados else 0,
    }
