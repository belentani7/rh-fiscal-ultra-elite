import customtkinter as ctk
from tkinter import messagebox
from logic.calculator import TaxEnginePro, TaxContext, TaxMode, TaxResult
from logic.reporter import AuditorReporter
from logic.pvcu_core import PVCUService, PVCUValidationError
import os
from datetime import datetime
from typing import Optional, Dict, Any

class RHAppUltra(ctk.CTk):
    """Interfaz de Ultra-Lujo: Estética Apple Glassmorphism Pro 10/10."""
    
    def __init__(self):
        super().__init__()
        
        # Inyección de Dependencias
        self.engine = TaxEnginePro()
        self.pvcu = PVCUService()
        self.reporter = AuditorReporter()
        
        self.current_mode = TaxMode.SL
        self.last_result: Optional[TaxResult] = None
        self.last_evidence: Optional[Dict[str, Any]] = None
        
        self._configure_window()
        self._draw_ultra_interface()

    def _configure_window(self):
        self.title("RH FISCAL PRO - ULTRA ECOSYSTEM")
        self.geometry("1280x900")
        self.configure(fg_color="#000000") # Fondo negro puro para resaltar el cristal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _draw_ultra_interface(self):
        # Sidebar Glassmorphism (Blur simulado con colores profundos)
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#0a0a0a")
        self.sidebar.grid(row=0, column:0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="RH PRO", font=ctk.CTkFont(family="SF Pro Display", size=28, weight="bold"), text_color="#ffffff")
        self.logo_label.pack(pady=(50, 40))
        
        self.nav_btns = {}
        for mode in TaxMode:
            btn = ctk.CTkButton(self.sidebar, text=mode.value.replace("_", " "), command=lambda m=mode: self._switch_mode(m),
                               fg_color="transparent", text_color="#8e8e93", anchor="w", height=50, font=ctk.CTkFont(size=14))
            btn.pack(fill="x", padx=25, pady=5)
            self.nav_btns[mode] = btn

        # Área de Contenido con efecto de Cristal Glacé
        self.main_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column:1, padx=40, pady=40, sticky="nsew")
        
        self._render_dynamic_content()

    def _switch_mode(self, mode: TaxMode):
        self.current_mode = mode
        for m, btn in self.nav_btns.items():
            is_active = (m == mode)
            btn.configure(fg_color="#1c1c1e" if is_active else "transparent", text_color="#ffffff" if is_active else "#8e8e93")
        self._render_dynamic_content()

    def _render_dynamic_content(self):
        for w in self.main_area.winfo_children(): w.destroy()
        
        # Header Pro
        header = ctk.CTkLabel(self.main_area, text=f"Auditoría Sistémica: {self.current_mode.value}", font=ctk.CTkFont(size=32, weight="bold"), text_color="#ffffff")
        header.pack(anchor="w", pady=(0, 30))

        # Panel de Datos (Cristal Glacé)
        self.data_card = ctk.CTkFrame(self.main_area, fg_color="#1c1c1e", corner_radius=25, border_width=1, border_color="#3a3a3c")
        self.data_card.pack(fill="x", pady=10)
        
        self.inputs = {}
        fields = [("Ingresos Anuales", "inc"), ("Gastos Deducibles", "exp")]
        if self.current_mode == TaxMode.SL:
            fields += [("Valor de Activos", "assets"), ("Dividendos", "div")]
        elif self.current_mode == TaxMode.AUTONOMO:
            fields += [("Pluriactividad", "sal"), ("Deducciones", "ded")]

        for label, key in fields:
            row = ctk.CTkFrame(self.data_card, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=12)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=14), text_color="#a1a1a6").pack(side="left")
            entry = ctk.CTkEntry(row, width=250, height=35, corner_radius=10, fg_color="#2c2c2e", border_color="#3a3a3c")
            entry.pack(side="right")
            self.inputs[key] = entry

        # Botón de Acción Elite
        self.exec_btn = ctk.CTkButton(self.main_area, text="EJECUTAR INTELIGENCIA FISCAL", command=self._execute_analysis,
                                     fg_color="#007aff", hover_color="#005bb5", height=60, corner_radius=15, font=ctk.CTkFont(size=16, weight="bold"))
        self.exec_btn.pack(fill="x", pady=30)

        # Monitor de Resultados
        self.monitor_card = ctk.CTkFrame(self.main_area, fg_color="#1c1c1e", corner_radius=25, border_width=1, border_color="#3a3a3c")
        self.monitor_card.pack(fill="both", expand=True, pady=10)
        
        self.monitor_text = ctk.CTkTextbox(self.monitor_card, fg_color="transparent", font=ctk.CTkFont(family="Consolas", size=15), text_color="#e5e5e7")
        self.monitor_text.pack(padx=30, pady=30, fill="both", expand=True)
        
        # Barra de Exportación de Lujo
        export_bar = ctk.CTkFrame(self.monitor_card, fg_color="transparent")
        export_bar.pack(fill="x", padx=30, pady=(0, 30))
        ctk.CTkButton(export_bar, text="EXPORTAR AUDITORÍA PDF", command=self._export_audit, fg_color="#ff9500", corner_radius=10, width=220).pack(side="right", padx=10)

    def _execute_analysis(self):
        try:
            raw = {k: float(v.get() or 0) for k, v in self.inputs.items()}
            raw["mode"] = self.current_mode.value
            raw["income"] = raw.get("inc", 0)
            raw["expenses"] = raw.get("exp", 0)
            
            # Validación PVC-U (Garantía de Integridad)
            self.last_evidence = self.pvcu.validate(raw)
            
            # Ejecución de Motor Pro
            ctx = TaxContext(
                income=raw["income"],
                expenses=raw["expenses"],
                assets_value=raw.get("assets", 0),
                dividend_payout=raw.get("div", 0),
                salary_other=raw.get("sal", 0),
                deductions=raw.get("ded", 0)
            )
            
            self.last_result = self.engine.run(self.current_mode, ctx)
            self._update_monitor()
            
        except PVCUValidationError as e:
            messagebox.showwarning("PVC-U Integrity Alert", str(e))
        except Exception as e:
            messagebox.showerror("System Error", f"Fallo Crítico: {e}")

    def _update_monitor(self):
        res, ev = self.last_result, self.last_evidence
        output = f"╔══════════════════════════════════════════════════════════╗\n"
        output += f"║ CERTIFICACIÓN DE INTEGRIDAD PVC-U v12.0 ║\n"
        output += f"╚══════════════════════════════════════════════════════════╝\n\n"
        output += f"🛡️ EVIDENCIA ID: {ev['id'][:12]}...\n"
        output += f"🛡️ HASH: {ev['hash'][:24]}...\n"
        output += f"🛡️ RIESGO: {ev['risk']}\n"
        output += f"────────────────────────────────────────────────────────────\n"
        output += f"➤ BASE IMPONIBLE: {res.taxable_base:,.2f} €\n"
        output += f"➤ IMPUESTOS:      {res.total_tax:,.2f} €\n"
        output += f"➤ BENEFICIO NETO: {res.net_profit:,.2f} €\n"
        output += f"➤ TIPO EFECTIVO:  {res.effective_rate:.2f} %\n"
        
        if res.alerts:
            output += f"\n⚡ ALERTAS DE INTUICIÓN FISCAL:\n"
            for a in res.alerts: output += f"  • {a}\n"
            
        self.monitor_text.delete("1.0", "end")
        self.monitor_text.insert("1.0", output)

    def _export_audit(self):
        if not self.last_result: return
        path = f"rh_tax_calc/templates/audit_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        self.reporter.generate_pdf(self.last_result, self.last_evidence, path)
        messagebox.showinfo("Exportación Exitosa", f"Auditoría de alta fidelidad generada en:\n{path}")

if __name__ == "__main__":
    app = RHAppUltra()
    app.mainloop()
