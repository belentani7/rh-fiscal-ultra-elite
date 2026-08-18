import customtkinter as ctk
from tkinter import messagebox
from logic.calculator import TaxEnginePro, TaxContext, TaxMode, TaxResult
from logic.reporter import AuditorReporter
from logic.pvcu_core import PVCUService, PVCUValidationError
import os
from datetime import datetime
from typing import Optional, Dict, Any

class RHAppUltra(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.engine = TaxEnginePro()
        self.pvcu = PVCUService()
        self.reporter = AuditorReporter()
        
        self.current_mode = TaxMode.SL
        self.last_result: Optional[TaxResult] = None
        self.last_evidence: Optional[Dict[str, Any]] = None
        
        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.title("RH FISCAL ULTRA - SISTEMA DE INTELIGENCIA")
        self.geometry("1300x950")
        self.configure(fg_color="#050505")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _build_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0d0d0d")
        self.sidebar.grid(row=0, column:0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="RH PRO", font=ctk.CTkFont(size=36, weight="bold"), text_color="#0a84ff").pack(pady=60)
        
        self.nav_btns = {}
        for mode in TaxMode:
            btn = ctk.CTkButton(self.sidebar, text=mode.value.replace("_", " "), 
                               command=lambda m=mode: self._on_nav(m),
                               fg_color="transparent", text_color="#636366", 
                               anchor="w", height=55, corner_radius=12)
            btn.pack(fill="x", padx=20, pady=5)
            self.nav_btns[mode] = btn

        self.canvas = ctk.CTkScrollableFrame(self, fg_color="transparent")
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
        
        ctk.CTkLabel(self.canvas, text=self.current_mode.value.replace("_", " "), 
                    font=ctk.CTkFont(size=34, weight="bold")).pack(anchor="w", pady=(0, 40))
        
        input_grid = ctk.CTkFrame(self.canvas, fg_color="#121212", corner_radius=30, border_width=1, border_color="#2c2c2e")
        input_grid.pack(fill="x", pady=10)
        
        self.inputs = {}
        fields = [("Ingresos Anuales (€)", "inc"), ("Gastos Operativos (€)", "exp"), ("Pasivos Totales (€)", "liab")]
        if self.current_mode == TaxMode.SL:
            fields += [("Activos Fijos (€)", "assets"), ("Dividendos (€)", "div")]
        else:
            fields += [("Rentas Trabajo (€)", "sal"), ("Deducciones (€)", "ded")]

        for label, key in fields:
            row = ctk.CTkFrame(input_grid, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=15)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
            entry = ctk.CTkEntry(row, width=280, height=40, corner_radius=12, fg_color="#1c1c1e")
            entry.pack(side="right")
            self.inputs[key] = entry

        ctk.CTkButton(self.canvas, text="GENERAR AUDITORÍA SISTÉMICA", 
                     command=self._run, fg_color="#0a84ff", height=65, corner_radius=20, 
                     font=ctk.CTkFont(size=17, weight="bold")).pack(fill="x", pady=40)

        self.monitor = ctk.CTkTextbox(self.canvas, fg_color="#121212", corner_radius=30, 
                                     border_width=1, border_color="#2c2c2e", 
                                     font=ctk.CTkFont(family="Consolas", size=15), height=350)
        self.monitor.pack(fill="both", expand=True)
        
        action_bar = ctk.CTkFrame(self.canvas, fg_color="transparent")
        action_bar.pack(fill="x", pady=30)
        ctk.CTkButton(action_bar, text="DESCARGAR PDF", command=lambda: self._export("pdf"), 
                     fg_color="#30d158", corner_radius=15, height=50, width=200).pack(side="right", padx=10)
        ctk.CTkButton(action_bar, text="EXPORTAR MD", command=lambda: self._export("md"), 
                     fg_color="#5856d6", corner_radius=15, height=50, width=200).pack(side="right", padx=10)

    def _run(self):
        try:
            raw = {k: float(v.get() or 0) for k, v in self.inputs.items()}
            raw.update({"mode": self.current_mode.value, "income": raw.get("inc", 0), "expenses": raw.get("exp", 0)})
            self.last_evidence = self.pvcu.validate(raw)
            ctx = TaxContext(
                income=raw["income"], expenses=raw["expenses"], liabilities=raw.get("liab", 0),
                assets_value=raw.get("assets", 0), dividend_payout=raw.get("div", 0),
                salary_other=raw.get("sal", 0), deductions=raw.get("ded", 0)
            )
            self.last_result = self.engine.run(self.current_mode, ctx)
            self._update_dash()
        except PVCUValidationError as e: messagebox.showwarning("Error PVC-U", str(e))
        except Exception as e: messagebox.showerror("Error", str(e))

    def _update_dash(self):
        res, ev = self.last_result, self.last_evidence
        out = f"--- CERTIFICACIÓN PVC-U ---\nID: {ev['id']}\nHASH: {ev['hash']}\n"
        out += "-"*40 + "\n"
        out += f"BASE IMPONIBLE:  {res.taxable_base:,.2f} €\nCARGA FISCAL:    {res.total_tax:,.2f} €\nTIPO EFECTIVO:   {res.effective_rate:.2f} %\n\n"
        out += f"MÉTRICAS ESTRATÉGICAS:\nCASH FLOW:       {res.cash_flow:,.2f} €\nSOLVENCIA:       {res.solvency_ratio:.2f}\nVALORACIÓN:      {res.estimated_valuation:,.2f} €\n"
        if res.alerts:
            out += "\nALERTAS:\n"
            for a in res.alerts: out += f" • {a}\n"
        self.monitor.delete("1.0", "end")
        self.monitor.insert("1.0", out)

    def _export(self, fmt):
        if not self.last_result: return
        path = f"rh_tax_calc/templates/audit_{datetime.now().strftime('%Y%m%d_%H%M')}.{fmt}"
        if fmt == "pdf": self.reporter.generate_pdf(self.last_result, self.last_evidence, path)
        else: self.reporter.generate_markdown(self.last_result, self.last_evidence, path)
        messagebox.showinfo("Éxito", f"Documento generado: {path}")

if __name__ == "__main__":
    app = RHAppUltra()
    app.mainloop()
