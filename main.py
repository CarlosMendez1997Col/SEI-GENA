import os, requests, pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carga del modelo de búsqueda
model = SentenceTransformer('intfloat/multilingual-e5-small')

# Clase sincronizada con el Frontend
class QueryRequest(BaseModel):
    query: str  # <--- Sincronizado con script.js

@app.post("/ask")
async def ask_ai(request: QueryRequest):
    try:
        db_pass = os.getenv('POSTGRES_PASSWORD')
        # Asegúrate de que la IP de la BD sea accesible desde esta VM
        engine = create_engine(f'postgresql://postgres:{db_pass}@34.39.132.137:5432/GENA_database')
        
        # RAG: Buscamos en la BD (Limitamos a 10 para velocidad)
        df = pd.read_sql('SELECT titulo, institucion, informacion FROM "GENA_Schema"."licitaciones" LIMIT 10', engine)
        
        if df.empty:
            raise ValueError("La base de datos no devolvió registros.")

        textos = ("passage: " + df["institucion"].fillna("") + " " + df["titulo"].fillna("")).tolist()
        embs = model.encode(textos)
        q_vec = model.encode([f"query: {request.query}"])
        idx = cosine_similarity(q_vec, embs)[0].argmax()
        
        # CONEXIÓN CON OLLAMA (Localhost)
        res = requests.post("http://127.0.0.1:11434/api/generate", json={
            "model": "phi3",
            "prompt": f"Contexto: {df.iloc[idx]['informacion']}\nPregunta: {request.query}\nResponde en español de forma profesional:",
            "stream": False
        }, timeout=150) # Aumentado a 150 segundos
        
        return {
            "response": res.json().get('response'),
            "metadata": {
                "titulo": df.iloc[idx]['titulo'], 
                "institucion": df.iloc[idx]['institucion']
            }
        }
    except Exception as e:
        print(f"Error en el servidor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
