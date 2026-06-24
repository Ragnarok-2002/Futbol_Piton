# pip install Flask mysql-connector-python

from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
import calendar
import re
from datetime import datetime, date, timedelta
import os
from urllib.parse import quote
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Clave secreta obligatoria en Flask para manejar sesiones en el futuro
app.secret_key = 'clave_secreta_escuela_futbol'

# ==========================================
# CONFIGURACIÓN DE SUBIDA DE ARCHIVOS
# ==========================================
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'pagos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # Límite de 5MB por imagen

# Crear la carpeta automáticamente si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

NOMBRES_MESES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def formatear_mes_pago(mes_str):
    if not mes_str:
        return 'Sin mes'
    try:
        partes = mes_str.split('-')
        anio = partes[0]
        mes_num = int(partes[1])
        return f"{NOMBRES_MESES.get(mes_num, mes_str)} {anio}"
    except (ValueError, IndexError):
        return mes_str

def agrupar_soportes_por_mes(soportes):
    grupos = {}
    for soporte in soportes:
        mes = soporte.get('mes_correspondiente') or 'sin-mes'
        grupos.setdefault(mes, []).append(soporte)

    resultado = []
    for mes in sorted(grupos.keys(), reverse=True):
        resultado.append({
            'clave': mes,
            'etiqueta': formatear_mes_pago(mes) if mes != 'sin-mes' else 'Sin mes',
            'pagos': grupos[mes]
        })
    return resultado

def validar_mes_pago(mes_str):
    """Valida formato YYYY-MM y que no sea un mes futuro."""
    if not mes_str or len(mes_str) != 7 or mes_str[4] != '-':
        return False, 'Selecciona un mes válido del calendario'
    try:
        anio = int(mes_str[:4])
        mes_num = int(mes_str[5:7])
    except ValueError:
        return False, 'Selecciona un mes válido del calendario'
    if mes_num < 1 or mes_num > 12:
        return False, 'Selecciona un mes válido del calendario'
    hoy = datetime.now()
    if anio > hoy.year or (anio == hoy.year and mes_num > hoy.month):
        return False, 'No puedes seleccionar un mes futuro'
    if anio < hoy.year - 2:
        return False, 'El mes seleccionado es demasiado antiguo'
    return True, mes_str

# ==========================================
# 1. CONFIGURACIÓN DE CONEXIÓN A LA BASE DE DATOS
# ==========================================
def obtener_conexion():
    return mysql.connector.connect(
        host="127.0.0.1",          # Tu IP local (localhost)
        user="root",               # Usuario por defecto de XAMPP
        password="",               # Contraseña vacía por defecto de XAMPP
        database="bd_escuela_futbol", # El nombre exacto de tu BD limpia
        port=3306                  # Puerto por defecto de MySQL en XAMPP
    )

# ==========================================
# 2. FUNCIONES AUXILIARES DE SESIÓN Y NAVEGACIÓN
# ==========================================
def usuario_tiene_sesion():
    return 'id_usuario' in session

def obtener_id_rol_sesion():
    if 'id_rol' in session:
        return session['id_rol']
    if not usuario_tiene_sesion():
        return None
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_rol FROM usuario WHERE id_usuario = %s", (session['id_usuario'],))
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    if fila:
        session['id_rol'] = fila['id_rol']
        return fila['id_rol']
    return None

def panel_por_rol(id_rol):
    if id_rol == 4:
        return '/dashboard-jugador'
    elif id_rol == 5:
        return '/modulo-acudiente'
    elif id_rol == 3:
        return '/modulo-entrenador'
    else:
        return '/dashboard-admin'

def obtener_panel_actual():
    if not usuario_tiene_sesion():
        return '/'
    return panel_por_rol(obtener_id_rol_sesion())

@app.context_processor
def inyectar_contexto_navegacion():
    if not usuario_tiene_sesion():
        return {}
    return {
        'id_rol': obtener_id_rol_sesion(),
        'url_panel_usuario': obtener_panel_actual(),
    }

def calcular_edad(fecha_nacimiento):
    nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    fecha_hoy = datetime.now()
    return fecha_hoy.year - nacimiento.year - ((fecha_hoy.month, fecha_hoy.day) < (nacimiento.month, nacimiento.day))

REGEX_SOLO_NUMEROS = re.compile(r'^\d+$')
REGEX_SOLO_LETRAS = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s-]+$')

def validar_solo_numeros(valor, nombre_campo='Este campo'):
    valor = (valor or '').strip()
    if not valor:
        return False, f'{nombre_campo} es obligatorio.'
    if not REGEX_SOLO_NUMEROS.match(valor):
        return False, f'{nombre_campo} solo puede contener números.'
    return True, valor

def validar_solo_letras(valor, nombre_campo='Este campo'):
    valor = (valor or '').strip()
    if not valor:
        return False, f'{nombre_campo} es obligatorio.'
    if not REGEX_SOLO_LETRAS.match(valor):
        return False, f'{nombre_campo} solo puede contener letras.'
    return True, valor

def validar_campos_persona(telefono, documento=None, nombres=None, apellidos=None, nombre=None, apellido=None):
    datos = {}

    if documento is not None:
        ok, documento = validar_solo_numeros(documento, 'El documento')
        if not ok:
            return False, documento, None
        datos['documento'] = documento

    ok, telefono = validar_solo_numeros(telefono, 'El teléfono')
    if not ok:
        return False, telefono, None
    datos['telefono'] = telefono

    if nombres is not None:
        ok, nombres = validar_solo_letras(nombres, 'Los nombres')
        if not ok:
            return False, nombres, None
        datos['nombres'] = nombres
    if apellidos is not None:
        ok, apellidos = validar_solo_letras(apellidos, 'Los apellidos')
        if not ok:
            return False, apellidos, None
        datos['apellidos'] = apellidos
    if nombre is not None:
        ok, nombre = validar_solo_letras(nombre, 'El nombre')
        if not ok:
            return False, nombre, None
        datos['nombre'] = nombre
    if apellido is not None:
        ok, apellido = validar_solo_letras(apellido, 'El apellido')
        if not ok:
            return False, apellido, None
        datos['apellido'] = apellido

    return True, None, datos

def validar_numero_decimal(valor, nombre_campo):
    if valor is None or str(valor).strip() == '':
        return False, f'{nombre_campo} es obligatorio.'
    try:
        numero = float(str(valor).replace(',', '.'))
    except ValueError:
        return False, f'{nombre_campo} debe ser un número válido.'
    if numero < 0:
        return False, f'{nombre_campo} debe ser un valor positivo.'
    return True, numero

def validar_edad_acudiente(fecha_nacimiento):
    if not fecha_nacimiento:
        return False, 'La fecha de nacimiento es obligatoria para registrar un acudiente.'
    if calcular_edad(fecha_nacimiento) < 18:
        return False, 'No tiene la mayoría de edad para ser acudiente/tutor. Debe ser mayor de 18 años.'
    return True, None

def validar_edad_jugador(fecha_nacimiento):
    if not fecha_nacimiento:
        return False, 'La fecha de nacimiento es obligatoria para registrar un jugador.'
    edad = calcular_edad(fecha_nacimiento)
    if edad < 10:
        return False, 'Aún no tienes la edad mínima (10 años). Te invitamos a inscribirte en nuestra escuela aliada JUNIOR.'
    if edad > 22:
        return False, 'Superaste la edad máxima (22 años). Te invitamos a inscribirte en nuestra escuela aliada MASTER.'
    return True, None

ESPECIALIDADES_ENTRENADOR = [
    'Delanteros',
    'Mediocampistas',
    'Defensas',
    'Porteros',
    'General',
]

def validar_especialidad_entrenador(especialidad):
    if especialidad not in ESPECIALIDADES_ENTRENADOR:
        return False, 'La especialidad seleccionada no es válida.'
    return True, None

POSICIONES_JUGADOR = ['Delantero', 'Mediocampista', 'Defensa', 'Portero', 'Por definir']

def validar_apodo_ficha(apodo):
    apodo = apodo.strip()
    if not apodo:
        return False, 'El nombre en ficha es obligatorio.'
    if len(apodo.split()) > 1:
        return False, 'Solo se permite una palabra (apodo, nombre o apellido).'
    if len(apodo) > 30:
        return False, 'El nombre en ficha no puede superar 30 caracteres.'
    if re.search(r'\d', apodo):
        return False, 'El nombre en ficha no puede contener números.'
    if not REGEX_SOLO_LETRAS.match(apodo):
        return False, 'El nombre en ficha solo puede contener letras.'
    return True, apodo

def asegurar_columna_apodo_ficha():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(*) AS existe
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'ficha_jugador'
          AND COLUMN_NAME = 'apodo'
    """)
    if cursor.fetchone()['existe'] == 0:
        cursor = conexion.cursor()
        cursor.execute("ALTER TABLE ficha_jugador ADD COLUMN apodo VARCHAR(50) DEFAULT NULL")
        conexion.commit()
    cursor.close()
    conexion.close()

def obtener_id_acudiente_sesion():
    if obtener_id_rol_sesion() != 5:
        return None
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_acudiente FROM acudiente WHERE id_usuario = %s", (session['id_usuario'],))
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    return fila['id_acudiente'] if fila else None

def obtener_id_jugador_sesion():
    if obtener_id_rol_sesion() != 4:
        return None
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_jugador FROM jugador WHERE id_usuario = %s", (session['id_usuario'],))
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    return fila['id_jugador'] if fila else None

def obtener_datos_acudiente_por_id(id_acudiente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id_acudiente, a.nombre, a.apellido, a.documento, a.telefono, a.email,
               a.fecha_nacimiento, u.estado
        FROM acudiente a
        JOIN usuario u ON a.id_usuario = u.id_usuario
        WHERE a.id_acudiente = %s
    """, (id_acudiente,))
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()
    return datos

