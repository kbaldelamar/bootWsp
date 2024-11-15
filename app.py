from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import http.client



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

def agregar_log(texto):
    mensajes_log.append(texto)
 
    #guardar mensaje en DB
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()
TOKEN_KEVINCODE = "KEVINCODE"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
 
    if challenge and token == TOKEN_KEVINCODE:
        return challenge
    else:
        return jsonify({'error': 'Token invalido'}), 401

def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_messages = value['messages']
        if objeto_messages:
            messages=objeto_messages[0]
            if "type" in messages:
                tipo=messages["type"]
                if tipo == "interative":
                    return 0
                if "text" in messages:
                    text=messages["text"]["body"]
                    numero=messages["from"]
                    text1 = json.dumps(text)
                    numero1 = json.dumps(numero)
                    agregar_log(text1)
                    agregar_log(numero1)
                    enviar_mensaje(text1,numero1)
                    
        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})
    
def enviar_mensaje(texto, numero):
    texto = texto.lower()
    agregar_log("Mensaje recibido: " + texto)

    if "hola" in texto:
        agregar_log("Mensaje contiene 'hola'")
        mensaje = "hola soy robot"
    else:
        agregar_log("Mensaje no contiene 'hola'")
        mensaje = "hola soy robot nuetro menu es 1.resultados , 2.cotizar , 3.finalizar"

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": "false",
            "body": mensaje
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "EAAHXdfa87EQBO6YpEq4PNQBTYGDwBbOF7eZAweOaZAzC5wkwqQa1t5BPqt820HVsiTeFgVFApjC1Mbqq8rlj8sp6AHx4WUnaChzZAZCSvqcxLgflci0wiZARqx8mZBZAv57P1fbKZA2MSdZCZBi6eJIc4aMGtwSveE8lLiVL0UX21DjwWhbvu5nkZCHpqV3VVZA4Tnhnu1AtfHlYJfwyDZCy3amQzAsXZBoZAMZD"
    }

    try:
        agregar_log("Enviando mensaje...")
        connection = http.client.HTTPSConnection("graph.facebook.com")
        connection.request("POST", "/v20.0/105171825953083/messages", json.dumps(data), headers)
        response = connection.getresponse()
        agregar_log(f"Respuesta HTTP: {response.status} {response.reason}")
    except Exception as e:
        agregar_log("Error al enviar mensaje:")
        agregar_log(str(e))
    finally:
        connection.close()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
