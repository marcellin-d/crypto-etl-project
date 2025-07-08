import os
import requests
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class CryptoAsset(Base):
    __tablename__ = "crypto_assets"

    id = Column(String, primary_key=True, index=True)
    rank = Column(Integer)
    symbol = Column(String(20))
    name = Column(String(255))
    price_usd = Column(Numeric)
    market_cap_usd = Column(Numeric)
    volume_usd_24hr = Column(Numeric)
    change_percent_24hr = Column(Numeric)
    last_updated = Column(DateTime)

def fetch_coins(api_key="52a651f8da767f9491506a6cc83f6d81540e0b55be1bd2a1900da49b041719e2"):
    url = f"https://rest.coincap.io/v3/assets?apiKey={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['data']


def clean_data(raw_data):
    df = pd.DataFrame(raw_data)
    # Garder les colonnes utiles
    df = df[['id', 'rank', 'symbol', 'name', 'priceUsd', 'marketCapUsd', 'volumeUsd24Hr', 'changePercent24Hr']]
    
    # Conversion des types (avec errors='coerce' pour éviter crash)
    df['rank'] = pd.to_numeric(df['rank'], errors='coerce').astype('Int64')
    df['priceUsd'] = pd.to_numeric(df['priceUsd'], errors='coerce')
    df['marketCapUsd'] = pd.to_numeric(df['marketCapUsd'], errors='coerce')
    df['volumeUsd24Hr'] = pd.to_numeric(df['volumeUsd24Hr'], errors='coerce')
    df['changePercent24Hr'] = pd.to_numeric(df['changePercent24Hr'], errors='coerce')

    df['last_updated'] = datetime.now(timezone.utc)

    # Renommer colonnes pour correspondre à la base
    df.rename(columns={
        'priceUsd': 'price_usd',
        'marketCapUsd': 'market_cap_usd',
        'volumeUsd24Hr': 'volume_usd_24hr',
        'changePercent24Hr': 'change_percent_24hr',
        'last_updated': 'last_updated'
    }, inplace=True)

    return df

from sqlalchemy import create_engine, text
import os

def load_data(df):
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError("DB_URL is not set")

    engine = create_engine(db_url)

    # Crée la table si elle n'existe pas
    Base.metadata.create_all(engine)

    # Charger les données (remplace la table si elle existe déjà)
    df.to_sql("crypto_assets", con=engine, if_exists="replace", index=False)

    # Vérifier le nombre de lignes insérées
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM crypto_assets"))
        count = result.scalar()
        print(f"✅ Chargé {count} lignes dans la table 'crypto_assets'.")


def main():
    print("🚀 Extraction des données depuis CoinCap...")
    raw = fetch_coins()

    print("🔧 Nettoyage et transformation des données...")
    df = clean_data(raw)

    print("💾 Chargement des données dans PostgreSQL...")
    load_data(df)

    print("🎉 Pipeline ETL terminée avec succès.")

if __name__ == "__main__":
    main()
