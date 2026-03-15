from app.extensions import db

class Mesa(db.Model):

    __tablename__ = "mesas"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False, unique=True)
    status = db.Column(db.String(20), default="livre")
    capacidade = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "status": self.status,
            "capacidade": self.capacidade
        }