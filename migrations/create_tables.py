import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from models.models import Base
from config import Config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_tables():
    try:
        # Create PostgreSQL database engine
        engine = create_engine(
            Config.get_database_url()
        )
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully!")
        
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

if __name__ == '__main__':
    success = create_tables()
    sys.exit(0 if success else 1)