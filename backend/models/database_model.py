from backend.models import db
from datetime import datetime

class VehicleDetected(db.Model):
    __tablename__ = 'vehicles_detected'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String, nullable=False)
    original_plate = db.Column(db.String)
    correct_plate = db.Column(db.String) 
    valid_plate = db.Column(db.String) 
    xmin = db.Column(db.Integer)
    ymin = db.Column(db.Integer)
    xmax = db.Column(db.Integer)
    ymax = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    
    __table_args__ = (
        db.UniqueConstraint('image_path', 'original_plate', name='unique_image_plate_constraint'),
    )