"""
Start_AI.py - Servidor de inferencia AI para ESP32-CAM

Este script recibe el stream MJPEG de una cámara ESP32-CAM, realiza inferencia con un modelo YOLO entrenado,
y muestra los resultados en tiempo real. Documentado paso a paso para facilitar su comprensión y modificación.
"""

import cv2 # OpenCV para manejo de imágenes
from ultralytics import YOLO # Modelo YOLO para detección de objetos

# URL de stream del ESP32-CAM (mjpeg)
url = "http://192.168.0.171/david/Dev"  # Cambia la IP según tu red

# Cargar modelo YOLO entrenado
model = YOLO("model/runs/detect/train/weights/best.pt")

# Captura del stream MJPEG
cap = cv2.VideoCapture(url)

while True:
    # Leer frame del stream
    ret, frame = cap.read()
    if not ret: # Condicional para verificar si se pudo leer el frame
        print("No se pudo leer el frame del ESP32-CAM")
        break

    # Predicción con YOLO (pasando el frame como array)
    results = model.predict(frame, conf=0.25)

    # Procesar resultados de detección
    if len(results[0].boxes) > 0: # Verifica si hay detecciones
        # Extraer clases y coordenadas de las cajas
        clases = results[0].boxes.cls.cpu().numpy()
        cajas = results[0].boxes.xyxy.cpu().numpy()  # también puedes usar xywh

        for i, caja in enumerate(cajas): # Iterar sobre cada detección
            # Extraer coordenadas y clase
            x_min, y_min, x_max, y_max = caja
            clase = int(clases[i]) # Convertir a entero
            nombre = model.names[clase] # Obtener nombre de la clase
            print(f"Detección {i}: {nombre} en [{x_min:.1f}, {y_min:.1f}, {x_max:.1f}, {y_max:.1f}]") # Mostrar información de la detección

    # Mostrar resultados (OpenCV dibuja las cajas y etiquetas)
    annotated_frame = results[0].plot() # Dibuja las detecciones en el frame
    cv2.imshow("ESP32-CAM", annotated_frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release() # Liberar captura de video
cv2.destroyAllWindows() # Liberar recursos de captura y cerrar ventanas
