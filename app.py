import streamlit as st
import pandas as pd
import requests
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="SEI-GENA IA", layout="wide")

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('intfloat/multilingual-e5-small')

def conectar_base_datos(password):
    try:
        USER, HOST, PORT, DB_NAME = "postgres", "34.39.132.137", "5432", "GENA_database"
        engine = create_engine(f'postgresql://{USER}:{password}@{HOST}:{PORT}/{DB_NAME}')
        query = 'SELECT * FROM "GENA_Schema"."licitaciones" LIMIT 5'
        df_local = pd.read_sql(query, engine)
        model = get_embedding_model()
        textos = ("passage: " + df_local["institucion"].fillna("") + " - " + 
                  df_local["titulo"].fillna("") + " - " + 
                  df_local["informacion"].fillna("")).tolist()
        embeddings_local = model.encode(textos, show_progress_bar=False)
        return df_local, embeddings_local
    except Exception as e:
        st.error(f"DB Connection Error: {e}")
        return None, None

st.title("Welcome to SEI-GENA")
st.subheader("Search for International calls for proposals using GENerative AI")

with st.sidebar:
    st.header("Control Panel")
    pw = st.text_input("Database Password", type="password")
    if st.button("Connect"):
        with st.spinner("Synchronizing data..."):
            df, embs = conectar_base_datos(pw)
            if df is not None:
                st.session_state.df = df
                st.session_state.embeddings = embs
                st.success("✅ Connected! Data is ready.")

query_usuario = st.chat_input("Enter your search here...")

if query_usuario and 'df' in st.session_state:
    with st.spinner("AI is analyzing tenders..."):
        model = get_embedding_model()
        q_vec = model.encode([f"query: {query_usuario}"])
        sims = cosine_similarity(q_vec, st.session_state.embeddings)[0]
        top_idx = sims.argsort()[-3:][::-1]
        results = st.session_state.df.iloc[top_idx]
        contexto = "\n".join([f"- {r['institucion']}: {r['titulo']}" for _, r in results.iterrows()])
        
        try:
            url_ollama = "http://10.158.0.2:11434/api/generate"
            res = requests.post(url_ollama, 
                                json={
                                    "model": "llama3",
                                    "prompt": f"Analyze these tenders for: {query_usuario}\nContext:\n{contexto}\nRespond briefly in English:",
                                    "stream": False
                                }, timeout=180) 
            
            if res.status_code == 200:
                st.chat_message("assistant").markdown(res.json().get('response'))
            else:
                st.error(f"Error from AI Engine: Status {res.status_code}")
                
        except requests.exceptions.Timeout:
            st.error("The AI is taking too long. Please try again.")
        except Exception as e:
            st.error(f"AI Engine Error: {e}")