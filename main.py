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
fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")
captura =  cv2.VideoCapture(0)

UBICACION_FECHA_HORA = (0, 15)
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN
ESCALA_FUENTE = 1
COLOR_FECHA_HORA = (255, 255, 255)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA
FRAMES_VIDEO = 30.0
RESOLUCION_VIDEO = (int(captura.get(3)),int(captura.get(4)))
print(f'Resolucion -> {RESOLUCION_VIDEO}')

salida = None
gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=192.168.86.26 port=5000"
salida = cv2.VideoWriter('video1.avi',cv2.VideoWriter_fourcc(*'XVID'),FRAMES_VIDEO,RESOLUCION_VIDEO)
def guardar_video():
    global salida
    global captura
    salida.release()
    captura.release() 
    print('--VIDEO GUARDADO--')
    print(f'Se ha completado un total de {n_frames_max}, equivalente a {int(n_frames_max / FRAMES_VIDEO)} ')
    print(f'Numero de frames totales : {n_frames} ...')
    print(f'Longitud final en ListaFrames: {len(list_frames)} ...')
        
    
    
        


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
                agregar_fecha_hora_frame(frame)
                frame = cv2.flip(frame, 1)
                list_frames.append(frame)
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
    