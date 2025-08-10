# Instalación del proyecto de forma local

---

Se requiere tener instalado uv, si no está instalado hacerlo con:

````pip install uv````

1. En la consola posicionarse en la carpeta que contendrá el proyecto y crear el venv
    ````bash
    uv venv
    ````

2. Instalar dependencias. Para instalar las dependencias del proyecto se debe tener el venv activado, sino se van a instalar de manera global.

     - **Para consola linux**
    ````bash
    source .venv/bin/activate
    ````
    
    - **Para command prompt**
    ````bash
    .venv\Scripts\activate.bat
    ````
    
    - **Para powershell**
     ````bash
     .\.venv\Scripts\activate.bat
     ````

3. Instalar Django localmente

    ````bash
    uv pip install django uvicorn
    ````

4. Instalar las dependencias y librerías

    ````pip install -r requirements.txt````


5. Probar que el proyecto funcione de manera local de forma correcta

   ````python manage.py runserver````

