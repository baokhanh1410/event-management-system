import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

def get_db_engine():
    user = os.getenv('DB_USER')
    raw_password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_NAME')

    print("--- Database Configuration ---")
    print(f"Host:     {host}")
    print(f"Port:     {port}")
    print(f"User:     {user}")
    print(f"Database: {database}")
    print("------------------------------")

    # Mã hóa mật khẩu để xử lý ký tự đặc biệt nếu có
    password = urllib.parse.quote_plus(raw_password) if raw_password else ""
    
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            print("Kết nối đến MySQL thành công!")
        return engine
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return None

def get_session():
    engine = get_db_engine()
    if engine:
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return Session()
    return None