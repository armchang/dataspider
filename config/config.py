import os

# connection.py passes these backend-neutral values to database.py.
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql").lower()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:PASSWORD@localhost:5433/dataspider",
)

