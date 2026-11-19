import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from authlib.integrations.flask_client import OAuth
from models import db, Rol, Usuario, Cliente

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
oauth = OAuth()

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not usuario.password_hash or not check_password_hash(usuario.password_hash, password):
            flash("Credenciales invalidas. Verifica tu correo y contrasena.")
            return redirect(url_for("auth.login"))

        session["id_usuario"] = usuario.id_usuario
        session["nombre"] = usuario.nombre
        session["rol"] = usuario.rol.nombre

        flash(f"Bienvenido/a, {usuario.nombre} ({usuario.rol.nombre}).")

        if usuario.rol.nombre == "Veterinario":
            return redirect(url_for("veterinaria.agenda_dia"))
        return redirect(url_for("clientes.panel_cliente"))

    return render_template("auth/login.html")

@auth_bp.route("/google")
def login_google():
    if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv("GOOGLE_CLIENT_SECRET"):
        flash("Faltan configurar GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en el archivo .env.")
        return redirect(url_for("auth.login"))
    try:
        redirect_uri = url_for("auth.callback_google", _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        flash(f"Error al conectar con Google OAuth: {e}")
        return redirect(url_for("auth.login"))

@auth_bp.route("/callback")
def callback_google():
    try:
        token = google.authorize_access_token()
        user_info = token.get("userinfo")

        if not user_info or not user_info.get("email"):
            flash("No se pudo obtener el correo desde Google.")
            return redirect(url_for("auth.login"))

        email = user_info["email"].strip().lower()
        nombre = user_info.get("given_name", "Usuario")
        apellido = user_info.get("family_name", "Google")

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            rol_cliente = Rol.query.filter_by(nombre="Cliente").first()
            if not rol_cliente:
                rol_cliente = Rol(nombre="Cliente")
                db.session.add(rol_cliente)
                db.session.flush()

            usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=None,
                password_hash=None,
                id_rol=rol_cliente.id_rol
            )
            db.session.add(usuario)
            db.session.flush()

            nuevo_cliente = Cliente(id_usuario=usuario.id_usuario)
            db.session.add(nuevo_cliente)
            db.session.commit()

        session["id_usuario"] = usuario.id_usuario
        session["nombre"] = usuario.nombre
        session["rol"] = usuario.rol.nombre

        flash(f"Sesion iniciada con Google como {usuario.nombre}.")

        if usuario.rol.nombre == "Veterinario":
            return redirect(url_for("veterinaria.agenda_dia"))
        return redirect(url_for("clientes.panel_cliente"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error en el callback de Google OAuth: {e}")
        return redirect(url_for("auth.login"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada correctamente.")
    return redirect(url_for("auth.login"))
