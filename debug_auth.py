#!/usr/bin/env python3
"""
Script de débogage pour tester l'authentification
"""
import sys
import os

# Ajouter le chemin du backend pour pouvoir importer les modules
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

def test_auth_debug():
    """Test de débogage pour authentification"""
    from services.auth_service import AuthentificationService
    
    # Test de hachage et vérification
    password = 'admin123'
    print(f"Mot de passe original : {password}")
    
    # Hacher le mot de passe
    hashed = AuthentificationService.get_password_hash(password)
    print(f"Mot de passe haché : {hashed}")
    
    # Vérifier le mot de passe
    is_valid = AuthentificationService.verify_password(password, hashed)
    print(f"Vérification correcte : {is_valid}")
    
    # Vérifier avec un mot de passe incorrect
    is_invalid = AuthentificationService.verify_password('wrong_password', hashed)
    print(f"Vérification incorrecte : {is_invalid}")
    
    # Vérifier un hachage vide ou mal formé
    is_invalid_format = AuthentificationService.verify_password(password, '')
    print(f"Vérification avec hachage vide : {is_invalid_format}")
    
    is_invalid_format2 = AuthentificationService.verify_password(password, 'not_a_hash')
    print(f"Vérification avec hachage incorrect : {is_invalid_format2}")

if __name__ == "__main__":
    test_auth_debug()