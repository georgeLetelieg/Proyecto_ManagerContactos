import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
# OBLIGATORIO para usar flash(): Flask necesita una llave para firmar los mensajes temporales
app.secret_key = "una_clave_secreta_muy_segura" 

# --- CONEXIÓN A LA BASE DE DATOS ---
def conectar_db():
    host = os.environ.get('MYSQLHOST', '127.0.0.1')
    user = os.environ.get('MYSQLUSER', 'root')
    password = os.environ.get('MYSQLPASSWORD', '')
    # Aquí está la corrección clave que arregló el despliegue
    database = os.environ.get('MYSQL_DATABASE', 'railway') 
    port = int(os.environ.get('MYSQLPORT', 3306))

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

# --- RUTAS DE EJEMPLO (LOGIN) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuario WHERE username = %s AND password = %s", (username, password))
        usuario = cursor.fetchone()
        conexion.close()
        
        if usuario:
            return redirect(url_for('lista_categorias')) # Ajusta a tu ruta principal
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for('login'))
            
    return render_template('login.html')

# --- RUTAS DE CATEGORÍAS ---
@app.route('/crear_categoria', methods=['POST'])
def crear_categoria():
    nombre = request.form['nombre']
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Validación: ¿Ya existe?
    cursor.execute("SELECT * FROM categoria WHERE nombre = %s", (nombre,))
    categoria_existente = cursor.fetchone()
    
    if categoria_existente:
        flash("Error: Ya existe una categoría con ese nombre.")
    else:
        cursor.execute("INSERT INTO categoria (nombre) VALUES (%s)", (nombre,))
        conexion.commit()
        flash("Categoría creada con éxito.")
        
    conexion.close()
    return redirect(url_for('lista_categorias')) # Ajusta a tu ruta real

@app.route('/eliminar_categoria/<int:id>', methods=['POST'])
def eliminar_categoria(id):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Validación: ¿Tiene grupos asociados?
    cursor.execute("SELECT * FROM grupo WHERE fk_categoria = %s", (id,))
    grupos_asociados = cursor.fetchone()
    
    if grupos_asociados:
        flash("Error: No puedes eliminar esta categoría porque tiene grupos dentro.")
    else:
        cursor.execute("DELETE FROM categoria WHERE id_categoria = %s", (id,))
        conexion.commit()
        flash("Categoría eliminada correctamente.")
        
    conexion.close()
    return redirect(url_for('lista_categorias')) # Ajusta a tu ruta real

# --- RUTAS DE GRUPOS ---
@app.route('/eliminar_grupo/<int:id>', methods=['POST'])
def eliminar_grupo(id):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Se eliminan en cascada los contactos asociados gracias al diseño de tu BD
    cursor.execute("DELETE FROM grupo WHERE id_grupo = %s", (id,))
    conexion.commit()
    conexion.close()
    
    flash("Grupo y sus contactos eliminados correctamente.")
    return redirect(url_for('lista_grupos')) # Ajusta a tu ruta real


if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=puerto)