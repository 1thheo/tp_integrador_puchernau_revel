from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
    
    perfil_cliente = db.relationship('Cliente', backref='usuario', uselist=False)
    perfil_veterinario = db.relationship('Veterinario', backref='usuario', uselist=False)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    mascotas = db.relationship('Mascota', backref='dueno', lazy=True)

class Mascota(db.Model):
    __tablename__ = 'mascota'
    id_mascota = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(80), nullable=False)
    fecha_nacimiento = db.Column(db.String(20), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    
    turnos = db.relationship('Turno', backref='mascota', lazy=True)
    historia_clinica = db.relationship('HistoriaClinica', backref='mascota', uselist=False)

class Veterinario(db.Model):
    __tablename__ = 'veterinario'
    id_veterinario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    
    turnos = db.relationship('Turno', backref='veterinario', lazy=True)
    registros = db.relationship('RegistroClinico', backref='veterinario', lazy=True)

class Servicio(db.Model):
    __tablename__ = 'servicio'
    id_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    turnos = db.relationship('Turno', backref='servicio', lazy=True)

class Turno(db.Model):
    __tablename__ = 'turno'
    id_turno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascota.id_mascota'), nullable=False)
    id_veterinario = db.Column(db.Integer, db.ForeignKey('veterinario.id_veterinario'), nullable=False)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio'), nullable=False)

class HistoriaClinica(db.Model):
    __tablename__ = 'historia_clinica'
    id_historia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascota.id_mascota'), unique=True, nullable=False)
    registros = db.relationship('RegistroClinico', backref='historia', lazy=True)

class RegistroClinico(db.Model):
    __tablename__ = 'registro_clinico'
    id_registro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_historia = db.Column(db.Integer, db.ForeignKey('historia_clinica.id_historia'), nullable=False)
    id_veterinario = db.Column(db.Integer, db.ForeignKey('veterinario.id_veterinario'), nullable=False)
    diagnostico = db.Column(db.Text, nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    medicacion = db.Column(db.Text, nullable=True)