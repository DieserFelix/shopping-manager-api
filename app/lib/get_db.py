def get_db():
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()