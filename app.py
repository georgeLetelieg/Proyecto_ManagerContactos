from flask import Flask, render_template

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
    contactos_vista = []
    for c in contactos:
        # Buscamos el nombre del grupo correspondiente
        grupo_encontrado = next((g for g in grupos if g['id_grupo'] == c['fk_grupo']), None)
        nombre_grupo = grupo_encontrado['nombre'] if grupo_encontrado else "Desconocido"
        
        # Armamos el contacto con el nombre del grupo ya incluido
        contacto_completo = {
            "id": c['id_contacto'],
            "nombre": c['nombre_completo'],
            "telefono": c['telefono'],
            "correo": c['correo'],
            "grupo": nombre_grupo
        }
    contactos_vista.append(contacto_completo)
    return render_template('lista.html', lista_contactos=contactos_vista)


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

# Hacer que corra el servidor

if __name__ == '__main__':
    app.run(debug=True)
