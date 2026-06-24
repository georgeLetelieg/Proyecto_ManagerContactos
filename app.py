from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# DATOS

# Categorías
categorias = [
    {"id_categoria": 1, "nombre": "Familia"},
    {"id_categoria": 2, "nombre": "Universidad"},
    {"id_categoria": 3, "nombre": "Servicios"}
]

# Grupos
grupos = [
    {"id_grupo": 1, "nombre": "Familia Materna", "descripcion": "Tíos y primos", "fk_categoria": 1},
    {"id_grupo": 2, "nombre": "Compañeros de Tesis", "descripcion": "Proyecto integrador", "fk_categoria": 2},
    {"id_grupo": 3, "nombre": "Mecánicos", "descripcion": "Mantención del auto", "fk_categoria": 3}
]

# Contactos
contactos = [
    {
        "id_contacto": 1, 
        "nombre_completo": "Ana López", 
        "telefono": "912345678", 
        "correo": "ana@ejemplo.com", 
        "fk_grupo": 1
    },
    {
        "id_contacto": 2, 
        "nombre_completo": "Carlos Martínez", 
        "telefono": "987654321", 
        "correo": "",
        "fk_grupo": 2
    }
]

# Rutas


@app.route('/')
def inicio():
    total_contactos = len(contactos)
    return render_template('inicio.html', total=total_contactos)


@app.route('/contactos/')
def lista_contactos():
    # 1. Capturamos el filtro de la URL (ej: /contactos/?categoria=1)
    categoria_filtro = request.args.get('categoria')

    # 2. Decidimos qué grupos mostrar
    grupos_a_mostrar = grupos
    if categoria_filtro:
        # Filtramos solo los grupos que pertenecen a la categoría seleccionada
        grupos_a_mostrar = [g for g in grupos if str(g['fk_categoria']) == categoria_filtro]

    # 3. Armamos una estructura agrupada: [ {grupo, nombre_categoria, contactos_del_grupo: []} ]
    vista_agrupada = []
    
    for g in grupos_a_mostrar:
        # Buscar el nombre de la categoría de este grupo
        cat = next((c for c in categorias if c['id_categoria'] == g['fk_categoria']), None)
        nombre_cat = cat['nombre'] if cat else "Sin Categoría"

        # Buscar todos los contactos que pertenecen SOLAMENTE a este grupo
        contactos_del_grupo = [c for c in contactos if c['fk_grupo'] == g['id_grupo']]

        # Guardamos el "paquete" completo
        vista_agrupada.append({
            "id_grupo": g['id_grupo'],
            "nombre_grupo": g['nombre'],
            "nombre_categoria": nombre_cat,
            "contactos": contactos_del_grupo
        })

    # Enviamos los datos, la lista de categorías (para el select) y cuál está seleccionada
    return render_template('lista.html', 
                           vista_agrupada=vista_agrupada, 
                           categorias=categorias,
                           categoria_seleccionada=categoria_filtro)


@app.route('/contactos/<int:id>/')
def detalle_contacto(id):
    # 1. Buscamos el contacto específico usando su ID
    contacto_encontrado = next((c for c in contactos if c['id_contacto'] == id), None)
    
    # Si alguien escribe una ID que no existe en la URL, mostramos un error 404
    if not contacto_encontrado:
        return "Contacto no encontrado", 404

    # 2. Buscamos el grupo al que pertenece para tener su nombre y descripción
    grupo_encontrado = next((g for g in grupos if g['id_grupo'] == contacto_encontrado['fk_grupo']), None)
    
    # 3. Buscamos la categoría mayor usando la llave foránea del grupo
    categoria_encontrada = None
    if grupo_encontrado:
        categoria_encontrada = next((cat for cat in categorias if cat['id_categoria'] == grupo_encontrado['fk_categoria']), None)

    # Enviamos todos estos datos estructurados a la plantilla
    return render_template('detalle.html', 
        contacto=contacto_encontrado, 
        grupo=grupo_encontrado, 
        categoria=categoria_encontrada
        )