def obtener_jugadores_por_acudiente(id_acudiente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT j.id_jugador, j.id_usuario, j.id_acudiente, j.documento, j.nombres, j.apellidos,
               j.telefono, j.email, j.fecha_nacimiento, j.fecha_registro, u.estado
        FROM jugador j
        JOIN usuario u ON j.id_usuario = u.id_usuario
        WHERE j.id_acudiente = %s
        ORDER BY j.apellidos ASC, j.nombres ASC
    """, (id_acudiente,))
    jugadores = cursor.fetchall()
    cursor.close()
    conexion.close()
    for jugador in jugadores:
        jugador['edad'] = edad_jugador(jugador['fecha_nacimiento'])
        jugador['puede_editar'] = (
            jugador['edad'] is not None and jugador['edad'] < 18
        )
    return jugadores

def puede_editar_datos_jugador_acudiente(datos_jugador):
    if not datos_jugador:
        return False
    id_rol = obtener_id_rol_sesion()
    if id_rol in [1, 2]:
        return True
    if id_rol != 5:
        return False
    id_acudiente = obtener_id_acudiente_sesion()
    edad = edad_jugador(datos_jugador.get('fecha_nacimiento'))
    return (
        id_acudiente
        and datos_jugador.get('id_acudiente') == id_acudiente
        and edad is not None
        and edad < 18
    )

def obtener_datos_ficha_jugador(id_jugador):
    asegurar_columna_apodo_ficha()
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    query = """
        SELECT j.id_jugador, j.id_usuario, j.id_acudiente, j.nombres, j.apellidos,
               j.documento, j.telefono, j.email, j.fecha_nacimiento,
               f.posicion, f.estatura, f.peso, f.id_estado, f.id_equipo, f.apodo,
               e.nombre_equipo, s.nombre AS division,
               ej.disponibilidad
        FROM jugador j
        LEFT JOIN ficha_jugador f ON j.id_jugador = f.id_jugador
        LEFT JOIN equipo e ON f.id_equipo = e.id_equipo
        LEFT JOIN subdivisiones s ON e.id_division = s.id_division
        LEFT JOIN estado_jugador ej ON f.id_estado = ej.id_estado
        WHERE j.id_jugador = %s
    """
    cursor.execute(query, (id_jugador,))
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()
    return datos

def nombre_en_ficha(datos):
    if datos.get('apodo'):
        return datos['apodo'].upper()
    if datos.get('apellidos'):
        return datos['apellidos'].split()[0].upper()
    if datos.get('nombres'):
        return datos['nombres'].split()[0].upper()
    return 'JUGADOR'

def edad_jugador(fecha_nacimiento):
    if not fecha_nacimiento:
        return None
    if isinstance(fecha_nacimiento, str):
        return calcular_edad(fecha_nacimiento)
    nacimiento = fecha_nacimiento
    fecha_hoy = datetime.now().date()
    return fecha_hoy.year - nacimiento.year - ((fecha_hoy.month, fecha_hoy.day) < (nacimiento.month, nacimiento.day))

def puede_ver_ficha_jugador(datos):
    if not datos:
        return False
    id_rol = obtener_id_rol_sesion()
    id_usuario = session.get('id_usuario')
    if id_rol in [1, 2, 3]:
        return True
    if id_rol == 4 and datos['id_usuario'] == id_usuario:
        return True
    if id_rol == 5:
        id_acudiente = obtener_id_acudiente_sesion()
        return id_acudiente and datos['id_acudiente'] == id_acudiente
    return False

def puede_editar_ficha_jugador(datos):
    if not puede_ver_ficha_jugador(datos):
        return False
    id_rol = obtener_id_rol_sesion()
    id_usuario = session.get('id_usuario')
    if id_rol in [1, 2, 3]:
        return True
    if id_rol == 4 and datos['id_usuario'] == id_usuario:
        return True
    if id_rol == 5:
        id_acudiente = obtener_id_acudiente_sesion()
        edad = edad_jugador(datos['fecha_nacimiento'])
        return id_acudiente and datos['id_acudiente'] == id_acudiente and edad is not None and edad < 18
    return False

def obtener_estados_jugador():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_estado, disponibilidad FROM estado_jugador ORDER BY id_estado ASC")
    estados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return estados

# ==========================================
# MÓDULO: REGISTRO/NUEVO USUARIO (JUGADOR O ACUDIENTE)
# ==========================================
@app.route('/registro', methods=['GET', 'POST'])
def registro_publico():
    if request.method == 'POST':
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True) # Usamos dictionary para las validaciones      
        # Recogemos los datos del formulario
        id_rol = request.form.get('rol') 
        documento = request.form.get('documento')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        contrasena = request.form.get('password')
        fecha_nacimiento = request.form.get('fecha_nacimiento')

        es_valido, mensaje_error, datos_persona = validar_campos_persona(
            telefono, documento=documento, nombres=nombres, apellidos=apellidos
        )
        if not es_valido:
            return render_template('registro.html', error=mensaje_error)
        documento = datos_persona['documento']
        telefono = datos_persona['telefono']
        nombres = datos_persona['nombres']
        apellidos = datos_persona['apellidos']

        # --------------------------------------------------------
        # BLOQUE DE PRUEBAS QA (VALIDACIONES DE SEGURIDAD Y NEGOCIO)
        # --------------------------------------------------------
        
        # 1. Validar que no existan clones
        cursor.execute("SELECT id_usuario FROM usuario WHERE usuario = %s OR email = %s", (documento, email))
        if cursor.fetchone():
            return render_template('registro.html', error='Estos datos (Documento o Email) ya están registrados en la escuela.')

        # 2. REGLAS DE NEGOCIO: Edades por Rol
        if id_rol == '5':
            es_valido, mensaje_error = validar_edad_acudiente(fecha_nacimiento)
            if not es_valido:
                return render_template('registro.html', error=mensaje_error)
        elif id_rol == '4':
            es_valido, mensaje_error = validar_edad_jugador(fecha_nacimiento)
            if not es_valido:
                return render_template('registro.html', error=mensaje_error)

        # --------------------------------------------------------
        # SI PASA LAS PRUEBAS, GUARDAMOS NORMALMENTE
        # --------------------------------------------------------
        cursor = conexion.cursor() # Volvemos al cursor normal para los inserts
        
        # Creamos la cuenta de usuario
        cursor.execute("INSERT INTO usuario (id_rol, usuario, contrasena, email, estado) VALUES (%s, %s, %s, %s, %s)",
                       (id_rol, documento, contrasena, email, 'Activo'))
        id_usuario_nuevo = cursor.lastrowid
        
        if id_rol == '4': # Jugador
            query_jugador = """
                INSERT INTO jugador (id_usuario, id_rol, documento, nombres, apellidos, fecha_nacimiento, telefono, email, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
            """
            cursor.execute(query_jugador, (id_usuario_nuevo, id_rol, documento, nombres, apellidos, fecha_nacimiento, telefono, email))
            
        elif id_rol == '5': # Acudiente
            query_acudiente = """
                INSERT INTO acudiente (id_usuario, id_rol, nombre, apellido, documento, fecha_nacimiento, telefono, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_acudiente, (id_usuario_nuevo, id_rol, nombres, apellidos, documento, fecha_nacimiento, telefono, email))
            
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return redirect('/')
        
    return render_template('registro.html')

# ==========================================
# MODULO: LOGIN/INICIO DE SESIÓN
# ==========================================
@app.route('/')
def home():
    # Flask buscará automáticamente este archivo dentro de la carpeta 'templates'
    return render_template('Login_Final.html')

# ==========================================
# MÓDULO: CERRAR SESIÓN
# ==========================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==========================================
# 3. RUTA DEL PROCESO DE LOGIN
# ==========================================
@app.route('/login', methods=['POST'])
def login():
    usuario_ingresado = request.form.get('username')
    contrasena_ingresada = request.form.get('password')
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Buscamos en la columna 'usuario' O en la columna 'email'
    query = "SELECT * FROM usuario WHERE (usuario = %s OR email = %s) AND contrasena = %s"
    cursor.execute(query, (usuario_ingresado, usuario_ingresado, contrasena_ingresada))
    cuenta = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    if cuenta:
        # Guardamos en sesión quién inició sesión y su rol para la navegación
        session['id_usuario'] = cuenta['id_usuario']
        session['id_rol'] = cuenta['id_rol']
        
        id_rol = cuenta['id_rol']
        
        # Redirecciones según el rol exacto
        if id_rol == 4:
            return redirect('/dashboard-jugador')
        elif id_rol == 5: # Asumiendo que 5 es Acudiente
            return redirect('/modulo-acudiente')
        elif id_rol == 3: # Asumiendo que 3 es Entrenador
            return redirect('/modulo-entrenador')
        else:
            return redirect('/dashboard-admin') # Administradores
    else:
        return "<h3>Usuario o contraseña incorrectos.</h3><p>Por favor, regresa e intenta de nuevo.</p>"
# ==========================================
# 4. VISTAS DE LOS DASHBOARDS
# ==========================================
@app.route('/dashboard-admin')
def dashboard_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if session.get('id_rol') not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))
    return render_template('dashboard_admin.html')

# ==========================================
# MÓDULO: DASHBOARD DEL ENTRENADOR
# ==========================================
@app.route('/modulo-entrenador')
def dashboard_entrenador():
    # Validación de seguridad: debe tener una sesión activa
    if 'id_usuario' not in session:
        return redirect('/')
        
    id_usuario_actual = session['id_usuario']
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Hacemos el JOIN para traer sus datos de contacto y credenciales
    query_entrenador = """
        SELECT e.id_entrenador, e.nombres, e.apellidos, e.telefono,
               u.usuario AS documento, u.email 
        FROM entrenador e
        JOIN usuario u ON e.id_usuario = u.id_usuario
        WHERE e.id_usuario = %s
    """
    cursor.execute(query_entrenador, (id_usuario_actual,))
    datos_entrenador = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    if not datos_entrenador:
        return "Error: No se encontraron los datos de este entrenador en la base de datos."
        
    return render_template('dashboard_entrenador.html', entrenador=datos_entrenador)

# ==========================================
# 5. MÓDULO: MI PERFIL / ACCESO
# ==========================================
@app.route('/mi-perfil')
def mi_perfil():
    if not usuario_tiene_sesion():
        return redirect('/')

    id_rol = obtener_id_rol_sesion()
    id_usuario_actual = session['id_usuario']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT usuario FROM usuario WHERE id_usuario = %s", (id_usuario_actual,))
    cuenta = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not cuenta:
        return redirect(panel_por_rol(id_rol))

    return render_template(
        'perfil_usuario.html',
        cuenta=cuenta,
        solo_contrasena=id_rol not in [1, 2],
        error=request.args.get('error'),
        exito=request.args.get('exito')
    )

