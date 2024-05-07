from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import psycopg2
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexión con la bd
conn = psycopg2.connect(
    dbname="knoguera",
    user="knoguera",
    password="123456",
    host="labs-dbservices01.ucab.edu.ve"
)

# FUNCIONES PARA EL SISTEMA DE RECOMENDACIÓN

def obtener_recomendaciones(genre_ids, year_ranges, n):
    # Convertir genre_ids y year_ranges a strings y ajustar el formato para coincidir con el entrenamiento
    genres_text = ','.join(map(str, genre_ids))  # Los géneros simplemente se unen por comas
    years_text = ' '.join([f"{str(year[0])[:3]}0s" for year in year_ranges])  # Convertir cada rango de años en su década correspondiente
    
    # El input_text debe reflejar cómo se ve el combined_text en tu dataset
    input_text = f"{genres_text} {years_text}"
    input_tfidf = tfidf_vectorizer.transform([input_text])
    
    # Calcular similitud coseno
    similarities = cosine_similarity(input_tfidf, tfidf_matrix)
    
    # Obtener índices de las películas más similares
    similar_indices = similarities.argsort(axis=1)[:, -n:][0]
    
    # Construir la lista de recomendaciones basada en los índices obtenidos
    recommended_movies = []
    for idx in similar_indices:
        if idx < len(df):  # Asegurar que el índice esté dentro del rango del DataFrame original
            movie = df.iloc[idx]
            recommended_movies.append({'movie_id': movie['movie_id'], 'title': movie['title'], 'genre_id': movie['genre_id'], 'age_release': movie['age_release'], 'image_url': movie['image_url'], 'description': movie['description']})
    
    # Convierte cualquier valor numpy.int64 en int
    for movie in recommended_movies:
        for key, value in movie.items():
            if isinstance(value, np.int64):
                movie[key] = int(value)

    return recommended_movies[:n]  # Devolver hasta n recomendaciones

##### FUNCION PARA OBTENER PELÍCULAS VISTAS POR EL USUARIO #####
def obtener_peliculas_vistas(usuario_id):
    # Inicializa una lista vacía para almacenar las películas vistas
    peliculas_vistas = []
    try:
        # Crea un nuevo cursor
        cur = conn.cursor()
        # Ejecuta una consulta SQL para obtener todas las películas vistas por el usuario
        cur.execute("SELECT pelicula_id FROM interaccionesusuariopelicula WHERE usuario_id = %s", (usuario_id,))
        # Obtiene todos los resultados de la consulta
        resultados = cur.fetchall()
        # Itera sobre cada fila en los resultados
        for fila in resultados:
            # Agrega el ID de la película a la lista de películas vistas
            peliculas_vistas.append(fila[0])
        # Cierra el cursor
        cur.close()
    except Exception as e:
        # Imprime cualquier error que ocurra
        print(f"Error al obtener películas vistas por el usuario {usuario_id}: {e}")

    # Devuelve la lista de películas vistas
    return peliculas_vistas

def actualizar_perfil_usuario(usuario_id):
    # Crea un cursor para interactuar con la base de datos
    cur = conn.cursor()
    # Ejecuta una consulta SQL para obtener las interacciones del usuario con las películas
    cur.execute("SELECT pelicula_id, valoracion FROM interaccionesusuariopelicula WHERE usuario_id = %s", (usuario_id,))
    # Obtiene todas las filas de la consulta
    interacciones = cur.fetchall()
    
    # Inicializa el perfil del usuario con ceros
    perfil_usuario = np.zeros(tfidf_matrix.shape[1])
    # Obtiene el número de filas en la matriz TF-IDF
    num_rows = tfidf_matrix.shape[0]
    
    # Itera sobre las interacciones del usuario
    for pelicula_id, valoracion in interacciones:
        try:
            # Encuentra el índice de la película en el DataFrame
            pelicula_idx = df.index[df['movie_id'] == pelicula_id].tolist()[0]

            # Ajusta los pesos según la valoración del usuario
            peso = 0.5 if valoracion == 2 else 1 if valoracion == 1 else -1
            # Si el índice de la película es válido, actualiza el perfil del usuario
            if pelicula_idx < num_rows:
                perfil_usuario += peso * tfidf_matrix[pelicula_idx, :].toarray().flatten()
            
        except IndexError:
            # Imprime una advertencia si no se encuentra el índice de la película
            print(f"Warning: No se encontró el índice para la película con ID {pelicula_id}.")
            continue

    # Normaliza el perfil del usuario
    norma = np.linalg.norm(perfil_usuario)
    if norma > 0:
        perfil_usuario = perfil_usuario / norma

    # Devuelve el perfil del usuario
    return perfil_usuario

