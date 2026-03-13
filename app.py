import streamlit as st
import pandas as pd
import requests
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('intfloat/multilingual-e5-small')

def conectar_base_datos(password):
    try:
        USER, HOST, PORT, DB_NAME = "postgres", "localhost", "5432", "GENA_database"
        engine = create_engine(f'postgresql://{USER}:{password}@{HOST}:{PORT}/{DB_NAME}')
        
        query = 'SELECT * FROM "GENA_Schema"."licitaciones"'
        df_local = pd.read_sql(query, engine)
        
        model = get_embedding_model()
        textos = ("passage: " + df_local["institucion"].fillna("") + " - " + 
                  df_local["titulo"].fillna("") + " - " + 
                  df_local["informacion"].fillna("")).tolist()
        
        embeddings_local = model.encode(textos, show_progress_bar=False)
        
        return df_local, embeddings_local, True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None, False

st.set_page_config(page_title="SEI-GENA Core", layout="wide")
st.title("SEarch for International calls for proposals using GENerative Artificial intelligence")

with st.sidebar:
    st.header(" Acceso a Datos")
    pwd = st.text_input("Contraseña de PostgreSQL", type="password")
    if st.button("Establecer Conexión Total"):
        with st.spinner("Conectando DB + Cargando IA..."):
            df, embs, status = conectar_base_datos(pwd)
            if status:
                st.session_state.df = df
                st.session_state.embeddings = embs
                st.session_state.db_connected = True
                st.success("Conexión Exitosa")

if st.session_state.db_connected:
    st.write(f"**Base de Datos conectada:** {len(st.session_state.df)} registros listos.")
    
    query_usuario = st.chat_input("Realiza una consulta técnica (Ej: Proyectos de infraestructura verde)")

    if query_usuario:
        model = get_embedding_model()
        q_vec = model.encode([f"query: {query_usuario}"])
        sims = cosine_similarity(q_vec, st.session_state.embeddings)[0]
        top_idx = sims.argsort()[-3:][::-1]
        results = st.session_state.df.iloc[top_idx]

        contexto_para_ia = "\n".join([f"- {r['institucion']}: {r['titulo']}" for _, r in results.iterrows()])

        with st.chat_message("assistant"):
            try:
                res = requests.post("http://localhost:11434/api/generate", 
                                    json={
                                        "model": "llama3",
                                        "prompt": f"Usuario busca: {query_usuario}\nResultados:\n{contexto_para_ia}\nAnaliza el mejor match en español:",
                                        "stream": False
                                    }, timeout=30)
                analisis = res.json().get('response')
                st.markdown(f"### 🎯 Síntesis\n{analisis}")
            except:
                st.error("Ollama no responde. Verifica que el servicio esté activo.")

        st.subheader("Fuentes detectadas")
        for _, row in results.iterrows():
            with st.expander(f"{row['institucion']} - {row['titulo']}"):
                st.write(f"**URL:** {row['url']}")
                st.write(f"**Detalle:** {row.get('informacion', 'Sin detalle')}")

else:
    st.warning("Esperando conexión con PostgreSQL para activar el LLM.")