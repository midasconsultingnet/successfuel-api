"""
Fichier de debug pour tester la connexion admin
Ce fichier vous permet de tester la fonction d'authentification indépendamment
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from models.structures import Utilisateur
from sqlalchemy import create_engine
from config.config import settings

def debug_admin_login(login: str, password: str):
    """Fonction de débogage pour tester la connexion admin"""
    print(f"Test de connexion pour l'utilisateur: {login}")
    
    db = SessionLocal()
    try:
        # Test 1: Vérifier si l'utilisateur existe
        user = db.query(Utilisateur).filter(Utilisateur.login == login).first()
        print(f"Utilisateur trouvé: {user is not None}")
        
        if user:
            print(f"ID utilisateur: {user.id}")
            print(f"Type utilisateur: {user.type_utilisateur}")
            print(f"Statut utilisateur: {user.statut}")
            print(f"Champ mot_de_passe existe: {hasattr(user, 'mot_de_passe')}")
        
        # Test 2: Si utilisateur trouvé, tester le mot de passe
        if user:
            from utils.security import verify_password
            password_match = verify_password(password, user.mot_de_passe)
            print(f"Mot de passe correct: {password_match}")
        
        # Test 3: Vérifier si l'utilisateur est admin
        if user and hasattr(user, 'type_utilisateur'):
            is_admin = user.type_utilisateur in ["super_administrateur", "administrateur"]
            print(f"Est administrateur: {is_admin}")
        
    except Exception as e:
        print(f"Erreur lors du test de connexion: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Remplacez 'super' et 'admin123' par vos identifiants
    debug_admin_login("super", "admin123")