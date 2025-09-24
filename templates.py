from typing import Dict, List
from utils import show_success, show_error, show_info, log_action
from api_gemini import GeminiAndroidAssistant


class AndroidTemplateGenerator:
    """Generador de templates Android usando IA"""
    
    def __init__(self):
        self.ai_assistant = GeminiAndroidAssistant()
        
    def generate_basic_layout(self, layout_type: str = "LinearLayout") -> str:
        """Genera un layout básico"""
        templates = {
            "LinearLayout": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/hello_world"
        android:textSize="18sp" />

</LinearLayout>""",
            "ConstraintLayout": """<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/hello_world"
        android:textSize="18sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>"""
        }
        
        return templates.get(layout_type, templates["LinearLayout"])
        
    def generate_login_form(self) -> str:
        """Genera un formulario de login básico"""
        if self.ai_assistant.is_available():
            result = self.ai_assistant.generate_layout_template(
                "Formulario de login con email, contraseña y botón de iniciar sesión",
                "LinearLayout"
            )
            if result.get("success"):
                return result["response"]
                
        # Fallback template
        return """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:gravity="center">

    <EditText
        android:id="@+id/editTextEmail"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="@string/email"
        android:inputType="textEmailAddress"
        android:layout_marginBottom="16dp" />

    <EditText
        android:id="@+id/editTextPassword"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="@string/password"
        android:inputType="textPassword"
        android:layout_marginBottom="24dp" />

    <Button
        android:id="@+id/buttonLogin"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="@string/login" />

</LinearLayout>"""
        
    def generate_basic_colors(self) -> str:
        """Genera archivo colors.xml básico"""
        return """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>"""
        
    def generate_basic_strings(self) -> str:
        """Genera archivo strings.xml básico"""
        return """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Mi App</string>
    <string name="hello_world">Hola Mundo</string>
    <string name="email">Email</string>
    <string name="password">Contraseña</string>
    <string name="login">Iniciar Sesión</string>
</resources>"""