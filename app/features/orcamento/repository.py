from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.features.orcamento.schema import Orcamento, OrcamentoItem, OrcamentoItemComponente


def _money(value: float | int) -> Decimal:
    return Decimal(str(round(float(value), 2)))


def save_finalized_orcamento(
    db: Session,
    *,
    session_id: str,
    moveis_configurados: list,
    pdf_filename: str | None = None,
    status: str = "FINALIZADO",
) -> Orcamento:
    orcamento = Orcamento(
        session_id=session_id,
        status=status,
        quantidade_moveis=len(moveis_configurados),
        pdf_filename=pdf_filename,
    )

    total_geral = 0.0

    for item_idx, config in enumerate(moveis_configurados, start=1):
        preco_movel = float(getattr(config, "preco_atual", 0) or 0)
        total_componentes = float(sum(comp.total() for comp in getattr(config, "componentes", [])))
        total_item = float(config.total_geral())
        total_geral += total_item

        item = OrcamentoItem(
            ordem=item_idx,
            nome_movel=str(getattr(config, "nome_movel", "Movel")),
            material=getattr(config, "material", None),
            cor=getattr(config, "cor", None),
            largura_mm=float(getattr(config, "L_mm", 0) or 0),
            altura_mm=float(getattr(config, "A_mm", 0) or 0),
            profundidade_mm=float(getattr(config, "P_mm", 0) or 0),
            preco_movel=_money(preco_movel),
            total_componentes=_money(total_componentes),
            total_item=_money(total_item),
        )

        for comp_idx, comp in enumerate(getattr(config, "componentes", []), start=1):
            item.componentes.append(
                OrcamentoItemComponente(
                    ordem=comp_idx,
                    nome=str(getattr(comp, "nome", "")),
                    categoria_funcional=str(getattr(comp, "categoria_funcional", "")),
                    quantidade=int(getattr(comp, "quantidade", 1) or 1),
                    preco_unitario=_money(float(getattr(comp, "preco_unitario", 0) or 0)),
                    subtotal=_money(float(comp.total())),
                    material=getattr(comp, "material", None),
                    cor=getattr(comp, "cor", None),
                )
            )

        orcamento.itens.append(item)

    orcamento.total = _money(total_geral)

    db.add(orcamento)
    db.commit()
    db.refresh(orcamento)
    return orcamento


def get_latest_orcamento_by_session_id(db: Session, session_id: str) -> Orcamento | None:
    stmt = (
        select(Orcamento)
        .options(selectinload(Orcamento.itens).selectinload(OrcamentoItem.componentes))
        .where(Orcamento.session_id == session_id)
        .order_by(Orcamento.created_at.desc())
    )
    return db.scalars(stmt).first()