def obtener_recomendaciones_usuario_regular(usuario_id, n):
    # Actualiza el perfil del usuario basado en sus interacciones con las películas
    perfil_usuario = actualizar_perfil_usuario(usuario_id)
    
    # Calcula la similitud del coseno entre el perfil del usuario y todas las películas
    similitudes = cosine_similarity(perfil_usuario.reshape(1, -1), tfidf_matrix)
    # Obtiene una lista de las películas que el usuario ya ha visto
    peliculas_vistas = obtener_peliculas_vistas(usuario_id)
    # Ordena las películas por su similitud con el perfil del usuario, en orden descendente
    recomendaciones_indices = np.argsort(similitudes.flatten())[::-1]
    
    recommended_movies = []
    # Itera sobre los índices de las películas recomendadas
    for idx in recomendaciones_indices:
        # Si ya hemos encontrado suficientes recomendaciones, termina el bucle
        if len(recommended_movies) >= n:
            break
        # Obtiene el ID de la película en el índice actual
        pelicula_id = df.iloc[idx]['movie_id']
        # Si el usuario no ha visto esta película, la añade a las recomendaciones
        if pelicula_id not in peliculas_vistas:
            # Convierte la fila del DataFrame en un diccionario y asegura que el ID de la película sea un entero
            movie = df.iloc[idx].to_dict()
            movie['movie_id'] = int(movie['movie_id'])
            # Añade la película a la lista de recomendaciones
            recommended_movies.append(movie)
    
    # Devuelve las recomendaciones
    return recommended_movies


def cargar_datos():
    movies_df = pd.read_csv("app/static/movies-dataset.csv")
    return movies_df

# Cargar los datos al iniciar la aplicación
movies_df = cargar_datos()

# Eliminar filas con valores np.nan en las columnas 'genre_id' y 'age_release'
df = movies_df.dropna(subset=['genre_id', 'age_release', 'description'])
df = df.reset_index(drop=True)

# Concatenar columnas 'genre_id' y 'age_release' para obtener un texto combinado
df['combined_text'] = df.apply(lambda x: f"{x['genre_id']} {str(x['age_release'])[:3]}0s {x['description']}", axis=1)

# Crear un TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_text'])

print(tfidf_matrix)


# RUTAS DE LA APLICACION WEB PARA LA RECOMENDACIÓN DE PELÍCULAS

@app.route("/")
def index():
    return redirect(url_for('welcome'))

@app.route('/welcome')
def welcome():
    return render_template('start.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = conn.cursor()
        cur.execute("SELECT * FROM public.\"usuario\" WHERE usuario_email = %s", (email,))
        result = cur.fetchone()

        if result:
            if result[3] == password:
                name = result[1]
                usuario_id = result[0]
                session['usuario_id'] = usuario_id
                session['usuario_nombre'] = name
                # Aquí se verifica si el usuario tiene preferencias registradas
                cur.execute("SELECT COUNT(*) FROM public.preferenciasusuario WHERE usuario_id = %s", (usuario_id,))
                pref_count = cur.fetchone()[0]
                cur.close()
                if pref_count > 0:
                    return redirect(url_for('swipe'))
                else:
                    return redirect(url_for('home'))
            else:
                return jsonify({'error': 'Clave inválida.'}), 400
        else:
            return jsonify({'error': 'El correo ingresado no pertenece a ninguna cuenta.'}), 400

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        passwordcf = request.form['passwordcf']

        if password != passwordcf:
            return jsonify({'error': 'Las contraseñas no coinciden.'}), 400

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.\"usuario\" WHERE usuario_email = %s", (email,))
        result = cur.fetchone()[0]

        if result > 0:
            return jsonify({'error': 'El correo electrónico ya está registrado.'}), 400
        else:
            cur.execute("INSERT INTO public.\"usuario\" (usuario_nombre, usuario_email, usuario_password) VALUES (%s, %s, %s)", (fullname, email, password))
            conn.commit()
            cur.close()
            return jsonify({'success': 'Usuario registrado correctamente.'}), 200

    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():

    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        return "Error: No se pudo obtener el ID del usuario"

    if request.method == 'POST':
        generos = request.form.getlist('generos')
        epocas = request.form.getlist('epocas')

        try:
            cur = conn.cursor()
            for genero in generos:
                for epoca in epocas:
                    ano_inicio, ano_fin = epoca.split('-')
                    cur.execute("INSERT INTO PreferenciasUsuario (usuario_id, genero, ano_inicio, ano_fin) VALUES (%s, %s, %s, %s)", (usuario_id, genero, ano_inicio, ano_fin))

            conn.commit()

            cur.close()

            # Mantener los datos del usuario en la sesión
            session['generos'] = generos
            session['epocas'] = epocas

            return redirect(url_for('swipe'))

        except psycopg2.Error as e:
            conn.rollback()
            return f"Error al guardar las preferencias: {e}"

    return render_template('home.html', id=id)

import requests

