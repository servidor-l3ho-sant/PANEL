import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from utils import (
    show_success, show_error, show_warning, show_info, 
    log_action, Colors, console
)
from rich.panel import Panel
from rich.table import Table


class AndroidResourceValidator:
    """Validador para recursos Android (XML, layouts, valores)"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_xml_file(self, file_path: str, content: str = None) -> Dict:
        """Valida un archivo XML individual"""
        self.errors.clear()
        self.warnings.clear()
        
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return {
                    "valid": False,
                    "errors": [f"No se pudo leer el archivo: {str(e)}"],
                    "warnings": []
                }
        
        # Validación básica de XML
        xml_valid = self._validate_xml_syntax(content)
        
        # Validaciones específicas por tipo de archivo
        file_path_obj = Path(file_path)
        if "layout" in str(file_path_obj.parent):
            self._validate_layout_file(content)
        elif "values" in str(file_path_obj.parent):
            self._validate_values_file(content, file_path_obj.name)
        elif file_path_obj.name == "AndroidManifest.xml":
            self._validate_manifest_file(content)
            
        return {
            "valid": xml_valid and len(self.errors) == 0,
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy()
        }
        
    def _validate_xml_syntax(self, content: str) -> bool:
        """Valida la sintaxis básica XML"""
        try:
            ET.fromstring(content)
            return True
        except ET.ParseError as e:
            self.errors.append(f"Error de sintaxis XML: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Error al procesar XML: {str(e)}")
            return False
            
    def _validate_layout_file(self, content: str):
        """Validaciones específicas para archivos de layout"""
        # Verificar ViewGroup roots válidos
        root_tags = ["LinearLayout", "RelativeLayout", "ConstraintLayout", 
                    "FrameLayout", "TableLayout", "ScrollView", "androidx.constraintlayout.widget.ConstraintLayout"]
        
        if not any(f"<{tag}" in content for tag in root_tags):
            self.warnings.append("Layout podría necesitar un ViewGroup root válido")
            
        # Verificar atributos comunes problemáticos
        if 'android:layout_width=""' in content or 'android:layout_height=""' in content:
            self.errors.append("Atributos layout_width o layout_height vacíos")
            
        # Verificar referencias a recursos
        self._validate_resource_references(content)
        
        # Verificar IDs duplicados
        self._validate_duplicate_ids(content)
        
    def _validate_values_file(self, content: str, filename: str):
        """Validaciones específicas para archivos values"""
        if filename == "strings.xml":
            self._validate_strings_file(content)
        elif filename == "colors.xml":
            self._validate_colors_file(content)
        elif filename == "styles.xml":
            self._validate_styles_file(content)
            
    def _validate_strings_file(self, content: str):
        """Valida archivo strings.xml"""
        # Verificar strings vacíos
        if re.search(r'<string[^>]*></string>', content):
            self.warnings.append("Se encontraron strings vacíos")
            
        # Verificar caracteres especiales sin escapar
        if re.search(r'[&<>](?![a-zA-Z]+;)', content):
            self.warnings.append("Posibles caracteres especiales sin escapar")
            
    def _validate_colors_file(self, content: str):
        """Valida archivo colors.xml"""
        # Verificar formato de colores hexadecimales
        color_matches = re.findall(r'<color[^>]*>(.*?)</color>', content)
        for color in color_matches:
            if not re.match(r'^#[0-9A-Fa-f]{3,8}$', color.strip()):
                self.errors.append(f"Formato de color inválido: {color}")
                
    def _validate_styles_file(self, content: str):
        """Valida archivo styles.xml"""
        # Verificar herencia de estilos
        parent_matches = re.findall(r'parent="([^"]*)"', content)
        for parent in parent_matches:
            if not parent.startswith("@style/") and not parent.startswith("android:"):
                self.warnings.append(f"Referencia de estilo padre podría ser inválida: {parent}")
                
    def _validate_manifest_file(self, content: str):
        """Valida AndroidManifest.xml"""
        required_elements = ["manifest", "application"]
        for element in required_elements:
            if f"<{element}" not in content:
                self.errors.append(f"Elemento requerido faltante: <{element}>")
                
        # Verificar permisos duplicados
        permissions = re.findall(r'<uses-permission[^>]*android:name="([^"]*)"', content)
        if len(permissions) != len(set(permissions)):
            self.warnings.append("Posibles permisos duplicados")
            
    def _validate_resource_references(self, content: str):
        """Valida referencias a recursos (@string/, @color/, etc.)"""
        # Encontrar todas las referencias a recursos
        references = re.findall(r'@([^/]+)/([^"\s>]+)', content)
        
        for ref_type, ref_name in references:
            if ref_type not in ["string", "color", "dimen", "style", "drawable", "layout", "id", "android"]:
                self.warnings.append(f"Tipo de recurso posiblemente inválido: @{ref_type}/{ref_name}")
                
    def _validate_duplicate_ids(self, content: str):
        """Verifica IDs duplicados en layouts"""
        ids = re.findall(r'android:id="@\+?id/([^"]+)"', content)
        duplicates = [id_name for id_name in set(ids) if ids.count(id_name) > 1]
        
        for dup_id in duplicates:
            self.errors.append(f"ID duplicado: {dup_id}")
            
    def validate_project_resources(self, apk_path: str) -> Dict:
        """Valida todos los recursos de un proyecto APK"""
        apk_path_obj = Path(apk_path)
        validation_results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "files_with_warnings": 0,
            "errors": [],
            "warnings": [],
            "file_results": {}
        }
        
        if not apk_path_obj.exists():
            validation_results["errors"].append(f"Ruta de proyecto no existe: {apk_path}")
            return validation_results
            
        # Validar archivos XML en res/
        res_dir = apk_path_obj / "res"
        if res_dir.exists():
            xml_files = list(res_dir.rglob("*.xml"))
            validation_results["total_files"] = len(xml_files)
            
            for xml_file in xml_files:
                try:
                    result = self.validate_xml_file(str(xml_file))
                    validation_results["file_results"][str(xml_file)] = result
                    
                    if result["valid"]:
                        validation_results["valid_files"] += 1
                    else:
                        validation_results["invalid_files"] += 1
                        validation_results["errors"].extend([
                            f"{xml_file.name}: {error}" for error in result["errors"]
                        ])
                        
                    if result["warnings"]:
                        validation_results["files_with_warnings"] += 1
                        validation_results["warnings"].extend([
                            f"{xml_file.name}: {warning}" for warning in result["warnings"]
                        ])
                        
                except Exception as e:
                    validation_results["invalid_files"] += 1
                    validation_results["errors"].append(f"Error procesando {xml_file.name}: {str(e)}")
                    
        # Validar AndroidManifest.xml
        manifest = apk_path_obj / "AndroidManifest.xml"
        if manifest.exists():
            result = self.validate_xml_file(str(manifest))
            validation_results["file_results"][str(manifest)] = result
            validation_results["total_files"] += 1
            
            if result["valid"]:
                validation_results["valid_files"] += 1
            else:
                validation_results["invalid_files"] += 1
                validation_results["errors"].extend([
                    f"AndroidManifest.xml: {error}" for error in result["errors"]
                ])
                
            if result["warnings"]:
                validation_results["files_with_warnings"] += 1
                validation_results["warnings"].extend([
                    f"AndroidManifest.xml: {warning}" for warning in result["warnings"]
                ])
                
        log_action("validate_project", {
            "path": apk_path,
            "total_files": validation_results["total_files"],
            "valid_files": validation_results["valid_files"],
            "invalid_files": validation_results["invalid_files"]
        })
        
        return validation_results
        
    def show_validation_report(self, results: Dict):
        """Muestra un reporte detallado de validación"""
        # Resumen general
        summary_table = Table(title="Resumen de Validación")
        summary_table.add_column("Métrica", style="cyan")
        summary_table.add_column("Valor", style="green")
        
        summary_table.add_row("Total archivos", str(results["total_files"]))
        summary_table.add_row("Archivos válidos", str(results["valid_files"]))
        summary_table.add_row("Archivos con errores", str(results["invalid_files"]))
        summary_table.add_row("Archivos con advertencias", str(results["files_with_warnings"]))
        
        console.print(summary_table)
        
        # Errores
        if results["errors"]:
            error_panel = Panel(
                "\n".join(results["errors"][:10]),  # Mostrar solo primeros 10
                title=f"Errores ({len(results['errors'])})",
                border_style="red"
            )
            console.print(error_panel)
            
            if len(results["errors"]) > 10:
                show_info(f"Se mostraron 10 de {len(results['errors'])} errores")
                
        # Advertencias
        if results["warnings"]:
            warning_panel = Panel(
                "\n".join(results["warnings"][:10]),  # Mostrar solo primeras 10
                title=f"Advertencias ({len(results['warnings'])})",
                border_style="yellow"
            )
            console.print(warning_panel)
            
            if len(results["warnings"]) > 10:
                show_info(f"Se mostraron 10 de {len(results['warnings'])} advertencias")
                
        # Estado general
        if results["invalid_files"] == 0:
            show_success("✓ Todos los archivos XML son válidos")
        else:
            show_error(f"✗ Se encontraron {results['invalid_files']} archivos con errores")
            
    def suggest_fixes(self, errors: List[str]) -> List[str]:
        """Sugiere correcciones para errores comunes"""
        suggestions = []
        
        for error in errors:
            if "layout_width" in error.lower() or "layout_height" in error.lower():
                suggestions.append("Especificar 'wrap_content', 'match_parent' o un valor dp específico")
            elif "duplicate" in error.lower():
                suggestions.append("Renombrar o eliminar IDs duplicados en el layout")
            elif "syntax" in error.lower():
                suggestions.append("Verificar que todas las etiquetas XML estén correctamente cerradas")
            elif "color" in error.lower():
                suggestions.append("Usar formato hexadecimal válido: #RRGGBB o #AARRGGBB")
            elif "resource" in error.lower():
                suggestions.append("Verificar que el recurso referenciado existe en el proyecto")
            else:
                suggestions.append("Revisar la documentación de Android para el elemento específico")
                
        return list(set(suggestions))  # Eliminar duplicados