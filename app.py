# pip install Flask mysql-connector-python

from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
# Clave secreta obligatoria en Flask para manejar sesiones en el futuro
app.secret_key = 'clave_secreta_escuela_futbol'

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

def calcular_edad(fecha_nacimiento):
    nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    fecha_hoy = datetime.now()
    return fecha_hoy.year - nacimiento.year - ((fecha_hoy.month, fecha_hoy.day) < (nacimiento.month, nacimiento.day))

def validar_edad_acudiente(fecha_nacimiento):
    if not fecha_nacimiento:
        return False, 'La fecha de nacimiento es obligatoria para registrar un acudiente.'
    if calcular_edad(fecha_nacimiento) < 18:
        return False, 'No tiene la mayoría de edad para ser acudiente/tutor. Debe ser mayor de 18 años.'
    return True, None

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
        elif fecha_nacimiento:
            edad = calcular_edad(fecha_nacimiento)

            if id_rol == '4':  # Reglas exclusivas para JUGADORES
                if edad < 10:
                    return render_template('registro.html', error='Aún no tienes la edad mínima (10 años). Te invitamos a inscribirte en nuestra escuela aliada JUNIOR.')
                elif edad > 22:
                    return render_template('registro.html', error='Superaste la edad máxima (22 años). Te invitamos a inscribirte en nuestra escuela aliada MASTER.')

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
# 5. MÓDULO: MI PERFIL (ADMINISTRADOR)
# ==========================================
@app.route('/mi-perfil')
def mi_perfil():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    id_usuario_actual = session['id_usuario']
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("SELECT usuario FROM usuario WHERE id_usuario = %s", (id_usuario_actual,))
    datos_admin = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    return render_template('perfil_admin.html', admin=datos_admin, url_panel=obtener_panel_actual())

@app.route('/actualizar-perfil', methods=['POST'])
def actualizar_perfil():
    if not usuario_tiene_sesion():
        return redirect('/')
    if obtener_id_rol_sesion() not in [1, 2]:
        return redirect(panel_por_rol(obtener_id_rol_sesion()))

    nuevo_usuario = request.form.get('username')
    nueva_contrasena = request.form.get('password')
    id_usuario_actual = session['id_usuario']
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    query = "UPDATE usuario SET usuario = %s, contrasena = %s WHERE id_usuario = %s"
    cursor.execute(query, (nuevo_usuario, nueva_contrasena, id_usuario_actual))
    conexion.commit()
    
    cursor.close()
    conexion.close()
    
    return redirect(obtener_panel_actual())

# ==========================================
# MÓDULO: GESTIÓN DE JUGADORES (VISTA)
# ==========================================
@app.route('/jugadores')
def gestion_jugadores():
    if 'id_usuario' not in session:
        return redirect('/')

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Hacemos JOIN con usuario para traer el ESTADO de la cuenta y su ID
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
    
    return render_template('gestion_jugadores.html', jugadores=jugadores)

# ==========================================
# MÓDULO: GESTIÓN DE ACUDIENTES (VISTA)
# ==========================================
def obtener_lista_acudientes():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT a.id_acudiente, a.id_usuario, a.nombre, a.apellido, a.documento,
               a.telefono, a.email, u.estado, u.usuario AS usuario_acceso,
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
# RUTAS DE ACCIÓN: EDITAR Y BORRAR JUGADORES
# ==========================================
@app.route('/editar-jugador-admin', methods=['POST'])
def editar_jugador_admin():
    # 1. Recogemos los datos del formulario modal
    id_jugador = request.form.get('id_jugador')
    id_usuario = request.form.get('id_usuario')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    estado = request.form.get('estado')

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
        SELECT nombres, apellidos, documento, fecha_nacimiento 
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
@app.route('/equipos')
def modulo_equipos():
    if 'id_usuario' not in session:
        return redirect('/')
        
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # 1. Obtenemos el rol para saber si habilitamos la edición y qué menú lateral mostrar
    id_rol = obtener_id_rol_sesion()
    es_admin = id_rol in [1, 2]
    es_entrenador = id_rol in [1, 2, 3] if id_rol else False
    
    # 2. Traemos todos los equipos para la lista desplegable del modal
    cursor.execute("SELECT id_equipo, nombre_equipo FROM equipo")
    lista_equipos = cursor.fetchall()
    
    # 3. LA MAGIA: Cambiamos a LEFT JOIN para incluir a los jugadores huérfanos
    # COALESCE cambia los valores vacíos (NULL) por textos por defecto
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
    
    equipos_db = {}
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
        
    return render_template(
        'equipos.html',
        equipos=equipos_db,
        es_entrenador=es_entrenador,
        es_admin=es_admin,
        id_rol=id_rol,
        lista_equipos=lista_equipos
    )

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
@app.route('/entrenadores')
def gestion_entrenadores():
    if 'id_usuario' not in session:
        return redirect('/')
        
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # AHORA SÍ extraemos e.documento de la tabla entrenador.
    # También traemos u.usuario por si lo necesitas mostrar después como "Usuario de Acceso"
    query = """
        SELECT e.id_entrenador, e.documento, e.nombres, e.apellidos, e.telefono, e.email, e.especialidad,
               u.usuario AS usuario_acceso
        FROM entrenador e
        JOIN usuario u ON e.id_usuario = u.id_usuario
    """
    cursor.execute(query)
    entrenadores = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return render_template('gestion_entrenadores.html', entrenadores=entrenadores)

# ==========================================
# INICIALIZADOR DEL PROYECTO (¡SIEMPRE AL FINAL!)
# ==========================================
if __name__ == '__main__':
    # debug=True hace que el servidor se actualice solo cada vez que guardas un cambio con Ctrl+S
    app.run(debug=True)