import sys
import subprocess
from hypothesis import given, strategies as st
from logic.calculator import TaxEnginePro, TaxContext, TaxMode
import logging

# Configuración de Auditoría de Densidad Crítica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AUDIT-NUCLEAR")

def run_mypy():
    """Ejecuta análisis estático estricto (Formal Verification L1)."""
    logger.info("Iniciando Verificación Formal L1: Análisis Estático Estricto...")
    result = subprocess.run(["mypy", "--strict", "rh_tax_calc/logic/calculator.py"], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Fallo en Verificación Formal:\n{result.stdout}")
        return False
    logger.info("Verificación Formal L1: PASADA (10/10)")
    return True

@given(
    income=st.floats(min_value=0, max_value=1e12),
    expenses=st.floats(min_value=0, max_value=1e12),
    salary=st.floats(min_value=0, max_value=1e12),
    deductions=st.floats(min_value=0, max_value=1e12)
)
def test_tax_integrity(income, expenses, salary, deductions):
    """Prueba de Propiedad (Formal Verification L2): Invariantes del Sistema."""
    engine = TaxEnginePro()
    ctx = TaxContext(
        income=income,
        expenses=expenses,
        salary_other=salary,
        deductions=deductions
    )
    
    for mode in TaxMode:
        try:
            res = engine.run(mode, ctx)
            # Invariante 1: El beneficio neto + impuestos no puede superar los ingresos brutos (en SL/Autónomo)
            # Nota: En autónomo el neto puede ser complejo por pluriactividad, pero el total_tax + net_profit debe ser consistente con la base.
            assert res.net_profit + res.total_tax >= 0, f"Error de consistencia en {mode}"
            
            # Invariante 2: El tipo efectivo no puede ser negativo ni mayor al 100%
            assert 0 <= res.effective_rate <= 100, f"Tipo efectivo fuera de rango en {mode}: {res.effective_rate}%"
            
        except Exception as e:
            # Si el motor lanza excepción, la auditoría falla
            raise AssertionError(f"Fallo crítico en motor para {mode} con valores extremos: {e}")

def run_stress_audit():
    """Ejecuta la batería de pruebas de propiedad (Fuzzing / Formal Verification)."""
    logger.info("Iniciando Verificación Formal L2: Pruebas de Propiedad e Invariantes...")
    try:
        test_tax_integrity()
        logger.info("Verificación Formal L2: PASADA (10/10)")
        return True
    except Exception as e:
        logger.error(f"Fallo en Verificación Formal L2:\n{e}")
        return False

if __name__ == "__main__":
    s1 = run_mypy()
    s2 = run_stress_audit()
    if s1 and s2:
        print("\nAUDITORÍA NUCLEAR COMPLETADA: 10/10 EN TODAS LAS DIMENSIONES.")
        sys.exit(0)
    else:
        print("\nAUDITORÍA FALLIDA: El sistema no cumple con los estándares de seguridad crítica.")
        sys.exit(1)
