from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import psycopg2
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexión con la base de datos
conn = psycopg2.connect(
    dbname="knoguera",
    user="knoguera",
    password="123456",
    host="labs-dbservices01.ucab.edu.ve"
)

# Configuración API TMDB
API_KEY = '3837bf656a27f8c1fa184ba6fd14df31'
BASE_URL = 'https://api.themoviedb.org/3'

# Rutas de la aplicación

#Ruta de inicio
@app.route("/")
def index():
    return redirect(url_for('start'))

@app.route('/start')
def start():
    return render_template('start.html')

#Ruta de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM public.\"Usuario\" WHERE usuario_email = %s", (email,))
            result = cur.fetchone()

        if result:
            if result[3] == password:
                session['email'] = email
                session['name'] = result[1]
                return redirect(url_for('home'))
            else:
                return jsonify({'error': 'Clave inválida.'}), 400
        else:
            return jsonify({'error': 'El correo ingresado no pertenece a ninguna cuenta.'}), 400

    return render_template('login.html')

#Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        passwordcf = request.form['passwordcf']

        if password != passwordcf:
            return jsonify({'error': 'Las contraseñas no coinciden.'}), 400

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM public.\"Usuario\" WHERE usuario_email = %s", (email,))
            result = cur.fetchone()[0]

            if result > 0:
                return jsonify({'error': 'El correo electrónico ya está registrado.'}), 400
            else:
                cur.execute("INSERT INTO public.\"Usuario\" (usuario_email, usuario_password, usuario_nombre) VALUES (%s, %s, %s)", (email, password, fullname))
                conn.commit()
                return jsonify({'success': 'Usuario registrado correctamente.'}), 200

    return render_template('register.html')

#Ruta home base
@app.route('/home')
def home():
    name = session.get('name', 'Invitado')
    return render_template('home.html', name=name)

#Ruta para buscar peliculas
@app.route('/fetch_popular_movies')
def fetch_popular_movies():
    popular_movies = obtener_peliculas_populares()
    return jsonify(popular_movies)

#Obtener peliculas medite la API
def obtener_peliculas_populares():
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

#Ruta llamada a recomendaciones
@app.route('/recommend_movies')
def recommend_movies():
    user_id = request.args.get('user_id')
    recommendations = recommend_movies_for_user(user_id)
    return jsonify(recommendations)

#######################################################################################################
#Algoritmo de recomendaciones segun usuarios y preferencias
def recommend_movies_for_user(user_id):
    user_preferences = get_user_preferences(user_id)
    available_movies = get_available_movies()
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform([movie['description'] for movie in available_movies])
    user_pref_vector = tfidf.transform([user_preferences['genres']])
    sim_scores = cosine_similarity(user_pref_vector, tfidf_matrix)
    recommended_movie_indices = sim_scores.argsort()[0][-10:][::-1]
    recommended_movies = [available_movies[idx] for idx in recommended_movie_indices]
    return recommended_movies

#Obtener preferencia de los usuarios
def get_user_preferences(user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM public.\"PreferenciasUsuario\" WHERE usuario_id = %s", (user_id,))
        preferences = cur.fetchone()
        return {
            'genres': preferences[2]
        }

#Obtener peliculas
def get_available_movies():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM public.\"Pelicula\"")
        movies = cur.fetchall()
        return [{'description': movie[2]} for movie in movies]
    
#Almacenar peliculas
def guardar_pelicula_si_no_existe(pelicula):
    pelicula_id = pelicula['id']
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM public.\"Pelicula\" WHERE pelicula_id = %s", (pelicula_id,))
        exists = cur.fetchone()[0]

        if exists == 0:
            # Asumiendo que 'titulo', 'descripcion', 'generos', 'poster_path', 'release_date', y 'vote_average' están disponibles en el diccionario 'pelicula'
            cur.execute(
                "INSERT INTO public.\"Pelicula\" (pelicula_id, titulo, descripcion, generos, poster_path, release_date, vote_average) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (pelicula_id, pelicula['title'], pelicula.get('overview', ''), pelicula.get('genres', []), pelicula.get('poster_path', ''), pelicula.get('release_date', ''), pelicula.get('vote_average', 0))
            )
            conn.commit()

if __name__ == '__main__':
    app.run(debug=True)
