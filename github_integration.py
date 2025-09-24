import os
import requests
import json
import time
from typing import Dict, List, Optional
from utils import show_success, show_error, show_info, log_action


class GitHubManager:
    """Gestor para integración con GitHub usando la conexión de Replit"""
    
    def __init__(self):
        self.access_token = None
        self.connection_settings = None
        
    def get_access_token(self) -> Optional[str]:
        """Obtiene el token de acceso de GitHub"""
        try:
            if (self.connection_settings and 
                self.connection_settings.get('settings', {}).get('expires_at') and
                self.connection_settings['settings']['expires_at'] > time.time()):
                return self.connection_settings['settings']['access_token']
            
            hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
            x_replit_token = None
            
            if os.environ.get('REPL_IDENTITY'):
                x_replit_token = 'repl ' + os.environ.get('REPL_IDENTITY')
            elif os.environ.get('WEB_REPL_RENEWAL'):
                x_replit_token = 'depl ' + os.environ.get('WEB_REPL_RENEWAL')
            
            if not x_replit_token:
                show_error('Token de Replit no encontrado')
                return None
                
            url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github'
            headers = {
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
            
            response = requests.get(url, headers=headers)
            data = response.json()
            self.connection_settings = data.get('items', [{}])[0]
            
            access_token = (
                self.connection_settings.get('settings', {}).get('access_token') or
                self.connection_settings.get('settings', {}).get('oauth', {}).get('credentials', {}).get('access_token')
            )
            
            if not access_token:
                show_error('GitHub no está conectado correctamente')
                return None
                
            self.access_token = access_token
            show_success('Token de GitHub obtenido exitosamente')
            return access_token
            
        except Exception as e:
            show_error(f'Error obteniendo token de GitHub: {str(e)}')
            return None
    
    def get_headers(self) -> Dict[str, str]:
        """Obtiene headers para peticiones a la API de GitHub"""
        if not self.access_token:
            return {}
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
    
    def list_repositories(self, username: str = None) -> List[Dict]:
        """Lista repositorios del usuario"""
        try:
            if not self.access_token:
                return []
                
            url = 'https://api.github.com/user/repos' if not username else f'https://api.github.com/users/{username}/repos'
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                repos = response.json()
                log_action('list_repositories', {'count': len(repos)})
                return repos
            else:
                show_error(f'Error listando repositorios: {response.status_code}')
                return []
                
        except Exception as e:
            show_error(f'Error en list_repositories: {str(e)}')
            return []
    
    def get_repository_contents(self, owner: str, repo: str, path: str = '') -> List[Dict]:
        """Obtiene contenidos de un repositorio"""
        try:
            if not self.access_token:
                return []
                
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                contents = response.json()
                if not isinstance(contents, list):
                    contents = [contents]
                log_action('get_repository_contents', {'owner': owner, 'repo': repo, 'path': path})
                return contents
            else:
                show_error(f'Error obteniendo contenidos: {response.status_code}')
                return []
                
        except Exception as e:
            show_error(f'Error en get_repository_contents: {str(e)}')
            return []
    
    def download_file(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Descarga contenido de un archivo"""
        try:
            if not self.access_token:
                return None
                
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                if data.get('type') == 'file':
                    import base64
                    content = base64.b64decode(data['content']).decode('utf-8')
                    log_action('download_file', {'owner': owner, 'repo': repo, 'path': path})
                    return content
                else:
                    show_error('El elemento no es un archivo')
                    return None
            else:
                show_error(f'Error descargando archivo: {response.status_code}')
                return None
                
        except Exception as e:
            show_error(f'Error en download_file: {str(e)}')
            return None
    
    def upload_file(self, owner: str, repo: str, path: str, content: str, message: str = "Update from APK Editor") -> bool:
        """Sube o actualiza un archivo en el repositorio"""
        try:
            if not self.access_token:
                return False
                
            # Primero verificar si el archivo existe para obtener el SHA
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            response = requests.get(url, headers=self.get_headers())
            
            import base64
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                'message': message,
                'content': encoded_content
            }
            
            if response.status_code == 200:
                # El archivo existe, necesitamos el SHA
                existing_data = response.json()
                data['sha'] = existing_data['sha']
            
            # Subir el archivo
            response = requests.put(url, headers=self.get_headers(), json=data)
            
            if response.status_code in [200, 201]:
                show_success(f'Archivo subido exitosamente: {path}')
                log_action('upload_file', {'owner': owner, 'repo': repo, 'path': path})
                return True
            else:
                show_error(f'Error subiendo archivo: {response.status_code}')
                return False
                
        except Exception as e:
            show_error(f'Error en upload_file: {str(e)}')
            return False
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Optional[Dict]:
        """Crea un nuevo repositorio"""
        try:
            if not self.access_token:
                return None
                
            url = 'https://api.github.com/user/repos'
            data = {
                'name': name,
                'description': description,
                'private': private,
                'auto_init': True
            }
            
            response = requests.post(url, headers=self.get_headers(), json=data)
            
            if response.status_code == 201:
                repo_data = response.json()
                show_success(f'Repositorio creado: {name}')
                log_action('create_repository', {'name': name, 'private': private})
                return repo_data
            else:
                show_error(f'Error creando repositorio: {response.status_code}')
                return None
                
        except Exception as e:
            show_error(f'Error en create_repository: {str(e)}')
            return None
    
    def is_connected(self) -> bool:
        """Verifica si GitHub está conectado"""
        return self.access_token is not None