from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Initialiser FastAPI
app = FastAPI()

# Charger l'URL de la base de données
db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("La variable d'environnement DB_URL n'est pas définie")

# Chemin vers le dossier des templates
templates = Jinja2Templates(directory="templates")

# 🏠 Route principale (dashboard)
@app.get("/")
def home(request: Request):
    engine = create_engine(db_url)
    df = pd.read_sql("SELECT * FROM crypto_assets", engine)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cryptos": df.to_dict(orient="records"),
        "now": datetime.now()
    })

# 🔁 Route API - toutes les cryptos (JSON brut)
@app.get("/cryptos")
def get_cryptos():
    engine = create_engine(db_url)
    df = pd.read_sql("SELECT * FROM crypto_assets", engine)
    return df.to_dict(orient="records")

# 🔍 Route API - crypto par symbole (e.g. /cryptos/btc)
@app.get("/cryptos/{symbol}")
def get_crypto_by_symbol(symbol: str):
    engine = create_engine(db_url)
    query = "SELECT * FROM crypto_assets WHERE UPPER(symbol) = UPPER(%s)"
    df = pd.read_sql(query, engine, params=[symbol])
    if df.empty:
        return {"message": f"Aucune crypto trouvée avec le symbole '{symbol}'"}
    return df.to_dict(orient="records")[0]
