import requests
from pprint import pprint
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


root = Path(__file__).parents[2]
sys.path.append(str(root))

from backend.controllers.base_plate_recognizer import BasePlateRecognizer

dotenv_path = Path(__file__).parents[2].joinpath('.env')
load_dotenv(dotenv_path=str(dotenv_path))

class   PlateRecognizerAPI(BasePlateRecognizer):
    def __init__(self):
        self.api_key  = os.getenv("API_KEY")
        self.url = "https://api.platerecognizer.com/v1/plate-reader/" 
        self.headers = {'Authorization': f"Token {self.api_key}"}
    
    def find_plate(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                files = {"upload": image_file}
                response = requests.post(self.url, headers=self.headers, files=files)
        except Exception as e:
            print(f"Error ao abrir ou enviar imagem: {e}")
            return []
        
        if not response.ok:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
            return []
        
        results = response.json().get("results", [])
        placas_detectadas = []
        
        for result in results:
            placa_original = result.get("plate", '')
            box = result.get("box", {})
            corrected_plate = self._standardize_plate(placa_original)
            validate_plated = self._validate_plate(corrected_plate)
        
            placas_detectadas.append({
                "image_path": image_path,
                "plate": placa_original,
                "corrected_plate": corrected_plate,
                "validate_plated": validate_plated,
                "xmin": box.get("xmin"),
                "xmax": box.get("xmax"),
                "ymin": box.get("ymin"),
                "ymax": box.get("ymax"),
            })
        
        return placas_detectadas
