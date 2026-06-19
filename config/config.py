import os

# connection.py passes these backend-neutral values to database.py.
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql").lower()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/dataspider",
)

TURSO_URL = 'libsql://dataspider-manskie.aws-ap-northeast-1.turso.io'
TURSO_TOKEN = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzExNDQzNzEsImlkIjoiM2NjZjc3YjEtZmFkNi00NzUzLWJjZjQtOGJmZjI3Nzc4M2MxIiwicmlkIjoiY2FkOWY5NjMtNzc0OC00ODJhLTgwODgtMTJjOTk2MjljMWJkIn0.QiEOCcTcgq6u6iieoIZYFaj_78ivosMzLDkaITF5U5WNn_XCBV3eGSd1UIONfXsqHx9LNSEdGHW0TxfCI0VFBw'
