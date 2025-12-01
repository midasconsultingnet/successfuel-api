import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from backend.services.auth_service import AuthentificationService

def test_basic_functionality():
    print("Démarrage des tests de base...")
    
    # Test simple du hachage de mot de passe
    password = 'test_password_123'
    hashed = AuthentificationService.get_password_hash(password)
    print(f'Hachage réussi: {password != hashed}')
    print(f'Vérification correcte: {AuthentificationService.verify_password(password, hashed)}')
    print(f'Vérification incorrecte: {AuthentificationService.verify_password("wrong_password", hashed)}')

    # Test de génération de token JWT
    from backend.services.auth_service import SECRET_KEY, ALGORITHM
    from jose import jwt
    import uuid

    data = {'sub': 'test_user', 'user_id': str(uuid.uuid4())}
    token = AuthentificationService.create_access_token(data)
    print(f'Token généré: {token is not None}')

    # Vérifier qu'on peut décoder le token
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f'Token décodé avec succès: {decoded["sub"] == "test_user"}')
    
    print("Tests de base terminés avec succès !")

if __name__ == "__main__":
    test_basic_functionality()