from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Veterinario, Turno, Mascota, HistoriaClinica, RegistroClinico

vet_bp = Blueprint("veterinaria", __name__, url_prefix="/veterinaria")

def obtener_veterinario_actual():
    id_usuario = session.get("id_usuario")
    if not id_usuario or session.get("rol") != "Veterinario":
        return None
    return Veterinario.query.filter_by(id_usuario=id_usuario).first()

@vet_bp.route("/agenda")
def agenda_dia():
    vet = obtener_veterinario_actual()
    if not vet:
        flash("Acceso exclusivo para personal veterinario.")
        return redirect(url_for("auth.login"))

    fecha_filtro = request.args.get("fecha", date.today().isoformat())
    estado_filtro = request.args.get("estado", "todos")

    query = Turno.query.filter_by(id_veterinario=vet.id_veterinario, fecha=fecha_filtro)

    if estado_filtro in ["pendiente", "finalizado"]:
        query = query.filter_by(estado=estado_filtro)

    turnos = query.order_by(Turno.hora.asc()).all()

    return render_template(
        "veterinaria/agenda.html",
        turnos=turnos,
        fecha_filtro=fecha_filtro,
        estado_filtro=estado_filtro
    )

@vet_bp.route("/atender/<int:id_turno>", methods=["GET", "POST"])
def registrar_consulta(id_turno):
    vet = obtener_veterinario_actual()
    if not vet:
        flash("Acceso exclusivo para personal veterinario.")
        return redirect(url_for("auth.login"))

    turno = Turno.query.get_or_404(id_turno)

    if request.method == "POST":
        diagnostico = request.form.get("diagnostico", "").strip()
        observaciones = request.form.get("observaciones", "").strip()
        medicacion = request.form.get("medicacion", "").strip()

        if not diagnostico:
            flash("Error: El diagnostico de la consulta no puede estar vacio.")
            return redirect(url_for("veterinaria.registrar_consulta", id_turno=id_turno))

        try:
            historia = HistoriaClinica.query.filter_by(id_mascota=turno.id_mascota).first()
            if not historia:
                historia = HistoriaClinica(id_mascota=turno.id_mascota)
                db.session.add(historia)
                db.session.flush()

            nueva_nota = RegistroClinico(
                id_historia=historia.id_historia,
                id_veterinario=vet.id_veterinario,
                diagnostico=diagnostico,
                observaciones=observaciones,
                medicacion=medicacion
            )
            db.session.add(nueva_nota)

            turno.estado = "finalizado"
            db.session.commit()

            flash("Nota clinica registrada y turno finalizado con exito.")
            return redirect(url_for("veterinaria.ver_historial", id_mascota=turno.id_mascota))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar la consulta: {e}")
            return redirect(url_for("veterinaria.registrar_consulta", id_turno=id_turno))

    return render_template("veterinaria/registrar_consulta.html", turno=turno)

@vet_bp.route("/historial/<int:id_mascota>")
def ver_historial(id_mascota):
    vet = obtener_veterinario_actual()
    if not vet:
        flash("Acceso exclusivo para personal veterinario.")
        return redirect(url_for("auth.login"))

    mascota = Mascota.query.get_or_404(id_mascota)
    registros = []

    if mascota.historia_clinica:
        registros = RegistroClinico.query.filter_by(
            id_historia=mascota.historia_clinica.id_historia
        ).order_by(RegistroClinico.id_registro.desc()).all()

    return render_template("veterinaria/historial.html", mascota=mascota, registros=registros)
