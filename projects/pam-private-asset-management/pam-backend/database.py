from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Sử dụng SQLite, file database sẽ được tạo ở thư mục gốc pam-backend
SQLALCHEMY_DATABASE_URL = "sqlite:///./pam_database.db"

engine = create_engine(
	SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

