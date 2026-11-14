import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models import db, Rol, Usuario, Cliente

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

def validar_password(password):
    """
    Criterio 2: Superior a 8 caracteres (> 8, es decir, 9 o más) 
    y alfanumérico (al menos una letra y un número).
    """
    if len(password) <= 8:
        return False
    tiene_letra = re.search(r"[a-zA-Z]", password) is not None
    tiene_numero = re.search(r"[0-9]", password) is not None
    return tiene_letra and tiene_numero

@clientes_bp.route("/registro", methods=["GET", "POST"])
def registrar_cliente():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefono = request.form.get("telefono", "").strip()
        password = request.form.get("password", "")

        # validación campos obligatorios
        if not nombre or not apellido or not email or not telefono or not password:
            flash("Todos los campos son obligatorios.")
            return redirect(url_for("clientes.registrar_cliente"))

        # validación criterio 2 (contraseña)
        if not validar_password(password):
            flash("La contraseña debe tener más de 8 caracteres e incluir letras y números.")
            return redirect(url_for("clientes.registrar_cliente"))

        # validación criterio 1 (mails duplicados)
        if Usuario.query.filter_by(email=email).first():
            flash("El correo electrónico ya está registrado en el sistema.")
            return redirect(url_for("clientes.registrar_cliente"))

        try:
            # se busca/crea el rol cliente (en caso de no estar creado)
            rol_cliente = Rol.query.filter_by(nombre="Cliente").first()
            if not rol_cliente:
                rol_cliente = Rol(nombre="Cliente")
                db.session.add(rol_cliente)
                db.session.flush() # Genera el id_rol sin cerrar la transacción todavía

            # se crea el usuario y a su vez se encripta la contraseña desde antes de ingresarla a la bd
            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                password_hash=generate_password_hash(password),
                id_rol=rol_cliente.id_rol
            )
            db.session.add(nuevo_usuario)
            db.session.flush() # Genera el id_usuario

            # vinculamos su perfil de cliente
            nuevo_cliente = Cliente(id_usuario=nuevo_usuario.id_usuario)
            db.session.add(nuevo_cliente)
            
            # confirmamos atómicamente en sqlite
            db.session.commit()
            
            flash("¡Registro exitoso! Tu cuenta de cliente ha sido creada.")
            return redirect(url_for("clientes.registrar_cliente"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error interno al registrar el usuario: {e}")
            return redirect(url_for("clientes.registrar_cliente"))

    return render_template("clientes/registro.html")