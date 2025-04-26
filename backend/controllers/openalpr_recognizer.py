import os
import subprocess
import json
from pprint import pprint


def find_plate(image_path):
    comand = [
        "docker",                       # inicia o docker
        "run",                          # executa o container
        "--rm",                         # remove o container após a execução
        "-v",                           # monta o volume do container
        f"{os.getcwd()}:/data:ro",      # mapeia o diretório atual para o diretório /data no container
        "openalpr",                     # imagem do openalpr
        "-c",                           # definir país Brasil
        "br",                           # país Brasil
        "-j",                           # saída em JSON 
        image_path                      # caminho da imagem
    ]
    
    res = subprocess.run(comand, capture_output=True, text=True)
    
    if res.returncode != 0:
        print("Erro ao executar o OpenALPR:", res.stderr)
        return []
    
    data = json.loads(res.stdout) #carrega o JSON retornado pelo OpenALPR
    # pprint(data) # imprime o JSON retornado pelo OpenALPR
    detected_plates = [] # lista para armazenar as placas detectadas
    
    for result in data.get("results", []): # percorre os resultados retornados pelo OpenALPR
        plate = result.get("plate") # obtém a placa
        box = result.get("coordinates", [{}])
        
        xmin = min(p.get('x') for p in box)
        xmax = max(p.get('x') for p in box)
        ymin = min(p.get('y') for p in box)
        ymax = max(p.get('y') for p in box)
    
        detected_plates.append({
            "image_path":image_path,
            "Plate":plate,
            "xmin":xmin,
            "xmax":xmax,
            "ymin":ymin,
            "ymax":ymax,
        })

    return detected_plates # retorna a lista de placas detectadas 
    
r = find_plate("/data/backend/assets/image1.jpg") 
print(r)