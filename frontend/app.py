from flask import Flask, render_template
import requests

app = Flask(__name__)

BACKEND_URL = 'http://localhost:5000'

@app.route('/')
def index():
    coins = requests.get(f'{BACKEND_URL}/coins').json()
    return render_template('index.html', coins=coins)

@app.route('/duties/<string:duty_id>')
def duty_detail(duty_id):
    duty = requests.get(f'{BACKEND_URL}/duties/{duty_id}').json()
    all_coins = requests.get(f'{BACKEND_URL}/coins').json()
    associated_coins = [c for c in all_coins if any(d['id'] == duty_id for d in c['duties'])]
    return render_template('duty_detail.html', duty=duty, associated_coins=associated_coins)

if __name__ == '__main__':
    app.run(debug=True, port=3000)