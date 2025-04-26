import requests
from pprint import pprint
import unittest
import os
import sys
from pathlib import Path

# root = Path(__file__).resolve().parent.parent
root = Path(__file__).parents[2]
sys.path.append(str(root))

from backend.controllers.base_plate_recognize import standardize_plate, validate_plate

API_KEY = "d4ffbb76da7e737d648908519fe2208939a19eb3"
url = "https://api.platerecognizer.com/v1/plate-reader/"
headers = {'Authorization': f"Token {API_KEY}"}

    
def find_plate(image_path):
    try:
        with open(image_path, "rb") as image_file:
            files = {"upload": image_file}
            response = requests.post(url, headers=headers, files=files)
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
        corrected_plate = standardize_plate(placa_original)
        validate_plated = validate_plate(corrected_plate)
    
        placas_detectadas.append({
            "caminho_imagem": image_path,
            "placa": placa_original,
            "corrected_plate": corrected_plate,
            "validate_plated": validate_plated,
            "xmin": box.get("xmin"),
            "xmax": box.get("xmax"),
            "ymin": box.get("ymin"),
            "ymax": box.get("ymax"),
        })
    
    return placas_detectadas
    
# fp = find_plate("C:/Users/wwwdl/workspace/plateflet360/backend/assets/h1.jpg")

# pprint(fp)