import bcrypt
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./succes_fuel.db")

# Create engine
engine = create_engine(DATABASE_URL)

def hash_password_simple(plain_password):
    """Hash a password with bcrypt using a simple approach"""
    # Ensure the password is less than 72 bytes
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    
    # Convert password to bytes
    password_bytes = plain_password.encode('utf-8')
    
    # Hash the password
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    # Return as string
    return hashed.decode('utf-8')

def reset_user_password():
    """Reset the user's password to a properly hashed version"""
    
    # Hash the password "123456"
    hashed_password = hash_password_simple("123456")
    
    print(f"Original password: 123456")
    print(f"Hashed password: {hashed_password}")
    
    # Update the user in the database
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
        
        print(f"Updated {result.rowcount} user(s) with new hashed password")
        print("User 'rado' should now be able to login with password '123456'")

if __name__ == "__main__":
    reset_user_password()