import os
import pymysql
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# CLAVE SECRETA OBLIGATORIA PARA LAS SESIONES
app.secret_key = 'manager_super_secreto_2026'

# ==========================================
# 1. CONFIGURACIÓN DE BASE DE DATOS (MySQL / Railway)
# ==========================================
def conectar_db():
    # Railway inyectará estas variables automáticamente. 
    # Si no existen (estás en local), usará los valores de XAMPP por defecto.
    host = os.environ.get('MYSQLHOST', '127.0.0.1')
    user = os.environ.get('MYSQLUSER', 'root')
    password = os.environ.get('MYSQLPASSWORD', '')
    database = os.environ.get('MYSQLDATABASE', 'manager_contactos')
    port = int(os.environ.get('MYSQLPORT', 3306))

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

# ==========================================
# MANEJO GLOBAL DE ERRORES (404 Not Found)
# ==========================================
@app.errorhandler(404)
def pagina_no_encontrada(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Recurso no encontrado (404)"}), 404
    return "<h1>Error 404</h1><p>El registro o la página que buscas no existe en el sistema.</p><a href='/'>Volver al inicio</a>", 404

# ==========================================
# 2. SISTEMA DE AUTENTICACIÓN (LOGIN)
# ==========================================

def login_requerido(f):
    @wraps(f)
    def funcion_decorada(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return funcion_decorada

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        password_form = request.form['password']
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute(
            "SELECT * FROM usuario WHERE username = %s AND password = %s", 
            (usuario_form, password_form)
        )
        usuario_db = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        if usuario_db:
            session['usuario'] = usuario_db['username'] 
            return redirect(url_for('inicio')) 
        else:
            error = "Usuario o contraseña incorrectos."
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# ==========================================
# 3. RUTAS HTML (Frontend)
# ==========================================

@app.route('/')
@login_requerido
def inicio():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM contacto")
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('inicio.html', total=resultado['total'])

@app.route('/contactos/', methods=['GET'])
@login_requerido
def lista_contactos():
    conexion = conectar_db()
    cursor = conexion.cursor()
    categoria_seleccionada = request.args.get('categoria', '')
    
    cursor.execute("SELECT * FROM categoria")
    categorias_db = cursor.fetchall()
    
    if categoria_seleccionada:
        cursor.execute("SELECT * FROM grupo WHERE fk_categoria = %s", (categoria_seleccionada,))
    else:
        cursor.execute("SELECT * FROM grupo")
    grupos_db = cursor.fetchall()
    
    vista_agrupada = []
    for grupo in grupos_db:
        cat_nombre = next((c['nombre'] for c in categorias_db if c['id_categoria'] == grupo['fk_categoria']), "Sin Categoría")
        cursor.execute("SELECT * FROM contacto WHERE fk_grupo = %s", (grupo['id_grupo'],))
        contactos_del_grupo = cursor.fetchall()
        vista_agrupada.append({
            "id_grupo": grupo['id_grupo'],
            "nombre_grupo": grupo['nombre'],
            "nombre_categoria": cat_nombre,
            "contactos": contactos_del_grupo
        })
        
    cursor.close()
    conexion.close()
    return render_template('lista.html', vista_agrupada=vista_agrupada, categorias=categorias_db, categoria_seleccionada=categoria_seleccionada)

@app.route('/contactos/<int:id_contacto>/', methods=['GET'])
@login_requerido
def detalle_contacto(id_contacto):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM contacto WHERE id_contacto = %s", (id_contacto,))
    contacto = cursor.fetchone()
    
    if not contacto:
        cursor.close()
        conexion.close()
        from flask import abort
        abort(404) 
        
    cursor.execute("SELECT * FROM grupo WHERE id_grupo = %s", (contacto['fk_grupo'],))
    grupo = cursor.fetchone()
    
    categoria = None
    if grupo:
        cursor.execute("SELECT * FROM categoria WHERE id_categoria = %s", (grupo['fk_categoria'],))
        categoria = cursor.fetchone()
        
    cursor.close()
    conexion.close()
    return render_template('detalle.html', contacto=contacto, grupo=grupo, categoria=categoria)

@app.route('/contactos/nuevo/', methods=['GET', 'POST'])
@login_requerido
def crear_contacto():
    conexion = conectar_db()
    cursor = conexion.cursor()
    error = None
    
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        telefono = request.form['telefono'].strip()
        correo = request.form.get('correo', '').strip()
        fk_grupo = request.form['grupo']
        
        if not telefono.isdigit() or len(telefono) != 9:
            error = "El teléfono debe contener exactamente 9 dígitos numéricos."
        elif len(nombre) < 3:
            error = "El nombre ingresado es muy corto. Debe tener al menos 3 letras."
            
        if not error:
            cursor.execute(
                "INSERT INTO contacto (nombre_completo, telefono, correo, fk_grupo) VALUES (%s, %s, %s, %s)",
                (nombre, telefono, correo, int(fk_grupo))
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect(url_for('lista_contactos'))
            
    cursor.execute("SELECT * FROM grupo")
    grupos_db = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('form_crear.html', grupos=grupos_db, error=error)

@app.route('/contactos/<int:id_contacto>/editar/', methods=['GET', 'POST'])
@login_requerido
def editar_contacto(id_contacto):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form.get('correo', '')
        fk_grupo = int(request.form['grupo'])
        
        cursor.execute(
            "UPDATE contacto SET nombre_completo=%s, telefono=%s, correo=%s, fk_grupo=%s WHERE id_contacto=%s",
            (nombre, telefono, correo, fk_grupo, id_contacto)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('detalle_contacto', id_contacto=id_contacto))
        
    cursor.execute("SELECT * FROM contacto WHERE id_contacto = %s", (id_contacto,))
    contacto = cursor.fetchone()
    
    cursor.execute("SELECT * FROM grupo")
    grupos_db = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('form_editar.html', contacto=contacto, grupos=grupos_db)

@app.route('/contactos/<int:id_contacto>/eliminar/', methods=['GET', 'POST'])
@login_requerido
def eliminar_contacto(id_contacto):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    if request.method == 'POST':
        cursor.execute("DELETE FROM contacto WHERE id_contacto = %s", (id_contacto,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('lista_contactos'))
        
    cursor.execute("SELECT * FROM contacto WHERE id_contacto = %s", (id_contacto,))
    contacto = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('confirmar_eliminar.html', contacto=contacto)

@app.route('/categorias/nuevo/', methods=['GET', 'POST'])
@login_requerido
def crear_categoria():
    if request.method == 'POST':
        conexion = conectar_db()
        cursor = conexion.cursor()
        nombre = request.form['nombre']
        cursor.execute("INSERT INTO categoria (nombre) VALUES (%s)", (nombre,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('crear_grupo'))
    return render_template('form_categoria.html')

@app.route('/grupos/nuevo/', methods=['GET', 'POST'])
@login_requerido
def crear_grupo():
    conexion = conectar_db()
    cursor = conexion.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        fk_categoria = int(request.form['categoria'])
        cursor.execute(
            "INSERT INTO grupo (nombre, descripcion, fk_categoria) VALUES (%s, %s, %s)",
            (nombre, descripcion, fk_categoria)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('crear_contacto'))
        
    cursor.execute("SELECT * FROM categoria")
    categorias_db = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('form_grupo.html', categorias=categorias_db)

# ==========================================
# 4. RUTAS API (Documentadas y en Formato JSON)
# ==========================================

@app.route('/api/contactos', methods=['GET'])
def api_contactos():
    """
    Obtener la lista completa de contactos
    ---
    tags:
      - Contactos API
    responses:
      200:
        description: Lista de contactos
    """
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM contacto")
    contactos_db = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(contactos_db), 200

@app.route('/api/contactos/<int:id_contacto>', methods=['GET'])
def api_detalle_contacto(id_contacto):
    """
    Obtener un solo contacto por su ID
    ---
    tags:
      - Contactos API
    parameters:
      - in: path
        name: id_contacto
        type: integer
        required: true
    responses:
      200:
        description: Datos del contacto
      404:
        description: Contacto no encontrado
    """
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM contacto WHERE id_contacto = %s", (id_contacto,))
    contacto = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if contacto:
        return jsonify(contacto), 200
    return jsonify({"error": "Contacto no encontrado"}), 404

@app.route('/api/contactos', methods=['POST'])
def api_crear_contacto():
    """
    Crear un nuevo contacto
    ---
    tags:
      - Contactos API
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nombre_completo: {type: string}
            telefono: {type: string}
            correo: {type: string}
            fk_grupo: {type: integer}
    responses:
      201:
        description: Contacto creado
      400:
        description: Error de validación
    """
    datos = request.get_json()
    telefono = datos.get('telefono', '').strip()
    nombre = datos.get('nombre_completo', '').strip()
    
    if not telefono.isdigit() or len(telefono) != 9:
        return jsonify({"error": "Validación fallida: El teléfono debe contener exactamente 9 dígitos numéricos."}), 400
        
    if len(nombre) < 3:
        return jsonify({"error": "Validación fallida: El nombre debe tener al menos 3 caracteres."}), 400
        
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO contacto (nombre_completo, telefono, correo, fk_grupo) VALUES (%s, %s, %s, %s)",
        (nombre, telefono, datos.get('correo', ''), datos.get('fk_grupo'))
    )
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Contacto creado", "id_insertado": nuevo_id}), 201

@app.route('/api/contactos/<int:id_contacto>', methods=['PUT'])
def api_editar_contacto(id_contacto):
    """
    Actualizar un contacto existente
    ---
    tags:
      - Contactos API
    parameters:
      - in: path
        name: id_contacto
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nombre_completo: {type: string}
            telefono: {type: string}
            correo: {type: string}
            fk_grupo: {type: integer}
    responses:
      200:
        description: Contacto actualizado
    """
    datos = request.get_json()
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE contacto SET nombre_completo=%s, telefono=%s, correo=%s, fk_grupo=%s WHERE id_contacto=%s",
        (datos.get('nombre_completo'), datos.get('telefono'), datos.get('correo', ''), datos.get('fk_grupo'), id_contacto)
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": f"Contacto {id_contacto} actualizado"}), 200

@app.route('/api/contactos/<int:id_contacto>', methods=['DELETE'])
def api_eliminar_contacto(id_contacto):
    """
    Eliminar un contacto
    ---
    tags:
      - Contactos API
    parameters:
      - in: path
        name: id_contacto
        type: integer
        required: true
    responses:
      200:
        description: Contacto eliminado
    """
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM contacto WHERE id_contacto = %s", (id_contacto,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": f"Contacto {id_contacto} eliminado"}), 200

@app.route('/api/resumen/', methods=['GET'])
def api_resumen_estadisticas():
    """
    Obtener estadísticas del sistema (Punto Extra)
    ---
    tags:
      - Resumen API
    responses:
      200:
        description: JSON con los totales de entidades
    """
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT COUNT(*) AS total FROM contacto")
    total_contactos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM grupo")
    total_grupos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM categoria")
    total_categorias = cursor.fetchone()['total']
    
    cursor.close()
    conexion.close()
    
    return jsonify({
        "estadisticas": {
            "total_contactos": total_contactos,
            "total_grupos": total_grupos,
            "total_categorias": total_categorias
        },
        "mensaje": "Resumen generado exitosamente"
    }), 200

if __name__ == '__main__':
    # Usamos el puerto que inyecta la nube, o el 5000 si estás en tu PC
    puerto = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=puerto)