import cv2
import numpy as np
import requests
import json
from time import sleep
from datetime import datetime
import sys
from threading import Thread
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

cam = FastAPI()

print(f'Version OPENCV {cv2.__version__}')
print('---SOFTWARE by Michel Alvarez---')


## FECHA Y HORA DEL SISTEMA ##
ahora = datetime.now()
fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")
print(f'Fecha: {fecha}')
## INICIAR CAMARA ##
captura =  cv2.VideoCapture(0)
# Configuracion Imagen camara
codec = 0x47504A4D  # MJPG
captura_ancho = 640#int(int(captura.get(3))*escala/100)
captura_alto = 480#int(int(captura.get(4))*escala/100)
FRAMES_VIDEO = 30.0
captura.set(cv2.CAP_PROP_FPS, FRAMES_VIDEO)
captura.set(cv2.CAP_PROP_FOURCC, codec)
captura.set(cv2.CAP_PROP_FRAME_WIDTH, captura_ancho)
captura.set(cv2.CAP_PROP_FRAME_HEIGHT, captura_alto)
captura.set(cv2.CAP_PROP_AUTOFOCUS,0)

# Llamada al método
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(history=200, nmixtures=5, backgroundRatio=0.7, noiseSigma=0)
# Deshabilitamos OpenCL, si no hacemos esto no funciona
cv2.ocl.setUseOpenCL(False)

## CONSTANTES CONFIGURACION CAMARA ##
UBICACION_FECHA_HORA = (20, 40)
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN
ESCALA_FUENTE = 1
COLOR_FECHA_HORA = (255, 255, 255)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA

escala = 100

RESOLUCION_VIDEO = (captura_ancho,captura_alto) #(int(captura.get(3)),int(captura.get(4)))
print(f'Resolucion video-> {RESOLUCION_VIDEO}')

## ENVIO SERVIDOR ##

url = 'http://192.168.1.129:8000/upload'
nombre_video = f'video_{fecha}.mp4'
grabando= False
n_frames = 0
n_frames_max = 900
list_frames =[]
## GUARDAR VIDEO ##
salida = None
gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=192.168.86.26 port=5000"


## DETECCION MOVIMIENTO ##
fondo = None
contornosimg = None
n_max = 0

## FUNCION GUARDAR VIDEO EN RPI ##
def guardar_video():
    global salida
    global captura
    global fecha
    
    salida.release()
    print('--VIDEO GUARDADO--')
    print(f'Se ha completado un total de {n_frames_max}, equivalente a {int(n_frames_max / FRAMES_VIDEO)} segundos')
    print(f'Longitud final en ListaFrames: {len(list_frames)} ...')
    print('Preparando envio...')
    enviar_video()

## ENVIAR VIDEO AL SERVIDOR ##
def enviar_video():
    print('Enviando video ...')
    global url
    global nombre_video

    files = {'file': open(nombre_video, 'rb')}
    response = requests.post(url, files=files)  
    print('-- Video enviado --')
    if str(response) == '<Response [200]>':
        print('-- Video recibido en Server OK --')
    else:
        print(f'---Error en server: {response} ---')
        
## AGREGAR FECHA Y HORA AL VIDEO ##
def agregar_fecha_hora_frame(frame):
    cv2.putText(frame, fecha, UBICACION_FECHA_HORA, FUENTE_FECHA_Y_HORA,
                ESCALA_FUENTE, COLOR_FECHA_HORA, GROSOR_TEXTO, TIPO_LINEA_TEXTO)

def detectado():
    global n_frames
    global n_frames_max
    global grabando
    global salida
    global n_max
    global list_frames
    global ahora
    global fecha
    global nombre_video
    global salida

    if (n_frames == n_frames_max):
        grabando = False
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")
        nombre_video = f'video_{fecha}.mp4'
        salida = cv2.VideoWriter(nombre_video,cv2.VideoWriter_fourcc(*'mp4v'),FRAMES_VIDEO,RESOLUCION_VIDEO)
        for i in range(len(list_frames)):
            salida.write(list_frames[i])
        print('GUARDANDO VIDEO ....')
        n_frames = 0
        n_max = 0
        list_frames = []
        guardar_video()

## CAPTURAR Y MODIFICAR VIDEO DE LA CAMARA ##
def video_camara():
    global n_frames
    global n_frames_max
    global salida
    global captura
    global grabando
    global n_max
    global fondo
    global contornosimg
    while n_frames != n_frames_max:

        #n_frames_max = int(FRAMES_VIDEO) * int(input('Indica segundos de duracion:\n'))
        print(f'Frames a reproducir: {n_frames_max}\n')
        #print(f'Estado de camara: {grabando} ...')

            
        ret, frame = captura.read()
        if not ret:
		        print('CAMARA NO OK')
        if ret:

                    print('CAMARA OK...')   
                    '''
                    ancho = int(frame.shape[1]*escala/100)
                    alto = int(frame.shape[0]*escala/100)
                    print(f'Dimensiones escaladas: ancho={ancho} x alto={alto}')
                    frame_escala = cv2.resize(frame,(ancho,alto),interpolation=cv2.INTER_AREA)
                    '''
                    #ALGORITMO 
                    fgmask = fgbg.apply(frame)
                    contornosimg = fgmask.copy()
                    
                    # Buscamos contorno en la imagen
                    contornos, hierarchy = cv2.findContours(contornosimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    
                    # Recorremos todos los contornos encontrados
                    for n,c in enumerate(contornos):
                        # Eliminamos los contornos más pequeños
                        if cv2.contourArea(c) < 400:
                            continue
                        if n > n_max:
                            n_max = n
                        # Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
                        (x, y, w, h) = cv2.boundingRect(c)
                        # Dibujamos el rectángulo del bounds
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    agregar_fecha_hora_frame(frame)
                    #frame_escala = cv2.flip(frame_escala, 1)
                    if (n_max > 10) or grabando:
                        grabando = True
                        list_frames.append(frame)
                        n_frames = n_frames + 1
                        print('GRABANDO VIDEO...')
                        print(f'Numero de frame: {n_frames} ...')
                        print(f'Contenido ListaFrames: {len(list_frames)} ...')
        else:
            print('---ERROR CAMARA---')
        detectado()

if __name__ == "__main__":
    chequeo = Thread(target=video_camara, daemon=True)
    chequeo.start()
    detectado()
    uvicorn.run(cam, host="0.0.0.0", port=8000)
    