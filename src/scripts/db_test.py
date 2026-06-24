from sqlalchemy import text

from src.database.session import SessionLocal

db = SessionLocal()

print(db.execute(text("SELECT 1")).scalar())

db.close()