@app.route('/actualizar-perfil', methods=['POST'])
def actualizar_perfil():
    if not usuario_tiene_sesion():
        return redirect('/')

    id_rol = obtener_id_rol_sesion()
    nueva_contrasena = request.form.get('password', '').strip()
    id_usuario_actual = session['id_usuario']

    if not nueva_contrasena or len(nueva_contrasena) < 4:
        return redirect(f'/mi-perfil?error={quote("La contraseña debe tener al menos 4 caracteres")}')

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if id_rol in [1, 2]:
        nuevo_usuario = request.form.get('username', '').strip()
        if not nuevo_usuario:
            cursor.close()
            conexion.close()
            return redirect(f'/mi-perfil?error={quote("El nombre de usuario no puede estar vacío")}')
        es_valido, mensaje_error = validar_solo_numeros(nuevo_usuario, 'El documento de usuario')
        if not es_valido:
            cursor.close()
            conexion.close()
            return redirect(f'/mi-perfil?error={quote(mensaje_error)}')
        nuevo_usuario = mensaje_error
        cursor.execute(
            "UPDATE usuario SET usuario = %s, contrasena = %s WHERE id_usuario = %s",
            (nuevo_usuario, nueva_contrasena, id_usuario_actual)
        )
    else:
        cursor.execute(
            "UPDATE usuario SET contrasena = %s WHERE id_usuario = %s",
            (nueva_contrasena, id_usuario_actual)
        )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(f'/mi-perfil?exito={quote("Contraseña actualizada correctamente")}')

# ==========================================
# MÓDULO: GESTIÓN DE JUGADORES (VISTA)
# ==========================================
def obtener_lista_jugadores():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT j.id_jugador, j.documento, j.nombres, j.apellidos,
               j.telefono, j.email, j.fecha_nacimiento, j.fecha_registro,
               a.nombre AS nombre_acudiente, a.apellido AS apellido_acudiente,
               u.estado, u.id_usuario
        FROM jugador j
        LEFT JOIN acudiente a ON j.id_acudiente = a.id_acudiente
        JOIN usuario u ON j.id_usuario = u.id_usuario
    """
    cursor.execute(query)
    jugadores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jugadores

def render_gestion_jugadores(error=None, jugadores=None, es_admin=True):
    return render_template(
        'gestion_jugadores.html',
        jugadores=jugadores if jugadores is not None else obtener_lista_jugadores(),
        es_admin=es_admin,
        error=error
    )

@app.route('/jugadores')
def gestion_jugadores():
    if not usuario_tiene_sesion():
        return redirect('/')
    id_rol = obtener_id_rol_sesion()
    if id_rol not in [1, 2, 3]:
        return redirect(panel_por_rol(id_rol))

    return render_gestion_jugadores(es_admin=id_rol in [1, 2])

# ==========================================
# MÓDULO: GESTIÓN DE ACUDIENTES (VISTA)
# ==========================================
def obtener_lista_acudientes():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT a.id_acudiente, a.id_usuario, a.nombre, a.apellido, a.documento,
               a.telefono, a.email, a.fecha_nacimiento, u.estado,
               (SELECT COUNT(*) FROM jugador j WHERE j.id_acudiente = a.id_acudiente) AS total_jugadores,
               (SELECT GROUP_CONCAT(CONCAT(j.nombres, ' ', j.apellidos) SEPARATOR ', ')
                FROM jugador j WHERE j.id_acudiente = a.id_acudiente) AS jugadores_a_cargo
        FROM acudiente a
        JOIN usuario u ON a.id_usuario = u.id_usuario
        ORDER BY a.apellido ASC, a.nombre ASC
    """
    cursor.execute(query)
    acudientes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return acudientes

def obtener_lista_jugadores_vinculacion():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT j.id_jugador, j.nombres, j.apellidos, j.documento, j.id_acudiente,
               CONCAT(a.nombre, ' ', a.apellido) AS nombre_acudiente_actual
        FROM jugador j
        LEFT JOIN acudiente a ON j.id_acudiente = a.id_acudiente
        ORDER BY j.apellidos ASC, j.nombres ASC
    """
    cursor.execute(query)
    jugadores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jugadores

def render_gestion_acudientes(error=None):
    id_rol = obtener_id_rol_sesion()
    return render_template(
        'gestion_acudientes.html',
        acudientes=obtener_lista_acudientes(),
        jugadores=obtener_lista_jugadores_vinculacion(),
        es_admin=id_rol in [1, 2],
        es_entrenador=id_rol == 3,
        error=error
    )

@app.route('/acudientes')
def gestion_acudientes():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2, 3]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    return render_gestion_acudientes()

# ==========================================
# RUTAS DE ACCIÓN: EDITAR Y BORRAR ACUDIENTES
# ==========================================
@app.route('/nuevo-acudiente-admin', methods=['POST'])
def nuevo_acudiente_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    documento = request.form.get('documento')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    contrasena = request.form.get('password')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    id_rol = '5'

    es_valido, mensaje_error, datos_persona = validar_campos_persona(
        telefono, documento=documento, nombres=nombres, apellidos=apellidos
    )
    if not es_valido:
        return render_gestion_acudientes(error=mensaje_error)
    documento = datos_persona['documento']
    telefono = datos_persona['telefono']
    nombres = datos_persona['nombres']
    apellidos = datos_persona['apellidos']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_usuario FROM usuario WHERE usuario = %s OR email = %s", (documento, email))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        return render_gestion_acudientes(error='Estos datos (Documento o Email) ya están registrados en la escuela.')

    es_valido, mensaje_error = validar_edad_acudiente(fecha_nacimiento)
    if not es_valido:
        cursor.close()
        conexion.close()
        return render_gestion_acudientes(error=mensaje_error)

    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO usuario (id_rol, usuario, contrasena, email, estado) VALUES (%s, %s, %s, %s, %s)",
        (id_rol, documento, contrasena, email, 'Activo')
    )
    id_usuario_nuevo = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO acudiente (id_usuario, id_rol, nombre, apellido, documento, fecha_nacimiento, telefono, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (id_usuario_nuevo, id_rol, nombres, apellidos, documento, fecha_nacimiento, telefono, email)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/acudientes')

@app.route('/vincular-jugadores-acudiente', methods=['POST'])
def vincular_jugadores_acudiente():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2, 3]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_acudiente = request.form.get('id_acudiente')
    jugadores_seleccionados = request.form.getlist('jugadores')

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("UPDATE jugador SET id_acudiente = NULL WHERE id_acudiente = %s", (id_acudiente,))

    for id_jugador in jugadores_seleccionados:
        cursor.execute(
            "UPDATE jugador SET id_acudiente = %s WHERE id_jugador = %s",
            (id_acudiente, id_jugador)
        )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/acudientes')

@app.route('/editar-acudiente-admin', methods=['POST'])
def editar_acudiente_admin():
    id_acudiente = request.form.get('id_acudiente')
    id_usuario = request.form.get('id_usuario')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    documento = request.form.get('documento')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    estado = request.form.get('estado')

    es_valido, mensaje_error, datos_persona = validar_campos_persona(
        telefono, documento=documento, nombre=nombre, apellido=apellido
    )
    if not es_valido:
        return render_gestion_acudientes(error=mensaje_error)
    documento = datos_persona['documento']
    telefono = datos_persona['telefono']
    nombre = datos_persona['nombre']
    apellido = datos_persona['apellido']

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE acudiente
        SET nombre = %s, apellido = %s, documento = %s, telefono = %s, email = %s
        WHERE id_acudiente = %s
    """, (nombre, apellido, documento, telefono, email, id_acudiente))

    cursor.execute("""
        UPDATE usuario
        SET estado = %s, email = %s
        WHERE id_usuario = %s
    """, (estado, email, id_usuario))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/acudientes')

@app.route('/borrar-acudiente-admin', methods=['POST'])
def borrar_acudiente_admin():
    id_acudiente = request.form.get('id_acudiente')

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_usuario FROM acudiente WHERE id_acudiente = %s", (id_acudiente,))
    resultado = cursor.fetchone()

    # Desvinculamos jugadores antes de borrar para evitar Error 1451
    cursor.execute("UPDATE jugador SET id_acudiente = NULL WHERE id_acudiente = %s", (id_acudiente,))
    cursor.execute("DELETE FROM acudiente WHERE id_acudiente = %s", (id_acudiente,))

    if resultado:
        cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (resultado['id_usuario'],))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/acudientes')

