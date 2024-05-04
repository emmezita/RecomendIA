from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexión con la bd
conn = psycopg2.connect(
    dbname="knoguera",
    user="knoguera",
    password="123456",
    host="labs-dbservices01.ucab.edu.ve"
)

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
                name = result[1]
                usuario_id = result[0]
                session['usuario_id'] = usuario_id  # Guardar el ID del usuario en la sesión
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

            return "Preferencias guardadas correctamente"
        except psycopg2.Error as e:
            conn.rollback()
            return f"Error al guardar las preferencias: {e}"

    return render_template('home.html', name=name)


@app.route('/swipe')
def swipe():
    return render_template('swipe.html')

if __name__ == '__main__':
    app.run(debug=True)
