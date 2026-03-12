"""Regras de validação e cálculo de orçamentos."""

from app.features.empresas.memberships.enums import MembershipRole


PROJETISTA_PCT = 0.01
GESTORA_PCT = 0.01
CONSULTOR_PCT_DEFAULT = 0.04


def requires_owner_admin_for_descontos(
    desconto_cliente_pct: float,
    taxa_arquiteto_pct: float,
    user_role: MembershipRole,
) -> bool:
    """Retorna True se precisa de OWNER/ADMIN para aplicar descontos/taxas acima de 2%."""
    if desconto_cliente_pct > 0.02 or taxa_arquiteto_pct > 0.02:
        return user_role not in {MembershipRole.OWNER, MembershipRole.ADMIN}
    return False


def calcular_total_movel(
    base_total: float,
    lucro_liquido_pct: float,
    desconto_cliente_pct: float,
    comissao_arquiteto_pct: float,
    consultor_pct: float = CONSULTOR_PCT_DEFAULT,
    projetista_pct: float = PROJETISTA_PCT,
    gestora_pct: float = GESTORA_PCT,
) -> float:
    """
    Valor do móvel:
    base_total + ((lucro + projetista + gestora + consultor) - desconto_cliente)% * base_total + comissao_arquiteto% * base_total
    """
    fator = 1 + (lucro_liquido_pct + projetista_pct + gestora_pct + consultor_pct) - desconto_cliente_pct
    fator += comissao_arquiteto_pct
    return base_total * fator
