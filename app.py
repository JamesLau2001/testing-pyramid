from flask import Flask, render_template, request, redirect, url_for, jsonify
from controllers.automate_duty import AutomateDutyController

import uuid
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)

duties = []

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"

db = SQLAlchemy(app)

coin_duties = db.Table('coin_duties',
    db.Column('coin_id', db.String(36), db.ForeignKey('coins.id'), primary_key=True),
    db.Column('duty_id', db.String(36), db.ForeignKey('duties.id'), primary_key=True)
)

duty_ksb = db.Table('duty_ksb',
    db.Column('duty_id', db.String(36), db.ForeignKey('duties.id'), primary_key=True),
    db.Column('ksb_id', db.String(36), db.ForeignKey('ksbs.id'), primary_key=True)
)

class Coin(db.Model):
    __tablename__ = "coins"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4))
    coin_name = db.Column(db.String(100), nullable=False, unique=True)

    duties = db.relationship('Duty', secondary=coin_duties, backref='coins')

class Duty(db.Model):
    __tablename__ = "duties"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4))
    duty_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False, unique=True)

    ksbs = db.relationship('KSB', secondary=duty_ksb, backref='ksbs')


class KSB(db.Model):
    __tablename__ = "ksbs"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4))
    ksb_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False, unique=True)

@app.route('/coins', methods=['GET'])
def get_coins():
    return [], 200

@app.route('/create-duties', methods=['POST'])
def create_duties():
    number = request.form['number']
    description = request.form['description']
    ksbs = request.form['ksbs']

    duty = AutomateDutyController.create_duties(number, description, ksbs)
    duties.append(duty)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)