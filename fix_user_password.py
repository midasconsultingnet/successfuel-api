import uuid
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./succes_fuel_v2/succes_fuel.db")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def hash_password_bcrypt(plain_password):
    # Convert the password to bytes
    password_bytes = plain_password.encode('utf-8')
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return the hashed password as a string
    return hashed.decode('utf-8')

def fix_user_password():
    """Fix the password for the user 'rado' by hashing it properly"""
    
    # Hash the password "123456"
    hashed_password = hash_password_bcrypt("123456")
    
    print(f"Original password: 123456")
    print(f"Hashed password: {hashed_password}")
    
    # Update the user in the database
    try:
        with engine.connect() as connection:
            # Update the password for the user with login 'rado'
            query = text("""
                UPDATE utilisateur 
                SET mot_de_passe_hash = :hashed_password 
                WHERE login = :login
            """)
            
            result = connection.execute(query, {
                "hashed_password": hashed_password,
                "login": "rado"
            })
            
            connection.commit()
            
            print(f"Updated {result.rowcount} user(s) with proper hashed password")
            print("User 'rado' should now be able to login with password '123456'")
            
    except Exception as e:
        print(f"Error updating user password: {str(e)}")

if __name__ == "__main__":
    fix_user_password()