@app.route('/swipe', methods=['GET'])
def swipe():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        return "Error: No se pudo obtener el ID del usuario"

    try:
        # Verificar si el usuario es nuevo o regular
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM interaccionesusuariopelicula WHERE usuario_id = %s LIMIT 1", (usuario_id,))
        result = cur.fetchone()

        # Si 'result' es None, entonces 'count_interacciones' será 0, de lo contrario será 1
        count_interacciones = 0 if result is None else 1

        print(f"Contador de interacciones: {count_interacciones}")
        
        if count_interacciones == 0:
            # Usuario nuevo: Obtener preferencias y generar recomendaciones iniciales
            cur.execute("SELECT DISTINCT genero, ano_inicio, ano_fin FROM PreferenciasUsuario WHERE usuario_id = %s", (usuario_id,))    
            preferencias = cur.fetchall()

            if preferencias:
                generos = list(set([preferencia[0] for preferencia in preferencias]))
                epocas = list(set([(preferencia[1], preferencia[2]) for preferencia in preferencias]))
                print (generos, epocas)
                recomendaciones = obtener_recomendaciones(generos, epocas, 5)
                print (recomendaciones)
            else:
                print(f"No se encontraron preferencias para el usuario con ID {usuario_id}")
                recomendaciones = []
        else:
            # Usuario regular: Generar recomendaciones basadas en interacciones previas
            recomendaciones = obtener_recomendaciones_usuario_regular(usuario_id, 5)
            print(recomendaciones)
        
        cur.close()
        return render_template('swipe.html', recomendaciones=recomendaciones)
        
    except Exception as e:
        return f"Error al obtener las recomendaciones: {e}"

@app.route('/genres', methods=['GET'])
def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    headers = { "accept": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkMGI3OTVhMjQ2MzBkYTRhZjVkMTgwOTJkZGNlODE4MSIsInN1YiI6IjY2MjJhMTAwZTRjOWViMDBjN2Y0ZTFjYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.y6uNWZ--j5-V1-HTOdWk59EiCjvrNRMNHPzAwtu8ncg" }
    response = requests.get(url, headers=headers)
    genres = response.json().get('genres', [])
    return jsonify(genres)


@app.route('/guardar_interaccion', methods=['POST'])
def guardar_interaccion():
    # Obtener los datos de la solicitud AJAX
    data = request.json
    movie_id = data.get('movie_id')
    action = data.get('action')
    usuario_id = session.get('usuario_id')
    
    if usuario_id is None:
        return jsonify({'error': 'No se pudo obtener el ID del usuario'}), 400
    
    if action == 'love':
        valoracion = 1
    elif action == 'ignore':
        valoracion = 2
    else:  # action == 'nolove'
        valoracion = 0

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO interaccionesusuariopelicula (usuario_id, pelicula_id, valoracion) VALUES (%s, %s, %s)",
                    (usuario_id, movie_id, valoracion))
        conn.commit()
        cur.close()

        # Incrementar el contador de interacciones en la sesión
        if 'contador_interacciones' not in session:
            session['contador_interacciones'] = 0
        session['contador_interacciones'] += 1
        
        return jsonify({'success': 'Interacción del usuario guardada correctamente.'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': f'Error al guardar la interacción del usuario: {e}'}), 500
    
@app.route('/mostrar_recomendaciones', methods=['GET'])
def mostrar_recomendaciones():
    recomendaciones = obtener_recomendaciones_usuario_regular(session.get('usuario_id'), n=5)
    return jsonify(recomendaciones)


@app.route('/suggest', methods=['GET'])
def suggest():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        return "Error: No se pudo obtener el ID del usuario"

    try:
        # Verificar si el usuario es nuevo o regular
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM interaccionesusuariopelicula WHERE usuario_id = %s LIMIT 1", (usuario_id,))
        result = cur.fetchone()

        # Si 'result' es None, entonces 'count_interacciones' será 0, de lo contrario será 1
        count_interacciones = 0 if result is None else 1

        print(f"Contador de interacciones: {count_interacciones}")
        
        if count_interacciones == 0:
            # Usuario nuevo: Obtener preferencias y generar recomendaciones iniciales
            cur.execute("SELECT DISTINCT genero, ano_inicio, ano_fin FROM PreferenciasUsuario WHERE usuario_id = %s", (usuario_id,))    
            preferencias = cur.fetchall()

            if preferencias:
                generos = list(set([preferencia[0] for preferencia in preferencias]))
                epocas = list(set([(preferencia[1], preferencia[2]) for preferencia in preferencias]))
                print (generos, epocas)
                recomendaciones = obtener_recomendaciones(generos, epocas, 10)
                print (recomendaciones)
            else:
                print(f"No se encontraron preferencias para el usuario con ID {usuario_id}")
                recomendaciones = []
        else:
            # Usuario regular: Generar recomendaciones basadas en interacciones previas
            recomendaciones = obtener_recomendaciones_usuario_regular(usuario_id, 10)
            print(recomendaciones)
        
        cur.close()
        return render_template('suggest.html', recomendaciones=recomendaciones)
        
    except Exception as e:
        return f"Error al obtener las recomendaciones: {e}"

if __name__ == '__main__':
    app.run(debug=True)