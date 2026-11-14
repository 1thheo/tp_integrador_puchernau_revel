from flask import Flask, redirect, url_for
from models import db
from blueprints.clientes import clientes_bp

app = Flask(__name__)
app.secret_key = "dev_secret_key_vet"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veterinaria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(clientes_bp)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("clientes.registrar_cliente"))

if __name__ == "__main__":
    app.run(debug=True)