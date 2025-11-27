import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, get_db
from app import app  # Import the main app
from utils.security import hash_password, verify_password, create_access_token
from models.structures import Utilisateur, Profil, Permission, Module
from datetime import timedelta
import json


# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_security.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create sample data for testing
    db = TestingSessionLocal()
    
    # Create a test module
    test_module = Module(libelle="Test Module", statut="ACTIF")
    db.add(test_module)
    db.commit()
    db.refresh(test_module)
    
    # Create a test permission
    test_permission = Permission(
        libelle="test.permission",
        description="Test permission",
        module_id=test_module.id,
        statut="ACTIF"
    )
    db.add(test_permission)
    db.commit()
    db.refresh(test_permission)
    
    # Create a test profile
    test_profil = Profil(
        code="TEST",
        libelle="Test Profile",
        description="Test profile for security testing"
    )
    db.add(test_profil)
    db.commit()
    db.refresh(test_profil)
    
    # Create a test user
    hashed_password = hash_password("testpassword123")
    test_user = Utilisateur(
        login="testuser",
        mot_de_passe=hashed_password,
        nom="Test User",
        email="test@example.com",
        profil_id=test_profil.id,
        type_utilisateur="utilisateur_compagnie"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Create another test user with admin rights
    admin_user = Utilisateur(
        login="adminuser",
        mot_de_passe=hashed_password,  # Using same hashed password for simplicity
        nom="Admin User",
        email="admin@example.com",
        profil_id=test_profil.id,
        type_utilisateur="administrateur"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    yield db
    
    # Clean up: drop all tables
    Base.metadata.drop_all(bind=engine)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False


def test_create_access_token():
    """Test JWT token creation and verification"""
    data = {"sub": "testuser", "type_utilisateur": "utilisateur_compagnie", "type_endpoint": "utilisateur"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=30))
    assert token is not None
    assert len(token) > 0


def test_user_login_success(setup_database):
    """Test successful user login"""
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]


def test_user_login_failure(setup_database):
    """Test failed user login with wrong credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_admin_login_success(setup_database):
    """Test successful admin login"""
    response = client.post(
        "/api/v1/admin/login",
        json={"login": "adminuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]


def test_admin_login_failure_for_regular_user(setup_database):
    """Test that regular user can't access admin login"""
    response = client.post(
        "/api/v1/admin/login",
        json={"login": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 403  # Forbidden


def test_get_user_profile(setup_database):
    """Test getting user profile after authentication"""
    # First, authenticate to get token
    auth_response = client.post(
        "/api/v1/auth/login",
        json={"login": "testuser", "password": "testpassword123"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["data"]["token"]
    
    # Then access profile endpoint
    response = client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "user" in data["data"]
    assert data["data"]["user"]["login"] == "testuser"


def test_admin_endpoints_access_with_user_token(setup_database):
    """Test that user tokens can't access admin endpoints"""
    # Authenticate regular user to get token
    auth_response = client.post(
        "/api/v1/auth/login",
        json={"login": "testuser", "password": "testpassword123"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["data"]["token"]
    
    # Try to access an admin endpoint
    response = client.get(
        "/api/v1/admin/profils",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should be forbidden due to middleware
    assert response.status_code == 403


def test_user_endpoints_access_with_admin_token(setup_database):
    """Test that admin tokens can't access regular user endpoints"""
    # Authenticate admin user to get token
    auth_response = client.post(
        "/api/v1/admin/login",
        json={"login": "adminuser", "password": "testpassword123"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["data"]["token"]
    
    # Try to access a regular user endpoint
    response = client.get(
        "/api/v1/users/12345",  # This will fail due to ID format but tests the access control
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should be forbidden due to middleware
    assert response.status_code == 403


def test_permissions_endpoint(setup_database):
    """Test permissions endpoint access"""
    # Authenticate admin user to get token
    auth_response = client.post(
        "/api/v1/admin/login",
        json={"login": "adminuser", "password": "testpassword123"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["data"]["token"]
    
    # Access permissions endpoint
    response = client.get(
        "/api/v1/admin/permissions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_securit_logs_access(setup_database):
    """Test security logs endpoint access"""
    # Authenticate admin user to get token
    auth_response = client.post(
        "/api/v1/admin/login",
        json={"login": "adminuser", "password": "testpassword123"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["data"]["token"]
    
    # Access login attempts endpoint
    response = client.get(
        "/api/v1/security/login-attempts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "pagination" in data