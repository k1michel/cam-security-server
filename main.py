import cv2
import requests
import json
from time import sleep
from datetime import datetime
import sys

ahora = datetime.now()
fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")


UBICACION_FECHA_HORA = (0, 15)
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN
ESCALA_FUENTE = 1
COLOR_FECHA_HORA = (255, 255, 255)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA
FRAMES_VIDEO = 20.0
RESOLUCION_VIDEO = (640, 480)
salida = None
captura =  cv2.VideoCapture(0)
gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=192.168.86.26 port=5000"

def agregar_fecha_hora_frame(frame):
    cv2.putText(frame, fecha, UBICACION_FECHA_HORA, FUENTE_FECHA_Y_HORA,
                ESCALA_FUENTE, COLOR_FECHA_HORA, GROSOR_TEXTO, TIPO_LINEA_TEXTO)

def video_camara():
    global salida
    global captura
    while True:
        ret, frame = captura.read()
        if ret:   
            agregar_fecha_hora_frame(frame)
            salida = cv2.VideoWriter(gst_str_rtp,0,FRAMES_VIDEO,RESOLUCION_VIDEO,True)
            frame = cv2.flip(frame, 1)
            salida.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
        else:
            print('---ERROR CAMARA---')
            break
            '''
            try:
                enviar = requests.post('http://localhost:8000/upload', file='video1.avi',timeout=4)
                print(f'Respuesta envio server {enviar}')
            except (requests.exceptions.ConnectTimeout):
                print('ERROR SERVER')
                continue
            '''
    salida.release()
    salida = None
    captura.release() 
    captura = None

if __name__ == "__main__":
    video_camara()