# utils
from src.connection import get_session
# sample
from src.sample_data import generate_seed_data, insert_seed_data

def main():
    session = get_session()
    
    if session:
        try:
            print("Successfully connected to the database. Starting setup...")
            # Generate Seed Data
            print("Generating seed data...")
            generate_seed_data()
            # Insert seed data into database 
            print("Inserting seed data into the database...")
            insert_seed_data(session)
            session.commit()
        except Exception as e:
            print(f"Error at setup_database: {e}")
        finally:
            session.close()
            print("Database setup completed.")
    else:
        print("Failed to connect to the database. Please check your configuration.")

if __name__ == "__main__":
    main()