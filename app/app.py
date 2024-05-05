from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import psycopg2
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import pickle


app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexión con la bd
conn = psycopg2.connect(
    dbname="knoguera",
    user="knoguera",
    password="123456",
    host="labs-dbservices01.ucab.edu.ve"
)

def cargar_datos():
    movies_df = pd.read_csv("app/static/movies-dataset.csv")
    return movies_df

# Cargar los datos al iniciar la aplicación
movies_df = cargar_datos()

# Eliminar filas con valores np.nan en las columnas 'genre_id' y 'age_release'
df = movies_df.dropna(subset=['genre_id', 'age_release', 'description'])

# Concatenar columnas 'genre_id' y 'age_release' para obtener un texto combinado
df['combined_text'] = df.apply(lambda x: f"{x['genre_id']} {str(x['age_release'])[:3]}0s {x['description']}", axis=1)

# Crear un TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_text'])

# Guardar la matriz TF-IDF
# with open('app/static/tfidf_matrix.pkl', 'wb') as f:
#     pickle.dump(tfidf_matrix, f)

# Guardar el modelo tfidf_vectorizer para futuras transformaciones
# with open('app/static/tfidf_vectorizer.pkl', 'wb') as f:
#     pickle.dump(tfidf_vectorizer, f)

# Cargar la matriz TF-IDF y el modelo TfidfVectorizer
# with open('app/static/tfidf_matrix.pkl', 'rb') as f:
#     tfidf_matrix = pickle.load(f)

# with open('app/static/tfidf_vectorizer.pkl', 'rb') as f:
#     tfidf_vectorizer = pickle.load(f)


# RUTAS DE LA APLICACION

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

def obtener_recomendaciones(genre_ids, year_ranges, n=10):
    # Convertir genre_ids y year_ranges a strings y ajustar el formato para coincidir con el entrenamiento
    genres_text = ','.join(map(str, genre_ids))  # Los géneros simplemente se unen por comas, sin el prefijo "genre_"
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
            recommended_movies.append({'title': movie['title'], 'genre_id': movie['genre_id'], 'age_release': movie['age_release'], 'image_url': movie['image_url']})
    
    return recommended_movies[:n]  # Devolver hasta n recomendaciones


@app.route('/swipe', methods=['GET', 'POST'])
def swipe():
    usuario_id = session.get('usuario_id')
    generos = session.get('generos')
    epocas = session.get('epocas')
    if usuario_id is None:
        return "Error: No se pudo obtener el ID del usuario"
    try:
        
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT genero, ano_inicio, ano_fin FROM PreferenciasUsuario WHERE usuario_id = %s", (usuario_id,))    

        preferencias = cur.fetchall()
        
        cur.close()

        if preferencias:
            generos = []
            epocas = []
            for preferencias in preferencias:
                genero, ano_inicio, ano_fin = preferencias
                if genero not in generos:
                    generos.append(genero)
                epoca = (ano_inicio, ano_fin)
                if epoca not in epocas:
                    epocas.append(epoca)
        else:
            print(f"No se encontró al usuario con ID {usuario_id}")
            return None
        
        print(generos)
        print(epocas)

        # Obtener recomendaciones de películas para el usuario
        recomendaciones = obtener_recomendaciones(generos, epocas, 5)
        print(recomendaciones)

        # Pasar las recomendaciones a la plantilla swipe.html para mostrarlas en la interfaz de usuario
        return render_template('swipe.html', recomendaciones=recomendaciones)
        
    except Exception as e:
        return f"Error al obtener las recomendaciones: {e}"
    
# FUNCIONES DE LA API

# # Función para acceder a la API de TMDb y obtener películas populares
# @app.route('/obtener_peliculas')
# def obtener_peliculas():
#     url = "https://api.themoviedb.org/3/discover/movie"
#     headers = {
#         "accept": "application/json",
#         "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzZDk4MTNmN2QyMDlmZjhkZmZlODFhYWY4ZmRkNTY1YiIsInN1YiI6IjY2MzZhOGI3ZTkyZDgzMDEyNGQzM2NmMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.3jTtHSc5yMrEhPzP2MU-7mxI72TFrUqxG3ZmPgbOLbc"
#     }
#     params = {
#         "api_key": "3d9813f7d209ff8dffe81aaf8fdd565b"
#     }
#     all_movies = []

#     response = requests.get(url, headers=headers, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         # Iterar sobre cada película en los resultados
#         for movie in data['results']:
#             # Crear un diccionario con los campos que deseas
#             movie_info = {
#                 'title': movie['title'],
#                 'genres': [genre_id for genre_id in movie['genre_ids']],
#                 'release_year': movie['release_date'][:4],
#                 'overview': movie['overview'],
#                 'poster_path': movie['poster_path']
#             }
#             all_movies.append(movie_info)

#         return jsonify(all_movies)
#     else:
#         return jsonify({'error': 'No se pudieron obtener las películas'}), response.status_code

@app.route('/genres', methods=['GET'])
def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    headers = { "accept": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkMGI3OTVhMjQ2MzBkYTRhZjVkMTgwOTJkZGNlODE4MSIsInN1YiI6IjY2MjJhMTAwZTRjOWViMDBjN2Y0ZTFjYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.y6uNWZ--j5-V1-HTOdWk59EiCjvrNRMNHPzAwtu8ncg" }
    response = requests.get(url, headers=headers)
    genres = response.json().get('genres', [])
    return jsonify(genres)

if __name__ == '__main__':
    app.run(debug=True)