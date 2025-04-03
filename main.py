#// backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import shutil
import uuid
import os
from color_face2 import detect_skin_tone
from database import save_analysis, get_all_analyses

app = FastAPI()
security = HTTPBasic()

# CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://color-face-frontend.vercel.app/home",
    "https://color-face-frontend-kevins-projects-6bdc5737.vercel.app/home",
    "https://color-face-frontend-git-main-kevins-projects-6bdc5737.vercel.app/home",
    "https://color-face-frontend-9hwhsnmkx-kevins-projects-6bdc5737.vercel.app/home"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Credenciales simples (puedes cambiar esto a algo más robusto luego)
USERNAME = "admin"
PASSWORD = "1234"

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/analizar")
async def analizar_imagen(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    skin_tone, season = detect_skin_tone(file_path)
    save_analysis(filename, skin_tone, season)

    return JSONResponse({
        "skin_tone": skin_tone,
        "season": season,
        "image_filename": filename
    })

class QuizSubmission(BaseModel):
    answers: list[str]
    skin_tone: str | None = None
    season: str | None = None

@app.post("/quiz")
async def procesar_quiz(submission: QuizSubmission):
    # Lista de todos los estilos posibles
    all_styles = [
        "Streetwear", "Athleisure", "Vintage", "Minimalista",
        "Boho", "Grunge", "Cottagecore", "Dark Academia",
        "E-boy/E-girl", "Old Money"
    ]

    # Inicializar puntuaciones en 0
    style_scores = {style: 0 for style in all_styles}

    answer_to_styles = {
        # Pregunta 1
        "A1": ["Streetwear", "Athleisure"],
        "B1": ["Old Money", "Dark Academia"],
        "C1": ["Minimalista", "Boho"],
        # Pregunta 2
        "A2": ["Minimalista", "Old Money"],
        "B2": ["E-boy/E-girl", "Grunge"],
        "C2": ["Boho", "Cottagecore"],
        # Pregunta 3
        "A3": ["Minimalista", "Old Money"],
        "B3": ["Boho", "Cottagecore"],
        "C3": ["E-boy/E-girl", "Streetwear"],
        # Pregunta 4
        "A4": ["Athleisure", "Streetwear"],
        "B4": ["Old Money", "Dark Academia"],
        "C4": ["Boho", "Cottagecore"],
        # Pregunta 5
        "A5": ["E-boy/E-girl", "Grunge"],
        "B5": ["Dark Academia", "Old Money"],
        "C5": ["Streetwear", "Cottagecore"],
        # Pregunta 6
        "A6": ["Old Money", "Dark Academia"],
        "B6": ["Boho", "Cottagecore"],
        "C6": ["Streetwear", "Athleisure"],
        # Pregunta 7
        "A7": ["Dark Academia", "Old Money"],
        "B7": ["Cottagecore", "Boho"],
        "C7": ["Athleisure", "Streetwear"],
        # Pregunta 8
        "A8": ["Cottagecore", "Boho"],
        "B8": ["Grunge", "E-boy/E-girl"],
        "C8": ["Old Money", "Dark Academia"],
        # Pregunta 9
        "A9": ["Athleisure", "Streetwear"],
        "B9": ["Old Money", "Minimalista"],
        "C9": ["Grunge", "E-boy/E-girl"],
        # Pregunta 10
        "A10": ["E-boy/E-girl", "Streetwear"],
        "B10": ["Cottagecore", "Dark Academia"],
        "C10": ["Old Money", "Minimalista"],
        # Pregunta 11
        "A11": ["E-boy/E-girl", "Grunge"],
        "B11": ["Minimalista", "Boho"],
        "C11": ["Old Money", "Dark Academia", "Vintage"]
    }

    # Contar puntos
    for answer in submission.answers:
        styles = answer_to_styles.get(answer)
        if styles:
            for style in styles:
                style_scores[style] += 1

    # Devolver el ranking completo (ordenado por puntaje)
    ranked_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)

    return JSONResponse({
        "skin_tone": submission.skin_tone,
        "season": submission.season,
        "ranking": ranked_styles
    })

@app.get("/historial")
async def obtener_historial(credentials: HTTPBasicCredentials = Depends(check_auth)):
    historial = get_all_analyses()
    return JSONResponse(historial)
