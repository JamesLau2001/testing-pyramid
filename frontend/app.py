from flask import Flask, render_template, request, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

BACKEND_URL = 'http://localhost:5000'
completions = set()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['role'] = user.role
            return redirect('/')
        return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/')
def index():
    coins = requests.get(f'{BACKEND_URL}/coins').json()

    for coin in coins:
        coin['completed'] = coin['id'] in completions

    return render_template('index.html', coins=coins, username=session.get('username'), role=session.get('role'))

@app.post('/coins/<id>/toggle_completion')
def toggle_coin_completion(id):
    if session.get('role') not in ('authenticated', 'admin'):
        return redirect('/login')
    if id in completions:
        completions.discard(id)
    else:
        completions.add(id)
    return redirect('/')

@app.route('/duties/<string:duty_id>')
def duty_detail(duty_id):
    duty = requests.get(f'{BACKEND_URL}/duties/{duty_id}').json()
    all_coins = requests.get(f'{BACKEND_URL}/coins').json()
    associated_coins = [c for c in all_coins if any(d['id'] == duty_id for d in c['duties'])]
    return render_template('duty_detail.html', duty=duty, associated_coins=associated_coins, username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)