from app.extension import db

class Encuesta(db.Model):
    __tablename__ = 'encuestas'

    id = db.Column(db.Integer, primary_key=True)
    pregunta = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Encuesta {self.id}: {self.pregunta}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'pregunta': self.pregunta
        }
