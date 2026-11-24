import requests
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Cliente, Veterinario, Servicio, Turno

turnos_bp = Blueprint("turnos", __name__, url_prefix="/turnos")

BLOQUES_HORARIOS = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

def es_dia_valido(fecha_str):
    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    return fecha_dt.weekday() in [1, 3]

def buscar_feriado(fecha_str):
    anio = fecha_str[:4]
    try:
        respuesta = requests.get(f"https://api.argentinadatos.com/v1/feriados/{anio}", timeout=5)
        if respuesta.status_code != 200:
            return None
        for feriado in respuesta.json():
            if feriado["fecha"] == fecha_str:
                return feriado["nombre"]
    except Exception as e:
        print("Error consultando la api de feriados:", e)
    return None

def obtener_cliente_actual():
    id_usuario = session.get("id_usuario")
    if not id_usuario or session.get("rol") != "Cliente":
        return None
    return Cliente.query.filter_by(id_usuario=id_usuario).first()

@turnos_bp.route("/reservar", methods=["GET", "POST"])
def reservar_turno():
    cliente = obtener_cliente_actual()
    if not cliente:
        flash("Debes iniciar sesion como cliente para gestionar turnos.")
        return redirect(url_for("auth.login"))

    fecha_seleccionada = request.args.get("fecha", "")
    veterinarios = Veterinario.query.all()
    servicios = Servicio.query.all()
    horarios_disponibles = []

    if fecha_seleccionada:
        if not es_dia_valido(fecha_seleccionada):
            flash("La clinica solo atiende turnos los dias Martes y Jueves de 12:00 a 18:00 hs.")
        elif buscar_feriado(fecha_seleccionada):
            flash("Ese dia es feriado, la clinica no atiende turnos.")
        else:
            turnos_ocupados = Turno.query.filter(
                Turno.fecha == fecha_seleccionada,
                Turno.estado != "cancelado"
            ).all()
            horas_ocupadas = {t.hora for t in turnos_ocupados}
            horarios_disponibles = [h for h in BLOQUES_HORARIOS if h not in horas_ocupadas]

    if request.method == "POST":
        fecha = request.form.get("fecha", "").strip()
        hora = request.form.get("hora", "").strip()
        id_mascota = request.form.get("id_mascota")
        id_veterinario = request.form.get("id_veterinario")
        id_servicio = request.form.get("id_servicio")
        motivo = request.form.get("motivo", "").strip()

        if not all([fecha, hora, id_mascota, id_veterinario, id_servicio, motivo]):
            flash("Todos los campos del turno son obligatorios.")
            return redirect(url_for("turnos.reservar_turno", fecha=fecha))

        if not es_dia_valido(fecha) or hora not in BLOQUES_HORARIOS or buscar_feriado(fecha):
            flash("El dia u horario elegido esta fuera de la franja de atencion.")
            return redirect(url_for("turnos.reservar_turno"))

        solapado = Turno.query.filter(
            Turno.fecha == fecha,
            Turno.hora == hora,
            Turno.estado != "cancelado"
        ).first()

        if solapado:
            flash("Lo sentimos, ese horario acaba de ser reservado por otro usuario.")
            return redirect(url_for("turnos.reservar_turno", fecha=fecha))

        try:
            nuevo_turno = Turno(
                fecha=fecha,
                hora=hora,
                motivo=motivo,
                estado="pendiente",
                id_mascota=int(id_mascota),
                id_veterinario=int(id_veterinario),
                id_servicio=int(id_servicio)
            )
            db.session.add(nuevo_turno)
            db.session.commit()
            flash(f"Turno confirmado para el {fecha} a las {hora} hs (Motivo: {motivo}).")
            return redirect(url_for("clientes.panel_cliente"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agendar el turno: {e}")
            return redirect(url_for("turnos.reservar_turno", fecha=fecha))

    return render_template(
        "turnos/reservar.html",
        mascotas=cliente.mascotas,
        veterinarios=veterinarios,
        servicios=servicios,
        fecha_seleccionada=fecha_seleccionada,
        horarios_disponibles=horarios_disponibles
    )

@turnos_bp.route("/feriados/<int:anio>")
def ver_feriados(anio):
    try:
        respuesta = requests.get(f"https://api.argentinadatos.com/v1/feriados/{anio}", timeout=5)
        datos = respuesta.json()
        feriados = [{"fecha": f["fecha"], "nombre": f["nombre"]} for f in datos]
        return jsonify(feriados)
    except Exception as e:
        return jsonify({"error": f"No se pudo consultar la api de feriados: {e}"}), 500

@turnos_bp.route("/cancelar/<int:id_turno>", methods=["POST"])
def cancelar_turno(id_turno):
    cliente = obtener_cliente_actual()
    if not cliente:
        flash("Acceso no autorizado.")
        return redirect(url_for("auth.login"))

    turno = Turno.query.get_or_404(id_turno)

    if turno.mascota.id_cliente != cliente.id_cliente:
        flash("No tenes permisos para cancelar este turno.")
        return redirect(url_for("clientes.panel_cliente"))

    if turno.estado != "pendiente":
        flash("Solo se pueden cancelar turnos pendientes.")
        return redirect(url_for("clientes.panel_cliente"))

    fecha_hora_turno = datetime.strptime(f"{turno.fecha} {turno.hora}", "%Y-%m-%d %H:%M")
    ahora = datetime.now()

    if fecha_hora_turno <= ahora:
        flash("No es posible cancelar un turno pasado.")
        return redirect(url_for("clientes.panel_cliente"))

    if (fecha_hora_turno - ahora) < timedelta(hours=12):
        flash("La cancelacion requiere al menos 12 horas de antelacion.")
        return redirect(url_for("clientes.panel_cliente"))

    try:
        turno.estado = "cancelado"
        db.session.commit()
        flash("Turno cancelado correctamente. El horario ha sido liberado.")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al cancelar el turno: {e}")

    return redirect(url_for("clientes.panel_cliente"))
