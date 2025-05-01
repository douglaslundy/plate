import os
import sys
from pathlib import Path


from backend.controllers.openalpr_recognizer import OpenALPRDetector    
from backend.controllers.plate_recognizer import PlateRecognizerAPI
from backend.controllers.base_plate_recognizer import BasePlateRecognizer


root = Path(__file__).parents[2]
sys.path.append(str(root))


detector = OpenALPRDetector()
image_test = "/data/backend/assets/image1.jpg" # Teste com OpenALPR
# image_test = "backend/assets/image2.jpg" # Teste com PlateRecognizerAPI

plates = detector.find_plate(image_test)
print(plates)