# ==========================================
# RUTAS DE ACCIÓN: CREAR, EDITAR Y BORRAR JUGADORES
# ==========================================
@app.route('/nuevo-jugador-admin', methods=['POST'])
def nuevo_jugador_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    documento = request.form.get('documento')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    contrasena = request.form.get('password')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    id_rol = '4'

    es_valido, mensaje_error, datos_persona = validar_campos_persona(
        telefono, documento=documento, nombres=nombres, apellidos=apellidos
    )
    if not es_valido:
        return render_gestion_jugadores(error=mensaje_error)
    documento = datos_persona['documento']
    telefono = datos_persona['telefono']
    nombres = datos_persona['nombres']
    apellidos = datos_persona['apellidos']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_usuario FROM usuario WHERE usuario = %s OR email = %s", (documento, email))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        return render_gestion_jugadores(error='Estos datos (Documento o Email) ya están registrados en la escuela.')

    es_valido, mensaje_error = validar_edad_jugador(fecha_nacimiento)
    if not es_valido:
        cursor.close()
        conexion.close()
        return render_gestion_jugadores(error=mensaje_error)

    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO usuario (id_rol, usuario, contrasena, email, estado) VALUES (%s, %s, %s, %s, %s)",
        (id_rol, documento, contrasena, email, 'Activo')
    )
    id_usuario_nuevo = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO jugador (id_usuario, id_rol, documento, nombres, apellidos, fecha_nacimiento, telefono, email, fecha_registro)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
        """,
        (id_usuario_nuevo, id_rol, documento, nombres, apellidos, fecha_nacimiento, telefono, email)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/jugadores')

@app.route('/editar-jugador-admin', methods=['POST'])
def editar_jugador_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    # 1. Recogemos los datos del formulario modal
    id_jugador = request.form.get('id_jugador')
    id_usuario = request.form.get('id_usuario')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    estado = request.form.get('estado')

    es_valido, mensaje_error, datos_persona = validar_campos_persona(
        telefono, nombres=nombres, apellidos=apellidos
    )
    if not es_valido:
        return render_gestion_jugadores(error=mensaje_error)
    telefono = datos_persona['telefono']
    nombres = datos_persona['nombres']
    apellidos = datos_persona['apellidos']

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 2. Actualizamos los datos personales en la tabla jugador
    cursor.execute("""
        UPDATE jugador 
        SET nombres = %s, apellidos = %s, telefono = %s, email = %s 
        WHERE id_jugador = %s
    """, (nombres, apellidos, telefono, email, id_jugador))

    # 3. Actualizamos el estado de acceso y el email en la tabla usuario
    cursor.execute("""
        UPDATE usuario 
        SET estado = %s, email = %s
        WHERE id_usuario = %s
    """, (estado, email, id_usuario))

    conexion.commit()
    cursor.close()
    conexion.close()
    
    return redirect('/jugadores')

@app.route('/borrar-jugador-admin', methods=['POST'])
def borrar_jugador_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_jugador = request.form.get('id_jugador')
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Buscamos el ID del usuario asociado antes de empezar a borrar
    cursor.execute("SELECT id_usuario FROM jugador WHERE id_jugador = %s", (id_jugador,))
    resultado = cursor.fetchone()

    # ELIMINACIÓN EN CASCADA (Orden estricto de hijos a padres para evitar Error 1451)
    cursor.execute("DELETE FROM asistencia WHERE id_jugador = %s", (id_jugador,))
    cursor.execute("DELETE FROM ficha_jugador WHERE id_jugador = %s", (id_jugador,))
    cursor.execute("DELETE FROM detalle_pago WHERE id_pago IN (SELECT id_pago FROM pago WHERE id_jugador = %s)", (id_jugador,))
    cursor.execute("DELETE FROM pago WHERE id_jugador = %s", (id_jugador,))
    cursor.execute("DELETE FROM jugador WHERE id_jugador = %s", (id_jugador,))
    
    if resultado:
        cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (resultado['id_usuario'],))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/jugadores')

# ==========================================
# MÓDULO: DASHBOARD DEL JUGADOR
# ==========================================
@app.route('/dashboard-jugador')
def dashboard_jugador():
    if 'id_usuario' not in session:
        return redirect('/')
        
    id_usuario_actual = session['id_usuario']
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # IMPORTANTE: Ahora también traemos la fecha_nacimiento y el id_acudiente
    query = """
        SELECT nombres, apellidos, documento, email, telefono, fecha_nacimiento, id_acudiente 
        FROM jugador 
        WHERE id_usuario = %s
    """
    cursor.execute(query, (id_usuario_actual,))
    datos_jugador = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    if not datos_jugador:
        return "Error: No se encontraron los datos de este jugador."
        
    # LÓGICA DE BLOQUEO PARA MENORES SIN ACUDIENTE
    nacimiento = datos_jugador['fecha_nacimiento']
    # En caso de que MySQL lo devuelva como texto, lo pasamos a fecha
    if isinstance(nacimiento, str):
        nacimiento = datetime.strptime(nacimiento, '%Y-%m-%d').date()
        
    fecha_hoy = datetime.now().date()
    edad = fecha_hoy.year - nacimiento.year - ((fecha_hoy.month, fecha_hoy.day) < (nacimiento.month, nacimiento.day))
    
    # La regla: Está bloqueado SI tiene menos de 18 años Y (and) su id_acudiente es nulo (None)
    bloqueado = (edad < 18) and (datos_jugador['id_acudiente'] is None)
        
    # Le mandamos la variable 'bloqueado' al HTML para que decida qué mostrar
    return render_template('dashboard_jugador.html', jugador=datos_jugador, bloqueado=bloqueado)

@app.route('/mi-acudiente')
def mi_acudiente():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() != 4:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_acudiente FROM jugador WHERE id_usuario = %s",
        (session['id_usuario'],)
    )
    jugador = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not jugador or not jugador.get('id_acudiente'):
        return render_template('mi_acudiente.html', acudiente=None, sin_acudiente=True)

    acudiente = obtener_datos_acudiente_por_id(jugador['id_acudiente'])
    return render_template('mi_acudiente.html', acudiente=acudiente, sin_acudiente=False)

@app.route('/mis-jugadores')
def mis_jugadores():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() != 5:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_acudiente = obtener_id_acudiente_sesion()
    if not id_acudiente:
        return render_template('mis_jugadores.html', jugadores=[], error='No se encontró tu perfil de acudiente.')

    return render_template(
        'mis_jugadores.html',
        jugadores=obtener_jugadores_por_acudiente(id_acudiente),
        error=request.args.get('error')
    )

@app.route('/editar-jugador-acudiente', methods=['POST'])
def editar_jugador_acudiente():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() != 5:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_jugador = request.form.get('id_jugador')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    email = request.form.get('email')

    es_valido, mensaje_error, datos_persona = validar_campos_persona(
        telefono, nombres=nombres, apellidos=apellidos
    )
    if not es_valido:
        return redirect(f'/mis-jugadores?error={quote(mensaje_error)}')

    nombres = datos_persona['nombres']
    apellidos = datos_persona['apellidos']
    telefono = datos_persona['telefono']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_jugador, id_usuario, id_acudiente, fecha_nacimiento FROM jugador WHERE id_jugador = %s",
        (id_jugador,)
    )
    jugador = cursor.fetchone()
    if not jugador or not puede_editar_datos_jugador_acudiente(jugador):
        cursor.close()
        conexion.close()
        return redirect('/mis-jugadores')

    cursor.execute("""
        UPDATE jugador
        SET nombres = %s, apellidos = %s, telefono = %s, email = %s
        WHERE id_jugador = %s
    """, (nombres, apellidos, telefono, email, id_jugador))
    cursor.execute(
        "UPDATE usuario SET email = %s WHERE id_usuario = %s",
        (email, jugador['id_usuario'])
    )
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/mis-jugadores')

# ==========================================
# MÓDULO: DASHBOARD DEL ACUDIENTE
# ==========================================
@app.route('/modulo-acudiente')
def dashboard_acudiente():
    if 'id_usuario' not in session:
        return redirect('/')
        
    id_usuario_actual = session['id_usuario']
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Hacemos un JOIN con la tabla usuario para traer el email y el documento (que es el nombre de usuario)
    query_acudiente = """
        SELECT a.id_acudiente, a.nombre, a.apellido, a.telefono,
               u.usuario AS documento, u.email 
        FROM acudiente a
        JOIN usuario u ON a.id_usuario = u.id_usuario
        WHERE a.id_usuario = %s
    """
    cursor.execute(query_acudiente, (id_usuario_actual,))
    datos_acudiente = cursor.fetchone()
    
    if not datos_acudiente:
        cursor.close()
        conexion.close()
        return "Error: No se encontraron los datos de este acudiente."

    # Buscamos a los jugadores que están a su cargo
    query_hijos = """
        SELECT id_jugador, nombres, apellidos, documento, fecha_nacimiento
        FROM jugador
        WHERE id_acudiente = %s
    """
    cursor.execute(query_hijos, (datos_acudiente['id_acudiente'],))
    jugadores_acargo = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return render_template('dashboard_acudiente.html', acudiente=datos_acudiente, hijos=jugadores_acargo)

# ==========================================
# MÓDULO: GESTIÓN Y VISUALIZACIÓN DE EQUIPOS
# ==========================================
def obtener_datos_equipos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_equipo, nombre_equipo FROM equipo ORDER BY nombre_equipo ASC")
    lista_equipos = cursor.fetchall()

    cursor.execute("SELECT id_division, nombre FROM subdivisiones ORDER BY id_division ASC")
    subdivisiones = cursor.fetchall()

    equipos_db = {eq['nombre_equipo']: [] for eq in lista_equipos}

    query = """
        SELECT
            COALESCE(e.id_equipo, 0) AS id_equipo,
            COALESCE(e.nombre_equipo, 'Nuevos (Sin Equipo)') AS nombre_equipo,
            j.id_jugador, j.nombres, j.apellidos,
            COALESCE(f.posicion, 'Por definir') AS posicion
        FROM jugador j
        LEFT JOIN ficha_jugador f ON j.id_jugador = f.id_jugador
        LEFT JOIN equipo e ON f.id_equipo = e.id_equipo
        ORDER BY e.id_equipo ASC, f.posicion ASC
    """
    cursor.execute(query)
    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    for fila in resultados:
        equipo_nombre = fila['nombre_equipo']
        if equipo_nombre not in equipos_db:
            equipos_db[equipo_nombre] = []

        equipos_db[equipo_nombre].append({
            "id_jugador": fila['id_jugador'],
            "id_equipo": fila['id_equipo'],
            "nombres": fila['nombres'],
            "apellidos": fila['apellidos'],
            "posicion": fila['posicion']
        })

    if not equipos_db.get('Nuevos (Sin Equipo)'):
        equipos_db.pop('Nuevos (Sin Equipo)', None)

    return equipos_db, lista_equipos, subdivisiones

def render_modulo_equipos(error=None):
    id_rol = obtener_id_rol_sesion()
    es_admin = id_rol in [1, 2]
    es_entrenador = id_rol in [1, 2, 3] if id_rol else False
    puede_crear_equipo = id_rol in [1, 2, 3]
    equipos_db, lista_equipos, subdivisiones = obtener_datos_equipos()

    return render_template(
        'equipos.html',
        equipos=equipos_db,
        es_entrenador=es_entrenador,
        es_admin=es_admin,
        puede_crear_equipo=puede_crear_equipo,
        id_rol=id_rol,
        lista_equipos=lista_equipos,
        subdivisiones=subdivisiones,
        error=error
    )

@app.route('/equipos')
def modulo_equipos():
    if not usuario_tiene_sesion():
        return redirect('/')

    return render_modulo_equipos()

@app.route('/nuevo-equipo', methods=['POST'])
def nuevo_equipo():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2, 3]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    nombre_equipo = request.form.get('nombre_equipo', '').strip()
    id_division = request.form.get('id_division')

    if not nombre_equipo:
        return render_modulo_equipos(error='El nombre del equipo es obligatorio.')
    if not id_division:
        return render_modulo_equipos(error='Debes seleccionar una subdivisión.')

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_division FROM subdivisiones WHERE id_division = %s", (id_division,))
    if not cursor.fetchone():
        cursor.close()
        conexion.close()
        return render_modulo_equipos(error='La subdivisión seleccionada no es válida.')

    cursor.execute("SELECT id_equipo FROM equipo WHERE nombre_equipo = %s", (nombre_equipo,))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        return render_modulo_equipos(error='Ya existe un equipo con ese nombre.')

    cursor.execute("SELECT COALESCE(MAX(id_equipo), 0) + 1 AS nuevo_id FROM equipo")
    nuevo_id = cursor.fetchone()['nuevo_id']

    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO equipo (id_equipo, id_division, nombre_equipo) VALUES (%s, %s, %s)",
        (nuevo_id, id_division, nombre_equipo)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/equipos')

# ==========================================
# RUTAS DE ACCIÓN: MOVER Y ELIMINAR JUGADOR
# ==========================================
@app.route('/mover-jugador', methods=['POST'])
def mover_jugador():
    id_jugador = request.form.get('id_jugador')
    nuevo_equipo = request.form.get('nuevo_equipo')
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Verificamos si el jugador ya tiene una ficha creada o si está en ceros
    cursor.execute("SELECT id_jugador FROM ficha_jugador WHERE id_jugador = %s", (id_jugador,))
    tiene_ficha = cursor.fetchone()
    
    if tiene_ficha:
        # Si ya tiene, simplemente lo cambiamos de equipo (UPDATE)
        cursor.execute("UPDATE ficha_jugador SET id_equipo = %s WHERE id_jugador = %s", (nuevo_equipo, id_jugador))
    else:
        # Si es nuevo, le CREAMOS su ficha (INSERT) asignándole estado 1 (Disponible)
        cursor.execute("""
            INSERT INTO ficha_jugador (id_jugador, id_equipo, id_estado, posicion, estatura, peso) 
            VALUES (%s, %s, 1, 'Por definir', 0.00, 0.00)
        """, (id_jugador, nuevo_equipo))
        
    conexion.commit()
    cursor.close()
    conexion.close()
    
    return redirect('/equipos')

@app.route('/eliminar-jugador', methods=['POST'])
def eliminar_jugador():
    id_jugador = request.form.get('id_jugador')
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("SELECT id_usuario FROM jugador WHERE id_jugador = %s", (id_jugador,))
    resultado = cursor.fetchone()
    
    # Eliminación en cascada segura
    cursor.execute("DELETE FROM ficha_jugador WHERE id_jugador = %s", (id_jugador,))
    cursor.execute("DELETE FROM pago WHERE id_jugador = %s", (id_jugador,))
    cursor.execute("DELETE FROM jugador WHERE id_jugador = %s", (id_jugador,))
    if resultado:
        cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (resultado['id_usuario'],))
        
    conexion.commit()
    cursor.close()
    conexion.close()
    
    return redirect('/equipos')

# ==========================================
# MÓDULO: GESTIÓN DE ENTRENADORES
# ==========================================
def obtener_lista_entrenadores(solo_activos=False):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT e.id_entrenador, e.id_usuario, e.documento, e.nombres, e.apellidos,
               e.telefono, e.email, e.especialidad, e.fecha_nacimiento, u.estado
        FROM entrenador e
        JOIN usuario u ON e.id_usuario = u.id_usuario
    """
    if solo_activos:
        query += " WHERE u.estado = 'Activo'"
    query += " ORDER BY e.apellidos ASC, e.nombres ASC"
    cursor.execute(query)
    entrenadores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return entrenadores

