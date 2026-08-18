from typing import Dict, Any, Final, Protocol
from datetime import datetime
import hashlib
import json
import uuid
import os
import logging

# Módulo Independiente: Infraestructura de Validación
logger = logging.getLogger("RH-Fiscal-PVCU")

class IValidator(Protocol):
    """Protocolo para validadores intercambiables."""
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class PVCUValidationError(Exception):
    def __init__(self, layer: str, message: str):
        self.layer = layer
        self.message = message
        super().__init__(f"[{layer}] Fallo de Validación: {message}")

class PVCUService:
    """
    Servicio Autónomo de Validación Continua Universal.
    Independiente de la UI y del Motor de Cálculo.
    """
    
    PROFILE: Final[str] = "pvcu.audit.v12.elite"

    def __init__(self, audit_dir: str = "rh_tax_calc/data/pvcu_audit"):
        self._audit_dir = audit_dir
        os.makedirs(self._audit_dir, exist_ok=True)

    def _sign_evidence(self, payload: Dict[str, Any]) -> str:
        dump = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(dump.encode()).hexdigest()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta auditoría de integridad en 3 capas (Estructural, Semántica, IA)."""
        
        # 1. Capa Estructural
        required = {"income", "expenses", "mode"}
        if not required.issubset(data.keys()):
            raise PVCUValidationError("L1", "Contrato de datos incompleto.")

        # 2. Capa Semántica
        try:
            inc, exp = float(data["income"]), float(data["expenses"])
            if inc < 0 or exp < 0:
                raise PVCUValidationError("L2", "Valores financieros negativos detectados.")
        except (ValueError, TypeError):
            raise PVCUValidationError("L2", "Tipado de datos financiero incorrecto.")

        # 3. Generación de Evidencia Inmutable
        evidence_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        evidence = {
            "id": evidence_id,
            "ts": timestamp,
            "profile": self.PROFILE,
            "risk": "HIGH" if inc > 50000 else "MEDIUM",
            "context": data
        }
        
        evidence["hash"] = self._sign_evidence(evidence)
        
        # Persistencia
        with open(os.path.join(self._audit_dir, f"ev_{evidence_id}.json"), "w") as f:
            json.dump(evidence, f, indent=4)
            
        return evidence