# get y post
@app.route('/contactos/nuevo/', methods=['GET', 'POST'])
def crear_contacto():
    if request.method == 'POST':
        # 1. Capturamos los datos enviados por el usuario en el formulario
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        grupo_id = int(request.form.get('grupo'))

        # 2. Validación planificada: Teléfono de exactamente 9 dígitos
        if len(telefono) != 9 or not telefono.isdigit():
            return "Error: El teléfono debe tener exactamente 9 números.", 400

        # 3. Calculamos un nuevo ID simulado
        nuevo_id = len(contactos) + 1

        # 4. Armamos el nuevo registro y lo guardamos en nuestra lista
        nuevo_contacto = {
            "id_contacto": nuevo_id,
            "nombre_completo": nombre,
            "telefono": telefono,
            "correo": correo,
            "fk_grupo": grupo_id
        }
        contactos.append(nuevo_contacto)

        # 5. Redireccionamos a la tabla para ver el nuevo contacto agregado
        return redirect(url_for('lista_contactos'))

    # Si el método es GET (el usuario solo entró a la página), le mostramos el formulario
    # Le pasamos la lista de grupos para armar el menú desplegable (select)
    return render_template('form_crear.html', grupos=grupos)


#Edicion contactos
@app.route('/contactos/<int:id>/editar/', methods=['GET', 'POST'])
def editar_contacto(id):
    # 1. Buscamos el contacto que queremos editar
    contacto_encontrado = next((c for c in contactos if c['id_contacto'] == id), None)
    
    if not contacto_encontrado:
        return "Contacto no encontrado", 404

    if request.method == 'POST':
        # 2. Si el usuario envió el formulario, capturamos los nuevos datos
        nuevo_nombre = request.form.get('nombre')
        nuevo_telefono = request.form.get('telefono')
        nuevo_correo = request.form.get('correo')
        nuevo_grupo = int(request.form.get('grupo'))

        # Validación del teléfono
        if len(nuevo_telefono) != 9 or not nuevo_telefono.isdigit():
            return "Error: El teléfono debe tener exactamente 9 números.", 400

        # 3. Actualizamos los datos en nuestro diccionario en memoria
        contacto_encontrado['nombre_completo'] = nuevo_nombre
        contacto_encontrado['telefono'] = nuevo_telefono
        contacto_encontrado['correo'] = nuevo_correo
        contacto_encontrado['fk_grupo'] = nuevo_grupo

        # 4. Redireccionamos de vuelta a la lista
        return redirect(url_for('lista_contactos'))

    # Si es GET, mostramos el formulario con los datos actuales
    return render_template('form_editar.html', contacto=contacto_encontrado, grupos=grupos)


# Eliminira
@app.route('/contactos/<int:id>/eliminar/', methods=['GET', 'POST'])
def eliminar_contacto(id):
    # 1. Buscamos el contacto que se desea borrar
    contacto_encontrado = next((c for c in contactos if c['id_contacto'] == id), None)
    
    if not contacto_encontrado:
        return "Contacto no encontrado", 404

    if request.method == 'POST':
        # 2. Si el usuario confirma en el formulario (POST), lo eliminamos de la lista
        contactos.remove(contacto_encontrado)
        # 3. Redireccionamos de vuelta a la lista general
        return redirect(url_for('lista_contactos'))

    # Si es GET, mostramos la página de confirmación con los datos del contacto
    return render_template('confirmar_eliminar.html', contacto=contacto_encontrado)


# ==========================================
# RUTAS PARA CATEGORÍAS Y GRUPOS
# ==========================================

@app.route('/categorias/nuevo/', methods=['GET', 'POST'])
def crear_categoria():
    if request.method == 'POST':
        nombre_cat = request.form.get('nombre')
        nuevo_id = len(categorias) + 1
        
        nueva_categoria = {
            "id_categoria": nuevo_id,
            "nombre": nombre_cat
        }
        categorias.append(nueva_categoria)
        # Te redirige a crear un grupo para que uses tu nueva categoría de inmediato
        return redirect(url_for('crear_grupo'))
        
    return render_template('form_categoria.html')


@app.route('/grupos/nuevo/', methods=['GET', 'POST'])
def crear_grupo():
    if request.method == 'POST':
        nombre_grupo = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        fk_categoria = int(request.form.get('categoria'))
        
        nuevo_id = len(grupos) + 1
        
        nuevo_grupo = {
            "id_grupo": nuevo_id,
            "nombre": nombre_grupo,
            "descripcion": descripcion,
            "fk_categoria": fk_categoria
        }
        grupos.append(nuevo_grupo)
        return redirect(url_for('crear_contacto'))
        
    # Le pasamos las categorías para que el usuario elija a cuál pertenece el nuevo grupo
    return render_template('form_grupo.html', categorias=categorias)

# Hacer que corra el servidor

if __name__ == '__main__':
    app.run(debug=True)
