import os
import logging
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import track


console = Console()

# Configuración de logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "apk_editor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class Colors:
    """Constantes para colores usando Rich"""
    PRIMARY = "cyan"
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"
    INFO = "blue"
    ACCENT = "magenta"


def show_header(title: str, subtitle: str = ""):
    """Muestra un header profesional con título y subtítulo"""
    text = Text(title, style=f"bold {Colors.PRIMARY}")
    if subtitle:
        text.append(f"\n{subtitle}", style="dim")
    
    panel = Panel(
        text,
        border_style=Colors.PRIMARY,
        padding=(1, 2),
        expand=False
    )
    console.print(panel)


def show_success(message: str):
    """Muestra mensaje de éxito con formato profesional"""
    console.print(f"[{Colors.SUCCESS}]✓[/{Colors.SUCCESS}] {message}")


def show_error(message: str):
    """Muestra mensaje de error con formato profesional"""
    console.print(f"[{Colors.ERROR}]✗[/{Colors.ERROR}] {message}")


def show_warning(message: str):
    """Muestra mensaje de advertencia"""
    console.print(f"[{Colors.WARNING}]⚠[/{Colors.WARNING}] {message}")


def show_info(message: str):
    """Muestra mensaje informativo"""
    console.print(f"[{Colors.INFO}]ℹ[/{Colors.INFO}] {message}")


def create_menu_table(options: dict, title: str = "Menú Principal") -> Table:
    """Crea una tabla profesional para el menú"""
    table = Table(title=title, style=Colors.PRIMARY)
    table.add_column("Opción", style="bold", no_wrap=True)
    table.add_column("Descripción", style="dim")
    
    for key, desc in options.items():
        table.add_row(f"[{Colors.ACCENT}]{key}[/{Colors.ACCENT}]", desc)
    
    return table


def get_user_choice(prompt: str, choices: list = None) -> str:
    """Obtiene entrada del usuario con validación"""
    if choices:
        return Prompt.ask(
            f"[{Colors.PRIMARY}]{prompt}[/{Colors.PRIMARY}]",
            choices=choices,
            show_choices=True
        )
    return Prompt.ask(f"[{Colors.PRIMARY}]{prompt}[/{Colors.PRIMARY}]")


def confirm_action(message: str) -> bool:
    """Solicita confirmación del usuario"""
    return Confirm.ask(f"[{Colors.WARNING}]{message}[/{Colors.WARNING}]")


def log_action(action: str, details: dict = None):
    """Registra acciones en el log con contexto"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or {}
    }
    
    logger.info(f"Action: {action}")
    if details:
        logger.info(f"Details: {json.dumps(details, indent=2)}")
    
    # Guardar en archivo JSON para historial
    history_file = LOG_DIR / "action_history.json"
    history = []
    
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(log_entry)
    
    # Mantener solo los últimos 1000 registros
    if len(history) > 1000:
        history = history[-1000:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def show_progress(items, description="Procesando"):
    """Muestra barra de progreso para operaciones largas"""
    return track(items, description=description)


def format_file_size(size_bytes):
    """Formatea el tamaño de archivo legible"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names)-1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Trunca texto largo para mostrar en tablas"""
    if len(text) <= max_length:
        return text
    return f"{text[:max_length-3]}..."


def validate_path(path: str, must_exist: bool = True) -> bool:
    """Valida si una ruta es válida y existe si es requerido"""
    path_obj = Path(path)
    
    if must_exist and not path_obj.exists():
        return False
    
    # Verificar permisos de lectura
    try:
        if path_obj.exists() and path_obj.is_file():
            with open(path_obj, 'r'):
                pass
    except PermissionError:
        return False
    except:
        pass  # Archivo binario o no texto, pero existe
    
    return True


def clear_screen():
    """Limpia la pantalla de terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')


def show_separator():
    """Muestra una línea separadora"""
    console.print("─" * console.size.width, style="dim")


def display_code_snippet(code: str, language: str = "xml", title: str = "Código"):
    """Muestra fragmento de código con syntax highlighting"""
    from rich.syntax import Syntax
    
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    panel = Panel(syntax, title=title, border_style=Colors.INFO)
    console.print(panel)