def render_gestion_entrenadores(error=None, es_admin=True):
    return render_template(
        'gestion_entrenadores.html',
        entrenadores=obtener_lista_entrenadores(),
        especialidades=ESPECIALIDADES_ENTRENADOR,
        es_admin=es_admin,
        error=error
    )

@app.route('/entrenadores')
def gestion_entrenadores():
    if not usuario_tiene_sesion():
        return redirect('/')
    id_rol = obtener_id_rol_sesion()
    if id_rol not in [1, 2, 3]:
        return redirect(panel_por_rol(id_rol))

    return render_gestion_entrenadores(es_admin=id_rol in [1, 2])

@app.route('/nuevo-entrenador-admin', methods=['POST'])
def nuevo_entrenador_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    documento = request.form.get('documento')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    contrasena = request.form.get('password')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    especialidad = request.form.get('especialidad')
    id_rol = '3'

    es_valido, mensaje_error, datos_persona = validar_campos_persona(
        telefono, documento=documento, nombres=nombres, apellidos=apellidos
    )
    if not es_valido:
        return render_gestion_entrenadores(error=mensaje_error)
    documento = datos_persona['documento']
    telefono = datos_persona['telefono']
    nombres = datos_persona['nombres']
    apellidos = datos_persona['apellidos']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_usuario FROM usuario WHERE usuario = %s OR email = %s", (documento, email))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        return render_gestion_entrenadores(error='Estos datos (Documento o Email) ya están registrados en la escuela.')

    es_valido, mensaje_error = validar_edad_acudiente(fecha_nacimiento)
    if not es_valido:
        cursor.close()
        conexion.close()
        return render_gestion_entrenadores(error=mensaje_error)

    es_valido, mensaje_error = validar_especialidad_entrenador(especialidad)
    if not es_valido:
        cursor.close()
        conexion.close()
        return render_gestion_entrenadores(error=mensaje_error)

    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO usuario (id_rol, usuario, contrasena, email, estado) VALUES (%s, %s, %s, %s, %s)",
        (id_rol, documento, contrasena, email, 'Activo')
    )
    id_usuario_nuevo = cursor.lastrowid

    cursor.execute("SELECT COALESCE(MAX(id_entrenador), 0) + 1 AS nuevo_id FROM entrenador")
    nuevo_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO entrenador (id_entrenador, id_usuario, id_rol, nombres, apellidos, documento, fecha_nacimiento, telefono, email, especialidad)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (nuevo_id, id_usuario_nuevo, id_rol, nombres, apellidos, documento, fecha_nacimiento, telefono, email, especialidad)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/entrenadores')

@app.route('/cuerpo-tecnico')
def cuerpo_tecnico():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [4, 5]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_rol = obtener_id_rol_sesion()
    return render_template(
        'cuerpo_tecnico.html',
        entrenadores=obtener_lista_entrenadores(solo_activos=True),
        id_rol=id_rol
    )

@app.route('/editar-entrenador-admin', methods=['POST'])
def editar_entrenador_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_entrenador = request.form.get('id_entrenador')
    id_usuario = request.form.get('id_usuario')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    documento = request.form.get('documento')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    especialidad = request.form.get('especialidad')
    estado = request.form.get('estado')

    es_valido, mensaje_error, datos_persona = validar_campos_persona(
        telefono, documento=documento, nombres=nombres, apellidos=apellidos
    )
    if not es_valido:
        return render_gestion_entrenadores(error=mensaje_error)
    documento = datos_persona['documento']
    telefono = datos_persona['telefono']
    nombres = datos_persona['nombres']
    apellidos = datos_persona['apellidos']

    es_valido, mensaje_error = validar_especialidad_entrenador(especialidad)
    if not es_valido:
        return render_gestion_entrenadores(error=mensaje_error)

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE entrenador
        SET nombres = %s, apellidos = %s, documento = %s, telefono = %s, email = %s, especialidad = %s
        WHERE id_entrenador = %s
    """, (nombres, apellidos, documento, telefono, email, especialidad, id_entrenador))

    cursor.execute("""
        UPDATE usuario SET usuario = %s, estado = %s, email = %s WHERE id_usuario = %s
    """, (documento, estado, email, id_usuario))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/entrenadores')

@app.route('/borrar-entrenador-admin', methods=['POST'])
def borrar_entrenador_admin():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_entrenador = request.form.get('id_entrenador')

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_usuario FROM entrenador WHERE id_entrenador = %s", (id_entrenador,))
    resultado = cursor.fetchone()

    cursor.execute("DELETE FROM entrenamiento WHERE id_entrenador = %s", (id_entrenador,))
    cursor.execute("DELETE FROM entrenador WHERE id_entrenador = %s", (id_entrenador,))

    if resultado:
        cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (resultado['id_usuario'],))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/entrenadores')

# ==========================================
# MÓDULO: FICHA TÉCNICA DEL JUGADOR
# ==========================================
def render_ficha_tecnica(id_jugador, error=None, exito=None):
    datos = obtener_datos_ficha_jugador(id_jugador)
    if not datos or not puede_ver_ficha_jugador(datos):
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_rol = obtener_id_rol_sesion()
    return render_template(
        'ficha_tecnica.html',
        jugador=datos,
        edad=edad_jugador(datos['fecha_nacimiento']),
        nombre_ficha=nombre_en_ficha(datos),
        puede_editar=puede_editar_ficha_jugador(datos),
        estados=obtener_estados_jugador(),
        posiciones=POSICIONES_JUGADOR,
        id_rol=id_rol,
        error=error,
        exito=exito
    )

@app.route('/ficha-tecnica')
def ficha_tecnica_propia():
    if not usuario_tiene_sesion():
        return redirect('/')

    id_rol = obtener_id_rol_sesion()
    if id_rol == 4:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_jugador FROM jugador WHERE id_usuario = %s", (session['id_usuario'],))
        fila = cursor.fetchone()
        cursor.close()
        conexion.close()
        if not fila:
            return redirect('/dashboard-jugador')
        return render_ficha_tecnica(fila['id_jugador'])

    if id_rol in [1, 2, 3]:
        return redirect('/jugadores')

    return redirect(panel_por_rol(id_rol))

@app.route('/ficha-tecnica/<int:id_jugador>')
def ficha_tecnica_jugador(id_jugador):
    if not usuario_tiene_sesion():
        return redirect('/')
    return render_ficha_tecnica(id_jugador)

@app.route('/guardar-ficha-tecnica', methods=['POST'])
def guardar_ficha_tecnica():
    if not usuario_tiene_sesion():
        return redirect('/')

    id_jugador = request.form.get('id_jugador')
    datos = obtener_datos_ficha_jugador(id_jugador)

    if not datos or not puede_editar_ficha_jugador(datos):
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    apodo = request.form.get('apodo', '').strip()
    posicion = request.form.get('posicion')
    estatura = request.form.get('estatura')
    peso = request.form.get('peso')
    id_estado = request.form.get('id_estado')

    es_valido, resultado_apodo = validar_apodo_ficha(apodo)
    if not es_valido:
        return render_ficha_tecnica(id_jugador, error=resultado_apodo)

    if posicion not in POSICIONES_JUGADOR:
        return render_ficha_tecnica(id_jugador, error='La posición seleccionada no es válida.')

    es_valido, resultado_estatura = validar_numero_decimal(estatura, 'La estatura')
    if not es_valido:
        return render_ficha_tecnica(id_jugador, error=resultado_estatura)
    es_valido, resultado_peso = validar_numero_decimal(peso, 'El peso')
    if not es_valido:
        return render_ficha_tecnica(id_jugador, error=resultado_peso)
    estatura_val = resultado_estatura
    peso_val = resultado_peso
    if estatura_val > 2.50 or peso_val > 200:
        return render_ficha_tecnica(id_jugador, error='Estatura o peso fuera del rango permitido.')

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_estado FROM estado_jugador WHERE id_estado = %s", (id_estado,))
    if not cursor.fetchone():
        cursor.close()
        conexion.close()
        return render_ficha_tecnica(id_jugador, error='El estado seleccionado no es válido.')

    cursor = conexion.cursor()
    cursor.execute("SELECT id_jugador FROM ficha_jugador WHERE id_jugador = %s", (id_jugador,))
    tiene_ficha = cursor.fetchone()

    if tiene_ficha:
        cursor.execute("""
            UPDATE ficha_jugador
            SET apodo = %s, posicion = %s, estatura = %s, peso = %s, id_estado = %s
            WHERE id_jugador = %s
        """, (resultado_apodo, posicion, estatura_val, peso_val, id_estado, id_jugador))
    else:
        cursor.execute("SELECT id_equipo FROM equipo ORDER BY id_equipo ASC LIMIT 1")
        equipo_default = cursor.fetchone()
        id_equipo = equipo_default[0] if equipo_default else 1
        cursor.execute("""
            INSERT INTO ficha_jugador (id_jugador, id_equipo, id_estado, posicion, estatura, peso, apodo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_jugador, id_equipo, id_estado, posicion, estatura_val, peso_val, resultado_apodo))

    conexion.commit()
    cursor.close()
    conexion.close()

    return render_ficha_tecnica(id_jugador, exito='Ficha técnica actualizada correctamente.')

