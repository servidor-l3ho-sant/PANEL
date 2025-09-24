import os
import json
from typing import Dict, List, Optional, Tuple
from google import genai
from google.genai import types
from utils import (
    show_success, show_error, show_warning, show_info,
    log_action, console, Colors
)
from rich.panel import Panel
from rich.spinner import Spinner


class GeminiAndroidAssistant:
    """Asistente IA usando Gemini para desarrollo Android"""
    
    def __init__(self):
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self._initialize_client()
        
    def _initialize_client(self):
        """Inicializa el cliente de Gemini"""
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                show_error("GEMINI_API_KEY no encontrado en variables de entorno")
                return False
                
            self.client = genai.Client(api_key=api_key)
            show_success("Cliente Gemini inicializado correctamente")
            return True
            
        except Exception as e:
            show_error(f"Error al inicializar Gemini: {str(e)}")
            return False
            
    def is_available(self) -> bool:
        """Verifica si la API está disponible"""
        return self.client is not None
        
    def analyze_layout(self, layout_content: str, file_name: str = "") -> Dict:
        """Analiza un layout XML y sugiere mejoras"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        prompt = f"""
        Analiza este layout de Android XML y proporciona sugerencias de mejora:

        Archivo: {file_name}
        ```xml
        {layout_content}
        ```

        Por favor proporciona:
        1. Análisis general del layout
        2. Problemas potenciales identificados
        3. Sugerencias de mejora específicas
        4. Mejores prácticas que podrían aplicarse
        5. Optimizaciones de rendimiento

        Responde en español y sé específico sobre los cambios sugeridos.
        """
        
        return self._make_request(prompt, "analyze_layout", {"file": file_name})
        
    def suggest_layout_improvements(self, layout_content: str, requirements: str = "") -> Dict:
        """Sugiere mejoras específicas para un layout"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        prompt = f"""
        Tengo este layout Android XML que necesita mejoras:

        ```xml
        {layout_content}
        ```

        Requisitos específicos: {requirements}

        Por favor sugiere:
        1. Versión mejorada del XML con cambios aplicados
        2. Explicación detallada de cada cambio
        3. Beneficios de cada mejora
        4. Consideraciones de compatibilidad

        Proporciona el XML mejorado completo y mantén la funcionalidad original.
        """
        
        return self._make_request(prompt, "suggest_improvements", {"requirements": requirements})
        
    def fix_xml_errors(self, xml_content: str, errors: List[str]) -> Dict:
        """Sugiere correcciones para errores XML específicos"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        errors_text = "\n".join([f"- {error}" for error in errors])
        
        prompt = f"""
        Este archivo XML Android tiene los siguientes errores:

        {errors_text}

        Contenido XML:
        ```xml
        {xml_content}
        ```

        Por favor:
        1. Identifica la causa de cada error
        2. Proporciona el XML corregido completo
        3. Explica cada corrección realizada
        4. Sugiere cómo prevenir estos errores en el futuro

        Asegúrate de que el XML corregido mantenga la funcionalidad original.
        """
        
        return self._make_request(prompt, "fix_errors", {"errors": errors})
        
    def generate_layout_template(self, description: str, layout_type: str = "LinearLayout") -> Dict:
        """Genera un template de layout basado en descripción"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        prompt = f"""
        Genera un layout Android XML basado en esta descripción:

        Descripción: {description}
        Tipo de layout preferido: {layout_type}

        El layout debe incluir:
        1. Estructura XML completa y válida
        2. Atributos apropiados para cada elemento
        3. IDs únicos y descriptivos
        4. Comentarios explicando secciones importantes
        5. Mejores prácticas de Android UI

        Usa estilos modernos y asegúrate de que sea responsive.
        Incluye strings resources donde sea apropiado (@string/...).
        """
        
        return self._make_request(prompt, "generate_template", {
            "description": description, 
            "layout_type": layout_type
        })
        
    def suggest_color_scheme(self, app_theme: str, brand_colors: str = "") -> Dict:
        """Sugiere esquema de colores para la app"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        prompt = f"""
        Genera un esquema de colores completo para una aplicación Android:

        Tema de la app: {app_theme}
        Colores de marca (si los hay): {brand_colors}

        Proporciona:
        1. Archivo colors.xml completo con colores primarios, secundarios y de acento
        2. Colores para diferentes estados (pressed, disabled, etc.)
        3. Colores para modo claro y oscuro
        4. Explicación de cada color y su uso recomendado
        5. Códigos hexadecimales precisos

        Asegúrate de que los colores cumplan con las pautas de accesibilidad de Android.
        """
        
        return self._make_request(prompt, "suggest_colors", {
            "theme": app_theme,
            "brand_colors": brand_colors
        })
        
    def optimize_performance(self, layout_content: str) -> Dict:
        """Analiza y sugiere optimizaciones de rendimiento"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        prompt = f"""
        Analiza este layout Android para optimizaciones de rendimiento:

        ```xml
        {layout_content}
        ```

        Por favor identifica:
        1. Problemas de rendimiento actuales
        2. Jerarquía de vistas excesivamente anidada
        3. Uso ineficiente de ViewGroups
        4. Oportunidades para usar ConstraintLayout
        5. Optimizaciones específicas recomendadas

        Proporciona el layout optimizado y explica cada cambio.
        """
        
        return self._make_request(prompt, "optimize_performance")
        
    def explain_android_concept(self, concept: str, context: str = "") -> Dict:
        """Explica conceptos de desarrollo Android"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        prompt = f"""
        Explica este concepto de desarrollo Android de manera clara y práctica:

        Concepto: {concept}
        Contexto: {context}

        Por favor incluye:
        1. Definición clara y concisa
        2. Cuándo y por qué usarlo
        3. Ejemplo práctico de implementación
        4. Mejores prácticas relacionadas
        5. Errores comunes a evitar

        Explica como si fuera para un desarrollador Android intermedio.
        """
        
        return self._make_request(prompt, "explain_concept", {"concept": concept})
        
    def _make_request(self, prompt: str, action: str, metadata: Dict = None) -> Dict:
        """Realiza una petición a la API de Gemini"""
        try:
            with console.status("[cyan]Consultando a Gemini AI...", spinner="dots"):
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=2048,
                    )
                )
                
            if response.text:
                result = {
                    "success": True,
                    "response": response.text.strip(),
                    "action": action,
                    "metadata": metadata or {}
                }
                
                log_action(f"gemini_{action}", {
                    "prompt_length": len(prompt),
                    "response_length": len(response.text),
                    "metadata": metadata
                })
                
                return result
            else:
                return {
                    "success": False,
                    "error": "Respuesta vacía de Gemini",
                    "action": action
                }
                
        except Exception as e:
            error_msg = f"Error en petición a Gemini: {str(e)}"
            show_error(error_msg)
            log_action(f"gemini_error", {
                "action": action,
                "error": error_msg,
                "metadata": metadata
            })
            
            return {
                "success": False,
                "error": error_msg,
                "action": action
            }
            
    def apply_suggestions(self, original_content: str, suggestions: str) -> Tuple[str, List[str]]:
        """Intenta aplicar automáticamente las sugerencias al contenido"""
        # Esta función analizaría las sugerencias e intentaría aplicarlas
        # Por simplicidad, devuelve el contenido original y una lista de cambios manuales
        
        manual_changes = []
        modified_content = original_content
        
        # Aquí se implementaría lógica más sofisticada para aplicar cambios automáticamente
        # Por ahora, solo detectamos algunos patrones simples
        
        if "layout_width" in suggestions and 'layout_width=""' in original_content:
            modified_content = modified_content.replace('layout_width=""', 'layout_width="wrap_content"')
            manual_changes.append("Corregido layout_width vacío")
            
        if "layout_height" in suggestions and 'layout_height=""' in original_content:
            modified_content = modified_content.replace('layout_height=""', 'layout_height="wrap_content"')
            manual_changes.append("Corregido layout_height vacío")
            
        # Más patrones de corrección automática se pueden añadir aquí
        
        return modified_content, manual_changes
        
    def show_ai_response(self, response_data: Dict):
        """Muestra la respuesta de la IA de manera formateada"""
        if not response_data.get("success", False):
            show_error(f"Error en consulta IA: {response_data.get('error', 'Error desconocido')}")
            return
            
        response_text = response_data.get("response", "")
        action = response_data.get("action", "consulta")
        
        # Crear panel con la respuesta
        panel = Panel(
            response_text,
            title=f"🤖 Gemini AI - {action.replace('_', ' ').title()}",
            border_style=Colors.INFO,
            padding=(1, 2)
        )
        
        console.print(panel)
        
        # Registrar que se mostró la respuesta
        log_action("show_ai_response", {
            "action": action,
            "response_length": len(response_text)
        })
        
    def get_usage_tips(self) -> List[str]:
        """Devuelve consejos para usar efectivamente la IA"""
        return [
            "Sé específico en tus descripciones de layouts",
            "Incluye contexto sobre el tipo de aplicación que estás desarrollando", 
            "Menciona restricciones específicas (tamaño de pantalla, versión de Android)",
            "Proporciona detalles sobre errores que estés viendo",
            "Especifica si prefieres ciertos tipos de layouts (ConstraintLayout, LinearLayout, etc.)",
            "Incluye información sobre el tema visual de tu app",
            "Menciona si necesitas compatibilidad con versiones específicas de Android"
        ]
    
    def chat_with_context(self, prompt: str, filename: str = "") -> Dict:
        """Chat inteligente con contexto del proyecto Android"""
        if not self.is_available():
            return {"error": "API de Gemini no disponible"}
            
        # Sistema de prompt especializado para Android
        system_prompt = f"""
        Eres un experto desarrollador Android especializado en:
        - Análisis y optimización de layouts XML
        - Desarrollo de aplicaciones móviles
        - UI/UX para Android
        - Debugging y resolución de problemas
        - Mejores prácticas de Android
        - Generación de código limpio y eficiente
        
        Responde de manera clara, concisa y práctica. Proporciona ejemplos de código cuando sea útil.
        Si el usuario muestra código XML, analízalo cuidadosamente y ofrece mejoras específicas.
        
        Contexto del archivo actual: {filename}
        """
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        return self._make_request(full_prompt, "chat_context", {"filename": filename})