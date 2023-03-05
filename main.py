import cv2
import requests
import json
from time import sleep
from datetime import datetime
import sys


print(f'Version OPENCV {cv2.__version__}')
grabando= True
n_frames = 0
n_frames_max = 30
list_frames =[]
ahora = datetime.now()
fecha = ahora.strftime("%Y-%m-%d_%H-%M-%S")
captura =  cv2.VideoCapture(0)

UBICACION_FECHA_HORA = (20, 40)
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN
ESCALA_FUENTE = 2
COLOR_FECHA_HORA = (255, 255, 255)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA
FRAMES_VIDEO = 30.0
escala = 50
captura_ancho = int(int(captura.get(3))*escala/100)
captura_alto = int(int(captura.get(4))*escala/100)
RESOLUCION_VIDEO = (captura_ancho,captura_alto)#(int(captura.get(3)),int(captura.get(4)))
print(f'Resolucion -> {RESOLUCION_VIDEO}')

url = 'http://192.168.1.2:8000/upload'
nombre_video = f'video_{fecha}.avi'
salida = None
gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=192.168.86.26 port=5000"
salida = cv2.VideoWriter(nombre_video,cv2.VideoWriter_fourcc(*'XVID'),FRAMES_VIDEO,RESOLUCION_VIDEO)


def guardar_video():
    global salida
    global captura

    salida.release()
    captura.release() 
    print('--VIDEO GUARDADO--')
    print(f'Se ha completado un total de {n_frames_max}, equivalente a {int(n_frames_max / FRAMES_VIDEO)} ')
    print(f'Numero de frames totales : {n_frames} ...')
    print(f'Longitud final en ListaFrames: {len(list_frames)} ...')
    print('Preparando envio...')
    enviar_video()

def enviar_video():
    global url
    files = {'file': open(nombre_video, 'rb')}
    response = requests.post(url, files=files)  
    print('-- Video enviado --')
    if str(response) == '<Response [200]>':
        print('-- Video recibido en Server OK --')
    else:
        print(f'---Error en server: {response} ---')
        
    
    
        


def agregar_fecha_hora_frame(frame):
    cv2.putText(frame, fecha, UBICACION_FECHA_HORA, FUENTE_FECHA_Y_HORA,
                ESCALA_FUENTE, COLOR_FECHA_HORA, GROSOR_TEXTO, TIPO_LINEA_TEXTO)


def video_camara():
    global salida
    global captura
    global grabando
    global n_frames
    global n_frames_max

    n_frames_max = int(FRAMES_VIDEO) * int(input('Indica segundos de duracion:\n'))

    while n_frames != n_frames_max:
        print(f'Frames a reproducir: {n_frames_max}\n')
        print(f'Estado de camara: {grabando} ...')
        if grabando:
            print('GRABANDO VIDEO...')
            ret, frame = captura.read()
            if ret:
                print('Captura OK...')   
                ancho = int(frame.shape[1]*escala/100)
                alto = int(frame.shape[0]*escala/100)
                print(f'Dimensiones escaladas: ancho={ancho} x alto={alto}')
                frame_escala = cv2.resize(frame,(ancho,alto),interpolation=cv2.INTER_AREA)
                agregar_fecha_hora_frame(frame_escala)
                #frame_escala = cv2.flip(frame_escala, 1)
                list_frames.append(frame_escala)
                n_frames = n_frames + 1
                print(f'Numero de frame: {n_frames} ...')
                print(f'Contenido ListaFrames: {len(list_frames)} ...')
            else:
                print('---ERROR CAMARA---')
        else:
            print('---NO ESTA GRABANDO---')
    if n_frames == n_frames_max:
        for i in range(len(list_frames)):
            salida.write(list_frames[i])
        guardar_video()


if __name__ == "__main__":
    video_camara()
    