from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from dotenv import load_dotenv

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
    return render_template('index.html', coins=coins, username=session.get('username'))

@app.route('/duties/<string:duty_id>')
def duty_detail(duty_id):
    duty = requests.get(f'{BACKEND_URL}/duties/{duty_id}').json()
    all_coins = requests.get(f'{BACKEND_URL}/coins').json()
    associated_coins = [c for c in all_coins if any(d['id'] == duty_id for d in c['duties'])]
    return render_template('duty_detail.html', duty=duty, associated_coins=associated_coins, username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)