# ==========================================
# MÓDULO: ASISTENCIAS
# ==========================================
# asistio: 1 = presente (verde), 0 = ausente (rojo), 2 = justificado (azul)

MESES_ES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

def asegurar_columna_observacion_asistencia():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(*) AS existe
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'asistencia'
          AND COLUMN_NAME = 'observacion'
    """)
    if cursor.fetchone()['existe'] == 0:
        cursor = conexion.cursor()
        cursor.execute("ALTER TABLE asistencia ADD COLUMN observacion VARCHAR(255) DEFAULT NULL")
        conexion.commit()
    cursor.close()
    conexion.close()

def obtener_id_entrenador_sesion():
    if obtener_id_rol_sesion() != 3:
        return None
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_entrenador FROM entrenador WHERE id_usuario = %s", (session['id_usuario'],))
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    return fila['id_entrenador'] if fila else None

def obtener_lista_equipos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_equipo, nombre_equipo FROM equipo ORDER BY nombre_equipo ASC")
    equipos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return equipos

def obtener_jugadores_vista_asistencias(id_rol):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if id_rol == 4:
        cursor.execute(
            "SELECT id_jugador, nombres, apellidos FROM jugador WHERE id_usuario = %s",
            (session['id_usuario'],)
        )
    elif id_rol == 5:
        id_acudiente = obtener_id_acudiente_sesion()
        if not id_acudiente:
            cursor.close()
            conexion.close()
            return []
        cursor.execute(
            """
            SELECT id_jugador, nombres, apellidos
            FROM jugador WHERE id_acudiente = %s
            ORDER BY apellidos ASC, nombres ASC
            """,
            (id_acudiente,)
        )
    else:
        cursor.execute(
            """
            SELECT j.id_jugador, j.nombres, j.apellidos
            FROM jugador j
            ORDER BY j.apellidos ASC, j.nombres ASC
            """
        )

    jugadores = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jugadores

def jugador_permitido_asistencias(id_jugador, id_rol):
    permitidos = obtener_jugadores_vista_asistencias(id_rol)
    return any(j['id_jugador'] == int(id_jugador) for j in permitidos)

def obtener_registros_asistencia_mes(id_jugador, anio, mes):
    asegurar_columna_observacion_asistencia()
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT e.fecha, a.asistio, a.observacion, e.ubicacion, e.tipo_entrenamiento,
               eq.nombre_equipo
        FROM asistencia a
        JOIN entrenamiento e ON a.id_entrenamiento = e.id_entrenamiento
        JOIN equipo eq ON e.id_equipo = eq.id_equipo
        WHERE a.id_jugador = %s AND YEAR(e.fecha) = %s AND MONTH(e.fecha) = %s
        ORDER BY e.fecha ASC
        """,
        (id_jugador, anio, mes)
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()

    registros = {}
    for fila in filas:
        clave = fila['fecha'].strftime('%Y-%m-%d') if hasattr(fila['fecha'], 'strftime') else str(fila['fecha'])
        registros[clave] = fila
    return registros

def calcular_estadisticas_mes(registros):
    total = len(registros)
    presentes = sum(1 for r in registros.values() if r['asistio'] == 1)
    ausentes = sum(1 for r in registros.values() if r['asistio'] == 0)
    justificados = sum(1 for r in registros.values() if r['asistio'] == 2)
    porcentaje = round((presentes / total) * 100) if total else 0
    return {
        'total': total,
        'presentes': presentes,
        'ausentes': ausentes,
        'justificados': justificados,
        'porcentaje': porcentaje
    }

def construir_calendario_mes(anio, mes, registros):
    semanas = []
    for semana in calendar.Calendar(firstweekday=0).monthdatescalendar(anio, mes):
        dias = []
        for dia in semana:
            if dia.month != mes:
                dias.append({'vacio': True})
                continue
            clave = dia.strftime('%Y-%m-%d')
            registro = registros.get(clave)
            estado = registro['asistio'] if registro else None
            dias.append({
                'vacio': False,
                'dia': dia.day,
                'fecha': clave,
                'estado': estado,
                'observacion': registro.get('observacion') if registro else None,
                'ubicacion': registro.get('ubicacion') if registro else None,
                'equipo': registro.get('nombre_equipo') if registro else None,
                'tipo': registro.get('tipo_entrenamiento') if registro else None,
                'es_hoy': dia == date.today(),
                'futuro': dia > date.today()
            })
        semanas.append(dias)
    return semanas

def obtener_jugadores_equipo_para_lista(id_equipo, id_entrenamiento=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    if id_entrenamiento:
        cursor.execute(
            """
            SELECT j.id_jugador, j.nombres, j.apellidos,
                   a.asistio, a.observacion
            FROM jugador j
            JOIN ficha_jugador f ON j.id_jugador = f.id_jugador
            LEFT JOIN asistencia a ON a.id_jugador = j.id_jugador AND a.id_entrenamiento = %s
            WHERE f.id_equipo = %s
            ORDER BY j.apellidos ASC, j.nombres ASC
            """,
            (id_entrenamiento, id_equipo)
        )
    else:
        cursor.execute(
            """
            SELECT j.id_jugador, j.nombres, j.apellidos,
                   NULL AS asistio, NULL AS observacion
            FROM jugador j
            JOIN ficha_jugador f ON j.id_jugador = f.id_jugador
            WHERE f.id_equipo = %s
            ORDER BY j.apellidos ASC, j.nombres ASC
            """,
            (id_equipo,)
        )
    jugadores = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jugadores

def obtener_o_crear_entrenamiento(id_entrenador, id_equipo, fecha, ubicacion, tipo_entrenamiento):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_entrenamiento FROM entrenamiento WHERE id_equipo = %s AND fecha = %s",
        (id_equipo, fecha)
    )
    existente = cursor.fetchone()
    if existente:
        cursor.close()
        conexion.close()
        return existente['id_entrenamiento']

    cursor.execute("SELECT COALESCE(MAX(id_entrenamiento), 0) + 1 AS nuevo_id FROM entrenamiento")
    nuevo_id = cursor.fetchone()['nuevo_id']
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO entrenamiento (id_entrenamiento, id_entrenador, id_equipo, fecha, ubicacion, tipo_entrenamiento)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (nuevo_id, id_entrenador, id_equipo, fecha, ubicacion, tipo_entrenamiento)
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return nuevo_id

def render_asistencias(error=None, exito=None):
    if not usuario_tiene_sesion():
        return redirect('/')

    if request.args.get('guardado') == '1' and not exito:
        exito = 'Lista de asistencia guardada correctamente.'

    id_rol = obtener_id_rol_sesion()
    if id_rol not in [1, 2, 3, 4, 5]:
        return redirect(panel_por_rol(id_rol))

    hoy = date.today()
    try:
        mes = int(request.args.get('mes', hoy.month))
        anio = int(request.args.get('anio', hoy.year))
    except (TypeError, ValueError):
        mes, anio = hoy.month, hoy.year

    mes = max(1, min(12, mes))
    puede_registrar = id_rol in [1, 2, 3]
    jugadores_vista = obtener_jugadores_vista_asistencias(id_rol)

    if id_rol in [4, 5] and not jugadores_vista:
        return render_template(
            'asistencias.html',
            id_rol=id_rol,
            puede_registrar=False,
            sin_jugadores=True,
            mes=mes,
            anio=anio,
            nombre_mes=MESES_ES[mes],
            error=error,
            exito=exito
        )

    id_jugador_sel = request.args.get('id_jugador')
    if id_jugador_sel:
        id_jugador_sel = int(id_jugador_sel)
    elif jugadores_vista:
        id_jugador_sel = jugadores_vista[0]['id_jugador']
    else:
        id_jugador_sel = None

    if id_jugador_sel and id_rol in [4, 5] and not jugador_permitido_asistencias(id_jugador_sel, id_rol):
        return redirect(url_for('modulo_asistencias'))

    registros = obtener_registros_asistencia_mes(id_jugador_sel, anio, mes) if id_jugador_sel else {}
    estadisticas = calcular_estadisticas_mes(registros)
    semanas = construir_calendario_mes(anio, mes, registros)

    mes_anterior = mes - 1 if mes > 1 else 12
    anio_anterior = anio if mes > 1 else anio - 1
    mes_siguiente = mes + 1 if mes < 12 else 1
    anio_siguiente = anio if mes < 12 else anio + 1

    fecha_lista = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
    id_equipo_lista = request.args.get('id_equipo')
    equipos = obtener_lista_equipos() if puede_registrar else []
    if puede_registrar and not id_equipo_lista and equipos:
        id_equipo_lista = str(equipos[0]['id_equipo'])

    id_entrenamiento_lista = None
    jugadores_lista = []
    if puede_registrar and id_equipo_lista:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_entrenamiento FROM entrenamiento WHERE id_equipo = %s AND fecha = %s",
            (id_equipo_lista, fecha_lista)
        )
        fila_ent = cursor.fetchone()
        cursor.close()
        conexion.close()
        if fila_ent:
            id_entrenamiento_lista = fila_ent['id_entrenamiento']
        jugadores_lista = obtener_jugadores_equipo_para_lista(int(id_equipo_lista), id_entrenamiento_lista)

    jugador_actual = next((j for j in jugadores_vista if j['id_jugador'] == id_jugador_sel), None) if id_jugador_sel else None

    return render_template(
        'asistencias.html',
        id_rol=id_rol,
        puede_registrar=puede_registrar,
        sin_jugadores=False,
        mes=mes,
        anio=anio,
        nombre_mes=MESES_ES[mes],
        mes_anterior=mes_anterior,
        anio_anterior=anio_anterior,
        mes_siguiente=mes_siguiente,
        anio_siguiente=anio_siguiente,
        semanas=semanas,
        estadisticas=estadisticas,
        jugadores_vista=jugadores_vista,
        id_jugador_sel=id_jugador_sel,
        jugador_actual=jugador_actual,
        equipos=equipos,
        fecha_lista=fecha_lista,
        id_equipo_lista=id_equipo_lista,
        jugadores_lista=jugadores_lista,
        hoy=hoy.strftime('%Y-%m-%d'),
        error=error,
        exito=exito
    )

