import os
import sys
import cv2
import subprocess
import json
from pprint import pprint
from pathlib import Path

root = Path(__file__).parents[2]
sys.path.append(str(root))

from backend.controllers.base_plate_recognizer import BasePlateRecognizer


class OpenALPRDetector(BasePlateRecognizer):
    def find_plate(self, image_path):        
        # comand = [
        #     "docker",                       # inicia o docker
        #     "run",                          # executa o container
        #     "--rm",                         # remove o container após a execução
        #     "-v",                           # monta o volume do container
        #     f"{os.getcwd()}:/data:ro",      # mapeia o diretório atual para o diretório /data no container
        #     "openalpr",                     # imagem do openalpr
        #     "-c",                           # definir país Brasil
        #     "br",                           # país Brasil
        #     "-j",                           # saída em JSON 
        #     image_path                                        # caminho da imagem
        # ]
        image_dir = os.path.abspath(os.path.join(image_path, os.pardir))

        comand = [
            "docker",                       # inicia o docker
            "run",                          # executa o container
            "--rm",                         # remove o container após a execução
            "-v",                           # monta o volume do container
            f"{image_dir}:/data:ro",      # mapeia o diretório atual para o diretório /data no container
            "openalpr",                     # imagem do openalpr
            "-c",                           # definir país Brasil
            "br",                           # país Brasil
            "-j",                           # saída em JSON 
            f"/data/{Path(image_path).name}"                                        # caminho da imagem
        ]
        
        res = subprocess.run(comand, capture_output=True, text=True)
        
        if res.returncode != 0:
            print("Erro ao executar o OpenALPR:", res.stderr)
            return []
        
        
        if not res.stdout.strip():
            return {"error": "Saída vazia do OpenALPR", "details": "Verifique se a imagem está acessível pelo container."}

        try:
            data = json.loads(res.stdout)
        except json.JSONDecodeError as e:
            return {"error": "JSON inválido retornado pelo OpenALPR", "details": str(e)}
        
        
        detected_plates = [] # lista para armazenar as placas detectadas
        
        for result in data.get("results", []): # percorre os resultados retornados pelo OpenALPR
            plate = result.get("plate") # obtém a placa
            box = result.get("coordinates", [{}])
            
            xmin = min(p.get('x') for p in box)
            xmax = max(p.get('x') for p in box)
            ymin = min(p.get('y') for p in box)
            ymax = max(p.get('y') for p in box)
        
            corrected_plate = self._standardize_plate(plate) # padroniza a placa
            valid_plate = self._validate_plate(corrected_plate) # valida a placa
            
            detected_plates.append({
                "image_path":image_path,
                "plate":plate,
                "corrected_plate": corrected_plate,
                "validate_plated": valid_plate,
                "xmin":xmin,
                "xmax":xmax,
                "ymin":ymin,
                "ymax":ymax,
            })

        return detected_plates # retorna a lista de placas detectadas 
        
    def find_plate_in_video(self, video_path, frame_interval=30):
        
        videos_results = [] # lista para armazenar os resultados de cada frame
        video_capture = cv2.VideoCapture(video_path) # abre o vídeo 
        frame_count = 0 # contador de frames
        
        
        if not video_capture.isOpened():
            print("Erro ao abrir o vídeo:", video_path)
            return []
        
        while True:
            ret, frame = video_capture.read()
            
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                
                # Salva o frame em um arquivo temporário
                temp_frame_path = f"frame_temp_{frame_count}.jpg"
                cv2.imwrite(temp_frame_path, frame)
                
                docker_path = f"/data/{temp_frame_path}"
                
                # Chama a função find_plate para detectar placas no frame
                detected_plates = self.find_plate(docker_path)
                
                # for d in detected_plates:
                #     videos_results.append(d)
                
                # Adiciona os resultados à lista de vídeos
                videos_results.extend(detected_plates)
                
                # Remove o arquivo temporário
                os.remove(temp_frame_path)
            
            frame_count += 1
            
        video_capture.release() # libera o vídeo
        return videos_results # retorna a lista de placas detectadas no vídeo
