"""
VISTAS PARA RESPALDO Y RESTAURACION DE BD 
Permite crear respaldo completo y restaurarlo desde archivo SQL
"""
import os
import subprocess
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import shutil
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from usuarios.models import RolUsuario


def verificar_administrador(request):
    if not (request.user.is_staff or request.user.rol == RolUsuario.ADMIN):
        raise PermissionDenied

# ========== OBTENER DATOS DE LA BD ==========

def obtener_credenciales_mysql():
    """Obtiene las credenciales de MySQL desde settings.py"""
    db_config = settings.DATABASES['default']
    return {
        'host': db_config.get('HOST') or 'localhost',
        'user': db_config.get('USER') or 'root',
        'password': db_config.get('PASSWORD') or '',
        'database': db_config.get('NAME') or '',
        'port': db_config.get('PORT') or 3306,
        'mysqldump_path': shutil.which('mysqldump') or r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe',
        'mysql_path': shutil.which('mysql') or r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe',
    }

def probar_conexion_mysql():
    """Prueba la conexión a MySQL"""
    creds = obtener_credenciales_mysql()
    try:
        cmd = [
            creds["mysql_path"],
            '-h', creds["host"],
            '-u', creds["user"],
            '-P', str(creds["port"]),
            '--password=' + creds["password"],
            '-e', 'SELECT 1;',
            creds["database"]
        ]

        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return resultado.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False

# ========== VISTA PARA MOSTRAR OPCIONES DE RESPALDO ==========
@require_http_methods(["GET", "POST"])
@login_required
def backup(request):
    """Muestra el menu de opciones para respaldo y restauracion"""
    verificar_administrador(request)

    if request.method == "POST":
        accion = request.POST.get('accion')

        try:
            if accion == 'backup_completo':
                if not probar_conexion_mysql():
                    return JsonResponse({'error': 'No se puede conectar a MySQL. Verifica que el servidor esté ejecutándose y que las credenciales sean válidas.'}, status=400)
                return realizar_respaldo_completo()
            return JsonResponse({'error': 'Acción no válida'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    mysql_ok = probar_conexion_mysql()
    context = {
        'titulo': 'Respaldo y Restauración de Base de Datos',
        'mysql_conectado': mysql_ok,
    }
    return render(request, 'backup/menu.html', context)

# ========== VISTA PARA RESTAURAR DATOS ==========
@require_http_methods(["POST"])
@login_required
def restaurar_datos(request):
    """Restaura datos desde un archivo SQL"""
    verificar_administrador(request)

    if 'archivo' not in request.FILES:
        return JsonResponse({'error': 'No se proporcionó archivo'}, status=400)

    archivo = request.FILES['archivo']

    try:
        if not archivo.name.lower().endswith('.sql'):
            return JsonResponse({'error': 'El archivo debe tener extensión .sql'}, status=400)

        contenido_sql = archivo.read().decode('utf-8')
        restaurar_bd_desde_sql(contenido_sql)
        return JsonResponse({'exito': True, 'mensaje': 'Base de datos restaurada correctamente'})

    except Exception as e:
        return JsonResponse({'error': f'Error al restaurar: {str(e)}'}, status=400)

# ========== FUNCIONES DE RESPALDO ==========

def realizar_respaldo_completo():
    """Realiza un respaldo completo (estructura + datos)"""
    creds = obtener_credenciales_mysql()

    try:
        # Construir comando mysqldump
        cmd = [
            os.path.join(creds["mysqldump_path"]),
            '-h', creds["host"],
            '-u', creds["user"],
            '-P', str(creds["port"]),
            '--password=' + creds["password"],
            creds["database"]
        ]


        # Ejecutar mysqldump y capturar output
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  
        )


        if resultado.returncode != 0:
            raise Exception(f"Error mysqldump: {resultado.stderr}")

        sql_content = resultado.stdout

        if not sql_content.strip():
            raise Exception("El respaldo esta vacio")

        # Agregar comentario con fecha
        sql_content = f"-- Respaldo Completo de {creds['database']}\n" \
                      f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" \
                      f"-- Tipo: Completo (Estructura + Datos)\n\n" + sql_content

        return generar_archivo_descarga(sql_content, 'backup_completo')

    except subprocess.TimeoutExpired:
        raise Exception("Timeout al ejecutar mysqldump")
    except Exception as e:
        print(f"Error en respaldo completo: {str(e)}")
        raise Exception(f"Error en respaldo completo: {str(e)}")

# ========== FUNCIONES PARA RESTAURAR ==========

def restaurar_bd_desde_sql(contenido_sql):
    """Restaura la BD ejecutando el SQL"""
    creds = obtener_credenciales_mysql()

    try:
        cmd = [
            creds["mysql_path"],
            '-h', creds["host"],
            '-u', creds["user"],
            '-P', str(creds["port"]),
            '--password=' + creds["password"],
            creds["database"]
        ]

        proceso = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        _stdout, stderr = proceso.communicate(input=contenido_sql, timeout=120)

        if proceso.returncode != 0:
            raise Exception(f"Error MySQL: {stderr}")

        return True

    except subprocess.TimeoutExpired:
        raise Exception("Timeout al restaurar la base de datos")
    except Exception as e:
        print(f"Error al restaurar: {str(e)}")
        raise Exception(f"Error al restaurar: {str(e)}")

# ========== FUNCION PARA GENERAR DESCARGA ==========

def generar_archivo_descarga(contenido_sql, nombre_archivo):
    """Genera un archivo SQL para descargar"""
    response = HttpResponse(contenido_sql.encode('utf-8'), content_type='application/sql')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}_{timestamp}.sql"'

    return response

