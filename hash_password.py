import sys
import os
# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

# Add the api directory to the path
sys.path.insert(0, os.path.abspath('api'))

from api.auth.auth_handler import get_password_hash

if __name__ == "__main__":
    password = "123456"
    try:
        hashed_password = get_password_hash(password)
        print(f"Original password: {password}")
        print(f"Hashed password: {hashed_password}")
    except Exception as e:
        print(f"Error hashing password: {str(e)}")