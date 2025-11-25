"""
Module utilitaire pour la protection des données sensibles
"""
from typing import Any, Dict, Union
import re


class DonneesSensiblesService:
    """
    Service pour la protection des données sensibles
    """
    
    @staticmethod
    def masquer_donnees_personnelles(data: str) -> str:
        """
        Masque les données personnelles sensibles comme les numéros de téléphone, emails, etc.
        """
        # Masquer les emails: nom@domaine.com -> n**@d*****.com
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        def masquer_email(match):
            email = match.group(0)
            parts = email.split('@')
            if len(parts) == 2:
                local, domain = parts
                masked_local = local[0] + '*' * max(0, len(local) - 2) + local[-1] if len(local) > 2 else local[0] + '*'
                
                domain_parts = domain.split('.')
                if len(domain_parts) >= 2:
                    domain_name, extension = domain_parts[-2], domain_parts[-1]
                    masked_domain = domain_name[0] + '*' * max(0, len(domain_name) - 1)
                    masked_domain = f"{masked_domain}.{extension}"
                    return f"{masked_local}@{masked_domain}"
            return email  # Si le format n'est pas reconnu, retourner l'original

        masked_data = re.sub(email_pattern, masquer_email, str(data))
        
        # Masquer les numéros de téléphone
        # Supporte formats: +261 34 123 4567, 034 123 4567, 34 123 4567
        phone_pattern = r'(\+\d{3}|\d{2,3})\s*\d{2}\s*\d{3}\s*\d{4}'
        
        def masquer_telephone(match):
            phone = match.group(0)
            # Garder les 2 premiers chiffres et masquer le reste
            digits = re.sub(r'\D', '', phone)
            if len(digits) >= 6:
                visible_part = digits[:2]
                hidden_part = '*' * (len(digits) - 4)
                last_part = digits[-2:] if len(digits) >= 2 else ''
                return f"{visible_part}{hidden_part}{last_part}"
            return '******'
        
        masked_data = re.sub(phone_pattern, masquer_telephone, masked_data)
        
        return masked_data
    
    @staticmethod
    def filtrer_donnees_sensibles(
        data: Union[Dict, Any],
        champs_sensibles: list = ['mot_de_passe', 'password', 'token', 'secret', 'key']
    ) -> Union[Dict, Any]:
        """
        Filtre les champs sensibles d'un objet/dictionnaire
        """
        if isinstance(data, dict):
            filtered_data = {}
            for key, value in data.items():
                if key.lower() in [champ.lower() for champ in champs_sensibles]:
                    filtered_data[key] = '***MASQUÉ***'
                elif isinstance(value, (dict, list)):
                    filtered_data[key] = DonneesSensiblesService.filtrer_donnees_sensibles(value, champs_sensibles)
                else:
                    filtered_data[key] = value
            return filtered_data
        elif isinstance(data, list):
            return [DonneesSensiblesService.filtrer_donnees_sensibles(item, champs_sensibles) for item in data]
        else:
            return data
    
    @staticmethod
    def masquer_donnees_utilisateur(utilisateur_data: Dict) -> Dict:
        """
        Masque les données sensibles d'un utilisateur pour l'affichage
        """
        masked_data = utilisateur_data.copy()
        
        # Masquer les champs sensibles
        if 'mot_de_passe' in masked_data:
            masked_data['mot_de_passe'] = '***MASQUÉ***'
        
        if 'email' in masked_data and masked_data['email']:
            masked_data['email'] = DonneesSensiblesService.masquer_donnees_personnelles(masked_data['email'])
        
        if 'telephone' in masked_data and masked_data['telephone']:
            masked_data['telephone'] = DonneesSensiblesService.masquer_donnees_personnelles(masked_data['telephone'])
        
        return masked_data