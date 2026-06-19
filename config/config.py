from pathlib import Path

# Resolve the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Absolute path to the SQLite database
DATABASE_PATH = PROJECT_ROOT / 'datas' / 'dataspider.db'

TURSO_URL = 'libsql://dataspider-manskie.aws-ap-northeast-1.turso.io'
TURSO_TOKEN = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzExNDQzNzEsImlkIjoiM2NjZjc3YjEtZmFkNi00NzUzLWJjZjQtOGJmZjI3Nzc4M2MxIiwicmlkIjoiY2FkOWY5NjMtNzc0OC00ODJhLTgwODgtMTJjOTk2MjljMWJkIn0.QiEOCcTcgq6u6iieoIZYFaj_78ivosMzLDkaITF5U5WNn_XCBV3eGSd1UIONfXsqHx9LNSEdGHW0TxfCI0VFBw'
