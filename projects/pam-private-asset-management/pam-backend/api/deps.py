from app.db.session import SessionLocal

# This is our dependency. It will create a new SQLAlchemy SessionLocal
# for each request, and then close it when the request is finished.
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