@app.route('/asistencias')
def modulo_asistencias():
    return render_asistencias()

@app.route('/asistencias/registrar', methods=['POST'])
def registrar_asistencias():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2, 3]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    fecha = request.form.get('fecha')
    id_equipo = request.form.get('id_equipo')
    ubicacion = request.form.get('ubicacion', 'Cancha Principal').strip() or 'Cancha Principal'
    tipo_entrenamiento = request.form.get('tipo_entrenamiento', 'General').strip() or 'General'
    mes = request.form.get('mes')
    anio = request.form.get('anio')
    id_jugador_vista = request.form.get('id_jugador_vista')

    if not fecha or not id_equipo:
        return render_asistencias(error='Selecciona fecha y equipo para tomar la lista.')

    if datetime.strptime(fecha, '%Y-%m-%d').date() > date.today():
        return render_asistencias(error='No puedes registrar asistencia en fechas futuras.')

    id_entrenador = obtener_id_entrenador_sesion()
    if not id_entrenador:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_entrenador FROM entrenador ORDER BY id_entrenador ASC LIMIT 1")
        fila = cursor.fetchone()
        cursor.close()
        conexion.close()
        id_entrenador = fila['id_entrenador'] if fila else 1

    asegurar_columna_observacion_asistencia()
    id_entrenamiento = obtener_o_crear_entrenamiento(
        id_entrenador, int(id_equipo), fecha, ubicacion, tipo_entrenamiento
    )

    jugadores = obtener_jugadores_equipo_para_lista(int(id_equipo))

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    for jugador in jugadores:
        id_j = str(jugador['id_jugador'])
        estado_raw = request.form.get(f'estado_{id_j}')
        observacion = request.form.get(f'observacion_{id_j}', '').strip()

        if estado_raw not in ('0', '1', '2'):
            continue

        asistio = int(estado_raw)
        if asistio != 2:
            observacion = None
        elif not observacion:
            observacion = 'Justificado'

        cursor.execute(
            "SELECT id_asistencia FROM asistencia WHERE id_entrenamiento = %s AND id_jugador = %s",
            (id_entrenamiento, jugador['id_jugador'])
        )
        existente = cursor.fetchone()

        if existente:
            cursor.execute(
                """
                UPDATE asistencia SET asistio = %s, observacion = %s, id_equipo = %s
                WHERE id_entrenamiento = %s AND id_jugador = %s
                """,
                (asistio, observacion, id_equipo, id_entrenamiento, jugador['id_jugador'])
            )
        else:
            cursor.execute("SELECT COALESCE(MAX(id_asistencia), 0) + 1 AS nuevo_id FROM asistencia")
            nuevo_id = cursor.fetchone()['nuevo_id']
            cursor.execute(
                """
                INSERT INTO asistencia (id_asistencia, id_entrenamiento, id_jugador, id_equipo, asistio, observacion)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nuevo_id, id_entrenamiento, jugador['id_jugador'], id_equipo, asistio, observacion)
            )

    conexion.commit()
    cursor.close()
    conexion.close()

    params = f'mes={mes or date.today().month}&anio={anio or date.today().year}&fecha={fecha}&id_equipo={id_equipo}'
    if id_jugador_vista:
        params += f'&id_jugador={id_jugador_vista}'
    return redirect(f'/asistencias?{params}&guardado=1')

# ==========================================
# MÓDULO: ENTRENAMIENTOS (CALENDARIO)
# ==========================================

def asegurar_columna_hora_entrenamiento():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(*) AS existe
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'entrenamiento'
          AND COLUMN_NAME = 'hora'
    """)
    if cursor.fetchone()['existe'] == 0:
        cursor = conexion.cursor()
        cursor.execute("ALTER TABLE entrenamiento ADD COLUMN hora TIME DEFAULT NULL")
        conexion.commit()
    cursor.close()
    conexion.close()

def formatear_hora_entrenamiento(hora):
    if not hora:
        return 'Por definir'
    if isinstance(hora, timedelta):
        total = int(hora.total_seconds())
        horas, resto = divmod(total, 3600)
        minutos = resto // 60
        return f"{horas:02d}:{minutos:02d}"
    if hasattr(hora, 'strftime'):
        return hora.strftime('%H:%M')
    texto = str(hora)
    return texto[:5] if len(texto) >= 5 else texto

def obtener_entrenadores_para_select():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_entrenador, nombres, apellidos, especialidad
        FROM entrenador
        ORDER BY apellidos ASC, nombres ASC
    """)
    entrenadores = cursor.fetchall()
    cursor.close()
    conexion.close()
    return entrenadores

def obtener_equipos_filtro_entrenamientos(id_rol):
    if id_rol in [1, 2, 3]:
        return None

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    equipos = []

    if id_rol == 4:
        cursor.execute("""
            SELECT DISTINCT f.id_equipo
            FROM jugador j
            JOIN ficha_jugador f ON j.id_jugador = f.id_jugador
            WHERE j.id_usuario = %s AND f.id_equipo IS NOT NULL
        """, (session['id_usuario'],))
        equipos = [fila['id_equipo'] for fila in cursor.fetchall()]
    elif id_rol == 5:
        id_acudiente = obtener_id_acudiente_sesion()
        if id_acudiente:
            cursor.execute("""
                SELECT DISTINCT f.id_equipo
                FROM jugador j
                JOIN ficha_jugador f ON j.id_jugador = f.id_jugador
                WHERE j.id_acudiente = %s AND f.id_equipo IS NOT NULL
            """, (id_acudiente,))
            equipos = [fila['id_equipo'] for fila in cursor.fetchall()]

    cursor.close()
    conexion.close()
    return equipos

def obtener_entrenamientos_mes(anio, mes, equipos_filtro=None):
    asegurar_columna_hora_entrenamiento()
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT e.id_entrenamiento, e.fecha, e.hora, e.ubicacion, e.tipo_entrenamiento,
               eq.nombre_equipo, eq.id_equipo,
               ent.nombres AS ent_nombres, ent.apellidos AS ent_apellidos, ent.especialidad AS ent_especialidad
        FROM entrenamiento e
        JOIN equipo eq ON e.id_equipo = eq.id_equipo
        JOIN entrenador ent ON e.id_entrenador = ent.id_entrenador
        WHERE YEAR(e.fecha) = %s AND MONTH(e.fecha) = %s
    """
    params = [anio, mes]

    if equipos_filtro is not None:
        if not equipos_filtro:
            cursor.close()
            conexion.close()
            return {}
        placeholders = ','.join(['%s'] * len(equipos_filtro))
        query += f" AND e.id_equipo IN ({placeholders})"
        params.extend(equipos_filtro)

    query += " ORDER BY e.fecha ASC, e.hora ASC"
    cursor.execute(query, tuple(params))
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()

    por_fecha = {}
    for fila in filas:
        clave = fila['fecha'].strftime('%Y-%m-%d') if hasattr(fila['fecha'], 'strftime') else str(fila['fecha'])
        fila['hora_texto'] = formatear_hora_entrenamiento(fila.get('hora'))
        fila['entrenador_nombre'] = f"{fila['ent_nombres']} {fila['ent_apellidos']}"
        por_fecha.setdefault(clave, []).append(fila)
    return por_fecha

def construir_calendario_entrenamientos(anio, mes, entrenamientos_por_fecha):
    semanas = []
    for semana in calendar.Calendar(firstweekday=0).monthdatescalendar(anio, mes):
        dias = []
        for dia in semana:
            if dia.month != mes:
                dias.append({'vacio': True})
                continue
            clave = dia.strftime('%Y-%m-%d')
            entrenamientos = entrenamientos_por_fecha.get(clave, [])
            dias.append({
                'vacio': False,
                'dia': dia.day,
                'fecha': clave,
                'tiene_entrenamiento': len(entrenamientos) > 0,
                'cantidad': len(entrenamientos),
                'es_hoy': dia == date.today(),
            })
        semanas.append(dias)
    return semanas

def preparar_entrenamientos_vista(entrenamientos_por_fecha):
    datos = {}
    for fecha, lista in entrenamientos_por_fecha.items():
        datos[fecha] = [{
            'hora': e['hora_texto'],
            'tipo': e['tipo_entrenamiento'],
            'ubicacion': e['ubicacion'],
            'equipo': e['nombre_equipo'],
            'entrenador': e['entrenador_nombre'],
            'especialidad_entrenador': e.get('ent_especialidad') or ''
        } for e in lista]
    return datos

