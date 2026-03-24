from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import pandas as pd
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SEI-GENA API")

# 1. Configuración de CORS (Permite que tu HTML hable con la API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargamos el modelo de embeddings una sola vez
model = SentenceTransformer('intfloat/multilingual-e5-small')

class QueryRequest(BaseModel):
    user_question: str
    password: str

@app.get("/")
async def home():
    return {"status": "online", "message": "SEI-GENA API is ready"}

@app.post("/ask")
async def ask_ai(request: QueryRequest):
    try:
        # Configuración de tu DB PostgreSQL
        USER, HOST, PORT, DB_NAME = "postgres", "34.39.132.137", "5432", "GENA_database"
        engine = create_engine(f'postgresql://{USER}:{request.password}@{HOST}:{PORT}/{DB_NAME}')
        
        # Recuperación de datos (RAG)
        df = pd.read_sql('SELECT * FROM "GENA_Schema"."licitaciones" LIMIT 10', engine)
        textos = ("passage: " + df["institucion"].fillna("") + " - " + df["titulo"].fillna("")).tolist()
        
        embs = model.encode(textos)
        q_vec = model.encode([f"query: {request.user_question}"])
        sims = cosine_similarity(q_vec, embs)[0]
        
        # Seleccionamos la licitación más relevante
        idx_relevante = sims.argmax()
        contexto = df.iloc[idx_relevante]['informacion']
        titulo_doc = df.iloc[idx_relevante]['titulo']
        institucion = df.iloc[idx_relevante]['institucion']

        # Consulta a Ollama (IP Interna de tu VM)
        url_ollama = "http://10.158.0.2:11434/api/generate"
        prompt_final = f"""
        Contexto de la licitación: {contexto}
        Pregunta del usuario: {request.user_question}
        Responde de forma profesional y breve en español basándote en el contexto.
        """
        
        res = requests.post(url_ollama, json={
            "model": "llama3",
            "prompt": prompt_final,
            "stream": False
        }, timeout=120)
        
        # Devolvemos la respuesta de la IA + metadatos para el inspector
        return {
            "response": res.json().get('response'),
            "metadata": {
                "titulo": titulo_doc,
                "institucion": institucion,
                "score": float(sims[idx_relevante])
            }
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))