import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import uuid

from app import app
from database.database import Base, get_db, engine
from models.structures import Utilisateur, Profil, Permission, Module
from models.securite import TentativeConnexion, EvenementSecurite, ModificationSensible, AuthToken
from services.auth_service import AuthentificationService
from services.rbac_service import RBACService
from services.journalisation_service import JournalisationService
from config.config import settings

# Utiliser la même base de données que celle définie dans les paramètres
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cette fonction permet d'avoir une session de base de données pour les tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Remplacer la dépendance get_db dans l'application par notre version de test
from api.v1 import securite
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

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
    data = {"sub": "test_user", "user_id": str(uuid.uuid4())}
    token = AuthentificationService.create_access_token(data)
    
    # Vérifier que le token a été créé
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

@patch('services.auth_service.AuthentificationService.authenticate_user')
def test_login_endpoint(mock_authenticate):
    """Test de l'endpoint de connexion"""
    # Simuler un utilisateur existant
    mock_user = Mock()
    mock_user.id = uuid.uuid4()
    mock_user.login = "test_user"
    mock_user.profil_id = uuid.uuid4()
    mock_user.statut = "Actif"
    mock_user.stations_user = [str(uuid.uuid4())]
    mock_authenticate.return_value = mock_user
    
    response = client.post("/api/v1/auth/login", json={
        "login": "test_user",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "access_token" in data["data"]

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