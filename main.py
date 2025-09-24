#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from utils import (
    console, show_header, show_success, show_error, show_info, 
    create_menu_table, get_user_choice, confirm_action, clear_screen,
    log_action, Colors
)
from file_manager import APKFileManager
from validator import AndroidResourceValidator
from api_gemini import GeminiAndroidAssistant
from templates import AndroidTemplateGenerator
from rich.panel import Panel
from rich import print as rprint


class APKEditor:
    """Editor principal para APKs Android con IA"""
    
    def __init__(self):
        self.file_manager = APKFileManager()
        self.validator = AndroidResourceValidator()
        self.ai_assistant = GeminiAndroidAssistant()
        self.template_generator = AndroidTemplateGenerator()
        self.current_project = None
        
    def show_main_menu(self):
        """Muestra el menú principal"""
        clear_screen()
        show_header("APK Editor Pro con IA", "Editor profesional para aplicaciones Android descompiladas")
        
        options = {
            "1": "📁 Establecer proyecto APK",
            "2": "📋 Listar archivos",
            "3": "✏️  Editar archivo", 
            "4": "🤖 Consultar IA",
            "5": "✅ Validar recursos",
            "6": "🔧 Reconstruir APK",
            "7": "📝 Generar templates",
            "8": "📊 Ver historial",
            "9": "🗑️  Limpiar backups",
            "h": "❓ Ayuda",
            "q": "🚪 Salir"
        }
        
        table = create_menu_table(options, "Menú Principal")
        console.print(table)
        
        if self.current_project:
            console.print(f"\n[green]Proyecto actual:[/green] {self.current_project}")
        else:
            console.print(f"\n[yellow]No hay proyecto establecido[/yellow]")
            
    def run(self):
        """Ejecuta el loop principal de la aplicación"""
        log_action("app_start")
        show_success("APK Editor Pro iniciado correctamente")
        
        while True:
            try:
                self.show_main_menu()
                choice = get_user_choice("\nSelecciona una opción", 
                                       ["1", "2", "3", "4", "5", "6", "7", "8", "9", "h", "q"])
                
                if choice == "1":
                    self.setup_project()
                elif choice == "2":
                    self.list_files()
                elif choice == "3":
                    self.edit_file()
                elif choice == "4":
                    self.ai_consultation()
                elif choice == "5":
                    self.validate_resources()
                elif choice == "6":
                    self.rebuild_apk()
                elif choice == "7":
                    self.generate_templates()
                elif choice == "8":
                    self.show_history()
                elif choice == "9":
                    self.clean_backups()
                elif choice == "h":
                    self.show_help()
                elif choice == "q":
                    if confirm_action("¿Estás seguro de que quieres salir?"):
                        break
                        
                if choice != "q":
                    console.input("\nPresiona Enter para continuar...")
                    
            except KeyboardInterrupt:
                if confirm_action("\n¿Quieres salir de la aplicación?"):
                    break
            except Exception as e:
                show_error(f"Error inesperado: {str(e)}")
                log_action("error", {"error": str(e)})
                console.input("Presiona Enter para continuar...")
                
        show_success("¡Gracias por usar APK Editor Pro!")
        log_action("app_exit")
        
    def setup_project(self):
        """Configura un proyecto APK"""
        clear_screen()
        show_header("Configurar Proyecto APK")
        
        path = get_user_choice("Ingresa la ruta del APK descompilado")
        
        if self.file_manager.set_apk_path(path):
            self.current_project = path
            
            # Validar estructura
            validation = self.file_manager.validate_apk_structure()
            if validation["valid"]:
                show_success("Proyecto APK válido configurado")
            else:
                show_error("Estructura de APK con problemas:")
                for error in validation.get("errors", []):
                    console.print(f"  - {error}", style="red")
                    
    def list_files(self):
        """Lista archivos del proyecto"""
        if not self.current_project:
            show_error("No hay proyecto configurado")
            return
            
        clear_screen()
        show_header("Archivos del Proyecto")
        
        categories = ["all", "layouts", "values", "drawables", "manifests"]
        category = get_user_choice("Selecciona categoría", categories)
        
        table = self.file_manager.list_files(category)
        console.print(table)
        
    def edit_file(self):
        """Edita un archivo"""
        if not self.current_project:
            show_error("No hay proyecto configurado")
            return
            
        clear_screen()
        show_header("Editar Archivo")
        
        file_path = get_user_choice("Ingresa la ruta del archivo a editar")
        content = self.file_manager.read_file(file_path)
        
        if content is not None:
            console.print(Panel(content[:500] + "..." if len(content) > 500 else content, 
                              title="Contenido Actual"))
            
            new_content = console.input("Ingresa el nuevo contenido (Ctrl+D para terminar):\n")
            
            if confirm_action("¿Guardar cambios?"):
                if self.file_manager.write_file(file_path, new_content):
                    show_success("Archivo guardado correctamente")
                    
    def ai_consultation(self):
        """Menú de consultas IA"""
        if not self.ai_assistant.is_available():
            show_error("API de Gemini no está disponible")
            return
            
        clear_screen()
        show_header("Consulta a Gemini AI")
        
        ai_options = {
            "1": "Analizar layout",
            "2": "Sugerir mejoras",
            "3": "Corregir errores",
            "4": "Generar layout",
            "5": "Esquema de colores",
            "6": "Optimizar rendimiento",
            "7": "Explicar concepto"
        }
        
        table = create_menu_table(ai_options, "Opciones de IA")
        console.print(table)
        
        choice = get_user_choice("Selecciona opción", list(ai_options.keys()))
        
        if choice == "1":
            self.analyze_layout_with_ai()
        elif choice == "2":
            self.suggest_improvements_with_ai()
        # ... más opciones de IA
            
    def analyze_layout_with_ai(self):
        """Analiza layout con IA"""
        file_path = get_user_choice("Ruta del archivo layout")
        content = self.file_manager.read_file(file_path)
        
        if content:
            result = self.ai_assistant.analyze_layout(content, file_path)
            self.ai_assistant.show_ai_response(result)
            
    def validate_resources(self):
        """Valida recursos del proyecto"""
        if not self.current_project:
            show_error("No hay proyecto configurado")
            return
            
        clear_screen()
        show_header("Validación de Recursos")
        
        with console.status("Validando recursos..."):
            results = self.validator.validate_project_resources(self.current_project)
            
        self.validator.show_validation_report(results)
        
    def rebuild_apk(self):
        """Reconstruye el APK"""
        if not self.current_project:
            show_error("No hay proyecto configurado")
            return
            
        clear_screen()
        show_header("Reconstruir APK")
        
        console.print("Comandos para reconstruir APK:")
        console.print(f"[cyan]apktool b {self.current_project} -o output.apk[/cyan]")
        console.print("\nPara firmar el APK:")
        console.print("[cyan]jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore output.apk alias_name[/cyan]")
        
        if confirm_action("¿Ejecutar reconstrucción automáticamente?"):
            import subprocess
            try:
                result = subprocess.run(["apktool", "b", self.current_project, "-o", "output.apk"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    show_success("APK reconstruido exitosamente")
                else:
                    show_error(f"Error en reconstrucción: {result.stderr}")
            except FileNotFoundError:
                show_error("apktool no encontrado. Instálalo primero.")
                
    def generate_templates(self):
        """Genera templates"""
        clear_screen()
        show_header("Generar Templates")
        
        template_options = {
            "1": "Layout básico",
            "2": "Formulario de login", 
            "3": "Colores básicos",
            "4": "Strings básicos"
        }
        
        table = create_menu_table(template_options)
        console.print(table)
        
        choice = get_user_choice("Selecciona template", list(template_options.keys()))
        
        if choice == "1":
            template = self.template_generator.generate_basic_layout()
        elif choice == "2":
            template = self.template_generator.generate_login_form()
        elif choice == "3":
            template = self.template_generator.generate_basic_colors()
        elif choice == "4":
            template = self.template_generator.generate_basic_strings()
        else:
            return
            
        console.print(Panel(template, title="Template Generado"))
        
        if confirm_action("¿Guardar template en archivo?"):
            filename = get_user_choice("Nombre del archivo")
            if self.file_manager.write_file(filename, template):
                show_success(f"Template guardado en {filename}")
                
    def show_history(self):
        """Muestra historial"""
        clear_screen()
        show_header("Historial de Cambios")
        
        history = self.file_manager.get_file_history()
        if not history:
            show_info("No hay historial disponible")
            return
            
        for entry in history[-10:]:  # Últimas 10 entradas
            timestamp = entry.get("timestamp", "N/A")
            action = entry.get("action", "N/A")
            file_path = entry.get("file", "N/A")
            console.print(f"[yellow]{timestamp}[/yellow] - [cyan]{action}[/cyan] - {file_path}")
            
    def clean_backups(self):
        """Limpia backups antiguos"""
        clear_screen()
        show_header("Limpiar Backups")
        
        days = int(get_user_choice("Días de antigüedad para limpiar (30)", ["30", "7", "14", "60"]))
        cleaned = self.file_manager.clean_backups(days)
        
    def show_help(self):
        """Muestra ayuda"""
        clear_screen()
        show_header("Ayuda - APK Editor Pro")
        
        help_text = """
        🔧 Funcionalidades principales:
        
        1. Gestión de proyectos APK descompilados
        2. Editor de archivos con backup automático
        3. Validación de recursos XML Android
        4. Integración con Gemini AI para sugerencias
        5. Generación de templates básicos
        6. Reconstrucción y firma de APK
        7. Historial completo de cambios
        
        💡 Consejos de uso:
        - Siempre configura un proyecto antes de editar
        - La IA funciona mejor con descripciones específicas
        - Los backups se crean automáticamente al editar
        - Valida recursos antes de reconstruir el APK
        """
        
        console.print(Panel(help_text, border_style="green"))


if __name__ == "__main__":
    try:
        editor = APKEditor()
        editor.run()
    except KeyboardInterrupt:
        print("\n👋 Salida forzada del programa")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)