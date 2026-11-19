import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from models import db, Rol, Usuario, Cliente, Mascota

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

def validar_password(password):
    if len(password) <= 8:
        return False
    tiene_letra = re.search(r"[a-zA-Z]", password) is not None
    tiene_numero = re.search(r"[0-9]", password) is not None
    return tiene_letra and tiene_numero

def obtener_cliente_actual():
    id_usuario = session.get("id_usuario")
    if not id_usuario or session.get("rol") != "Cliente":
        return None
    return Cliente.query.filter_by(id_usuario=id_usuario).first()

@clientes_bp.route("/registro", methods=["GET", "POST"])
def registrar_cliente():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefono = request.form.get("telefono", "").strip()
        password = request.form.get("password", "")

        if not nombre or not apellido or not email or not telefono or not password:
            flash("Todos los campos son obligatorios.")
            return redirect(url_for("clientes.registrar_cliente"))

        if not validar_password(password):
            flash("La contrasena debe tener mas de 8 caracteres e incluir letras y numeros.")
            return redirect(url_for("clientes.registrar_cliente"))

        if Usuario.query.filter_by(email=email).first():
            flash("El correo electronico ya esta registrado en el sistema.")
            return redirect(url_for("clientes.registrar_cliente"))

        try:
            rol_cliente = Rol.query.filter_by(nombre="Cliente").first()
            if not rol_cliente:
                rol_cliente = Rol(nombre="Cliente")
                db.session.add(rol_cliente)
                db.session.flush()

            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                password_hash=generate_password_hash(password),
                id_rol=rol_cliente.id_rol
            )
            db.session.add(nuevo_usuario)
            db.session.flush()

            nuevo_cliente = Cliente(id_usuario=nuevo_usuario.id_usuario)
            db.session.add(nuevo_cliente)
            db.session.commit()
            
            flash("Registro exitoso! Ahora podes iniciar sesion.")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error interno al registrar el usuario: {e}")
            return redirect(url_for("clientes.registrar_cliente"))

    return render_template("clientes/registro.html")

@clientes_bp.route("/panel")
def panel_cliente():
    cliente = obtener_cliente_actual()
    if not cliente:
        flash("Debes iniciar sesion como cliente.")
        return redirect(url_for("auth.login"))
    return render_template("clientes/panel.html", cliente=cliente)

@clientes_bp.route("/mascotas/nueva", methods=["GET", "POST"])
def registrar_mascota():
    cliente = obtener_cliente_actual()
    if not cliente:
        flash("Debes iniciar sesion como cliente para registrar mascotas.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        especie = request.form.get("especie", "").strip()
        raza = request.form.get("raza", "").strip()
        fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()

        if not nombre or not especie or not raza or not fecha_nacimiento:
            flash("Todos los campos de la mascota son obligatorios.")
            return redirect(url_for("clientes.registrar_mascota"))

        try:
            nueva_mascota = Mascota(
                nombre=nombre,
                especie=especie,
                raza=raza,
                fecha_nacimiento=fecha_nacimiento,
                id_cliente=cliente.id_cliente
            )
            db.session.add(nueva_mascota)
            db.session.commit()
            flash(f"Mascota '{nombre}' registrada con exito.")
            return redirect(url_for("clientes.panel_cliente"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar la mascota: {e}")
            return redirect(url_for("clientes.registrar_mascota"))

    return render_template("clientes/nueva_mascota.html")
