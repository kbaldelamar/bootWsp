from flask import Flask, render_template , request , jsonify
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

def ordenarfecha(registros):
    return sorted(registros, key=lambda x: x.fecha_hora, reverse=True)

@app.route('/')
def index():
    registros = Log.query.all()
    registtrosorder=ordenarfecha(registros)
    return render_template('index.html', registros=registtrosorder)

mensajes_log = []

def agregar_log(req):
    texto = json.dumps(req.json)
    
    nuevo_log = Log(fecha_hora=datetime.utcnow(), texto=texto)
    db.session.add(nuevo_log)
    db.session.commit()


# agregar_log(json.dumps("asdasd"))


TOKENKEVINCODE="KEVINCODE"
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificarToken(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response

def verificarToken(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
 
    if challenge and token == TOKENKEVINCODE:
        return challenge
    else:
        return jsonify({'error':'Token invalido'}),401

def recibir_mensajes(req):
    req=request.get_json()
    agregar_log(req)
    return jsonify({'message':'EVENT_RECEIVED'})
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)



