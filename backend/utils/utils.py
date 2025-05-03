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
       