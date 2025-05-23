from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import uuid
from pathlib import Path
from backend.controllers.openalpr_recognizer import OpenALPRDetector
from backend.controllers.plate_recognizer import PlateRecognizerAPI
import mimetypes
import os
from backend.utils.utils import insert_vehicle, get_vehicles

dotenv_path = Path(__file__).parents[1].joinpath('.env').as_posix()
load_dotenv(dotenv_path=dotenv_path)

from flask_migrate import Migrate
from backend.models import db
from backend.models.database_model import VehicleDetected

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)
migrate = Migrate(
        app=app, 
        db=db,
        directory=Path(__file__).parents[0].joinpath('migrations').as_posix()
    )

@app.route('/detect-plate', methods=['POST'])
def detect_plate():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image = request.files["image"]
    
    extension = Path(image.filename).suffix
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = Path(__file__).parents[0].joinpath('assets', file_name).as_posix()
    
    print('file_path', file_path)
    
    image.save(file_path)
    
    mimetype, _ = mimetypes.guess_type(file_path)
    
    detector = OpenALPRDetector()
    
    print('mimetype', mimetype)
     
     
    if mimetype.startswith('image'):
        results = detector.find_plate(file_path)
    elif mimetype.startswith('video') and hasattr(detector, 'find_plate_in_video'):
        results = detector.find_plate_in_video(file_path, 30)
    else:   
        return jsonify({"error": "Unsupported file type"}), 400
    
    if results:    
        for r in results:
            insert_vehicle(r)
        
        res = get_vehicles(file_path)
            
        return jsonify({'success': res}), 200
    
    return jsonify({'error': 'No plates detected'}), 404


#cRud - Read
@app.route('/vehicles', methods=['GET'])
def list_vehicles():
    vehicles = VehicleDetected.query.with_entities(VehicleDetected.image_path).distinct().all()
    vehicles_list = []
    
    for vehicle in vehicles:
        res = get_vehicles(vehicle.image_path)
        vehicles_list.append(res)        
    
    return jsonify(vehicles_list), 200


#crUd - Update
@app.route('/vehicles/<int:vehicle_id>', methods=['patch'])
def update_vehicle(vehicle_id):
    # vehicle = VehicleDetected.query.get_or_404(vehicle_id)
    vehicle = VehicleDetected.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    data = request.json
    
    for key, value in data.items():
        if hasattr(vehicle, key):
            setattr(vehicle, key, value)    
    
    db.session.commit()
    
    return jsonify({'message': 'Vehicle updated successfully'}), 200


#crud - Delete
@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = VehicleDetected.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    db.session.delete(vehicle)
    db.session.commit()
    
    return jsonify({'message': 'Vehicle deleted successfully'}), 200

if __name__ == '__main__':
    app.run()