from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta

from models.structures import Utilisateur, Profil, ProfilPermission, Permission, Module, Station
from models.securite import ModificationSensible, EvenementSecurite
from services.auth_service import AuthentificationService


class RBACService:
    @staticmethod
    def check_permission(db: Session, utilisateur_id: str, permission_libelle: str) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique
        """
        # Récupérer le profil de l'utilisateur
        utilisateur = db.query(Utilisateur).filter(Utilisateur.id == utilisateur_id).first()
        if not utilisateur:
            return False

        # Récupérer la permission par son libellé
        permission = db.query(Permission).filter(Permission.libelle == permission_libelle).first()
        if not permission:
            return False

        # Vérifier si le profil de l'utilisateur a cette permission
        profil_permission = db.query(ProfilPermission).filter(
            ProfilPermission.profil_id == utilisateur.profil_id,
            ProfilPermission.permission_id == permission.id
        ).first()

        return profil_permission is not None

    @staticmethod
    def check_permission_by_user_obj(db: Session, utilisateur: Utilisateur, permission_libelle: str) -> bool:
        """
        Vérifie si un utilisateur (objet) a une permission spécifique
        """
        # Récupérer la permission par son libellé
        permission = db.query(Permission).filter(Permission.libelle == permission_libelle).first()
        if not permission:
            return False

        # Vérifier si le profil de l'utilisateur a cette permission
        profil_permission = db.query(ProfilPermission).filter(
            ProfilPermission.profil_id == utilisateur.profil_id,
            ProfilPermission.permission_id == permission.id
        ).first()

        return profil_permission is not None

    @staticmethod
    def get_user_permissions(db: Session, utilisateur_id: str) -> List[Permission]:
        """
        Récupère toutes les permissions d'un utilisateur
        """
        utilisateur = db.query(Utilisateur).filter(Utilisateur.id == utilisateur_id).first()
        if not utilisateur:
            return []

        permissions = (
            db.query(Permission)
            .join(ProfilPermission, Permission.id == ProfilPermission.permission_id)
            .filter(ProfilPermission.profil_id == utilisateur.profil_id)
            .all()
        )

        return permissions

    @staticmethod
    def get_user_stations(db: Session, utilisateur_id: str) -> List[str]:
        """
        Récupère les stations auxquelles un utilisateur a accès
        """
        utilisateur = db.query(Utilisateur).filter(Utilisateur.id == utilisateur_id).first()
        if not utilisateur:
            return []

        # Le champ stations_user est stocké en tant que JSONB
        # et contient une liste d'UUIDs de stations
        return utilisateur.stations_user if utilisateur.stations_user else []

    @staticmethod
    def check_station_access(db: Session, utilisateur_id: str, station_id: str) -> bool:
        """
        Vérifie si un utilisateur a accès à une station spécifique
        """
        utilisateur = db.query(Utilisateur).filter(Utilisateur.id == utilisateur_id).first()
        if not utilisateur:
            return False

        # Vérifier si la station_id est dans la liste des stations de l'utilisateur
        stations_user = utilisateur.stations_user if utilisateur.stations_user else []
        return station_id in stations_user

    @staticmethod
    def create_profile(db: Session, code: str, libelle: str, description: str, permission_ids: List[str]) -> Profil:
        """
        Crée un nouveau profil avec ses permissions
        """
        # Vérifier que le code de profil est unique
        existing_profile = db.query(Profil).filter(Profil.code == code).first()
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Un profil avec le code '{code}' existe déjà"
            )

        # Créer le profil
        nouveau_profil = Profil(
            code=code,
            libelle=libelle,
            description=description,
            statut='Actif'
        )
        db.add(nouveau_profil)
        db.flush()  # Pour obtenir l'ID du nouveau profil

        # Associer les permissions au profil
        for perm_id in permission_ids:
            # Vérifier que la permission existe
            permission = db.query(Permission).filter(Permission.id == perm_id).first()
            if not permission:
                continue  # Ignorer les permissions invalides

            profil_permission = ProfilPermission(
                profil_id=nouveau_profil.id,
                permission_id=perm_id
            )
            db.add(profil_permission)

        db.commit()
        db.refresh(nouveau_profil)

        return nouveau_profil

    @staticmethod
    def update_profile_permissions(db: Session, profil_id: str, permission_ids: List[str]) -> Profil:
        """
        Met à jour les permissions d'un profil existant
        """
        # Supprimer les associations existantes
        db.query(ProfilPermission).filter(ProfilPermission.profil_id == profil_id).delete()

        # Ajouter les nouvelles associations
        for perm_id in permission_ids:
            # Vérifier que la permission existe
            permission = db.query(Permission).filter(Permission.id == perm_id).first()
            if not permission:
                continue  # Ignorer les permissions invalides

            profil_permission = ProfilPermission(
                profil_id=profil_id,
                permission_id=perm_id
            )
            db.add(profil_permission)

        db.commit()

        # Récupérer et retourner le profil mis à jour
        return db.query(Profil).filter(Profil.id == profil_id).first()

    @staticmethod
    def check_access_control(db: Session, utilisateur_id: str, permission_libelle: str, station_id: str = None) -> bool:
        """
        Vérifie globalement si un utilisateur a accès à une action sur une station
        """
        # Vérifier la permission
        has_permission = RBACService.check_permission(db, utilisateur_id, permission_libelle)
        if not has_permission:
            return False

        # Si une station est spécifiée, vérifier l'accès à la station
        if station_id:
            return RBACService.check_station_access(db, utilisateur_id, station_id)

        return True

    @staticmethod
    def log_sensitive_action(
        db: Session,
        utilisateur_id: str,
        type_operation: str,
        objet_modifie: str,
        objet_id: str = None,
        ancienne_valeur: Dict = None,
        nouvelle_valeur: Dict = None,
        seuil_alerte: bool = False,
        commentaire: str = None,
        ip_utilisateur: str = None,
        poste_utilisateur: str = None
    ) -> ModificationSensible:
        """
        Enregistre une action sensible dans le journal
        """
        modification = ModificationSensible(
            utilisateur_id=utilisateur_id,
            type_operation=type_operation,
            objet_modifie=objet_modifie,
            objet_id=objet_id,
            ancienne_valeur=ancienne_valeur,
            nouvelle_valeur=nouvelle_valeur,
            seuil_alerte=seuil_alerte,
            commentaire=commentaire,
            ip_utilisateur=ip_utilisateur,
            poste_utilisateur=poste_utilisateur
        )
        
        db.add(modification)
        db.commit()
        db.refresh(modification)
        
        return modification

    @staticmethod
    def log_security_event(
        db: Session,
        type_evenement: str,
        description: str,
        utilisateur_id: str = None,
        ip_utilisateur: str = None,
        poste_utilisateur: str = None,
        session_id: str = None,
        donnees_supplementaires: Dict = None,
        statut: str = 'NonTraite'
    ) -> EvenementSecurite:
        """
        Enregistre un événement de sécurité
        """
        evenement = EvenementSecurite(
            type_evenement=type_evenement,
            description=description,
            utilisateur_id=utilisateur_id,
            ip_utilisateur=ip_utilisateur,
            poste_utilisateur=poste_utilisateur,
            session_id=session_id,
            donnees_supplementaires=donnees_supplementaires,
            statut=statut
        )
        
        db.add(evenement)
        db.commit()
        db.refresh(evenement)
        
        return evenement