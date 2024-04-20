# Backend | IA

RestAPI desarrollada en Flask para el proyecto de IA con el profesor Rolando Andrade.
SMBD: Postgres.

## Instalación

Para instalar las dependencias de este proyecto, sigue estos pasos:

### Windows

1. Abre una terminal en el directorio del proyecto.
2. Ejecuta el siguiente comando para crear un entorno virtual:

`python -m venv venv`


3. Activa el entorno virtual:

`venv\Scripts\activate`


4. Instala las dependencias:

`pip install -r requirements.txt`


5. Instala las dependencias de Node:

`npm install`


### macOS

1. Abre una terminal en el directorio del proyecto.
2. Ejecuta el siguiente comando para crear un entorno virtual:

`python3 -m venv venv`


3. Activa el entorno virtual:

`source venv/bin/activate`


4. Instala las dependencias:

`pip3 install -r requirements.txt`


5. Instala las dependencias de Node:

`npm install`


## Ejecución

Para ejecutar el proyecto, sigue estos pasos:

1. Corre Tailwindcss con el siguiente comando:

`npx tailwindcss -i ./app/static/src/input.css -o ./app/static/src/main.css --watch`


2. Activa el entorno virtual.
3. Ejecuta el siguiente comando:

`flask --app app/app.py run --debug`


Esto iniciará el servidor web de Flask en modo de desarrollo.


## Contribuciones

Se aceptan contribuciones al proyecto. Para contribuir, sigue estos pasos:

1. Crea una rama de desarrollo.
2. Realiza los cambios necesarios.
3. Realiza un commit de los cambios.
4. Crea una solicitud de extracción.

