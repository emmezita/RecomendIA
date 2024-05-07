# Backend | IA

RestAPI desarrollada en Flask para el proyecto de IA con el profesor Rolando Andrade.
SMBD: Postgres.

## Resumen del Proyecto

Este proyecto implementa un sistema de recomendación de películas sofisticado y personalizado, diseñado para ofrecer a los usuarios recomendaciones altamente relevantes basadas en sus preferencias y comportamientos de visualización anteriores. Utilizando técnicas avanzadas de procesamiento de lenguaje natural (NLP) y aprendizaje automático, el sistema analiza un vasto conjunto de datos de películas para identificar y recomendar contenido que resuene con los intereses individuales de cada usuario.

A través de un modelo de perfil de usuario dinámico, el sistema adapta sus recomendaciones basándose en las interacciones pasadas del usuario, incluyendo valoraciones de películas y géneros preferidos. Utilizando una matriz TF-IDF construida a partir de descripciones de películas, géneros y décadas de lanzamiento, el sistema evalúa la similitud entre el perfil del usuario y las características de las películas disponibles.La similitud coseno se emplea para identificar las películas más alineadas con los intereses del usuario, asegurando que las recomendaciones sean tanto precisas como diversas.

### Tecnología y Modelado

El corazón del sistema de recomendación es el uso del TF-IDF Vectorizer y la similitud coseno, técnicas fundamentales en el campo del NLP, para transformar y comparar los perfiles de usuarios y películas. Esta aproximación permite un análisis detallado del contenido textual asociado a cada película, incluyendo géneros y descripciones, para identificar patrones y similitudes con las preferencias del usuario.

### ¿Por que TD-IDF y Similitud de Coseno?

Al aplicar TF-IDF a las descripciones de películas, podemos cuantificar la relevancia de términos únicos, facilitando la comparación precisa entre películas y perfiles de usuario. Esta técnica transforma el texto en un espacio vectorial, destacando la importancia de términos específicos en relación a un conjunto de documentos. Al comparar vectores en el espacio TF-IDF, la similitud coseno ofrece una medida robusta de cómo de similares son dos documentos (en este caso, un perfil de usuario y una película), independientemente de su tamaño.

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