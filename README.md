# Proyecto_ManagerContactos
Descripción del Problema que resuelve: Resuelve el problema del dia a dia en el cual la
acumulación de contactos personales se desorganiza rápidamente, este proyecto resuelve
mediante un sistema web centralizado el registrar y clasificar contactos vinculándolos a
categorías y a grupos.


# Manager de Contactos

**Autor:** Jorge Letelier

# Descripción del Proyecto
El **Manager de Contactos** es una aplicación web centralizada diseñada para resolver la desorganización de los contactos personales y profesionales. Permite registrar, gestionar y clasificar contactos vinculándolos a categorías generales (ej. Familia, Trabajo) y a grupos específicos (ej. Familia Materna, Compañeros de Tesis), evitando la redundancia de datos.

# Características Principales
- Crear, leer, editar y eliminar registros de contactos con validaciones de longitud y formato (teléfono de 9 dígitos, correos opcionales).
- Creación de **Categorías** y **Grupos** en cadena, los cuales alimentan los formularios de registro de contactos.
- Sistema de filtrado por categoría utilizando parámetros de consulta en la URL (`GET`).
- Diseño limpio e intuitivo construido con Bootstrap 5

# Tecnologías Utilizadas
Python 3.12, framework Flask.


# Se creo el entorno virtual y se activo

- python -3.12 -m venv venv
- venv\Scripts\activate

# Para instalar las dependecias

- pip install -r requirements.txt

# Para ejecutar el proyecto

- python app.py

# Para ejecutar documentacion api con swager api

- http://127.0.0.1:5000/apidocs/

# Estructura del Directorio

Proyecto_Manager_de_Contactos/
--- venv/                   # Entorno virtual (ignorado en Git)
--- templates/              # Vistas HTML
│   --- base.html           # Plantilla maestra (Navbar y estructura base)
│   --- inicio.html         # Página de bienvenida
│   --- lista.html          # Vista principal con filtros
│   --- detalle.html        # Ficha individual del contacto
│   --- form_crear.html     # Formulario para nuevo contacto
│   --- form_editar.html    # Formulario de edición con datos precargados
│   --- confirmar_eliminar.html # Pantalla de advertencia de borrado
│   --- form_categoria.html # Formulario para nuevas categorías
│   --- form_grupo.html     # Formulario para nuevos grupos
--- static/                 # Recursos estáticos (CSS/Imágenes adicionales)
--- app.py                  # Main del proyecto y rutas
--- requirements.txt        # Dependencias del proyecto
--- .gitignore              # Archivos excluidos del control de versiones
--- README.md               # Documentación del proyecto

