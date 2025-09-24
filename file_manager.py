import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from utils import (
    console, show_success, show_error, show_warning, show_info, 
    log_action, Colors, create_menu_table, confirm_action, 
    format_file_size, truncate_text, validate_path
)
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint


class APKFileManager:
    """Gestor de archivos para proyectos APK descompilados"""
    
    def __init__(self, apk_path: str = ""):
        self.apk_path = Path(apk_path) if apk_path else None
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.history_file = Path("file_history.json")
        
    def set_apk_path(self, path: str) -> bool:
        """Establece la ruta del proyecto APK descompilado"""
        apk_path = Path(path)
        
        if not apk_path.exists():
            show_error(f"La ruta {path} no existe")
            return False
            
        # Verificar estructura básica de APK descompilado
        required_dirs = ["res"]
        if not all((apk_path / dir_name).exists() for dir_name in required_dirs):
            show_warning(f"La ruta {path} no parece ser un APK descompilado válido")
            if not confirm_action("¿Continuar de todas formas?"):
                return False
                
        self.apk_path = apk_path
        show_success(f"Proyecto APK establecido: {path}")
        log_action("set_apk_path", {"path": str(path)})
        return True
        
    def get_apk_structure(self) -> Dict[str, List[Path]]:
        """Obtiene la estructura de directorios del APK"""
        if not self.apk_path:
            return {}
            
        structure = {
            "layouts": [],
            "values": [],
            "drawables": [],
            "manifests": [],
            "java": [],
            "kotlin": [],
            "other": []
        }
        
        try:
            # Layouts
            layout_dir = self.apk_path / "res" / "layout"
            if layout_dir.exists():
                structure["layouts"] = list(layout_dir.glob("*.xml"))
                
            # Values (strings, colors, styles, etc.)
            values_dir = self.apk_path / "res" / "values"
            if values_dir.exists():
                structure["values"] = list(values_dir.glob("*.xml"))
                
            # Drawables
            for drawable_type in ["drawable", "drawable-hdpi", "drawable-xhdpi", "drawable-xxhdpi"]:
                drawable_dir = self.apk_path / "res" / drawable_type
                if drawable_dir.exists():
                    structure["drawables"].extend(list(drawable_dir.glob("*")))
                    
            # AndroidManifest
            manifest = self.apk_path / "AndroidManifest.xml"
            if manifest.exists():
                structure["manifests"] = [manifest]
                
            # Java/Kotlin (en smali)
            smali_dir = self.apk_path / "smali"
            if smali_dir.exists():
                structure["java"] = list(smali_dir.rglob("*.smali"))
                
        except Exception as e:
            show_error(f"Error al obtener estructura: {str(e)}")
            log_action("error_get_structure", {"error": str(e)})
            
        return structure
        
    def list_files(self, category: str = "all") -> Table:
        """Lista archivos de una categoría específica"""
        if not self.apk_path:
            show_error("No se ha establecido una ruta de proyecto APK")
            return Table()
            
        structure = self.get_apk_structure()
        table = Table(title=f"Archivos - {category.title()}")
        table.add_column("Archivo", style="cyan")
        table.add_column("Tamaño", justify="right", style="green")
        table.add_column("Modificado", style="yellow")
        table.add_column("Tipo", style="magenta")
        
        files_to_show = []
        
        if category == "all":
            for cat_files in structure.values():
                files_to_show.extend(cat_files)
        elif category in structure:
            files_to_show = structure[category]
        else:
            show_warning(f"Categoría '{category}' no reconocida")
            return table
            
        for file_path in files_to_show:
            try:
                stat = file_path.stat()
                size = format_file_size(stat.st_size)
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                file_type = file_path.suffix or "Sin extensión"
                
                table.add_row(
                    truncate_text(file_path.name, 40),
                    size,
                    modified,
                    file_type
                )
            except Exception as e:
                table.add_row(file_path.name, "Error", "Error", "Error")
                
        return table
        
    def read_file(self, file_path: str) -> Optional[str]:
        """Lee el contenido de un archivo"""
        try:
            full_path = self.apk_path / file_path if self.apk_path else Path(file_path)
            
            if not full_path.exists():
                show_error(f"Archivo no encontrado: {file_path}")
                return None
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            log_action("read_file", {"file": str(full_path), "size": len(content)})
            return content
            
        except UnicodeDecodeError:
            show_error(f"Error de codificación al leer {file_path}")
            return None
        except Exception as e:
            show_error(f"Error al leer archivo: {str(e)}")
            return None
            
    def write_file(self, file_path: str, content: str, create_backup: bool = True) -> bool:
        """Escribe contenido a un archivo con backup automático"""
        try:
            full_path = self.apk_path / file_path if self.apk_path else Path(file_path)
            
            # Crear backup si el archivo existe
            if create_backup and full_path.exists():
                if not self.create_backup(str(full_path)):
                    if not confirm_action("No se pudo crear backup. ¿Continuar sin backup?"):
                        return False
                        
            # Crear directorio si no existe
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            show_success(f"Archivo guardado: {file_path}")
            log_action("write_file", {"file": str(full_path), "size": len(content)})
            
            # Actualizar historial
            self._add_to_history("write", str(full_path), len(content))
            return True
            
        except Exception as e:
            show_error(f"Error al escribir archivo: {str(e)}")
            log_action("error_write_file", {"file": file_path, "error": str(e)})
            return False
            
    def create_backup(self, file_path: str) -> bool:
        """Crea backup de un archivo específico"""
        try:
            source = Path(file_path)
            if not source.exists():
                show_warning(f"Archivo no existe para backup: {file_path}")
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.stem}_{timestamp}{source.suffix}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(source, backup_path)
            show_info(f"Backup creado: {backup_name}")
            log_action("create_backup", {"source": str(source), "backup": str(backup_path)})
            return True
            
        except Exception as e:
            show_error(f"Error al crear backup: {str(e)}")
            return False
            
    def restore_backup(self, backup_file: str, target_path: str) -> bool:
        """Restaura un archivo desde backup"""
        try:
            backup_path = self.backup_dir / backup_file
            target = self.apk_path / target_path if self.apk_path else Path(target_path)
            
            if not backup_path.exists():
                show_error(f"Backup no encontrado: {backup_file}")
                return False
                
            # Crear backup del archivo actual antes de restaurar
            if target.exists():
                self.create_backup(str(target))
                
            shutil.copy2(backup_path, target)
            show_success(f"Archivo restaurado desde backup: {backup_file}")
            log_action("restore_backup", {"backup": backup_file, "target": str(target)})
            
            self._add_to_history("restore", str(target))
            return True
            
        except Exception as e:
            show_error(f"Error al restaurar backup: {str(e)}")
            return False
            
    def list_backups(self) -> Table:
        """Lista todos los backups disponibles"""
        table = Table(title="Backups Disponibles")
        table.add_column("Archivo", style="cyan")
        table.add_column("Tamaño", justify="right", style="green")
        table.add_column("Creado", style="yellow")
        
        try:
            backups = list(self.backup_dir.glob("*"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for backup in backups:
                stat = backup.stat()
                size = format_file_size(stat.st_size)
                created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M")
                
                table.add_row(backup.name, size, created)
                
        except Exception as e:
            show_error(f"Error al listar backups: {str(e)}")
            
        return table
        
    def get_file_history(self) -> List[Dict]:
        """Obtiene el historial de cambios de archivos"""
        try:
            if not self.history_file.exists():
                return []
                
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            show_error(f"Error al leer historial: {str(e)}")
            return []
            
    def _add_to_history(self, action: str, file_path: str, size: int = 0):
        """Añade entrada al historial de archivos"""
        try:
            history = self.get_file_history()
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "file": file_path,
                "size": size
            }
            
            history.append(entry)
            
            # Mantener solo los últimos 500 registros
            if len(history) > 500:
                history = history[-500:]
                
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            show_error(f"Error al actualizar historial: {str(e)}")
            
    def clean_backups(self, days_old: int = 30) -> int:
        """Limpia backups antiguos"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            cleaned = 0
            
            for backup in self.backup_dir.glob("*"):
                if backup.stat().st_mtime < cutoff_time:
                    backup.unlink()
                    cleaned += 1
                    
            if cleaned > 0:
                show_success(f"Se eliminaron {cleaned} backups antiguos")
            else:
                show_info("No hay backups antiguos para limpiar")
                
            log_action("clean_backups", {"days_old": days_old, "cleaned": cleaned})
            return cleaned
            
        except Exception as e:
            show_error(f"Error al limpiar backups: {str(e)}")
            return 0
            
    def validate_apk_structure(self) -> Dict[str, bool]:
        """Valida la estructura básica del APK"""
        if not self.apk_path:
            return {"valid": False, "error": "No se ha establecido ruta de APK"}
            
        results = {
            "valid": True,
            "has_manifest": False,
            "has_resources": False,
            "has_layouts": False,
            "errors": []
        }
        
        try:
            # Verificar AndroidManifest.xml
            manifest = self.apk_path / "AndroidManifest.xml"
            results["has_manifest"] = manifest.exists()
            
            # Verificar carpeta res
            res_dir = self.apk_path / "res"
            results["has_resources"] = res_dir.exists()
            
            # Verificar layouts
            layout_dir = self.apk_path / "res" / "layout"
            results["has_layouts"] = layout_dir.exists()
            
            if not results["has_manifest"]:
                results["errors"].append("AndroidManifest.xml no encontrado")
                results["valid"] = False
                
            if not results["has_resources"]:
                results["errors"].append("Carpeta res/ no encontrada")
                results["valid"] = False
                
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Error de validación: {str(e)}")
            
        return results