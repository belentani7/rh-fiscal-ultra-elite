from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Final
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RH-ULTRA-CORE")

class TaxMode(Enum):
    SL = "SOCIEDAD_LIMITADA"
    AUTONOMO = "AUTONOMO_PROFESIONAL"

@dataclass(frozen=True)
class TaxContext:
    income: float
    expenses: float
    salary_other: float = 0.0
    deductions: float = 0.0
    assets_value: float = 0.0
    liabilities: float = 0.0
    dividend_payout: float = 0.0
    is_pyme: bool = True
    is_new: bool = False

    def __post_init__(self) -> None:
        for f in ["income", "expenses", "salary_other", "deductions", "assets_value", "liabilities", "dividend_payout"]:
            if getattr(self, f) < 0:
                raise ValueError(f"El campo {f} no puede ser negativo.")

@dataclass(frozen=True)
class TaxResult:
    mode: TaxMode
    taxable_base: float
    total_tax: float
    net_profit: float
    effective_rate: float
    iva_result: float
    amortization: float = 0.0
    dividend_tax: float = 0.0
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
        cf = net_profit + amort
        solvency = (ctx.assets_value / ctx.liabilities) if ctx.liabilities > 0 else 10.0
        valuation = max(0.0, ebitda * 6.0)
        
        div_tax = 0.0
        if ctx.dividend_payout > 0:
            p = ctx.dividend_payout
            if p <= 6000: div_tax = p * 0.19
            elif p <= 50000: div_tax = 1140 + (p - 6000) * 0.21
            else: div_tax = 1140 + 9240 + (p - 50000) * 0.23
            
        alerts = []
        if solvency < 1.5: alerts.append("Alerta: Ratio de solvencia por debajo del umbral óptimo.")
        if cf < is_amount: alerts.append("Aviso: El flujo de caja es inferior a la carga fiscal proyectada.")

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
        tax, rem, prev = 0.0, total_base, 0.0
        for lim, rt in tramos:
            if rem > (lim - prev):
                tax += (lim - prev) * rt
                rem -= (lim - prev)
                prev = lim
            else:
                tax += rem * rt
                break
        
        irpf = max(0.0, tax - ctx.deductions)
        m = net_yield / 12
        if m <= 670: r = 200
        elif m <= 1700: r = 335
        elif m <= 3620: r = 465
        else: r = 590
        
        total_tax = irpf + (r * 12)
        valuation = max(0.0, net_yield * 3.0)
        
        eff_rate, alerts = 0.0, []
        if total_base > 0:
            eff_rate = (total_tax / total_base * 100.0)
            if eff_rate > 100:
                alerts.append("Alerta Crítica: Carga fiscal superior al 100% de la base imponible.")
                eff_rate = 100.0
        elif total_tax > 0:
            eff_rate = 100.0
            alerts.append("Alerta Crítica: Carga fiscal detectada sobre base nula o negativa.")

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
