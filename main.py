import os, requests, pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- BLOQUE DE MIDDLEWARE ACTUALIZADO ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Permite llamadas desde cualquier sitio (GitHub Pages)
    allow_credentials=True,
    allow_methods=["*"],           # Permite POST, GET, OPTIONS, etc.
    allow_headers=["*"],           # Permite todos los headers (Content-Type, etc.)
)
# ----------------------------------------

# Carga del modelo de búsqueda
model = SentenceTransformer('intfloat/multilingual-e5-small')

class QueryRequest(BaseModel):
    user_question: str

@app.post("/ask")
async def ask_ai(request: QueryRequest):
    try:
        db_pass = os.getenv('POSTGRES_PASSWORD')
        engine = create_engine(f'postgresql://postgres:{db_pass}@34.39.132.137:5432/GENA_database')
        
        # RAG: Buscamos en la BD
        df = pd.read_sql('SELECT titulo, institucion, informacion FROM "GENA_Schema"."licitaciones" LIMIT 10', engine)
        textos = ("passage: " + df["institucion"].fillna("") + " " + df["titulo"].fillna("")).tolist()
        embs = model.encode(textos)
        q_vec = model.encode([f"query: {request.user_question}"])
        idx = cosine_similarity(q_vec, embs)[0].argmax()
        
        # CONEXIÓN DIRECTA (Loopback)
        # Cambiamos 10.158.0.2 por 127.0.0.1 para evitar latencia de red
        res = requests.post("http://127.0.0.1:11434/api/generate", json={
            "model": "phi3",
            "prompt": f"Contexto: {df.iloc[idx]['informacion']}\nPregunta: {request.user_question}\nResponde en español:",
            "stream": False
        }, timeout=120)
        
        return {
            "response": res.json().get('response'),
            "metadata": {"titulo": df.iloc[idx]['titulo'], "institucion": df.iloc[idx]['institucion']}
        }
    except Exception as e:
        print(f"Error detectado: {e}")
        raise HTTPException(status_code=500, detail=str(e))