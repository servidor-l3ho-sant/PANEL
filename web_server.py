from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import asyncio
from pathlib import Path
from file_manager import APKFileManager
from validator import AndroidResourceValidator
from api_gemini import GeminiAndroidAssistant
from templates import AndroidTemplateGenerator
from github_integration import GitHubManager
from utils import log_action, show_success, show_error


class APKEditorWebApp:
    """Servidor web para APK Editor con interfaz creativa"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.environ.get('SESSION_SECRET', 'apk-editor-secret-key')
        
        # Inicializar componentes
        self.file_manager = APKFileManager()
        self.validator = AndroidResourceValidator()
        self.ai_assistant = GeminiAndroidAssistant()
        self.template_generator = AndroidTemplateGenerator()
        self.github_manager = GitHubManager()
        
        # Configurar rutas
        self.setup_routes()
        
    def setup_routes(self):
        """Configura todas las rutas de la aplicación web"""
        
        @self.app.route('/')
        def index():
            """Página principal con interfaz creativa"""
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def api_status():
            """Estado de los servicios"""
            return jsonify({
                'gemini_available': self.ai_assistant.is_available(),
                'github_connected': self.github_manager.is_connected(),
                'current_project': str(self.file_manager.apk_path) if self.file_manager.apk_path else None
            })
        
        @self.app.route('/api/set-project', methods=['POST'])
        def set_project():
            """Establece el proyecto APK"""
            data = request.json
            path = data.get('path', '')
            
            if self.file_manager.set_apk_path(path):
                return jsonify({'success': True, 'message': 'Proyecto establecido exitosamente'})
            else:
                return jsonify({'success': False, 'message': 'Error estableciendo proyecto'})
        
        @self.app.route('/api/list-files')
        def list_files():
            """Lista archivos del proyecto"""
            category = request.args.get('category', 'all')
            
            if not self.file_manager.apk_path:
                return jsonify({'error': 'No hay proyecto establecido'})
                
            structure = self.file_manager.get_apk_structure()
            
            files_data = []
            files_to_show = []
            
            if category == 'all':
                for cat_files in structure.values():
                    files_to_show.extend(cat_files)
            elif category in structure:
                files_to_show = structure[category]
                
            for file_path in files_to_show:
                try:
                    stat = file_path.stat()
                    files_data.append({
                        'name': file_path.name,
                        'path': str(file_path.relative_to(self.file_manager.apk_path)),
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'type': file_path.suffix
                    })
                except:
                    continue
                    
            return jsonify({'files': files_data})
        
        @self.app.route('/api/read-file', methods=['POST'])
        def read_file():
            """Lee contenido de un archivo"""
            data = request.json
            file_path = data.get('path', '')
            
            content = self.file_manager.read_file(file_path)
            if content is not None:
                return jsonify({'success': True, 'content': content})
            else:
                return jsonify({'success': False, 'message': 'Error leyendo archivo'})
        
        @self.app.route('/api/write-file', methods=['POST'])
        def write_file():
            """Escribe contenido a un archivo"""
            data = request.json
            file_path = data.get('path', '')
            content = data.get('content', '')
            
            if self.file_manager.write_file(file_path, content):
                return jsonify({'success': True, 'message': 'Archivo guardado exitosamente'})
            else:
                return jsonify({'success': False, 'message': 'Error guardando archivo'})
        
        @self.app.route('/api/validate-project')
        def validate_project():
            """Valida recursos del proyecto"""
            if not self.file_manager.apk_path:
                return jsonify({'error': 'No hay proyecto establecido'})
                
            results = self.validator.validate_project_resources(str(self.file_manager.apk_path))
            return jsonify(results)
        
        @self.app.route('/api/ai-analyze', methods=['POST'])
        def ai_analyze():
            """Analiza código con IA"""
            data = request.json
            content = data.get('content', '')
            file_name = data.get('fileName', '')
            
            if not self.ai_assistant.is_available():
                return jsonify({'success': False, 'message': 'IA no disponible'})
                
            result = self.ai_assistant.analyze_layout(content, file_name)
            return jsonify(result)
        
        @self.app.route('/api/ai-suggest', methods=['POST'])
        def ai_suggest():
            """Sugiere mejoras con IA"""
            data = request.json
            content = data.get('content', '')
            requirements = data.get('requirements', '')
            
            if not self.ai_assistant.is_available():
                return jsonify({'success': False, 'message': 'IA no disponible'})
                
            result = self.ai_assistant.suggest_layout_improvements(content, requirements)
            return jsonify(result)
        
        @self.app.route('/api/generate-template', methods=['POST'])
        def generate_template():
            """Genera template"""
            data = request.json
            template_type = data.get('type', 'basic')
            
            if template_type == 'login':
                template = self.template_generator.generate_login_form()
            elif template_type == 'colors':
                template = self.template_generator.generate_basic_colors()
            elif template_type == 'strings':
                template = self.template_generator.generate_basic_strings()
            else:
                template = self.template_generator.generate_basic_layout()
                
            return jsonify({'success': True, 'template': template})
        
        @self.app.route('/api/github/repos')
        def github_repos():
            """Lista repositorios de GitHub"""
            try:
                token = self.github_manager.get_access_token()
                if not token:
                    return jsonify({'error': 'GitHub no conectado'})
                    
                repos = self.github_manager.list_repositories()
                return jsonify({'repos': repos})
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/github/contents/<owner>/<repo>')
        def github_contents(owner, repo):
            """Obtiene contenidos de repositorio"""
            path = request.args.get('path', '')
            try:
                contents = self.github_manager.get_repository_contents(owner, repo, path)
                return jsonify({'contents': contents})
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/github/download', methods=['POST'])
        def github_download():
            """Descarga archivo de GitHub"""
            data = request.json
            owner = data.get('owner')
            repo = data.get('repo')
            path = data.get('path')
            
            try:
                content = self.github_manager.download_file(owner, repo, path)
                if content:
                    return jsonify({'success': True, 'content': content})
                else:
                    return jsonify({'success': False, 'message': 'Error descargando archivo'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/github/upload', methods=['POST'])
        def github_upload():
            """Sube archivo a GitHub"""
            data = request.json
            owner = data.get('owner')
            repo = data.get('repo')
            path = data.get('path')
            content = data.get('content')
            message = data.get('message', 'Update from APK Editor Pro')
            
            try:
                success = self.github_manager.upload_file(owner, repo, path, content, message)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/history')
        def get_history():
            """Obtiene historial de cambios"""
            history = self.file_manager.get_file_history()
            return jsonify({'history': history[-20:]})  # Últimos 20
        
        @self.app.route('/api/backups')
        def list_backups():
            """Lista backups disponibles"""
            try:
                backups = []
                backup_dir = self.file_manager.backup_dir
                
                for backup in backup_dir.glob("*"):
                    stat = backup.stat()
                    backups.append({
                        'name': backup.name,
                        'size': stat.st_size,
                        'created': stat.st_ctime
                    })
                    
                backups.sort(key=lambda x: x['created'], reverse=True)
                return jsonify({'backups': backups})
            except Exception as e:
                return jsonify({'error': str(e)})
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecuta el servidor web"""
        log_action('web_server_start', {'host': host, 'port': port})
        self.app.run(host=host, port=port, debug=debug)