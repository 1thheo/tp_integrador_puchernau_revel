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
    email = db.Column(db.String(120), unique=True, nullable=False) # criterio 1 de la us01, no mails duplicados
    telefono = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
    
    perfil_cliente = db.relationship('Cliente', backref='usuario', uselist=False)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)