import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Singleton engine — created once, reused for all sessions
_engine = None

def get_db_engine():
    global _engine
    if _engine is not None:
        return _engine

    user = os.getenv('DB_USER')
    raw_password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_NAME')

    # Validate required env vars
    if not all([user, host, port, database]):
        print("Error: Missing environment variables DB (DB_USER, DB_HOST, DB_PORT, DB_NAME).")
        return None

    # Encoding password to handle special characters if any
    password = urllib.parse.quote_plus(raw_password) if raw_password else ""
    
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    try:
        engine = create_engine(connection_string, pool_pre_ping=True)
        with engine.connect() as conn:
            print("Connected to MySQL successfully!")
        _engine = engine
        return _engine
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_session():
    engine = get_db_engine()
    if engine:
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return Session()
    return None