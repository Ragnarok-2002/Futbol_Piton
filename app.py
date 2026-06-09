from flask import Flask, render_template, request, redirect, session
import mysql.connector

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
# MÓDULO: REGISTRO/NUEVO USUARIO (JUGADOR O ACUDIENTE)
# ==========================================
@app.route('/registro', methods=['GET', 'POST'])
def registro_publico():
    if request.method == 'POST':
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Recogemos los datos del formulario
        id_rol = request.form.get('rol') 
        documento = request.form.get('documento')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        contrasena = request.form.get('password')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        
        # 1. Creamos la cuenta de usuario (Asegúrate de haber activado A_I en phpMyAdmin)
        cursor.execute("INSERT INTO usuario (id_rol, usuario, contrasena, email, estado) VALUES (%s, %s, %s, %s, %s)", 
                       (id_rol, documento, contrasena, email, 'Activo'))
        id_usuario_nuevo = cursor.lastrowid
        
        # 2. Guardamos los datos en su tabla correspondiente
        if id_rol == '4': # Jugador
            # AQUÍ ESTÁ LA MAGIA: Agregamos fecha_registro y usamos CURDATE()
            query_jugador = """
                INSERT INTO jugador (id_usuario, id_rol, documento, nombres, apellidos, fecha_nacimiento, telefono, email, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
            """
            cursor.execute(query_jugador, (id_usuario_nuevo, id_rol, documento, nombres, apellidos, fecha_nacimiento, telefono, email))
            
        elif id_rol == '5': # Acudiente
            query_acudiente = """
                INSERT INTO acudiente (id_usuario, id_rol, nombre, apellido)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_acudiente, (id_usuario_nuevo, id_rol, nombres, apellidos))
            
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
        # ¡MAGIA!: Guardamos el ID del usuario en la sesión para saber quién es
        session['id_usuario'] = cuenta['id_usuario']
        
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
    # Por ahora simulamos que tu ID de usuario en la base de datos es el 1 
    # (Revisa en tu phpMyAdmin qué ID tiene tu usuario administrador)
    id_usuario_admin = 1 
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Traemos tus datos actuales para mostrarlos en los campos de texto
    cursor.execute("SELECT usuario FROM usuario WHERE id_usuario = %s", (id_usuario_admin,))
    datos_admin = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    return render_template('perfil_admin.html', admin=datos_admin)

@app.route('/actualizar-perfil', methods=['POST'])
def actualizar_perfil():
    nuevo_usuario = request.form.get('username')
    nueva_contrasena = request.form.get('password')
    id_usuario_admin = 1 # El mismo ID de tu usuario admin
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Ejecutamos la actualización en la Base de Datos de XAMPP
    query = "UPDATE usuario SET usuario = %s, contrasena = %s WHERE id_usuario = %s"
    cursor.execute(query, (nuevo_usuario, nueva_contrasena, id_usuario_admin))
    conexion.commit() # ¡Obligatorio! Confirma los cambios de escritura en MySQL
    
    cursor.close()
    conexion.close()
    
    # Después de guardar, te regresamos al Dashboard con los datos nuevos
    return redirect('/dashboard-admin')

# ==========================================
# MÓDULO: GESTIÓN DE JUGADORES
# ==========================================
@app.route('/jugadores')
def gestion_jugadores():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Quitamos la tabla ficha_jugador y agregamos documento, telefono, email y fecha_registro
    query = """
        SELECT j.id_jugador, j.documento, j.nombres, j.apellidos, 
               j.telefono, j.email, j.fecha_nacimiento, j.fecha_registro,
               a.nombre AS nombre_acudiente, a.apellido AS apellido_acudiente
        FROM jugador j
        LEFT JOIN acudiente a ON j.id_acudiente = a.id_acudiente
    """
    cursor.execute(query)
    jugadores = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return render_template('gestion_jugadores.html', jugadores=jugadores)

# ==========================================
# MÓDULO: DASHBOARD DEL JUGADOR
# ==========================================
@app.route('/dashboard-jugador')
def dashboard_jugador():
    # Si alguien intenta entrar aquí sin iniciar sesión, lo devolvemos al login
    if 'id_usuario' not in session:
        return redirect('/')
        
    id_usuario_actual = session['id_usuario']
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Buscamos los datos personales del jugador usando el ID de su cuenta
    query = """
        SELECT nombres, apellidos, documento, email, telefono 
        FROM jugador 
        WHERE id_usuario = %s
    """
    cursor.execute(query, (id_usuario_actual,))
    datos_jugador = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    # Si por alguna razón no encuentra los datos en la tabla jugador
    if not datos_jugador:
        return "Error: No se encontraron los datos de este jugador."
        
    return render_template('dashboard_jugador.html', jugador=datos_jugador)

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
    
    # 1. Obtenemos el rol para saber si habilitamos la edición
    cursor.execute("SELECT id_rol FROM usuario WHERE id_usuario = %s", (session['id_usuario'],))
    usuario = cursor.fetchone()
    es_entrenador = usuario['id_rol'] in [1, 2, 3] if usuario else False
    
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
        
    return render_template('equipos.html', equipos=equipos_db, es_entrenador=es_entrenador, lista_equipos=lista_equipos)

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
# INICIALIZADOR DEL PROYECTO (¡SIEMPRE AL FINAL!)
# ==========================================
if __name__ == '__main__':
    # debug=True hace que el servidor se actualice solo cada vez que guardas un cambio con Ctrl+S
    app.run(debug=True)