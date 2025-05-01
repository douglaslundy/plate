import re
from abc import ABC, abstractmethod

#ABC = Essa classe base para definir uma interface, apenas serve como um modelo para outras classes
#abstractmethod = Decorador que indica que o método deve ser implementado por subclasses
class BasePlateRecognizer():
    
    @staticmethod
    def _standardize_plate(plate):
        plate = re.sub(r'[^A-Z0-9]', '', plate.upper())
        numbers_equivalence = {
            'O': '0',
            'I': '1',
            'A': '4',
            'S': '5',
            'B': '8',
            'Z': '2'
        }
        
        letters_equivalence = {
            '0': 'O',
            '1': 'I',
            '4': 'A',
            '5': 'S',
            '8': 'B',
            '2': 'Z',
        }
        
        correct_plate = list(plate)
        
        for i in range(3):
            if correct_plate[i] in letters_equivalence:
                correct_plate[i] = letters_equivalence[correct_plate[i]]
                
        for i in range(3, len(correct_plate)):
            #pula 5º caractere se for mercosul
            if i == 4 and len(correct_plate) == 7 and correct_plate[i].isalpha():
                continue
                    
            if correct_plate[i] in numbers_equivalence:
                correct_plate[i] = numbers_equivalence[correct_plate[i]]
        
        return ''.join(correct_plate)

    @staticmethod
    def _validate_plate(plate):
        old_pattern = r'^[A-Z]{3}[0-9]{4}$'
        new_pattern = r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$'    
        return bool(re.match(old_pattern, plate) or re.match(new_pattern, plate))


@abstractmethod
def find_plate(self):
    pass
