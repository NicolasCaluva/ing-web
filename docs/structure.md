# Estructura del proyecto

---

### `📁 app/`

Contiene las apps con toda la lógica del programa

### Dentro de cada app encontramos:

- **`/migrations`**: Migraciones a la base de datos
- **`admin.py`**: Models que se van a mapear en el panel de administrador de Django

- **`apps.py`**: Configuración de la app en la que nos encontramos

- **`models.py`**: Models que se van a mapear en la BD

- **`tests.py`**: Unit tests

- **`urls.py`**: URL de las vistas, se definen dentro de una variable urlpatterns que es una lista de las distintas url

  - Ejemplo:
    ````python
    urlpatterns = [
        path('/home', home_function, name='home'),
        path('/login', login_function, name='login')
    ]
    ````

    ### Donde:
    
    **1. path:** definir la url
  
    **2. view_function:** acá va la función que corresponde a la vista
  
    **3. name:** es un ‘alias’ que se le pone a la vista para que sea fácil de reconocer en el html (por ejemplo, en una etiqueta “a” que es un link, en vez de poner el link hardcodeado se puede poner {{ name }} y html reconoce que estás apuntando a esa url)


- **`views.py`**: Funciones que corresponden a las vistas.


### `📁 core/`

Código compartido que se usa en más de una funcionalidad, para evitar que se repita código en las distintas apps

- **`middleware.py`**: Middlewares, validaciones que se hacen antes de ingresar a la función

### `📁 dondeestudiar/`

Es la carpeta de la app que inicia el proyecto. Acá van las configuraciones generales del proyecto, base de datos y las url.

- **`asgi.py`**: Archivo de configuración que sirve para hacer un deploy

- **`local_settings.py`**: Archivo de configuraciones locales. Desde settings.py se importa el archivo para incluir estas configuraciones

- **`settings.py`**: Configuraciones generales del proyecto. Se deben registrar las apps del proyecto en INSTALLED_APPS

- **`urls.py`**: Es el punto principal de entrada del navegador hacia el proyecto en general, si bien cada app tiene un archivo urls.py, se tiene que incluir el archivo de cada app en este para que las urls que están en cada app sean reconocidas

- **`wsgi.py`**: Archivo de configuración que sirve para hacer un deploy

### `📁 static/`
Acá van a estar todos los archivos css, js y demás agregados del frontend

- **`📁 css/`:** Archivos de estilos

- **`📁 img/`**: Archivos de imágenes que se usan en el frontend de forma estática

- **`📁 js/`:** Archivos javascript

-  **`📁 fontawesome/`**: Integración extra de íconos

### `📁 templates/`

Acá van los archivos html. Se dividen en carpetas de la misma forma que las apps en el backend
base.html Es el html base principal, generalmente se arma un template con el panel lateral o el navbar y el footer, y luego en los otros archivos se usan los tags que ofrece Django para “heredar” de este template y no tener que repetir código
