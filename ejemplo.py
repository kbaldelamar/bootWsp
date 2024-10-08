from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

    def __repr__(self):
        return f'<Log {self.id}: {self.texto[:50]}...>'

    def __str__(self):
        return f"{self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}: {self.texto}"

with app.app_context():
    db.create_all()

def ordenar_fecha(registros):
    return sorted(registros, key=lambda x: x.fecha_hora, reverse=True)

@app.route('/')
def index():
    registros = Log.query.all()
    registros_order = ordenar_fecha(registros)
    return render_template('index.html', registros=registros_order)

mensajes_log = []

def agregar_log(data):
    texto = json.dumps(data)
    nuevo_log = Log(fecha_hora=datetime.utcnow(), texto=texto)
    db.session.add(nuevo_log)
    db.session.commit()

TOKEN_KEVINCODE = "KEVINCODE"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        data = request.get_json()
        agregar_log(data)
        return jsonify({'message': 'EVENT_RECEIVED'})

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
 
    if challenge and token == TOKEN_KEVINCODE:
        return challenge
    else:
        return jsonify({'error': 'Token invalido'}), 401

def recibir_mensajes(req):
    agregar_log(req)
    return jsonify({'message': 'EVENT_RECEIVED'})

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=80, debug=True)
