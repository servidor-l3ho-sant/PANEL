#!/usr/bin/env python3
"""
APK Editor Pro - Aplicación principal
Soporta tanto interfaz de terminal como interfaz web
"""
import sys
import threading
import time
from pathlib import Path

# Importar componentes
from main import APKEditor
from web_server import APKEditorWebApp
from utils import show_success, show_info, show_header, console


def run_terminal_mode():
    """Ejecuta la aplicación en modo terminal"""
    try:
        editor = APKEditor()
        editor.run()
    except Exception as e:
        print(f"Error en modo terminal: {e}")


def run_web_mode():
    """Ejecuta la aplicación en modo web"""
    try:
        web_app = APKEditorWebApp()
        show_info("Servidor web iniciado en http://0.0.0.0:5000")
        web_app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Error en modo web: {e}")


def run_both_modes():
    """Ejecuta ambos modos simultáneamente"""
    try:
        # Mostrar información inicial
        show_header("APK Editor Pro", "Iniciando en modo híbrido: Terminal + Web")
        
        show_info("🖥️  Interfaz de terminal: Disponible en esta ventana")
        show_info("🌐 Interfaz web: Disponible en http://0.0.0.0:5000")
        show_info("📱 Compatible con Termux y navegadores")
        
        # Iniciar servidor web en hilo separado
        web_thread = threading.Thread(target=run_web_mode, daemon=True)
        web_thread.start()
        
        # Esperar un momento para que el servidor web inicie
        time.sleep(2)
        show_success("Servidor web iniciado correctamente")
        
        # Ejecutar interfaz de terminal en hilo principal
        run_terminal_mode()
        
    except KeyboardInterrupt:
        show_info("Cerrando aplicación...")
    except Exception as e:
        print(f"Error en modo híbrido: {e}")


def main():
    """Función principal"""
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == '--web':
            run_web_mode()
        elif mode == '--terminal':
            run_terminal_mode()
        elif mode == '--help':
            print("""
APK Editor Pro - Editor profesional para aplicaciones Android

Modos de uso:
  python app.py            Modo híbrido (terminal + web)
  python app.py --web      Solo interfaz web
  python app.py --terminal Solo interfaz de terminal
  python app.py --help     Mostrar esta ayuda

Características:
  ✓ Edición de archivos APK descompilados
  ✓ Validación de recursos Android
  ✓ Integración con IA Gemini
  ✓ Gestión de repositorios GitHub
  ✓ Generación de templates
  ✓ Sistema de backups automático
  ✓ Compatible con Termux

Acceso web: http://0.0.0.0:5000 (cuando esté en modo web/híbrido)
            """)
        else:
            print(f"Modo desconocido: {mode}")
            print("Usa 'python app.py --help' para ver opciones disponibles")
    else:
        # Modo por defecto: ambos modos
        run_both_modes()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)