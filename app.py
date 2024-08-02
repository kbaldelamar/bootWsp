from flask import Flask, render_template
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
    prueba1 =Log(texto='mensaje de prueba 1')
    prueba2 =Log(texto='mensaje de prueba 2')
    db.session.add(prueba1)
    db.session.add(prueba2)
    db.session.commit()
def ordenarfecha(registros):
    return sorted(registros, key=lambda x: x.fecha_hora, reverse=True)

@app.route('/')
def index():
    registros = Log.query.all()
    registtrosorder=ordenarfecha(registros)
    return render_template('index.html', registros=registtrosorder)

mensajes_log = []

def agregar_log(texto):
    mensajes_log.append(texto)
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

# agregar_log(json.dumps("asdasd"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)



