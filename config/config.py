from pathlib import Path

# Resolve the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Absolute path to the SQLite database
DATABASE_PATH = PROJECT_ROOT / 'datas' / 'dataspider.db'

