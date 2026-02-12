from datetime import datetime
import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config.settings import ORCAMENTOS_DIR


def gerar_pdf_orcamento(moveis_configurados, session_id):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph(
        "ORCAMENTO - MOVEIS PLANEJADOS",
        ParagraphStyle(
            "title",
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName="Helvetica-Bold",
        ),
    )

    elements.append(title)
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    total_geral = 0
    for idx, config in enumerate(moveis_configurados, 1):
        elements.append(Paragraph(f"<b>{idx}. {config.nome_movel}</b>", styles["Heading3"]))
        elements.append(
            Paragraph(
                f"Dimensoes: {int(config.L_mm)} x {int(config.A_mm)} x {int(config.P_mm)} mm<br/>"
                f"Material: {config.material}<br/>"
                f"Cor: {config.cor}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 8))

        table_data = [["Componente", "Qtd", "Unitario", "Subtotal"]]
        for comp in config.componentes:
            subtotal = comp.quantidade * comp.preco_unitario
            table_data.append([comp.nome, str(comp.quantidade), f"R$ {comp.preco_unitario:.2f}", f"R$ {subtotal:.2f}"])

        table_data.append(["Preco base do movel", "-", "-", f"R$ {config.preco_atual:.2f}"])

        total_movel = config.total_geral()
        total_geral += total_movel
        table_data.append(["", "", "TOTAL:", f"R$ {total_movel:.2f}"])

        table = Table(table_data, colWidths=[7 * cm, 2 * cm, 3 * cm, 3 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>VALOR TOTAL DO ORCAMENTO: R$ {total_geral:.2f}</b>", styles["Heading2"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def salvar_pdf_local(moveis_configurados, session_id):
    Path(ORCAMENTOS_DIR).mkdir(parents=True, exist_ok=True)

    buffer = gerar_pdf_orcamento(moveis_configurados, session_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"orcamento_{session_id}_{timestamp}.pdf"
    filepath = Path(ORCAMENTOS_DIR) / filename

    with open(filepath, "wb") as f:
        f.write(buffer.getvalue())

    return filename
