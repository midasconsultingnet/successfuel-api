import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import uuid

from models.structures import Utilisateur, Profil, Permission, Module
from models.securite import TentativeConnexion, EvenementSecurite, ModificationSensible, AuthToken
from services.auth_service import AuthentificationService
from services.rbac_service import RBACService
from services.journalisation_service import JournalisationService
from database.database import engine, Base

# Utiliser la même base de données que celle définie dans les paramètres
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_hachage_mots_de_passe():
    """Test du hachage et vérification des mots de passe avec bcrypt"""
    password = "test_password_123"
    hashed = AuthentificationService.get_password_hash(password)
    
    # Vérifier que le mot de passe haché n'est pas égal au mot de passe original
    assert password != hashed
    
    # Vérifier que la vérification du mot de passe fonctionne
    assert AuthentificationService.verify_password(password, hashed) == True
    assert AuthentificationService.verify_password("wrong_password", hashed) == False

def test_generation_token_jwt():
    """Test de la génération et validation des tokens JWT"""
    from datetime import timedelta
    from services.auth_service import SECRET_KEY, ALGORITHM
    import jwt
    
    data = {"sub": "test_user", "user_id": str(uuid.uuid4())}
    token = AuthentificationService.create_access_token(data)
    
    # Vérifier que le token a été créé
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Vérifier qu'on peut décoder le token
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "test_user"

def test_verification_permission():
    """Test de la vérification des permissions"""
    db = TestingSessionLocal()
    
    try:
        # Tester la vérification des permissions sans créer d'utilisateur
        # Puisque nous utilisons la base de données réelle
        has_permission = RBACService.check_permission(db, str(uuid.uuid4()), "test_permission")
        # Cela devrait retourner False car l'utilisateur n'existe pas
        assert has_permission is False
    finally:
        db.close()

def test_journalisation_evenement_securite():
    """Test de la journalisation des événements de sécurité"""
    db = TestingSessionLocal()
    
    try:
        # Journaliser un événement de test
        evenement = JournalisationService.log_security_event(
            db,
            type_evenement="test_event",
            description="Test de journalisation",
            utilisateur_id=str(uuid.uuid4())
        )
        
        assert evenement is not None
        assert evenement.type_evenement == "test_event"
        assert evenement.description == "Test de journalisation"
        
        # Nettoyer l'enregistrement de test
        db.delete(evenement)
        db.commit()
    finally:
        db.close()

def test_journalisation_modification_sensible():
    """Test de la journalisation des modifications sensibles"""
    db = TestingSessionLocal()
    
    try:
        # Journaliser une modification de test
        modification = JournalisationService.log_sensitive_modification(
            db,
            utilisateur_id=str(uuid.uuid4()),
            type_operation="test_operation",
            objet_modifie="test_object",
            objet_id=str(uuid.uuid4())
        )
        
        assert modification is not None
        assert modification.type_operation == "test_operation"
        assert modification.objet_modifie == "test_object"
        
        # Nettoyer l'enregistrement de test
        db.delete(modification)
        db.commit()
    finally:
        db.close()

def test_verification_acces_station():
    """Test de la vérification d'accès aux stations"""
    db = TestingSessionLocal()
    
    try:
        # Tester l'accès à une station avec un utilisateur inexistant
        acces_autorise = RBACService.check_station_access(db, str(uuid.uuid4()), str(uuid.uuid4()))
        # Cela devrait retourner False car l'utilisateur n'existe pas
        assert acces_autorise is False
    finally:
        db.close()