from config.config import DATABASE_TYPE, DATABASE_URL
from scripts.db.database import load_database


# connection.py chooses the backend; database.py loads its adapter dynamically.
database = load_database(DATABASE_TYPE, {"url": DATABASE_URL})


def get_connection():
    """Compatibility helper for code that needs a raw backend connection."""
    return database.connect()
