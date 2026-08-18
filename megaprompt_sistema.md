# MEGAPROMPT MAESTRO DE ARQUITECTURA SISTÉMICA E INTELIGENCIA FISCAL 10/10
## Ecosistema de Predicción, Intuición y Gestión Tributaria para Recursos Humanos SL

### 1. Manifiesto y Visión Sistémica
El presente documento constituye el marco rector absoluto para el desarrollo, evolución y ejecución del sistema **RH Fiscal Pro (Ecosistema 10/10)**. La misión central es trascender la simple automatización contable para instaurar un motor cognitivo de intuición fiscal y predicción de entornos macroeconómicos y tributarios en España (2024-2030). El sistema está diseñado específicamente para la entidad **Recursos Humanos De la empresa SL**, abarcando con precisión quirúrgica las tres modalidades jurídicas fundamentales: Sociedad Limitada (SL), Autónomo (Persona Física) y Cooperativa de Trabajo Asociado.

La arquitectura se fundamenta en los siguientes pilares axiomáticos:
*   **Intuición Sistémica Proactiva:** Capacidad del software para anticipar desviaciones fiscales, sugerir optimizaciones de deducciones y alertar sobre cambios normativos (como la implantación progresiva de Verifactu y los tramos de cotización RETA).
*   **Estética de Vanguardia (Glassmorphic Apple Gray):** Interfaz visual inmersiva que simula profundidad y cristal esmerilado, priorizando la claridad cognitiva, la jerarquía tipográfica estricta y una experiencia de usuario sobria y elegante.
*   **Ingeniería de Código Impecable:** Modularidad estricta, tipado riguroso, manejo defensivo de excepciones, trazabilidad de logs y arquitectura desacoplada entre la lógica de negocio (`logic`), la interfaz de usuario (`ui`), la persistencia (`data`) y la generativa documental (`templates`).

---

### 2. Taxonomía Normativa y Reglas de Negocio (2026)

#### A. Régimen Sociedad Limitada (SL)
*   **IVA (Impuesto sobre el Valor Añadido):** Tipo general del 21% aplicable sobre facturación de servicios de consultoría y recursos humanos. Liquidación trimestral (Modelo 303) y anual (Modelo 390).
*   **Impuesto de Sociedades (IS):** 
    *   Tipo general: 25%.
    *   Tipo reducido para entidades de nueva creación (primeros dos ejercicios con base positiva): 15%.
    *   Tipo reducido para PYMES con cifra de negocio inferior a 1 millón de euros: 23% (proyectando descensos al 22% en ejercicios subsiguientes).
*   **Retenciones y Pagos Fraccionados:** Modelo 115 (alquileres al 19%) y Modelo 202 (pagos fraccionados a cuenta del IS).

#### B. Régimen Autónomo (Persona Física)
*   **IRPF (Estimación Directa Simplificada):** Acumulación de rendimientos netos de actividades económicas y rendimientos del trabajo (pluriactividad). Aplicación de los tramos progresivos oficiales:
    *   Hasta 12.450 €: 19%
    *   12.450 € a 20.200 €: 24%
    *   20.200 € a 35.200 €: 30%
    *   35.200 € a 60.000 €: 37%
    *   60.000 € a 300.000 €: 45%
    *   Más de 300.000 €: 47%
*   **Gastos de Difícil Justificación:** Deducción automática del 7% sobre el rendimiento neto previo, con un límite legal de 2.000 € anuales.
*   **Sistema de Cotización RETA (Ingresos Reales):** Tramos dinámicos que oscilan desde cuotas mínimas para rendimientos inferiores a 670 €/mes hasta más de 590 €/mes para rentas superiores. Incorporación de bonificaciones por pluriactividad y tarifa plana inicial (87,6 €/mes).

#### C. Régimen Cooperativa de Trabajo Asociado
*   **Tratamiento Fiscal Especial (Ley 20/1990):**
    *   Cooperativas Especialmente Protegidas: Tipo impositivo reducido del 10% en el Impuesto de Sociedades sobre resultados cooperativos.
    *   Cooperativas Protegidas: Tipo del 20%.
    *   Resultados extracooperativos: Tributación al tipo general de PYMES (23%).
    *   Bonificaciones del 95% en el Impuesto sobre Actividades Económicas (IAE) y exención en Actos Jurídicos Documentados.

---

### 3. Arquitectura del Motor Predictivo y de Intuición

El sistema incorpora un módulo denominado **CognitiveTaxEngine**, capaz de proyectar escenarios a 1, 3 y 5 años mediante el análisis de variables estocásticas y deterministas:
1.  **Simulación de Crecimiento Anual (Growth Vector):** Permite aplicar vectores de incremento porcentual sobre ingresos y gastos (`g ∈ [-50%, +200%]`).
2.  **Análisis de Sensibilidad Fiscal:** Evalúa automáticamente el punto de inflexión exacto en el que a un autónomo le resulta jurídicamente más rentable y fiscalmente optimizado transformarse en una Sociedad Limitada.
3.  **Matriz de Alertas Inteligentes:** El sistema emite diagnósticos automáticos en tiempo real (ej. *"Atención: Sus ingresos superan el umbral de pluriactividad, optimice sus deducciones familiares para mitigar la progresividad fría del IRPF"*).

---

### 4. Especificaciones de Implementación y Código Impecable

El código fuente se estructurará bajo los siguientes cánones de ingeniería de software:
*   **Principio de Responsabilidad Única (SRP):** Cada clase y módulo posee una única razón para cambiar.
*   **Inmutabilidad y Tipado:** Uso de anotaciones de tipos en Python (`typing`) y estructuras de datos limpias.
*   **Resiliencia ante Errores:** Bloques de control de excepciones robustos en la interfaz gráfica, previniendo cierres inesperados por entradas de usuario vacías o malformadas.
