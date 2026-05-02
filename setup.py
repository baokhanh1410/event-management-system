import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.sample_data import generate_seed_data, insert_seed_data

load_dotenv()

# ============================================================
# DATABASE CREDENTIALS
# ============================================================
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# ============================================================
# ENGINE & DATABASE SETUP
# ============================================================

def get_server_engine():
    """
    Create engine to connect to MySQL server without selecting a DB.
    """
    password = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    url = f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/"
    return create_engine(url)

def get_db_engine():
    """
    Create engine to connect to the specific database.
    """
    password = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    url = f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

def create_database():
    """
    Drop database if exists and create a new one.
    """
    engine = get_server_engine()
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`"))
        conn.execute(text(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
    engine.dispose()
    print(f"✅ Database `{DB_NAME}` has been created successfully.")

# ============================================================
# SCHEMA EXECUTION
# ============================================================

def execute_schema():
    """Read and execute schema.sql to create all tables, SPs, and views."""
    engine = get_db_engine()
    with open('sql/schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    with engine.connect() as conn:
        # Separate blocks with DELIMITER (Stored Procedures)
        parts = schema_sql.split('DELIMITER //')
        
        # Part 1: Normal statements (before DELIMITER)
        normal_sql = parts[0]
        for statement in normal_sql.split(';'):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        
        # Part 2+: Stored Procedure blocks
        for i in range(1, len(parts)):
            sp_block = parts[i]
            # Separate SP body (ends with //) and statements after DELIMITER ;
            sp_parts = sp_block.split('//')
            
            # SP body (part before //)
            sp_body = sp_parts[0].strip()
            if sp_body:
                conn.execute(text(sp_body))
            
            # Part after DELIMITER ; (views, etc.)
            if len(sp_parts) > 1:
                remaining = sp_parts[1].replace('DELIMITER ;', '').strip()
                for statement in remaining.split(';'):
                    stmt = statement.strip()
                    if stmt:
                        conn.execute(text(stmt))
        
        conn.commit()
    engine.dispose()
    print("✅ Schema (tables, indexes, foreign keys, SPs, views) executed successfully.")

# ============================================================
# MAIN ORCHESTRATION
# ============================================================

def main():
    print("=" * 50)
    print("  EVENT MANAGEMENT SYSTEM — Full Setup")
    print("=" * 50)

    # Step 1: Create database
    print("\n[1/4] Creating database...")
    create_database()

    # Step 2: Run schema.sql
    print("\n[2/4] Executing schema.sql...")
    execute_schema()

    # Step 3: Generate seed data
    print("\n[3/4] Generating seed data...")
    generate_seed_data()

    # Step 4: Insert seed data
    print("\n[4/4] Inserting seed data...")
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        insert_seed_data(session)
    except Exception as e:
        print(f"❌ Error while inserting seed data: {e}")
    finally:
        session.close()
        engine.dispose()

    print("\n" + "=" * 50)
    print("  ✅ SETUP COMPLETE!")
    print("  Default accounts:")
    print("    admin   / admin123  (Admin)")
    print("    staff01 / staff123  (Staff)")
    print("    organizer01 / organizer123  (Organizer)")
    print("    guest01 / guest123  (Guest)")
    print("    guest02 / guest123  (Guest)")
    print("    guest03 / guest123  (Guest)")
    print("    guest04 / guest123  (Guest)")
    print("    guest05 / guest123  (Guest)")
    print("=" * 50)

if __name__ == "__main__":
    main()