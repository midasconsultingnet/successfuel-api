import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import uuid

from app import app
from database.database import Base
from models.structures import Utilisateur, Profil, Permission, Module
from models.securite import TentativeConnexion, EvenementSecurite, ModificationSensible, AuthToken
from services.auth_service import AuthentificationService
from services.rbac_service import RBACService
from services.journalisation_service import JournalisationService

# Configuration pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables pour les tests
Base.metadata.create_all(bind=engine)

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

def test_login_echoue():
    """Test de l'endpoint de connexion avec identifiants incorrects"""
    response = client.post("/api/v1/auth/login", json={
        "login": "nonexistent_user",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401

def test_verification_permission():
    """Test de la vérification des permissions"""
    db = TestingSessionLocal()
    
    try:
        # Créer un utilisateur de test
        utilisateur = Utilisateur(
            id=uuid.uuid4(),
            login="test_user",
            mot_de_passe=AuthentificationService.get_password_hash("password123"),
            nom="Test User",
            profil_id=uuid.uuid4()
        )
        db.add(utilisateur)
        db.commit()
        
        # Test de vérification de permission (devrait échouer car les tables nécessaires ne sont pas remplies)
        has_permission = RBACService.check_permission(db, str(utilisateur.id), "test_permission")
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
    finally:
        db.close()

def test_verification_acces_station():
    """Test de la vérification d'accès aux stations"""
    db = TestingSessionLocal()
    
    try:
        # Créer un utilisateur avec des stations autorisées
        utilisateur = Utilisateur(
            id=uuid.uuid4(),
            login="test_user",
            mot_de_passe=AuthentificationService.get_password_hash("password123"),
            nom="Test User",
            profil_id=uuid.uuid4(),
            stations_user=[str(uuid.uuid4()), str(uuid.uuid4())]  # Deux stations autorisées
        )
        db.add(utilisateur)
        db.commit()
        
        # Vérifier l'accès à une station autorisée
        station_autorisee = utilisateur.stations_user[0]
        acces_autorise = RBACService.check_station_access(db, str(utilisateur.id), station_autorisee)
        assert acces_autorise is True
        
        # Vérifier l'accès à une station non autorisée
        acces_refuse = RBACService.check_station_access(db, str(utilisateur.id), str(uuid.uuid4()))
        assert acces_refuse is False
    finally:
        db.close()