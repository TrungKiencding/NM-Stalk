import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import Base
from sqlalchemy import create_engine, text
from config import Config
import logging

def clear_database():
    try:
        # Create engine
        engine = create_engine(Config.get_database_url())
        
        # Drop all tables
        Base.metadata.drop_all(engine)
        logging.info("All tables dropped successfully")
        
        # Recreate all tables
        Base.metadata.create_all(engine)
        logging.info("Database tables recreated successfully")
        
    except Exception as e:
        logging.error(f"Error clearing database: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    clear_database() 