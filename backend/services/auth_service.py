from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer

from models.structures import Utilisateur, Profil, ProfilPermission, Permission, Station
from models.securite import AuthToken, TentativeConnexion, EvenementSecurite, ModificationSensible
from config.config import settings
from database.database import get_db

# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration pour l'authentification JWT
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Configuration pour la sécurité HTTP
security = HTTPBearer()

class AuthentificationService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe non haché correspond au mot de passe haché"""
        # Vérifier que le hachage bcrypt a un format valide
        if hashed_password and hashed_password.startswith('$2b$'):
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except ValueError:
                # Gérer les hachages malformés
                # Si le hachage est malformé, on retourne False pour indiquer une authentification échouée
                return False
        # Vérifier si c'est un hachage au format PBKDF2 (généré par notre endpoint temporaire)
        elif ':' in hashed_password:
            # Le format est hash:salt
            try:
                stored_hash, salt = hashed_password.split(':', 1)
                # Recalculer le hachage avec le mot de passe fourni
                import hashlib
                computed_hash = hashlib.pbkdf2_hmac('sha256',
                                                   plain_password.encode('utf-8'),
                                                   salt.encode('utf-8'),
                                                   100000)
                # Comparer les hachages
                return computed_hash.hex() == stored_hash
            except Exception:
                return False
        else:
            # Ni bcrypt ni PBKDF2 - format inconnu
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hache un mot de passe en utilisant bcrypt"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Assurer que le mot de passe est correctement encodé et dans les limites
            encoded_password = password.encode('utf-8')
            if len(encoded_password) > 72:
                # Tronquer le mot de passe à 72 octets, tout en préservant les caractères UTF-8
                truncated = encoded_password[:72]
                # Décoder et encoder à nouveau pour éviter les coupures de caractères multibytes
                password = truncated.decode('utf-8', errors='ignore')

            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Erreur lors du hachage du mot de passe: {str(e)}")
            raise e

    @staticmethod
    def authenticate_user(db: Session, login: str, password: str) -> Optional[Utilisateur]:
        """Authentifie un utilisateur avec son login et mot de passe"""
        import logging
        logger = logging.getLogger(__name__)

        # Récupérer l'utilisateur par login
        utilisateur = db.query(Utilisateur).filter(Utilisateur.login == login).first()

        # Vérifier si l'utilisateur existe
        if not utilisateur:
            logger.info(f"L'utilisateur avec login '{login}' n'existe pas dans la base de données")
            return None

        # Vérifier si le statut de l'utilisateur est actif
        if utilisateur.statut != "Actif":
            logger.info(f"L'utilisateur avec login '{login}' a un statut non actif : {utilisateur.statut}")
            return None

        # Vérifier si le mot de passe est correct
        password_check = AuthentificationService.verify_password(password, utilisateur.mot_de_passe)
        if not password_check:
            logger.info(f"Le mot de passe est incorrect pour l'utilisateur '{login}'")
            return None

        return utilisateur

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crée un jeton d'accès JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


    @staticmethod
    def login_user(db: Session, login: str, password: str, ip_connexion: str = None) -> Optional[Dict[str, Any]]:
        """Authentifie l'utilisateur et crée un jeton d'accès"""
        # Vérifier les tentatives de connexion récentes pour limiter les attaques par force brute
        tentative_recente = db.query(TentativeConnexion).filter(
            TentativeConnexion.login == login,
            TentativeConnexion.created_at > datetime.utcnow() - timedelta(minutes=15),
            TentativeConnexion.resultat_connexion == 'Echouee'
        ).count()
        
        # Si trop de tentatives échouées récemment, bloquer temporairement
        if tentative_recente >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Trop de tentatives de connexion échouées. Veuillez réessayer plus tard."
            )
        
        utilisateur = AuthentificationService.authenticate_user(db, login, password)
        
        # Enregistrer la tentative de connexion
        tentative = TentativeConnexion(
            login=login,
            ip_connexion=ip_connexion,
            resultat_connexion='Reussie' if utilisateur else 'Echouee',
            utilisateur_id=utilisateur.id if utilisateur else None
        )
        db.add(tentative)
        db.commit()
        
        if not utilisateur:
            return None
        
        # Créer le jeton d'accès
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthentificationService.create_access_token(
            data={"sub": utilisateur.login, "user_id": str(utilisateur.id)},
            expires_delta=access_token_expires
        )
        
        # Créer une entrée dans auth_tokens pour le suivi
        auth_token = AuthToken(
            token_hash=access_token,
            user_id=utilisateur.id,
            expires_at=datetime.utcnow() + access_token_expires
        )
        db.add(auth_token)
        db.commit()
        
        # Mettre à jour le dernier login
        utilisateur.last_login = datetime.utcnow()
        db.commit()
        
        # Récupérer les stations auxquelles l'utilisateur a accès
        stations = utilisateur.stations_user if utilisateur.stations_user else []
        
        # Récupérer le profil de l'utilisateur
        profil = db.query(Profil).filter(Profil.id == utilisateur.profil_id).first()
        
        return {
            "user_id": str(utilisateur.id),
            "login": utilisateur.login,
            "profile_id": str(utilisateur.profil_id),
            "profile_name": profil.libelle if profil else None,
            "access_token": access_token,
            "expires_at": datetime.utcnow() + access_token_expires,
            "stations": stations
        }

    @staticmethod
    def logout_user(db: Session, token: str) -> bool:
        """Déconnecte l'utilisateur en invalidant le jeton"""
        # Trouver le jeton dans la base de données
        auth_token = db.query(AuthToken).filter(
            AuthToken.token_hash == token,
            AuthToken.is_active == True
        ).first()
        
        if not auth_token:
            return False
        
        # Invalider le jeton
        auth_token.is_active = False
        db.commit()
        
        return True

    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Rafraîchit un jeton d'accès à partir d'un jeton de rafraîchissement"""
        # Pour l'instant, nous n'implémentons pas les jetons de rafraîchissement
        # Cette méthode est à implémenter dans une version future
        raise NotImplementedError("Fonctionnalité de rafraîchissement de token non implémentée")