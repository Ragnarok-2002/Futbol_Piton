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
# 2. RUTA RAÍZ / INICIAL (Muestra tu Login)
# ==========================================
@app.route('/')
def home():
    # Flask buscará automáticamente este archivo dentro de la carpeta 'templates'
    return render_template('Login_Final.html')

# ==========================================
# 3. RUTA DEL PROCESO DE LOGIN (Lógica de acceso)
# ==========================================
@app.route('/login', methods=['POST'])
def login():
    # Capturamos lo que escribiste en los inputs usando el atributo 'name' del HTML
    usuario_ingresado = request.form.get('username')
    contrasena_ingresada = request.form.get('password')
    
    # Abrimos la conexión con XAMPP
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True) # dictionary=True nos permite usar los nombres de las columnas
    
    # Consultamos si existe el usuario con esa contraseña exacta en la tabla 'usuario'
    query = "SELECT * FROM usuario WHERE usuario = %s AND contrasena = %s"
    cursor.execute(query, (usuario_ingresado, contrasena_ingresada))
    cuenta = cursor.fetchone() # Trae la fila si coincide, o None si no existe
    
    # Cerramos el cursor y la conexión inmediatamente por seguridad
    cursor.close()
    conexion.close()
    
    if cuenta:
        # ¡Usuario correcto! Evaluamos el id_rol para saber a qué pantalla mandarlo
        id_rol = cuenta['id_rol']
        
        # Evaluamos los roles según tu base de datos (Ejemplo: 3 = Acudiente, 2 = Entrenador)
        if id_rol == 3:
            return redirect('/modulo-acudiente')
        elif id_rol == 2:
            return redirect('/modulo-entrenador')
        else:
            return "<h1>Bienvenido Administrador</h1><p>Esta ruta está lista para conectarse a su respectivo módulo en el futuro.</p>"
    else:
        # Si los datos no coinciden, mostramos un mensaje simple de error
        return "<h3>Usuario o contraseña incorrectos.</h3><p>Por favor, regresa al navegador e intenta de nuevo.</p>"

# ==========================================
# 4. RUTAS TEMPORALES PARA COMPROBAR EL ÉXITO
# ==========================================
@app.route('/modulo-acudiente')
def modulo_acudiente():
    # Aquí es donde más adelante conectaremos el HTML final que haga tu compañero
    return "<h1>¡Inicio de sesión exitoso!</h1><p>Bienvenido al Módulo del Acudiente. Python procesó tus datos correctamente de la BD.</p>"

@app.route('/modulo-entrenador')
def modulo_entrenador():
    return "<h1>¡Inicio de sesión exitoso!</h1><p>Bienvenido al Módulo del Coach/Entrenador.</p>"


# INICIALIZADOR DEL PROYECTO
if __name__ == '__main__':
    # debug=True hace que el servidor se actualice solo cada vez que guardas un cambio con Ctrl+S
    app.run(debug=True)