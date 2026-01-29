from flask import Flask, render_template, request, redirect, url_for, jsonify
from controllers.automate_duty import AutomateDutyController

import uuid
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)

if not app.config.get("SQLALCHEMY_DATABASE_URI"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")

duties= []

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
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    coin_name = db.Column(db.String(100), nullable=False, unique=True)

    duties = db.relationship('Duty', secondary=coin_duties, backref='coins')

    def to_dict(self):
        return {
            "id": self.id,
            "coin_name": self.coin_name,
            "duties": [d.to_dict() for d in self.duties]
        }

class Duty(db.Model):
    __tablename__ = "duties"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    duty_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False, unique=True)

    ksbs = db.relationship('KSB', secondary=duty_ksb, backref='ksbs')

    def to_dict(self):
        return {
            "id": self.id,
            "duty_name": self.duty_name,
            "description": self.description,
            "ksbs": [k.to_dict() for k in self.ksbs]
        }

class KSB(db.Model):
    __tablename__ = "ksbs"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ksb_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "ksb_name": self.ksb_name,
            "description": self.description
        }

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

@app.route('/coins', methods=['GET'])
def get_coins():
    coins = Coin.query.all()
    return jsonify([c.to_dict() for c in coins])

@app.post('/coin')
def create_coin():
    data = request.get_json()
    
    existing_coin = Coin.query.filter_by(coin_name=data['coin_name']).first()
    if existing_coin:
        return jsonify({"error": "Coin already exists"}), 400

    new_coin = Coin(coin_name=data['coin_name'])

    if 'duties' in data:
        for duty_name in data['duties']:
            duty = Duty.query.filter_by(duty_name=duty_name).first()
            if duty:
                new_coin.duties.append(duty)
            else:
                return jsonify({"error": "Duty does not exist"}), 404
            

    db.session.add(new_coin)
    db.session.commit()

    return jsonify(new_coin.to_dict()), 201

@app.route('/coin/<string:coin_id>', methods=['GET'])
def get_single_coin(coin_id):
    coin = Coin.query.get_or_404(coin_id)
    return jsonify(coin.to_dict())

@app.route('/coin/<string:coin_id>', methods=['PUT'])
def update_coin(coin_id):
    coin = Coin.query.get_or_404(coin_id)
    data = request.get_json()
    
    if 'coin_name' in data:
        coin.coin_name = data['coin_name']
    
    if 'duties' in data:
        coin.duties = [] 
        for duty_name in data['duties']:
            duty = Duty.query.filter_by(duty_name=duty_name).first()
            if duty:
                coin.duties.append(duty)
            else:
                return jsonify({"error": "Duty does not exist"}), 404
            
    db.session.commit()

    return jsonify(coin.to_dict())

@app.delete('/coin/<string:coin_id>')
def delete_coin(coin_id):
    coin = Coin.query.get_or_404(coin_id)
    db.session.delete(coin)
    db.session.commit()
    return "Coin successfully deleted", 200

@app.route('/duties', methods=['GET'])
def get_duties():
    duties = Duty.query.all()
    return jsonify([d.to_dict() for d in duties])

@app.post('/duty')
def create_duty():
    data = request.get_json()

    existing_duty = Duty.query.filter_by(duty_name=data['duty_name']).first()
    if existing_duty:
        return jsonify({"error": "Duty already exists"}), 400
    
    new_duty = Duty(duty_name=data['duty_name'], description=data['description'])
    
    if 'ksbs' in data:
        for ksb_name in data['ksbs']:
            ksb = KSB.query.filter_by(ksb_name=ksb_name).first()
            if ksb:
                new_duty.ksbs.append(ksb)
            else:
                return jsonify({"error": "KSB does not exist"}), 404

    db.session.add(new_duty)
    db.session.commit()

    return jsonify(new_duty.to_dict()), 201

@app.route('/duty/<string:duty_id>', methods=['GET'])
def get_single_duty(duty_id):
    duty = Duty.query.get_or_404(duty_id)
    return jsonify(duty.to_dict())

@app.route('/duty/<string:duty_id>', methods=['PUT'])
def update_duty(duty_id):
    duty = Duty.query.get_or_404(duty_id)
    data = request.get_json()
    
    if 'duty_name' in data:
        duty.duty_name = data['duty_name']

    if 'ksbs' in data:
        duty.ksbs = [] 
        for ksb_name in data['ksbs']:
            ksb = KSB.query.filter_by(ksb_name=ksb_name).first()
            if ksb:
                duty.ksbs.append(ksb)
            else:
                return jsonify({"error": "KSB does not exist"}), 404

    db.session.commit()

    return jsonify(duty.to_dict())

@app.delete('/duty/<string:duty_id>')
def delete_duty(duty_id):
    duty = Duty.query.get_or_404(duty_id)

    db.session.delete(duty)
    db.session.commit()

    return "Duty successfully deleted", 200


@app.route('/ksbs', methods=['GET'])
def get_ksbs():
    ksbs = KSB.query.all()
    return jsonify([k.to_dict() for k in ksbs])

@app.post('/ksb')
def create_ksb():
    data = request.get_json()

    existing_ksb = KSB.query.filter_by(ksb_name=data['ksb_name']).first()
    if existing_ksb:
        return jsonify({"error": "KSB already exists"}), 400

    new_ksb = KSB(ksb_name=data['ksb_name'], description=data['description'])
    db.session.add(new_ksb)
    db.session.commit()

    return jsonify(new_ksb.to_dict()), 201

@app.route('/ksb/<string:ksb_id>', methods=['GET'])
def get_single_ksb(ksb_id):
    ksb = KSB.query.get_or_404(ksb_id)
    return jsonify(ksb.to_dict())

@app.route('/ksb/<string:ksb_id>', methods=['PUT'])
def update_ksb(ksb_id):
    ksb = KSB.query.get_or_404(ksb_id)
    data = request.get_json()
    
    ksb.ksb_name = data['ksb_name']
    db.session.commit()

    return jsonify(ksb.to_dict())

@app.delete('/ksb/<string:ksb_id>')
def delete_ksb(ksb_id):
    ksb = KSB.query.get_or_404(ksb_id)

    db.session.delete(ksb)
    db.session.commit()
    
    return "KSB successfully deleted", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)