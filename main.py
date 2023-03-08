import cv2
import numpy as np
import requests
import json
from time import sleep
from datetime import datetime
import sys


print(f'Version OPENCV {cv2.__version__}')
print('---SOFTWARE by Michel Alvarez---')


grabando= True
n_frames = 0
n_frames_max = 15
list_frames =[]

## FECHA Y HORA DEL SISTEMA ##
ahora = datetime.now()
fecha = ahora.strftime("%Y-%m-%d_%H-%M-%S")

## INICIAR CAMARA ##
captura =  cv2.VideoCapture(0)

## CONSTANTES CONFIGURACION CAMARA ##
UBICACION_FECHA_HORA = (20, 40)
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN
ESCALA_FUENTE = 2
COLOR_FECHA_HORA = (255, 255, 255)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA
FRAMES_VIDEO = 15.0
escala = 25
captura_ancho = int(int(captura.get(3))*escala/100)
captura_alto = int(int(captura.get(4))*escala/100)
RESOLUCION_VIDEO = (captura_ancho,captura_alto)#(int(captura.get(3)),int(captura.get(4)))
print(f'Resolucion -> {RESOLUCION_VIDEO}')

## ENVIO SERVIDOR ##

url = 'http://192.168.1.2:8000/upload'
nombre_video = f'video_{fecha}.mp4'

## GUARDAR VIDEO ##
salida = None
gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=192.168.86.26 port=5000"
salida = cv2.VideoWriter(nombre_video,cv2.VideoWriter_fourcc(*'mp4v'),FRAMES_VIDEO,RESOLUCION_VIDEO)

## DETECCION MOVIMIENTO ##
fondo = None
contornosimg = None

## FUNCION GUARDAR VIDEO EN RPI ##
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

## ENVIAR VIDEO AL SERVIDOR ##
def enviar_video():
    global url
    files = {'file': open(nombre_video, 'rb')}
    response = requests.post(url, files=files)  
    print('-- Video enviado --')
    if str(response) == '<Response [200]>':
        print('-- Video recibido en Server OK --')
    else:
        print(f'---Error en server: {response} ---')
        
## AGREGAR FECHA Y HORA AL VIDEO ##
def agregar_fecha_hora_frame(frame_escala):
    cv2.putText(frame_escala, fecha, UBICACION_FECHA_HORA, FUENTE_FECHA_Y_HORA,
                ESCALA_FUENTE, COLOR_FECHA_HORA, GROSOR_TEXTO, TIPO_LINEA_TEXTO)

## CAPTURAR Y MODIFICAR VIDEO DE LA CAMARA ##
def video_camara():
    global salida
    global captura
    global grabando
    global n_frames
    global n_frames_max
    global fondo
    global contornosimg

    n_frames_max = int(FRAMES_VIDEO) * int(input('Indica segundos de duracion:\n'))

    while n_frames != n_frames_max:
        print(f'Frames a reproducir: {n_frames_max}\n')
        #print(f'Estado de camara: {grabando} ...')
        if grabando:
            print('GRABANDO VIDEO...')
            ret, frame = captura.read()
            if not ret:
		            print('CAMARA NO OK')
            if ret:

                    print('Captura OK...')   
                    ancho = int(frame.shape[1]*escala/100)
                    alto = int(frame.shape[0]*escala/100)
                    print(f'Dimensiones escaladas: ancho={ancho} x alto={alto}')
                    frame_escala = cv2.resize(frame,(ancho,alto),interpolation=cv2.INTER_AREA)
                    gris = cv2.cvtColor(frame_escala,cv2.COLOR_BGR2GRAY)
                    # Aplicamos suavizado para eliminar ruido
                    gris = cv2.GaussianBlur(gris,(21,21),0)
                    # Si todavía no hemos obtenido el fondo, lo obtenemos
                    # Será el primer frame que obtengamos
                    if fondo is None:
                        fondo = gris
                        continue
                    
                    # Calculo de la diferencia entre el fondo y el frame actual
                    resta = cv2.absdiff(fondo, gris)
                
                    # Aplicamos un umbral
                    umbral = cv2.threshold(resta, 25, 255, cv2.THRESH_BINARY)[1]
                
                    # Dilatamos el umbral para tapar agujeros
                    umbral = cv2.dilate(umbral, None, iterations=2)
                
                    # Copiamos el umbral para detectar los contornos
                    contornosimg = umbral.copy()
                
                    # Buscamos contorno en la imagen
                    contornos, hierarchy = cv2.findContours(contornosimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                    # Recorremos todos los contornos encontrados
                    for c in contornos:
                        # Eliminamos los contornos más pequeños
                        if cv2.contourArea(c) < 500:
                            continue
                
                        # Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
                        (x, y, w, h) = cv2.boundingRect(c)
                        # Dibujamos el rectángulo del bounds
                        cv2.rectangle(frame_escala, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                    # Mostramos las imágenes de la cámara, el umbral y la resta
                    #cv2.imshow("Camara", frame)
                    #cv2.imshow("Umbral", umbral)
                    #cv2.imshow("Resta", resta)
                    #cv2.imshow("Contorno", contornosimg)
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
    