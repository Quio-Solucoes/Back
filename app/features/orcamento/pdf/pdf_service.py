from datetime import datetime
import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Image, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config.settings import ORCAMENTOS_DIR


def _brl(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _create_header_table() -> Table:
    logos_dir = Path(__file__).resolve().parent / "logos"
    boavista = logos_dir / "BV.png"
    quio = logos_dir / "quio.jpeg"

    left = "BOA VISTA"
    right = "QUIO"

    if boavista.exists():
        left_image = Image(str(boavista))
        left_image.drawHeight = 1.2 * cm
        left_image.drawWidth = 3.5 * cm
        left = left_image

    if quio.exists():
        right_image = Image(str(quio))
        right_image.drawHeight = 1.2 * cm
        right_image.drawWidth = 3.5 * cm
        right = right_image

    table = Table([[left, "", "", right]], colWidths=[7 * cm, 5 * cm, 3 * cm, 4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (3, 0), (3, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (0, 0), 10),
                ("RIGHTPADDING", (3, 0), (3, 0), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    return table


def _create_info_line(data_hora: str) -> Table:
    table = Table([[f"Data: {data_hora}", "", "Orcamento"]], colWidths=[10 * cm, 5 * cm, 4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ]
        )
    )
    return table


def _create_client_data_table() -> list[Table]:
    title = Table([["Dados do cliente:"]], colWidths=[19 * cm])
    title.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f0f0")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    client = Table(
        [
            ["Nome:", "OC:"],
            ["Endereco:", "CPF:"],
            ["Bairro:", "CEP:"],
            ["End. Entrega:", "UF:"],
            ["Telefone:", "Cidade:"],
            ["E-mail:", "Celular:"],
        ],
        colWidths=[9.5 * cm, 9.5 * cm],
    )
    client.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    return [title, client]


def _create_project_section(projeto_nome: str) -> Table:
    table = Table([[f"Projeto - {projeto_nome.upper()}"], ["- ACESSORIOS"]], colWidths=[19 * cm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (0, 0), 11),
                ("FONTSIZE", (0, 1), (0, 1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def _create_items_table(items: list[dict], show_peso: bool) -> Table:
    if show_peso:
        headers = ["Item", "Qtd", "Rep", "Peso", "Referencia", "Descricao", "Dimensoes", "Preco\nFinal"]
        col_widths = [1 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 2.5 * cm, 6 * cm, 3 * cm, 2.9 * cm]
    else:
        headers = ["Item", "Qtd", "Referencia", "Descricao", "Dimensoes", "Preco\nFinal"]
        col_widths = [1 * cm, 1.2 * cm, 2.5 * cm, 7.5 * cm, 4 * cm, 2.8 * cm]

    table_data = [headers]
    for item in items:
        if show_peso:
            row = [
                str(item.get("item", "")),
                item.get("qtd", "1 un"),
                "",
                item.get("peso", "0,000"),
                item.get("referencia", ""),
                item.get("descricao", ""),
                item.get("dimensoes", ""),
                item.get("preco", ""),
            ]
        else:
            row = [
                str(item.get("item", "")),
                item.get("qtd", "1 un"),
                item.get("referencia", ""),
                item.get("descricao", ""),
                item.get("dimensoes", ""),
                item.get("preco", ""),
            ]
        table_data.append(row)

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("ALIGN", (0, 1), (1, -1), "CENTER"),
                ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BOX", (0, 0), (-1, -1), 1, colors.grey),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _create_total_section(total_value: float) -> Table:
    table = Table(
        [["Total final:", "=" * 60, f"R$ {_brl(total_value)}"]],
        colWidths=[2.5 * cm, 13.5 * cm, 3 * cm],
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _create_footer_info() -> list[Table]:
    footer = Table([["TABELA DE PRECOS: BOA VISTA - TABELA LOJAS OFICIAL"]], colWidths=[19 * cm])
    footer.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    company = Table([["Razao social: | Endereco: | Telefone:"]], colWidths=[19 * cm])
    company.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    copyright_table = Table([["(c) Quio. Todos os direitos reservados."]], colWidths=[19 * cm])
    copyright_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    return [footer, company, copyright_table]


def gerar_pdf_orcamento(moveis_configurados, session_id):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
    )

    elements = []
    elements.append(_create_header_table())
    elements.append(Spacer(1, 0.3 * cm))

    data_hora = datetime.now().strftime("%d/%m/%Y    Hora: %H:%M:%S")
    elements.append(_create_info_line(data_hora))
    elements.append(Spacer(1, 0.3 * cm))

    for table in _create_client_data_table():
        elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))

    total_geral = 0.0
    for idx, config in enumerate(moveis_configurados, 1):
        elements.append(_create_project_section(config.nome_movel))
        elements.append(Spacer(1, 0.2 * cm))

        items: list[dict] = []
        item_counter = 1
        for comp in config.componentes:
            subtotal = comp.quantidade * comp.preco_unitario
            dim = ""
            if hasattr(comp, "largura") and hasattr(comp, "altura") and hasattr(comp, "profundidade"):
                dim = f"{int(comp.largura)} x {int(comp.altura)} x {int(comp.profundidade)}"

            items.append(
                {
                    "item": item_counter,
                    "qtd": f"{comp.quantidade} un",
                    "peso": "0,000",
                    "referencia": f"COMP{item_counter:03d}",
                    "descricao": comp.nome,
                    "dimensoes": dim,
                    "preco": _brl(subtotal),
                }
            )
            item_counter += 1

        elements.append(_create_items_table(items, show_peso=(idx == 1)))
        elements.append(Spacer(1, 0.5 * cm))
        total_geral += config.total_geral()

    elements.append(_create_total_section(total_geral))
    elements.append(Spacer(1, 0.5 * cm))

    for table in _create_footer_info():
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def salvar_pdf_local(moveis_configurados, session_id):
    Path(ORCAMENTOS_DIR).mkdir(parents=True, exist_ok=True)

    buffer = gerar_pdf_orcamento(moveis_configurados, session_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"orcamento_{session_id}_{timestamp}.pdf"
    filepath = Path(ORCAMENTOS_DIR) / filename

    with open(filepath, "wb") as output:
        output.write(buffer.getvalue())

    return filename
