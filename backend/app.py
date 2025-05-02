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
    
    return jsonify({'success': results}), 200

if __name__ == '__main__':
    app.run()