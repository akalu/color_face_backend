# backend/database.py
import sqlite3
from datetime import datetime
import os

DB_PATH = "skin_analysis.db"

# Crear la base de datos si no existe
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            skin_tone TEXT,
            season TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Guardar un nuevo resultado en la base de datos
def save_analysis(filename: str, skin_tone: str, season: str):
    timestamp = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO analysis (filename, skin_tone, season, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (filename, skin_tone, season, timestamp))
    conn.commit()
    conn.close()

# Obtener todos los análisis guardados
def get_all_analyses():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filename, skin_tone, season, timestamp FROM analysis')
    rows = c.fetchall()
    conn.close()
    return [
        {"filename": row[0], "skin_tone": row[1], "season": row[2], "timestamp": row[3]}
        for row in rows
    ]

# Inicializar la base de datos al cargar este archivo
init_db()