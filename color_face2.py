import cv2
import numpy as np
import mediapipe as mp


def determine_season(l, a, b, skin_tone):
    season = "Unknown"
    if skin_tone == "Warm (Cálido)":
        # Clasificación dentro de cálido
        if l > 60 and b < 150:
            season = "Spring (Primavera)"  # Claro y cálido
        else:
            season = "Autumn (Otoño)"  # Profundo y cálido
    elif skin_tone == "Cool (Frío)":
        # Clasificación dentro de frío
        if l > 60 and b < 148:
            season = "Summer (Verano)"  # Claro y frío
        else:
            season = "Winter (Invierno)"  # Profundo y frío
    else:
        season = "Neutral"  # No aplica a estaciones

    print(f"Estación: {season}")
    return season

# Inicializar el detector de rostros de MediaPipe
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)


def detect_skin_tone(image_path):
    # Cargar la imagen
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detectar rostros
    results = face_detection.process(image_rgb)
    
    if not results.detections:
        print("No se detectaron rostros.")
        return None
    
    # Tomar la primera detección de rostro
    for detection in results.detections:
        bboxC = detection.location_data.relative_bounding_box
        h, w, _ = image.shape
        x, y, w, h = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)
        
        # Extraer la región de la mejilla (zona central del rostro)
        roi_x1 = x + int(w * 0.3)
        roi_y1 = y + int(h * 0.4)
        roi_x2 = x + int(w * 0.7)
        roi_y2 = y + int(h * 0.7)
        roi = image[roi_y1:roi_y2, roi_x1:roi_x2]
        
        # Dibujar el rectángulo en la región analizada
        cv2.rectangle(image, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 0, 255), 2)

        # Convertir a espacio de color LAB (más preciso para tono de piel)
        roi_lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
        mean_lab = np.mean(roi_lab, axis=(0, 1))  # Obtener el promedio de color LAB
        
        # Extraer componente A (verde a magenta) y B (azul a amarillo)
        l, a, b = mean_lab
        
        # Clasificación de tono de piel
        if a >= 151 and b >= 144:
            skin_tone = "Warm (Cálido)"
        elif a <= 151 and b <= 148:
            skin_tone = "Cool (Frío)"
        else:
            skin_tone = "Neutral"
        season = determine_season(l, a, b, skin_tone)
        # Mostrar resultado
        print(f"Subtono de piel detectado: {skin_tone},valor de a :{a}, valor de b:{b}, season: {season}")
        cv2.putText(image, f"Skin Tone: {skin_tone}", (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Mostrar imagen con el resultado
        #cv2.imshow("Skin Tone Detection", image)
        
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        
        return skin_tone,season

# Prueba con una imagen
#image_path = "calido1.jpg"  # Cambia esto por tu imagen JPEG o PNG
#detect_skin_tone(image_path)