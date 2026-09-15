from datetime import datetime, timezone

from app.extensions import db

SPECIES = ('perro', 'gato', 'otro')


class Pet(db.Model):
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    species = db.Column(db.String(20), nullable=False)
    breed = db.Column(db.String(120), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    appointments = db.relationship(
        'Appointment', backref='pet', cascade='all, delete-orphan', lazy=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'age': self.age,
            'weight': self.weight,
            'created_at': self.created_at.isoformat(),
        }
