from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from typing import Any, Dict
import os

class AuditorReporter:
    """Módulo de generación de auditorías documentales certificadas."""

    @staticmethod
    def generate_pdf(result: Any, evidence: Dict[str, Any], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        c = canvas.Canvas(output_path, pagesize=A4)
        w, h = A4
        
        c.setFillColor(colors.HexColor("#1c1c1e"))
        c.rect(0, h - 4*cm, w, 4*cm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(2*cm, h - 2*cm, "RH FISCAL PRO")
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, h - 2.8*cm, "INFORME DE AUDITORÍA Y CERTIFICACIÓN TRIBUTARIA")
        
        y = h - 5.5*cm
        c.setFillColor(colors.HexColor("#f2f2f7"))
        c.rect(1.5*cm, y - 2*cm, w - 3*cm, 2.5*cm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y, "CERTIFICADO DE INTEGRIDAD PVC-U:")
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, y - 0.5*cm, f"ID: {evidence['id']}")
        c.drawString(2*cm, y - 1*cm, f"HASH: {evidence['hash']}")
        
        y -= 3.5*cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, y, f"ANÁLISIS DE RESULTADOS: {result.mode.value}")
        c.line(2*cm, y - 0.2*cm, w - 2*cm, y - 0.2*cm)
        y -= 1.5*cm
        
        c.setFont("Helvetica", 12)
        fields = [
            ("Base Imponible", f"{result.taxable_base:,.2f} €"),
            ("Impuestos Totales", f"{result.total_tax:,.2f} €"),
            ("Beneficio Neto", f"{result.net_profit:,.2f} €"),
            ("Tipo Efectivo", f"{result.effective_rate:.2f} %"),
            ("Cash Flow", f"{result.cash_flow:,.2f} €"),
            ("Ratio de Solvencia", f"{result.solvency_ratio:.2f}"),
            ("Valoración Estimada", f"{result.estimated_valuation:,.2f} €")
        ]
        
        for label, val in fields:
            c.drawString(2.5*cm, y, f"{label}:")
            c.drawRightString(w - 2.5*cm, y, val)
            y -= 0.8*cm
            
        if result.alerts:
            y -= 0.5*cm
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2*cm, y, "ALERTAS DEL SISTEMA:")
            c.setFont("Helvetica-Oblique", 9)
            y -= 0.6*cm
            for alert in result.alerts:
                c.drawString(2.5*cm, y, f"• {alert}")
                y -= 0.5*cm
        c.save()

    @staticmethod
    def generate_markdown(result: Any, evidence: Dict[str, Any], output_path: str):
        content = f"# AUDITORÍA FISCAL RH PRO - {result.mode.value}\n\n"
        content += f"## CERTIFICACIÓN PVC-U\n"
        content += f"- **ID:** {evidence['id']}\n"
        content += f"- **Hash:** `{evidence['hash']}`\n"
        content += f"- **Fecha:** {evidence['ts']}\n\n"
        content += "## RESULTADOS FINANCIEROS\n"
        content += f"| Concepto | Valor |\n| :--- | :--- |\n"
        content += f"| Base Imponible | {result.taxable_base:,.2f} € |\n"
        content += f"| Impuestos Totales | {result.total_tax:,.2f} € |\n"
        content += f"| Beneficio Neto | {result.net_profit:,.2f} € |\n"
        content += f"| Tipo Efectivo | {result.effective_rate:.2f} % |\n"
        content += f"| Cash Flow | {result.cash_flow:,.2f} € |\n"
        content += f"| Ratio Solvencia | {result.solvency_ratio:.2f} |\n"
        content += f"| Valoración Estimada | {result.estimated_valuation:,.2f} € |\n\n"
        
        if result.alerts:
            content += "## ALERTAS\n"
            for alert in result.alerts: content += f"- {alert}\n"
        
        with open(output_path, "w") as f: f.write(content)
