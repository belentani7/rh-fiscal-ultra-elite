from typing import Dict, Any, Final, Protocol
from datetime import datetime
import hashlib
import json
import uuid
import os
import logging

logger = logging.getLogger("RH-Fiscal-PVCU")

class PVCUValidationError(Exception):
    def __init__(self, layer: str, message: str):
        self.layer = layer
        self.message = message
        super().__init__(f"[{layer}] Error de Validación: {message}")

class PVCUService:
    """Servicio de Validación Continua Universal (PVC-U)."""
    
    PROFILE: Final[str] = "pvcu.audit.v12.production"

    def __init__(self, audit_dir: str = "rh_tax_calc/data/pvcu_audit"):
        self._audit_dir = audit_dir
        os.makedirs(self._audit_dir, exist_ok=True)

    def _sign(self, payload: Dict[str, Any]) -> str:
        dump = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(dump.encode()).hexdigest()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Auditoría de integridad en capas estructural, semántica y lógica."""
        
        # Validación Estructural
        if not {"income", "expenses", "mode"}.issubset(data.keys()):
            raise PVCUValidationError("L1", "Contrato de datos incompleto.")

        # Validación Semántica
        try:
            inc, exp = float(data["income"]), float(data["expenses"])
            if inc < 0 or exp < 0:
                raise PVCUValidationError("L2", "Valores financieros negativos no permitidos.")
        except (ValueError, TypeError):
            raise PVCUValidationError("L2", "Formato de datos financieros incorrecto.")

        # Generación de Evidencia
        evidence_id = str(uuid.uuid4())
        evidence = {
            "id": evidence_id,
            "ts": datetime.now().isoformat(),
            "profile": self.PROFILE,
            "risk": "HIGH" if inc > 50000 else "MEDIUM",
            "context": data
        }
        evidence["hash"] = self._sign(evidence)
        
        # Persistencia
        with open(os.path.join(self._audit_dir, f"ev_{evidence_id}.json"), "w") as f:
            json.dump(evidence, f, indent=4)
            
        return evidence
