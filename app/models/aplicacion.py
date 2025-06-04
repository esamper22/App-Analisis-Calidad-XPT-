import datetime
from app.extension import db

# ------------------------
# Modelo de Aplicaciones
# ------------------------
class Aplicacion(db.Model):
    __tablename__ = 'aplicaciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    version = db.Column(db.String(50), nullable=True, default='1.0.0')
    icono = db.Column(db.String(255), nullable=True)
    evaluada = db.Column(db.Boolean, default=False, nullable=False)  # Indica si la aplicación ha sido evaluada

    # Vincular nomenclador con el modelo de tipo de aplicación
    tipo_aplicacion_id = db.Column(db.Integer, db.ForeignKey('tipos_aplicacion.id'), nullable=True)
    tipo_aplicacion = db.relationship('TipoAplicacion', backref='aplicaciones', lazy=True)

    # Relaciones con otras entidades
    evaluaciones = db.relationship('ResultadoEvaluacion', backref='aplicacion', lazy=True)
    rondas = db.relationship('RondaEvaluacion', backref='aplicacion', lazy=True)

    def __init__(self, nombre, descripcion=None, tipo_aplicacion_id=None, version='1.0.0', icono=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_aplicacion_id = tipo_aplicacion_id
        self.version = version
        self.icono = icono

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f'<Aplicacion {self.nombre}>'

    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def actualizar(self, nombre=None, descripcion=None):
        if nombre:
            self.nombre = nombre
        if descripcion:
            self.descripcion = descripcion
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'icono': self.icono,
            'version': self.version,
            'categoria': self.tipo_aplicacion.nombre if self.tipo_aplicacion else None,
            # 'evaluaciones': [evaluacion.to_dict() for evaluacion in self.evaluaciones],
            # 'rondas': [ronda.to_dict() for ronda in self.rondas]
        }

    @staticmethod
    def obtener_todas():
        return Aplicacion.query.all()

    @staticmethod
    def obtener_por_id(aplicacion_id):
        return Aplicacion.query.get(aplicacion_id)

    @staticmethod
    def buscar_por_nombre(nombre):
        return Aplicacion.query.filter(Aplicacion.nombre.ilike(f'%{nombre}%')).all()

    @staticmethod
    def obtener_por_fecha(fecha_inicio, fecha_fin):
        return Aplicacion.query.filter(Aplicacion.fecha_creacion.between(fecha_inicio, fecha_fin)).all()

    @staticmethod
    def obtener_por_nombre_y_fecha(nombre, fecha_inicio, fecha_fin):
        return Aplicacion.query.filter(
            Aplicacion.nombre.ilike(f'%{nombre}%'),
            Aplicacion.fecha_creacion.between(fecha_inicio, fecha_fin)
        ).all()

    @staticmethod
    def obtener_por_descripcion(descripcion):
        return Aplicacion.query.filter(Aplicacion.descripcion.ilike(f'%{descripcion}%')).all()

    @staticmethod
    def obtener_por_nombre_y_descripcion(nombre, descripcion):
        return Aplicacion.query.filter(
            Aplicacion.nombre.ilike(f'%{nombre}%'),
            Aplicacion.descripcion.ilike(f'%{descripcion}%')
        ).all()

    @staticmethod
    def obtener_por_nombre_y_fecha_y_descripcion(nombre, fecha_inicio, fecha_fin, descripcion):
        return Aplicacion.query.filter(
            Aplicacion.nombre.ilike(f'%{nombre}%'),
            Aplicacion.fecha_creacion.between(fecha_inicio, fecha_fin),
            Aplicacion.descripcion.ilike(f'%{descripcion}%')
        ).all()
        
    @staticmethod
    def buscar_por_cualquier_parametro(nombre=None, fecha_inicio=None, fecha_fin=None, descripcion=None):
        query = Aplicacion.query
        if nombre:
            query = query.filter(Aplicacion.nombre.ilike(f'%{nombre}%'))
        if fecha_inicio and fecha_fin:
            query = query.filter(Aplicacion.fecha_creacion.between(fecha_inicio, fecha_fin))
        if descripcion:
            query = query.filter(Aplicacion.descripcion.ilike(f'%{descripcion}%'))
        return query.all()


# ------------------------
# Modelo Nomenclador para tipo de aplicación
# ------------------------
class TipoAplicacion(db.Model):
    __tablename__ = 'tipos_aplicacion'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)

    def __init__(self, nombre, descripcion=None):
        self.nombre = nombre
        self.descripcion = descripcion

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f'<TipoAplicacion {self.nombre}>'
    
    def guardar(self):
        db.session.add(self)
        db.session.commit()
    
    def eliminar(self):
        db.session.delete(self)
        db.session.commit()
    
    def actualizar(self, nombre=None, descripcion=None):
        if nombre:
            self.nombre = nombre
        if descripcion:
            self.descripcion = descripcion
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }
    
    @staticmethod
    def obtener_todos():
        return TipoAplicacion.query.all()
    
    @staticmethod
    def obtener_por_id(tipo_aplicacion_id):
        return TipoAplicacion.query.get(tipo_aplicacion_id)
    
    @staticmethod
    def buscar_por_nombre(nombre):
        return TipoAplicacion.query.filter(TipoAplicacion.nombre.ilike(f'%{nombre}%')).all()
    
    @staticmethod
    def buscar_por_descripcion(descripcion):
        return TipoAplicacion.query.filter(TipoAplicacion.descripcion.ilike(f'%{descripcion}%')).all()
    
    