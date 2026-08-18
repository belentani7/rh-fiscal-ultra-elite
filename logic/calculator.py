from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Final, Type
from enum import Enum
import logging

# Configuración de Logging de Grado Nuclear
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RH-NUCLEAR-CORE")

class TaxMode(Enum):
    SL = "SOCIEDAD_LIMITADA"
    AUTONOMO = "AUTONOMO_PROFESIONAL"

@dataclass(frozen=True)
class TaxContext:
    """Contexto Inmutable con Validación de Límites (Boundary Checks)."""
    income: float
    expenses: float
    salary_other: float = 0.0
    deductions: float = 0.0
    assets_value: float = 0.0
    dividend_payout: float = 0.0
    is_pyme: bool = True
    is_new: bool = False

    def __post_init__(self) -> None:
        """Validación de Invariantes de Entrada (Principio de Defensa en Profundidad)."""
        for field_name in ["income", "expenses", "salary_other", "deductions", "assets_value", "dividend_payout"]:
            val = getattr(self, field_name)
            if val < 0:
                raise ValueError(f"Atributo {field_name} no puede ser negativo.")
            if val > 1e15: # Límite de seguridad para evitar desbordamientos numéricos
                raise ValueError(f"Atributo {field_name} excede el límite de seguridad sistémica.")

@dataclass(frozen=True)
class TaxResult:
    """Entidad de Resultado Auditada con Precisión Decimal."""
    mode: TaxMode
    taxable_base: float
    total_tax: float
    net_profit: float
    effective_rate: float
    iva_result: float
    amortization: float = 0.0
    dividend_tax: float = 0.0
    alerts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ITaxStrategy(ABC):
    @abstractmethod
    def calculate(self, ctx: TaxContext) -> TaxResult:
        pass

class SLStrategy(ITaxStrategy):
    def calculate(self, ctx: TaxContext) -> TaxResult:
        amortization: float = ctx.assets_value * 0.12
        profit_pre: float = ctx.income - ctx.expenses
        taxable_profit: float = max(0.0, profit_pre - amortization)
        
        rate: float = 0.15 if ctx.is_new else (0.23 if ctx.is_pyme else 0.25)
        is_amount: float = taxable_profit * rate
        net_after_is: float = taxable_profit - is_amount
        
        div_tax: float = 0.0
        if ctx.dividend_payout > 0:
            payout: float = ctx.dividend_payout
            if payout <= 6000: div_tax = payout * 0.19
            elif payout <= 50000: div_tax = 1140.0 + (payout - 6000.0) * 0.21
            else: div_tax = 1140.0 + 9240.0 + (payout - 50000.0) * 0.23
            
        return TaxResult(
            mode=TaxMode.SL,
            taxable_base=taxable_profit,
            total_tax=is_amount,
            net_profit=max(0.0, net_after_is - ctx.dividend_payout),
            effective_rate=rate * 100.0,
            iva_result=max(0.0, (ctx.income - ctx.expenses) * 0.21),
            amortization=amortization,
            dividend_tax=div_tax,
            alerts=["Cálculo SL validado bajo norma nuclear."]
        )

class AutonomoStrategy(ITaxStrategy):
    def calculate(self, ctx: TaxContext) -> TaxResult:
        diff_expenses: float = min(2000.0, max(0.0, (ctx.income - ctx.expenses) * 0.07))
        net_yield: float = max(0.0, ctx.income - ctx.expenses - diff_expenses)
        total_base: float = net_yield + ctx.salary_other
        
        tramos: List[tuple[float, float]] = [
            (12450.0, 0.19), (20200.0, 0.24), (35200.0, 0.30), 
            (60000.0, 0.37), (300000.0, 0.45), (float('inf'), 0.47)
        ]
        
        tax: float = 0.0
        rem: float = total_base
        prev: float = 0.0
        for lim, rt in tramos:
            if rem > (lim - prev):
                tax += (lim - prev) * rt
                rem -= (lim - prev)
                prev = lim
            else:
                tax += rem * rt
                rem = 0.0
                break
        
        irpf: float = max(0.0, tax - ctx.deductions)
        
        m: float = net_yield / 12.0
        r: float = 200.0
        if m <= 670.0: r = 200.0
        elif m <= 1700.0: r = 335.0
        elif m <= 3620.0: r = 465.0
        else: r = 590.0
        
        if ctx.salary_other > 0: r *= 0.85
        
        total_tax: float = irpf + (r * 12.0)
        
        # Manejo de casos de rentabilidad negativa (Auditoría Nuclear)
        eff_rate: float = 0.0
        alerts: List[str] = []
        if total_base > 0:
            eff_rate = (total_tax / total_base * 100.0)
            if eff_rate > 100:
                alerts.append("ALERTA CRÍTICA: La carga fiscal supera el 100% de los ingresos (Inviabilidad).")
                eff_rate = 100.0 # Cap para visualización en auditoría
        
        return TaxResult(
            mode=TaxMode.AUTONOMO,
            taxable_base=total_base,
            total_tax=total_tax,
            net_profit=max(0.0, total_base - total_tax),
            effective_rate=eff_rate,
            iva_result=max(0.0, (ctx.income - ctx.expenses) * 0.21),
            alerts=alerts
        )

class TaxEnginePro:
    """Motor de Cálculo de Alta Integridad."""
    def __init__(self) -> None:
        self._strategies: Dict[TaxMode, ITaxStrategy] = {
            TaxMode.SL: SLStrategy(),
            TaxMode.AUTONOMO: AutonomoStrategy()
        }

    def run(self, mode: TaxMode, ctx: TaxContext) -> TaxResult:
        strategy = self._strategies.get(mode)
        if not strategy:
            raise ValueError(f"Estrategia {mode} no soportada.")
        return strategy.calculate(ctx)
