from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Define the database connection URL
DATABASE_URL = "postgresql://admin:admin123@localhost:5432/postgres"

# Replace with your actual database credentials
DB_USER = "admin"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"

DATABASE_URL_FORMATTED = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2. Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL_FORMATTED)

# 3. Define a base for declarative models
Base = declarative_base()

# 4. Define a database model (optional, but common with SQLAlchemy)
class User(Base):
    __tablename__ = "users"  # Specify the table name

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)

# 5. Create the database tables (if they don't exist)
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist).")

# 6. Create a database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 7. Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 8. Example function to interact with the database
def add_user(db: SessionLocal, name: str, email: str):
    db_user = User(name=name, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: SessionLocal):
    return db.query(User).all()

def main():
    print("Starting the SQLAlchemy PostgreSQL connection example...")

    # Create tables if they don't exist
    create_tables()

    # Create a database session
    db = next(get_db())

    try:
        # Example: Add a new user
        new_user = add_user(db, name="Alice", email="alice@example.com")
        print(f"Added user: {new_user}")

        # Example: Get all users
        users = get_users(db)
        print("\nAll users:")
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")

    finally:
        # The 'get_db' function handles closing the session
        pass

    print("Finished.")

if __name__ == "__main__":
    main()