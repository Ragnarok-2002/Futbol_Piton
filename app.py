from flask import Flask, render_template, request, redirect
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
    
    # EL TRUCO MAESTRO: Buscamos en la columna 'usuario' O en la columna 'email'
    query = "SELECT * FROM usuario WHERE (usuario = %s OR email = %s) AND contrasena = %s"
    
    # Pasamos 'usuario_ingresado' dos veces porque hay dos %s antes de la contraseña
    cursor.execute(query, (usuario_ingresado, usuario_ingresado, contrasena_ingresada))
    cuenta = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    if cuenta:
        id_rol = cuenta['id_rol']
        if id_rol == 3:
            return redirect('/modulo-acudiente')
        elif id_rol == 2:
            return redirect('/modulo-entrenador')
        else:
            return redirect('/dashboard-admin')
    else:
        return "<h3>Usuario o contraseña incorrectos.</h3><p>Por favor, regresa e intenta de nuevo.</p>"

# ==========================================
# 4. VISTAS DE LOS DASHBOARDS
# ==========================================
@app.route('/dashboard-admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')

@app.route('/modulo-acudiente')
def modulo_acudiente():
    return "<h1>Módulo del Acudiente</h1>"

@app.route('/modulo-entrenador')
def modulo_entrenador():
    return "<h1>Módulo del Entrenador</h1>"

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
# INICIALIZADOR DEL PROYECTO (¡SIEMPRE AL FINAL!)
# ==========================================
if __name__ == '__main__':
    # debug=True hace que el servidor se actualice solo cada vez que guardas un cambio con Ctrl+S
    app.run(debug=True)