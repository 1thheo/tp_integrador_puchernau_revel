from flask import Blueprint, render_template

publico_bp = Blueprint("publico", __name__)

@publico_bp.route("/contacto-guardias")
def contacto_guardias():
    info_clinica = {
        "nombre": "Clinica Veterinaria Integral",
        "direccion": "Av. San Martin 1450, Lujan, Buenos Aires",
        "telefono_turnos": "02323-421100",
        "whatsapp_guardia": "+54 9 2323 55-8899 (Urgencias 24 hs)",
        "horarios": "Martes y Jueves de 12:00 a 18:00 hs (Turnos) | Guardia Pasiva 24/7"
    }
    return render_template("publico/contacto_guardias.html", info=info_clinica)
