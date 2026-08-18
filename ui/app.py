import customtkinter as ctk
from tkinter import messagebox
from logic.calculator import TaxEnginePro, TaxContext, TaxMode, TaxResult
from logic.reporter import AuditorReporter
from logic.pvcu_core import PVCUService, PVCUValidationError
import os
from datetime import datetime
from typing import Optional, Dict, Any

class RHAppUltra(ctk.CTk):
    """Interfaz de Arquitectura Líquida: La Cúspide del Diseño Glassmorphism 2026."""
    
    def __init__(self):
        super().__init__()
        
        # Servicios Core
        self.engine = TaxEnginePro()
        self.pvcu = PVCUService()
        self.reporter = AuditorReporter()
        
        self.current_mode = TaxMode.SL
        self.last_result: Optional[TaxResult] = None
        self.last_evidence: Optional[Dict[str, Any]] = None
        
        self._setup_config()
        self._build_liquid_interface()

    def _setup_config(self):
        self.title("RH FISCAL ULTRA - LIQUID ARCHITECTURE")
        self.geometry("1300x950")
        self.configure(fg_color="#050505") # Negro profundo absoluto
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _build_liquid_interface(self):
        # 1. Sidebar con Proporción Áurea (Aprox 0.16 del ancho)
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0d0d0d", border_width=0)
        self.sidebar.grid(row=0, column:0, sticky="nsew")
        
        # Logo con Identidad 10/10
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(pady=(60, 50))
        ctk.CTkLabel(self.logo_frame, text="RH", font=ctk.CTkFont(size=36, weight="bold"), text_color="#0a84ff").pack(side="left")
        ctk.CTkLabel(self.logo_frame, text="ULTRA", font=ctk.CTkFont(size=36, weight="bold"), text_color="#ffffff").pack(side="left", padx=(5, 0))
        
        self.nav_btns = {}
        for mode in TaxMode:
            btn = ctk.CTkButton(self.sidebar, text=mode.value.replace("_", " "), 
                               command=lambda m=mode: self._on_nav(m),
                               fg_color="transparent", text_color="#636366", 
                               anchor="w", height=55, corner_radius=12,
                               font=ctk.CTkFont(family="SF Pro Text", size=15, weight="medium"))
            btn.pack(fill="x", padx=20, pady=4)
            self.nav_btns[mode] = btn

        # 2. Lienzo Principal (Canvas Líquido)
        self.canvas = ctk.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        self.canvas.grid(row=0, column:1, padx=50, pady=50, sticky="nsew")
        
        self._render_view()

    def _on_nav(self, mode: TaxMode):
        self.current_mode = mode
        for m, btn in self.nav_btns.items():
            active = (m == mode)
            btn.configure(fg_color="#1c1c1e" if active else "transparent", 
                          text_color="#ffffff" if active else "#636366")
        self._render_view()

    def _render_view(self):
        for w in self.canvas.winfo_children(): w.destroy()
        
        # Título de Sección con Medidas Áureas
        header_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 40))
        ctk.CTkLabel(header_frame, text=self.current_mode.value.replace("_", " "), 
                    font=ctk.CTkFont(size=34, weight="bold"), text_color="#ffffff").pack(side="left")
        
        # Panel de Inteligencia Financiera (Grid Líquido)
        input_grid = ctk.CTkFrame(self.canvas, fg_color="#121212", corner_radius=30, border_width=1, border_color="#2c2c2e")
        input_grid.pack(fill="x", pady=10)
        
        self.inputs = {}
        # Definición de campos con utilidades estratégicas
        fields = [
            ("Ingresos Anuales (€)", "inc", "Total facturación proyectada"),
            ("Gastos Operativos (€)", "exp", "Gastos deducibles directos"),
            ("Pasivos Totales (€)", "liab", "Deudas y obligaciones pendientes")
        ]
        
        if self.current_mode == TaxMode.SL:
            fields += [
                ("Activos Fijos (€)", "assets", "Maquinaria, inmuebles, tecnología"),
                ("Dividendos a Repartir (€)", "div", "Distribución de beneficios")
            ]
        else:
            fields += [
                ("Rentas del Trabajo (€)", "sal", "Ingresos por cuenta ajena"),
                ("Deducciones Familiares (€)", "ded", "Hijos, ascendientes, etc.")
            ]

        for label, key, hint in fields:
            row = ctk.CTkFrame(input_grid, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=15)
            
            lbl_box = ctk.CTkFrame(row, fg_color="transparent")
            lbl_box.pack(side="left")
            ctk.CTkLabel(lbl_box, text=label, font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").pack(anchor="w")
            ctk.CTkLabel(lbl_box, text=hint, font=ctk.CTkFont(size=11), text_color="#636366").pack(anchor="w")
            
            entry = ctk.CTkEntry(row, width=280, height=40, corner_radius=12, fg_color="#1c1c1e", border_color="#3a3a3c", font=ctk.CTkFont(size=15))
            entry.pack(side="right", pady=5)
            self.inputs[key] = entry

        # Botón de Ejecución con Micro-interacción Visual
        self.btn_run = ctk.CTkButton(self.canvas, text="GENERAR AUDITORÍA E INTELIGENCIA FISCAL", 
                                    command=self._run_analysis, fg_color="#0a84ff", hover_color="#007aff",
                                    height=65, corner_radius=20, font=ctk.CTkFont(size=17, weight="bold"))
        self.btn_run.pack(fill="x", pady=40)

        # Dashboard de Resultados (3 Columnas Gestalt)
        self.dash_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.dash_frame.pack(fill="x", pady=10)
        
        self.monitor = ctk.CTkTextbox(self.dash_frame, fg_color="#121212", corner_radius=30, 
                                     border_width=1, border_color="#2c2c2e", 
                                     font=ctk.CTkFont(family="JetBrains Mono", size=15), 
                                     text_color="#e5e5e7", height=350)
        self.monitor.pack(fill="both", expand=True)
        
        # Action Center (Cierre Gestalt)
        action_center = ctk.CTkFrame(self.canvas, fg_color="transparent")
        action_center.pack(fill="x", pady=30)
        ctk.CTkButton(action_center, text="DESCARGAR PDF CERTIFICADO", command=lambda: self._export("pdf"), 
                     fg_color="#30d158", text_color="#ffffff", corner_radius=15, height=50, width=250).pack(side="right", padx=10)
        ctk.CTkButton(action_center, text="ANÁLISIS ESTRATÉGICO MD", command=lambda: self._export("md"), 
                     fg_color="#5856d6", text_color="#ffffff", corner_radius=15, height=50, width=250).pack(side="right", padx=10)

    def _run_analysis(self):
        try:
            data = {k: float(v.get() or 0) for k, v in self.inputs.items()}
            data["mode"] = self.current_mode.value
            data["income"] = data.get("inc", 0)
            data["expenses"] = data.get("exp", 0)
            data["liabilities"] = data.get("liab", 0)
            
            # Validación Nuclear PVC-U
            self.last_evidence = self.pvcu.validate(data)
            
            # Motor Multidimensional
            ctx = TaxContext(
                income=data["income"],
                expenses=data["expenses"],
                liabilities=data["liabilities"],
                assets_value=data.get("assets", 0),
                dividend_payout=data.get("div", 0),
                salary_other=data.get("sal", 0),
                deductions=data.get("ded", 0)
            )
            
            self.last_result = self.engine.run(self.current_mode, ctx)
            self._update_dash()
            
        except PVCUValidationError as e:
            messagebox.showwarning("Fallo de Integridad", str(e))
        except Exception as e:
            messagebox.showerror("Error Sistémico", f"Fallo en la cadena de cálculo: {e}")

    def _update_dash(self):
        res, ev = self.last_result, self.last_evidence
        out = f"╔══════════════════════════════════════════════════════════╗\n"
        out += f"║ RH FISCAL ULTRA - CERTIFICACIÓN DE INTEGRIDAD v12.0 ║\n"
        out += f"╚══════════════════════════════════════════════════════════╝\n\n"
        out += f"🛡️ HASH EVIDENCIA: {ev['hash']}\n"
        out += f"🛡️ NIVEL DE RIESGO: {ev['risk']}\n"
        out += f"────────────────────────────────────────────────────────────\n"
        out += f"📊 MÉTRICAS TRIBUTARIAS:\n"
        out += f"   • Base Imponible:  {res.taxable_base:,.2f} €\n"
        out += f"   • Carga Fiscal:    {res.total_tax:,.2f} €\n"
        out += f"   • Tipo Efectivo:   {res.effective_rate:.2f} %\n\n"
        out += f"📈 INTELIGENCIA ESTRATÉGICA:\n"
        out += f"   • Cash Flow:       {res.cash_flow:,.2f} €\n"
        out += f"   • Ratio Solvencia: {res.solvency_ratio:.2f}\n"
        out += f"   • Valoración Est:  {res.estimated_valuation:,.2f} €\n\n"
        
        if res.alerts:
            out += f"⚡ ALERTAS DE INTUICIÓN FISCAL:\n"
            for a in res.alerts: out += f"   ! {a}\n"
            
        self.monitor.delete("1.0", "end")
        self.monitor.insert("1.0", out)

    def _export(self, fmt):
        if not self.last_result: return
        ts = datetime.now().strftime('%Y%m%d_%H%M')
        path = f"rh_tax_calc/templates/audit_{ts}.{fmt}"
        if fmt == "pdf": self.reporter.generate_pdf(self.last_result, self.last_evidence, path)
        else: self.reporter.generate_markdown(self.last_result, self.last_evidence, path)
        messagebox.showinfo("Éxito", f"Documento {fmt.upper()} generado en:\n{path}")

if __name__ == "__main__":
    app = RHAppUltra()
    app.mainloop()
