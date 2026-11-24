import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db
from blueprints.clientes import clientes_bp
from blueprints.auth import auth_bp, oauth
from blueprints.publico import publico_bp
from blueprints.turnos import turnos_bp
from blueprints.veterinaria import vet_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key_vet")
app.json.ensure_ascii = False

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veterinaria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
oauth.init_app(app)

app.register_blueprint(clientes_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(publico_bp)
app.register_blueprint(turnos_bp)
app.register_blueprint(vet_bp)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run(debug=True)
