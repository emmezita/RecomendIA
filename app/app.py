from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import psycopg2
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexión con la bd
conn = psycopg2.connect(
    dbname="knoguera",
    user="knoguera",
    password="123456",
    host="labs-dbservices01.ucab.edu.ve"
)

# RUTAS DE LA APLICACION

@app.route("/")
def index():
    return redirect(url_for('start'))

@app.route('/start')
def start():
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
                    return redirect(url_for('home', name=name))
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

@app.route('/home/<name>', methods=['GET', 'POST'])
def home(name=None):
    
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
            conn.close()
            
            return redirect(url_for('swipe'))
        
        except psycopg2.Error as e:
            conn.rollback()
            return f"Error al guardar las preferencias: {e}"

    return render_template('home.html', name=name)


@app.route('/swipe')
def swipe():
    return render_template('swipe.html')

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
