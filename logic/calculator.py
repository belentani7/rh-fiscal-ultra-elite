from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Final
from enum import Enum
import logging

# Configuración de Logging de Grado Nuclear
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RH-ULTRA-CORE")

class TaxMode(Enum):
    SL = "SOCIEDAD_LIMITADA"
    AUTONOMO = "AUTONOMO_PROFESIONAL"

@dataclass(frozen=True)
class TaxContext:
    """Contexto Inmutable de Alta Precisión con Activos y Pasivos."""
    income: float
    expenses: float
    salary_other: float = 0.0
    deductions: float = 0.0
    assets_value: float = 0.0
    liabilities: float = 0.0 # Pasivos para ratios de solvencia
    dividend_payout: float = 0.0
    is_pyme: bool = True
    is_new: bool = False

    def __post_init__(self) -> None:
        for f in ["income", "expenses", "salary_other", "deductions", "assets_value", "liabilities", "dividend_payout"]:
            if getattr(self, f) < 0: raise ValueError(f"{f} no puede ser negativo.")

@dataclass(frozen=True)
class TaxResult:
    """Resultado Multidimensional 10/10."""
    mode: TaxMode
    taxable_base: float
    total_tax: float
    net_profit: float
    effective_rate: float
    iva_result: float
    amortization: float = 0.0
    dividend_tax: float = 0.0
    # Nuevas métricas estratégicas
    cash_flow: float = 0.0
    solvency_ratio: float = 0.0
    estimated_valuation: float = 0.0
    alerts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ITaxStrategy(ABC):
    @abstractmethod
    def calculate(self, ctx: TaxContext) -> TaxResult:
        pass

class SLStrategy(ITaxStrategy):
    def calculate(self, ctx: TaxContext) -> TaxResult:
        amort = ctx.assets_value * 0.12
        ebitda = ctx.income - ctx.expenses
        taxable_profit = max(0.0, ebitda - amort)
        
        rate = 0.15 if ctx.is_new else (0.23 if ctx.is_pyme else 0.25)
        is_amount = taxable_profit * rate
        net_profit = taxable_profit - is_amount
        
        # Cash Flow = Beneficio Neto + Amortizaciones
        cf = net_profit + amort
        
        # Solvencia = Activo / Pasivo (Simulado con Assets/Liabilities)
        solvency = (ctx.assets_value / ctx.liabilities) if ctx.liabilities > 0 else 10.0
        
        # Valoración Estimada (Múltiplo de EBITDA x6)
        valuation = max(0.0, ebitda * 6.0)
        
        div_tax = 0.0
        if ctx.dividend_payout > 0:
            payout = ctx.dividend_payout
            if payout <= 6000: div_tax = payout * 0.19
            elif payout <= 50000: div_tax = 1140 + (payout - 6000) * 0.21
            else: div_tax = 1140 + 9240 + (payout - 50000) * 0.23
            
        alerts = []
        if solvency < 1.5: alerts.append("CRÍTICO: Ratio de solvencia bajo (< 1.5).")
        if cf < is_amount: alerts.append("ADVERTENCIA: Flujo de caja insuficiente para cubrir impuestos.")

        return TaxResult(
            mode=TaxMode.SL,
            taxable_base=taxable_profit,
            total_tax=is_amount,
            net_profit=max(0.0, net_profit - ctx.dividend_payout),
            effective_rate=rate * 100,
            iva_result=(ctx.income - ctx.expenses) * 0.21,
            amortization=amort,
            dividend_tax=div_tax,
            cash_flow=cf,
            solvency_ratio=solvency,
            estimated_valuation=valuation,
            alerts=alerts
        )

class AutonomoStrategy(ITaxStrategy):
    def calculate(self, ctx: TaxContext) -> TaxResult:
        diff_exp = min(2000.0, (ctx.income - ctx.expenses) * 0.07)
        net_yield = max(0.0, ctx.income - ctx.expenses - diff_exp)
        total_base = net_yield + ctx.salary_other
        
        tramos = [(12450, 0.19), (20200, 0.24), (35200, 0.30), (60000, 0.37), (300000, 0.45), (float('inf'), 0.47)]
        tax = 0.0
        rem = total_base
        prev = 0.0
        for lim, rt in tramos:
            if rem > (lim - prev):
                tax += (lim - prev) * rt
                rem -= (lim - prev)
                prev = lim
            else:
                tax += rem * rt
                break
        
        irpf = max(0.0, tax - ctx.deductions)
        
        # RETA 2026
        m = net_yield / 12
        r = 200
        if m <= 670: r = 200
        elif m <= 1700: r = 335
        elif m <= 3620: r = 465
        else: r = 590
        
        total_tax = irpf + (r * 12)
        
        # Valoración Autónomo (Múltiplo de Rendimiento Neto x3)
        valuation = max(0.0, net_yield * 3.0)
        
        # Manejo de casos de rentabilidad negativa (Auditoría Nuclear)
        eff_rate = 0.0
        alerts = ["Análisis de viabilidad profesional completado."]
        if total_base > 0:
            eff_rate = (total_tax / total_base * 100.0)
            if eff_rate > 100:
                alerts.append("ALERTA CRÍTICA: La carga fiscal supera el 100% de los ingresos.")
                eff_rate = 100.0
        elif total_tax > 0:
            eff_rate = 100.0
            alerts.append("ALERTA CRÍTICA: Carga fiscal sobre base cero o negativa.")

        return TaxResult(
            mode=TaxMode.AUTONOMO,
            taxable_base=total_base,
            total_tax=total_tax,
            net_profit=max(0.0, total_base - total_tax),
            effective_rate=eff_rate,
            iva_result=(ctx.income - ctx.expenses) * 0.21,
            cash_flow=net_yield - total_tax,
            estimated_valuation=valuation,
            alerts=alerts
        )

class TaxEnginePro:
    def __init__(self) -> None:
        self._strategies = {TaxMode.SL: SLStrategy(), TaxMode.AUTONOMO: AutonomoStrategy()}

    def run(self, mode: TaxMode, ctx: TaxContext) -> TaxResult:
        strategy = self._strategies.get(mode)
        if not strategy: raise ValueError(f"Modo {mode} no soportado.")
        return strategy.calculate(ctx)