def render_entrenamientos(error=None, exito=None):
    if not usuario_tiene_sesion():
        return redirect('/')

    id_rol = obtener_id_rol_sesion()
    if id_rol not in [1, 2, 3, 4, 5]:
        return redirect(panel_por_rol(id_rol))

    hoy = date.today()
    try:
        mes = int(request.args.get('mes', hoy.month))
        anio = int(request.args.get('anio', hoy.year))
    except (TypeError, ValueError):
        mes, anio = hoy.month, hoy.year
    mes = max(1, min(12, mes))

    puede_programar = id_rol in [1, 2, 3]
    equipos_filtro = obtener_equipos_filtro_entrenamientos(id_rol)

    if id_rol in [4, 5] and equipos_filtro is not None and not equipos_filtro:
        return render_template(
            'entrenamientos.html',
            id_rol=id_rol,
            puede_programar=False,
            sin_equipo=True,
            mes=mes,
            anio=anio,
            nombre_mes=MESES_ES[mes],
            entrenamientos_datos={},
            error=error,
            exito=exito
        )

    entrenamientos_por_fecha = obtener_entrenamientos_mes(anio, mes, equipos_filtro)
    semanas = construir_calendario_entrenamientos(anio, mes, entrenamientos_por_fecha)
    entrenamientos_datos = preparar_entrenamientos_vista(entrenamientos_por_fecha)

    mes_anterior = mes - 1 if mes > 1 else 12
    anio_anterior = anio if mes > 1 else anio - 1
    mes_siguiente = mes + 1 if mes < 12 else 1
    anio_siguiente = anio if mes < 12 else anio + 1

    equipos = obtener_lista_equipos() if puede_programar else []
    entrenadores = obtener_entrenadores_para_select() if puede_programar and id_rol in [1, 2] else []
    id_entrenador_sesion = obtener_id_entrenador_sesion()

    return render_template(
        'entrenamientos.html',
        id_rol=id_rol,
        puede_programar=puede_programar,
        sin_equipo=False,
        mes=mes,
        anio=anio,
        nombre_mes=MESES_ES[mes],
        mes_anterior=mes_anterior,
        anio_anterior=anio_anterior,
        mes_siguiente=mes_siguiente,
        anio_siguiente=anio_siguiente,
        semanas=semanas,
        entrenamientos_datos=entrenamientos_datos,
        equipos=equipos,
        entrenadores=entrenadores,
        especialidades=ESPECIALIDADES_ENTRENADOR,
        id_entrenador_sesion=id_entrenador_sesion,
        hoy=hoy.strftime('%Y-%m-%d'),
        error=error,
        exito=exito
    )

@app.route('/entrenamientos')
def modulo_entrenamientos():
    return render_entrenamientos(
        error=request.args.get('error'),
        exito=request.args.get('exito')
    )

@app.route('/entrenamientos/programar', methods=['POST'])
def programar_entrenamiento():
    if not usuario_tiene_sesion():
        return redirect('/')
    id_rol = obtener_id_rol_sesion()
    if id_rol not in [1, 2, 3]:
        return redirect(panel_por_rol(id_rol))

    fecha = request.form.get('fecha', '').strip()
    hora = request.form.get('hora', '').strip()
    id_equipo = request.form.get('id_equipo')
    tipo_entrenamiento = request.form.get('tipo_entrenamiento', '').strip()
    ubicacion = request.form.get('ubicacion', 'Cancha Principal').strip() or 'Cancha Principal'
    mes = request.form.get('mes')
    anio = request.form.get('anio')

    if not fecha or not hora or not id_equipo or not tipo_entrenamiento:
        return redirect(f'/entrenamientos?mes={mes}&anio={anio}&error={quote("Completa fecha, hora, equipo y especialidad")}')

    if tipo_entrenamiento not in ESPECIALIDADES_ENTRENADOR:
        return redirect(f'/entrenamientos?mes={mes}&anio={anio}&error={quote("Especialidad no válida")}')

    try:
        datetime.strptime(fecha, '%Y-%m-%d')
        datetime.strptime(hora, '%H:%M')
    except ValueError:
        return redirect(f'/entrenamientos?mes={mes}&anio={anio}&error={quote("Fecha u hora con formato inválido")}')

    if id_rol == 3:
        id_entrenador = obtener_id_entrenador_sesion()
        if not id_entrenador:
            return redirect(f'/entrenamientos?mes={mes}&anio={anio}&error={quote("No se encontró tu perfil de entrenador")}')
    else:
        id_entrenador = request.form.get('id_entrenador')
        if not id_entrenador:
            return redirect(f'/entrenamientos?mes={mes}&anio={anio}&error={quote("Selecciona el entrenador responsable")}')

    asegurar_columna_hora_entrenamiento()
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_entrenamiento FROM entrenamiento WHERE id_equipo = %s AND fecha = %s",
        (id_equipo, fecha)
    )
    existente = cursor.fetchone()

    if existente:
        cursor.execute("""
            UPDATE entrenamiento
            SET id_entrenador = %s, hora = %s, ubicacion = %s, tipo_entrenamiento = %s
            WHERE id_entrenamiento = %s
        """, (id_entrenador, hora, ubicacion, tipo_entrenamiento, existente['id_entrenamiento']))
    else:
        cursor.execute("SELECT COALESCE(MAX(id_entrenamiento), 0) + 1 AS nuevo_id FROM entrenamiento")
        nuevo_id = cursor.fetchone()['nuevo_id']
        cursor.execute("""
            INSERT INTO entrenamiento (id_entrenamiento, id_entrenador, id_equipo, fecha, hora, ubicacion, tipo_entrenamiento)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nuevo_id, id_entrenador, id_equipo, fecha, hora, ubicacion, tipo_entrenamiento))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(f'/entrenamientos?mes={mes}&anio={anio}&exito={quote("Entrenamiento programado correctamente")}')

# ==========================================
# MÓDULO: FINANZAS Y SOPORTES DE PAGO
# ==========================================
@app.route('/finanzas')
def modulo_finanzas():
    if not usuario_tiene_sesion():
        return redirect('/')
        
    id_rol = obtener_id_rol_sesion()
    id_usuario = session['id_usuario']
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # ---------------------------------------------------------
    # VISTA PARA JUGADOR (4) Y ACUDIENTE (5) - SUBIR SOPORTES
    # ---------------------------------------------------------
    if id_rol in [4, 5]:
        jugadores_disponibles = []
        if id_rol == 4:
            cursor.execute("SELECT id_jugador, nombres, apellidos FROM jugador WHERE id_usuario = %s", (id_usuario,))
            jugadores_disponibles = cursor.fetchall()
        elif id_rol == 5:
            id_acudiente = obtener_id_acudiente_sesion()
            if id_acudiente:
                cursor.execute("SELECT id_jugador, nombres, apellidos FROM jugador WHERE id_acudiente = %s", (id_acudiente,))
                jugadores_disponibles = cursor.fetchall()

        # Obtener el historial de pagos que han subido
        query_historial = """
            SELECT sp.id_soporte, sp.mes_correspondiente, sp.fecha_subida, sp.estado, sp.archivo_ruta,
                   j.nombres, j.apellidos
            FROM soporte_pago sp
            JOIN jugador j ON sp.id_jugador = j.id_jugador
            WHERE sp.id_usuario_sube = %s
            ORDER BY sp.fecha_subida DESC
        """
        cursor.execute(query_historial, (id_usuario,))
        historial = cursor.fetchall()
        historial_por_mes = agrupar_soportes_por_mes(historial)
        cursor.close()
        conexion.close()
        
        return render_template(
            'finanzas_pagos.html',
            id_rol=id_rol,
            jugadores=jugadores_disponibles,
            historial=historial,
            historial_por_mes=historial_por_mes,
            error=request.args.get('error'),
            exito=request.args.get('exito')
        )

    # ---------------------------------------------------------
    # VISTA PARA ADMIN (1, 2) Y ENTRENADOR (3) - REPORTE
    # ---------------------------------------------------------
    elif id_rol in [1, 2, 3]:
        query_reporte = """
            SELECT sp.id_soporte, sp.mes_correspondiente, sp.fecha_subida, sp.estado, sp.archivo_ruta,
                   j.nombres AS j_nombres, j.apellidos AS j_apellidos, j.documento,
                   u.usuario AS usuario_subio
            FROM soporte_pago sp
            JOIN jugador j ON sp.id_jugador = j.id_jugador
            JOIN usuario u ON sp.id_usuario_sube = u.id_usuario
            ORDER BY sp.fecha_subida DESC
        """
        cursor.execute(query_reporte)
        reporte = cursor.fetchall()
        reporte_por_mes = agrupar_soportes_por_mes(reporte)
        puede_gestionar = id_rol in [1, 2]
        cursor.close()
        conexion.close()
        
        return render_template(
            'finanzas_reporte.html',
            id_rol=id_rol,
            reporte=reporte,
            reporte_por_mes=reporte_por_mes,
            puede_gestionar=puede_gestionar,
            error=request.args.get('error'),
            exito=request.args.get('exito')
        )

    cursor.close()
    conexion.close()
    return redirect(panel_por_rol(id_rol))

@app.route('/subir-pago', methods=['POST'])
def subir_pago():
    if not usuario_tiene_sesion() or obtener_id_rol_sesion() not in [4, 5]:
        return redirect('/')

    id_jugador = request.form.get('id_jugador')
    mes = request.form.get('mes')
    archivo = request.files.get('comprobante')

    mes_valido, resultado_mes = validar_mes_pago(mes)
    if not mes_valido:
        return redirect(f'/finanzas?error={quote(resultado_mes)}')

    if not id_jugador:
        return redirect('/finanzas?error=Debes seleccionar un jugador')

    if not archivo or archivo.filename == '':
        return redirect('/finanzas?error=No se seleccionó ningún archivo')

    if archivo and archivo_permitido(archivo.filename):
        # Asegurar el nombre y guardar con un timestamp para evitar sobreescrituras
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = secure_filename(f"{timestamp}_{archivo.filename}")
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta_guardado)

        # Guardar en base de datos la ruta relativa para usarla en HTML
        ruta_db = f"uploads/pagos/{filename}"
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO soporte_pago (id_jugador, id_usuario_sube, mes_correspondiente, archivo_ruta)
            VALUES (%s, %s, %s, %s)
        """, (id_jugador, session['id_usuario'], resultado_mes, ruta_db))
        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect('/finanzas?exito=Comprobante subido correctamente')
    
    return redirect('/finanzas?error=Formato no permitido. Solo JPG y PNG')

@app.route('/finanzas/estado', methods=['POST'])
def actualizar_estado_pago():
    if not usuario_tiene_sesion() or obtener_id_rol_sesion() not in [1, 2]:
        return redirect('/')

    id_soporte = request.form.get('id_soporte')
    estado = request.form.get('estado')

    if estado not in ('Aprobado', 'Rechazado', 'Pendiente'):
        return redirect('/finanzas?error=Estado no válido')

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE soporte_pago SET estado = %s WHERE id_soporte = %s",
        (estado, id_soporte)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

    mensajes = {
        'Aprobado': 'Comprobante marcado como aprobado',
        'Rechazado': 'Comprobante marcado como rechazado',
        'Pendiente': 'Comprobante devuelto a pendiente'
    }
    return redirect(f'/finanzas?exito={quote(mensajes[estado])}')

# ==========================================
# INICIALIZADOR DEL PROYECTO (¡SIEMPRE AL FINAL!)
# ==========================================
if __name__ == '__main__':
    # debug=True hace que el servidor se actualice solo cada vez que guardas un cambio con Ctrl+S
    app.run(debug=True)