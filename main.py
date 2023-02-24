import cv2
import requests
import json
from time import sleep
from datetime import datetime

captura = cv2.VideoCapture(0)
salida = cv2.VideoWriter('video1.avi',cv2.VideoWriter_fourcc(*'XVID'),20.0,(640,480))
while (captura.isOpened()):
    ret, imagen = captura.read()
    if ret == True:
        print('Procesando video...')
        salida.write(imagen)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    else:
        print('Error camara...')
        break

    
    
        '''
        try:
            enviar = requests.post('http://localhost:8000/upload', file='video1.avi',timeout=4)
            print(f'Respuesta envio server {enviar}')
        except (requests.exceptions.ConnectTimeout):
            print('ERROR SERVER')
            continue
        '''
        

captura.release()
cv2.destroyAllWindows()