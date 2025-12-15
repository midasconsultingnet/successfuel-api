from pydantic import field_validator, BaseModel
from typing import Optional
import re
from decimal import Decimal

class BaseValidator:
    """Classe de base pour les validateurs partagés dans l'application"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Valide un format d'email"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError('Format d\'email invalide')
        return email.lower().strip()

    @staticmethod
    def validate_phone(phone: str) -> str:
        """Valide un numéro de téléphone"""
        # Accepte les formats internationaux avec ou sans signe +
        phone_regex = r'^\+?[1-9]\d{1,14}$'
        if not re.match(phone_regex, phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")):
            raise ValueError('Format de numéro de téléphone invalide')
        return phone.strip()

    @staticmethod
    def validate_positive_number(value: float) -> float:
        """Valide qu'un nombre est positif"""
        if value is not None and value <= 0:
            raise ValueError('La valeur doit être un nombre positif')
        return value

    @staticmethod
    def validate_non_empty_string(value: str) -> str:
        """Valide qu'une chaîne n'est pas vide ou ne contient que des espaces"""
        if not value or not value.strip():
            raise ValueError('Ce champ ne peut pas être vide')
        return value.strip()

    @staticmethod
    def validate_percentage(value: float) -> float:
        """Valide qu'un pourcentage est entre 0 et 100"""
        if value is not None and (value < 0 or value > 100):
            raise ValueError('Le pourcentage doit être entre 0 et 100')
        return value

    @staticmethod
    def validate_code_format(value: str) -> str:
        """Valide le format d'un code (alphanumérique avec tirets et underscores autorisés)"""
        if value and not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValueError('Format de code invalide. Seuls les lettres, chiffres, tirets et underscores sont autorisés')
        return value.strip()


class EnhancedValidationMixin:
    """Mixin pour ajouter des validateurs communs aux schémas Pydantic"""
    
    @field_validator('email', mode='before', check_fields=False)
    @classmethod
    def validate_email_format(cls, v):
        if v:
            return BaseValidator.validate_email(v)
        return v

    @field_validator('telephone', 'mobile', mode='before', check_fields=False)
    @classmethod
    def validate_phone_format(cls, v):
        if v:
            return BaseValidator.validate_phone(v)
        return v

    @field_validator('prix', 'montant', 'quantite', mode='before', check_fields=False)
    @classmethod
    def validate_positive_amount(cls, v):
        if v is not None:
            return BaseValidator.validate_positive_number(v)
        return v

    @field_validator('nom', 'prenom', 'description', mode='before', check_fields=False)
    @classmethod
    def validate_non_empty_text(cls, v):
        if v:
            return BaseValidator.validate_non_empty_string(v)
        return v

    @field_validator('code', mode='before', check_fields=False)
    @classmethod
    def validate_code(cls, v):
        if v:
            return BaseValidator.validate_code_format(v)
        return v