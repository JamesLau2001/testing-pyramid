from flask import Flask, render_template, request, redirect, url_for
from controllers.automate_duty import AutomateDutyController

app = Flask(__name__)

duties = []

@app.route('/')
def index():
    return render_template("automate_duty.html", duties=duties)

@app.route('/create-duties', methods=['POST'])
def create_duties():
    number = request.form['number']
    description = request.form['description']
    ksbs = request.form['ksbs']

    duty = AutomateDutyController.create_duties(number, description, ksbs)
    duties.append(duty)

    return redirect(url_for('index'))
