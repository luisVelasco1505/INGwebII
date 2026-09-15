from datetime import datetime, timezone

from app.extensions import db

STATUSES = ('pendiente', 'atendida', 'cancelada')


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    diagnosis = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pendiente')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'date': self.date.isoformat(),
            'reason': self.reason,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }
