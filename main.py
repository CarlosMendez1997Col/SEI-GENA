import os, requests, pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Abierto total para evitar bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer('intfloat/multilingual-e5-small')

# VARIABLE ÚNICA: pregunta
class QueryRequest(BaseModel):
    pregunta: str

@app.post("/ask")
async def ask_ai(request: QueryRequest):
    try:
        db_pass = os.getenv('POSTGRES_PASSWORD')
        engine = create_engine(f'postgresql://postgres:{db_pass}@34.39.132.137:5432/GEN_database')
        
        # RAG
        df = pd.read_sql('SELECT titulo, institucion, informacion FROM "GENA_Schema"."licitaciones" LIMIT 5', engine)
        textos = ("passage: " + df["institucion"].fillna("") + " " + df["titulo"].fillna("")).tolist()
        embs = model.encode(textos)
        q_vec = model.encode([f"query: {request.pregunta}"])
        idx = cosine_similarity(q_vec, embs)[0].argmax()
        
        # Ollama con Timeout extendido
        res = requests.post("http://127.0.0.1:11434/api/generate", json={
            "model": "phi3",
            "prompt": f"Contexto: {df.iloc[idx]['informacion']}\nPregunta: {request.pregunta}\nRespuesta corta en español:",
            "stream": False
        }, timeout=300)
        
        # Retorno de datos simple
        return {
            "respuesta": res.json().get('response'),
            "titulo": df.iloc[idx]['titulo'],
            "institucion": df.iloc[idx]['institucion']
        }
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
