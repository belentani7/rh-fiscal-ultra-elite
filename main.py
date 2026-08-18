import sys
import os

# Añadir el directorio actual al path para importaciones locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.app import RHAppPro

if __name__ == "__main__":
    try:
        app = RHAppPro()
        print("Iniciando Ecosistema de Inteligencia Fiscal RH PRO 10/10...")
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
