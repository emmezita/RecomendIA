from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexión con la bd
conn = psycopg2.connect(
    dbname="bd_recomend",
    user="postgres",
    password="1234",
    host="localhost"
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
        cur.execute("SELECT * FROM public.\"Usuario\" WHERE usuario_id = %s", (email,))
        result = cur.fetchone()

        if result:
            if result[1] == password:
                session['email'] = email
                name = result[2] 
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
        cur.execute("SELECT COUNT(*) FROM public.\"Usuario\" WHERE usuario_id = %s", (email,))
        result = cur.fetchone()[0]

        if result > 0:
            return jsonify({'error': 'El correo electrónico ya está registrado.'}), 400
        else:
            cur.execute("INSERT INTO public.\"Usuario\" (usuario_id, usuario_password, usuario_name) VALUES (%s, %s, %s)", (email, password, fullname))
            conn.commit()
            cur.close()
            return jsonify({'success': 'Usuario registrado correctamente.'}), 200

    return render_template('register.html')

@app.route('/home')
def home(name=None):
    return render_template('home.html', name=name)

@app.route('/swipe')
def swipe():
    return render_template('swipe.html')

if __name__ == '__main__':
    app.run(debug=True)
