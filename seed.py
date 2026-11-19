from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import db, Rol, Usuario, Cliente, Mascota, Veterinario, Servicio, Turno, HistoriaClinica, RegistroClinico

def proximo_dia_semana(dia_objetivo):
    hoy = date.today()
    dias_adelante = (dia_objetivo - hoy.weekday() + 7) % 7
    if dias_adelante == 0:
        dias_adelante = 7
    return (hoy + timedelta(days=dias_adelante)).isoformat()

def cargar_datos_iniciales():
    with app.app_context():
        if Rol.query.first():
            print("La base de datos ya contiene datos iniciales.")
            return

        r_cli = Rol(nombre="Cliente")
        r_vet = Rol(nombre="Veterinario")
        db.session.add_all([r_cli, r_vet])
        db.session.flush()

        u_vet = Usuario(nombre="Dra. Ana", apellido="Gomez", email="ana@vet.com", telefono="1199887766", password_hash=generate_password_hash("vet123456"), id_rol=r_vet.id_rol)
        db.session.add(u_vet)
        db.session.flush()
        vet = Veterinario(id_usuario=u_vet.id_usuario, matricula="MP-4521")
        db.session.add(vet)

        u_cli = Usuario(nombre="Juan", apellido="Perez", email="juan@mail.com", telefono="1122334455", password_hash=generate_password_hash("cli123456"), id_rol=r_cli.id_rol)
        db.session.add(u_cli)
        db.session.flush()
        cli = Cliente(id_usuario=u_cli.id_usuario)
        db.session.add(cli)
        db.session.flush()

        mascota = Mascota(nombre="Firulais", especie="Perro", raza="Labrador", fecha_nacimiento="2022-05-10", id_cliente=cli.id_cliente)
        db.session.add(mascota)
        db.session.flush()

        historia = HistoriaClinica(id_mascota=mascota.id_mascota)
        db.session.add(historia)
        db.session.flush()

        nota_previa = RegistroClinico(
            id_historia=historia.id_historia,
            id_veterinario=vet.id_veterinario,
            diagnostico="Control anual y esquema de vacunacion completo.",
            observaciones="Paciente en excelente estado general, peso 28 kg.",
            medicacion="Antiparasitario interno comprimido."
        )
        db.session.add(nota_previa)

        s1 = Servicio(nombre="Consulta General", precio=15000.0)
        s2 = Servicio(nombre="Vacunacion", precio=12000.0)
        s3 = Servicio(nombre="Control / Seguimiento", precio=10000.0)
        db.session.add_all([s1, s2, s3])
        db.session.flush()

        turno_hoy = Turno(fecha=date.today().isoformat(), hora="14:00", motivo="Revision de oido derecho", estado="pendiente", id_mascota=mascota.id_mascota, id_veterinario=vet.id_veterinario, id_servicio=s1.id_servicio)
        turno_futuro = Turno(fecha=proximo_dia_semana(1), hora="15:00", motivo="Refuerzo vacuna sextuple", estado="pendiente", id_mascota=mascota.id_mascota, id_veterinario=vet.id_veterinario, id_servicio=s2.id_servicio)
        db.session.add_all([turno_hoy, turno_futuro])
        db.session.commit()
        print("Datos semilla cargados con exito.")

if __name__ == "__main__":
    cargar_datos_iniciales()
