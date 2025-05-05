from backend.models.database_model import VehicleDetected
from backend.models import db
from sqlalchemy.exc import IntegrityError


def insert_vehicle(data):
   vehicle = VehicleDetected(**data)
   
   try:
       db.session.add(vehicle)
       db.session.commit()
       return True
   except IntegrityError:
       db.session.rollback()
       return False
       

def get_vehicles(image_path):
    v = VehicleDetected.query.filter_by(image_path=image_path).all()
         
    correct_plate = [v.correct_plate for v in v]
    last_date = max([v.created_at for v in v])  
         
    res = {
        'image_path': image_path,
        'plate': correct_plate,
        'data': last_date
    }
    
    return res