import uuid
import bcrypt
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from api.database import SessionLocal, engine, Base

# Define the model to match the database table structure
class Utilisateur(Base):
    __tablename__ = "utilisateur"  # This matches the SQL table name

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # gerant_compagnie, utilisateur_compagnie
    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())
    date_derniere_connexion = Column(DateTime)
    actif = Column(Boolean, default=True)
    compagnie_id = Column(UUID(as_uuid=True))  # Assuming UUID type based on usage

def hash_password_bcrypt(plain_password):
    # Convert the password to bytes
    password_bytes = plain_password.encode('utf-8')
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return the hashed password as a string
    return hashed.decode('utf-8')

def create_user():
    # Create a database session
    db = SessionLocal()
    
    try:
        # Hash the password using bcrypt
        plain_password = "123456"
        hashed_password = hash_password_bcrypt(plain_password)
        
        # Create the user object with the correct table model
        user = Utilisateur(
            nom="R",
            prenom="Rado",
            email="rado@test.com",
            login="rado",
            mot_de_passe_hash=hashed_password,
            role="gerant_compagnie",
            compagnie_id=uuid.UUID("af13bb1d-014d-4c3f-841b-554d44111f38")
        )
        
        # Add the user to the database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"User created successfully with ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Login: {user.login}")
        print(f"Role: {user.role}")
        return user
        
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    user = create_user()