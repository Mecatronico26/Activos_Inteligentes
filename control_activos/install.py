#!/usr/bin/env python
"""
Script de instalación para el sistema de Control de Activos para planta de carbonato de litio
Este script configura el entorno, instala dependencias y prepara la base de datos
"""

import os
import sys
import subprocess
import platform
import shutil
import time
import argparse

# Colores para mensajes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}\n")

def print_step(message):
    print(f"{Colors.BLUE}➤ {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def run_command(command, error_message=None):
    """Ejecuta un comando y maneja errores"""
    try:
        process = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        if process.returncode != 0:
            if error_message:
                print_error(error_message)
            print_error(f"Comando: {command}")
            print_error(f"Error: {process.stderr}")
            return False
        return True
    except Exception as e:
        print_error(f"Error al ejecutar '{command}': {str(e)}")
        return False

def check_python_version():
    """Verifica la versión de Python"""
    print_step("Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print_error(f"Se requiere Python 3.6 o superior. Versión actual: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def setup_virtualenv(venv_name="venv"):
    """Configura el entorno virtual"""
    print_step(f"Configurando entorno virtual '{venv_name}'...")
    
    # Verificar si ya existe
    if os.path.exists(venv_name):
        print_warning(f"El entorno virtual '{venv_name}' ya existe")
        response = input("¿Desea eliminarlo y crear uno nuevo? (s/n): ").strip().lower()
        if response == 's':
            shutil.rmtree(venv_name)
        else:
            print_step("Usando entorno virtual existente...")
            return activate_virtualenv(venv_name)
    
    # Crear entorno virtual
    if not run_command(
        f"python -m venv {venv_name}", 
        f"Error al crear el entorno virtual '{venv_name}'"
    ):
        return False
    
    print_success(f"Entorno virtual '{venv_name}' creado correctamente")
    return activate_virtualenv(venv_name)

def activate_virtualenv(venv_name="venv"):
    """Activa el entorno virtual y devuelve el comando de activación"""
    print_step("Activando entorno virtual...")
    
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_name, "Scripts", "activate")
        activate_cmd = f"{activate_script}"
    else:
        activate_script = os.path.join(venv_name, "bin", "activate")
        activate_cmd = f"source {activate_script}"
    
    # Verificar si el script de activación existe
    if not os.path.exists(activate_script.replace("source ", "").replace("\"", "")):
        print_error(f"No se encontró el script de activación en '{activate_script}'")
        return False
        
    print_success("Entorno virtual activado")
    return activate_cmd

def install_dependencies(activate_cmd):
    """Instala las dependencias del proyecto"""
    print_step("Instalando dependencias...")
    
    dependencies = [
        "django",
        "pandas",
        "openpyxl",
        "scikit-learn",
        "matplotlib",
        "django-crispy-forms",
        "crispy-bootstrap4",
        "pillow",
        "joblib",
    ]
    
    for dependency in dependencies:
        print_step(f"Instalando {dependency}...")
        if platform.system() == "Windows":
            cmd = f"{activate_cmd} && pip install {dependency}"
        else:
            cmd = f"{activate_cmd} && pip install {dependency}"
        
        if not run_command(cmd, f"Error al instalar {dependency}"):
            return False
    
    print_success("Todas las dependencias instaladas correctamente")
    return True

def create_django_project(activate_cmd, project_name="control_activos"):
    """Crea el proyecto Django"""
    print_step(f"Creando proyecto Django '{project_name}'...")
    
    # Verificar si el proyecto ya existe
    if os.path.exists(project_name):
        print_warning(f"El proyecto '{project_name}' ya existe")
        return True
    
    if platform.system() == "Windows":
        cmd = f"{activate_cmd} && django-admin startproject {project_name} ."
    else:
        cmd = f"{activate_cmd} && django-admin startproject {project_name} ."
    
    if not run_command(cmd, f"Error al crear el proyecto Django '{project_name}'"):
        return False
    
    print_success(f"Proyecto Django '{project_name}' creado correctamente")
    return True

def create_django_apps(activate_cmd, project_name="control_activos"):
    """Crea las aplicaciones Django"""
    print_step("Creando aplicaciones Django...")
    
    apps = ["activos", "stock", "criticos", "obsoletos", "mantenimiento"]
    
    for app in apps:
        print_step(f"Creando aplicación '{app}'...")
        
        if platform.system() == "Windows":
            cmd = f"{activate_cmd} && python manage.py startapp {app}"
        else:
            cmd = f"{activate_cmd} && python manage.py startapp {app}"
        
        if not run_command(cmd, f"Error al crear la aplicación '{app}'"):
            return False
    
    print_success("Todas las aplicaciones creadas correctamente")
    return True

def setup_database(activate_cmd):
    """Configura la base de datos"""
    print_step("Configurando base de datos...")
    
    # Aplicar migraciones
    if platform.system() == "Windows":
        cmd_makemigrations = f"{activate_cmd} && python manage.py makemigrations"
        cmd_migrate = f"{activate_cmd} && python manage.py migrate"
    else:
        cmd_makemigrations = f"{activate_cmd} && python manage.py makemigrations"
        cmd_migrate = f"{activate_cmd} && python manage.py migrate"
    
    print_step("Generando migraciones...")
    if not run_command(cmd_makemigrations, "Error al generar migraciones"):
        return False
    
    print_step("Aplicando migraciones...")
    if not run_command(cmd_migrate, "Error al aplicar migraciones"):
        return False
    
    print_success("Base de datos configurada correctamente")
    return True

def create_superuser(activate_cmd):
    """Crea un superusuario"""
    print_step("Creando superusuario para el panel de administración...")
    
    username = input("Nombre de usuario (por defecto 'admin'): ").strip() or "admin"
    email = input("Email (opcional): ").strip()
    
    # Crear script temporal para crear superusuario automáticamente
    with open("create_superuser.py", "w") as f:
        f.write(f"""
from django.contrib.auth.models import User
if not User.objects.filter(username='{username}').exists():
    User.objects.create_superuser('{username}', '{email}', 'admin123')
    print('Superusuario creado')
else:
    print('El usuario ya existe')
""")
    
    if platform.system() == "Windows":
        cmd = f"{activate_cmd} && python manage.py shell < create_superuser.py"
    else:
        cmd = f"{activate_cmd} && python manage.py shell < create_superuser.py"
    
    if not run_command(cmd, "Error al crear superusuario"):
        if os.path.exists("create_superuser.py"):
            os.remove("create_superuser.py")
        return False
    
    # Eliminar script temporal
    if os.path.exists("create_superuser.py"):
        os.remove("create_superuser.py")
    
    print_success(f"Superusuario '{username}' creado con contraseña 'admin123'")
    return True

def create_static_dirs():
    """Crea directorios estáticos necesarios"""
    print_step("Creando directorios estáticos...")
    
    directories = [
        "static/css",
        "static/js",
        "static/img",
        "media/models",
        "media/activos",
        "templates/activos",
        "templates/stock",
        "templates/criticos",
        "templates/obsoletos",
        "templates/mantenimiento",
        "templates/ai",
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print_success(f"Directorio '{directory}' creado")
        except Exception as e:
            print_error(f"Error al crear directorio '{directory}': {str(e)}")
            return False
    
    # Crear archivo CSS vacío
    css_file = "static/css/styles.css"
    if not os.path.exists(css_file):
        with open(css_file, "w") as f:
            f.write("""
/* Estilos personalizados */
.footer {
    margin-top: 2rem;
    padding-top: 1rem;
    padding-bottom: 1rem;
    border-top: 1px solid #e7e7e7;
}

.card {
    margin-bottom: 1rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header {
    font-weight: 500;
}
""")
    
    # Crear archivo JS vacío
    js_file = "static/js/scripts.js"
    if not os.path.exists(js_file):
        with open(js_file, "w") as f:
            f.write("""
// Scripts personalizados
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    console.log('Sistema de Control de Activos iniciado');
});

// Función para manejar la actualización de subáreas al cambiar el área
function actualizarSubareas() {
    const areaSelect = document.getElementById('id_area_select');
    const subareaSelect = document.getElementById('id_subarea_select');
    
    if (areaSelect && subareaSelect) {
        areaSelect.addEventListener('change', function() {
            const areaId = this.value;
            
            // Limpiar select de subáreas
            subareaSelect.innerHTML = '<option value="">---------</option>';
            
            if (areaId) {
                // Realizar petición AJAX para obtener subáreas
                fetch(`/activos/api/get-subareas/?area_id=${areaId}`)
                    .then(response => response.json())
                    .then(data => {
                        data.forEach(subarea => {
                            const option = document.createElement('option');
                            option.value = subarea.id;
                            option.textContent = subarea.nombre;
                            subareaSelect.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Error al obtener subáreas:', error);
                    });
            }
        });
    }
}

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    actualizarSubareas();
});
""")
    
    print_success("Archivos estáticos creados correctamente")
    return True

def run_server(activate_cmd):
    """Inicia el servidor de desarrollo"""
    print_step("Iniciando servidor de desarrollo...")
    
    if platform.system() == "Windows":
        cmd = f"start cmd /k \"{activate_cmd} && python manage.py runserver\""
    else:
        cmd = f"gnome-terminal -- bash -c '{activate_cmd} && python manage.py runserver; exec bash' || {activate_cmd} && python manage.py runserver"
    
    print_success("Servidor iniciado")
    print_success("Accede a http://127.0.0.1:8000/ para ver la aplicación")
    print_success(f"Panel de administración: http://127.0.0.1:8000/admin/ (usuario: admin, contraseña: admin123)")
    
    run_command(cmd)
    return True

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Instalador del Sistema de Control de Activos")
    parser.add_argument("--no-server", action="store_true", help="No iniciar el servidor automáticamente")
    args = parser.parse_args()
    
    print_header("INSTALADOR DEL SISTEMA DE CONTROL DE ACTIVOS")
    print("Este script configurará todo lo necesario para ejecutar el sistema.")
    print("Por favor, siga las instrucciones para completar la instalación.")
    
    # Verificar requisitos
    if not check_python_version():
        sys.exit(1)
    
    # Configurar entorno virtual
    activate_cmd = setup_virtualenv()
    if not activate_cmd:
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies(activate_cmd):
        sys.exit(1)
    
    # Crear proyecto Django
    if not create_django_project(activate_cmd):
        sys.exit(1)
    
    # Crear aplicaciones
    if not create_django_apps(activate_cmd):
        sys.exit(1)
    
    # Crear directorios estáticos
    if not create_static_dirs():
        sys.exit(1)
    
    # Configurar base de datos
    if not setup_database(activate_cmd):
        sys.exit(1)
    
    # Crear superusuario
    if not create_superuser(activate_cmd):
        sys.exit(1)
    
    print_header("INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print_success("El sistema de Control de Activos ha sido instalado correctamente.")
    print_success("Puede acceder al sistema en http://127.0.0.1:8000/")
    print_success("Panel de administración: http://127.0.0.1:8000/admin/")
    print_success("Usuario: admin")
    print_success("Contraseña: admin123")
    
    # Iniciar servidor
    if not args.no_server:
        run_server(activate_cmd)
    else:
        print_step("Para iniciar el servidor manualmente, ejecute:")
        if platform.system() == "Windows":
            print(f"\t{activate_cmd} && python manage.py runserver")
        else:
            print(f"\t{activate_cmd} && python manage.py runserver")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())