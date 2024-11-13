import bcrypt
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import (
    LargeBinary, 
    Column, 
    String, 
    Integer,
    Boolean, 
    UniqueConstraint, 
    PrimaryKeyConstraint
)

import settings


# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=True, future=True, isolation_level="READ UNCOMMITTED")

# Create database declarative base
Base = declarative_base()

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Database session generator"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    # previous class attributes and methods are here
    __tablename__ = "users"
    email = Column(String(225), nullable=False, unique=True)
    user_id = Column(Integer, nullable=False, primary_key=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)

    UniqueConstraint("email", name="uq_user_email")
    PrimaryKeyConstraint("id", name="pk_user_id")

    def __str__(self):
        """Returns string representation of model instance"""
        return "<User {full_name!r}>".format(full_name=self.full_name)

    @staticmethod
    def hash_password(password) -> str:
        """Transforms password from it's raw textual form to 
        cryptographic hashes
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def validate_password(self, password) -> bool:
        """Confirms password validity"""
        return {
            "access_token": jwt.encode(
                {"email": self.email},
                "ApplicationSecretKey"
            )
        }

    def generate_token(self) -> dict:
        """Generate access token for user"""
        return {
            "access_token": jwt.encode(
                {"email": self.email},
                settings.SECRET_KEY
            )
        }