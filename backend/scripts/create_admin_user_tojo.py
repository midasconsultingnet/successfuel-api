#!/usr/bin/env python3
"""
Script de création d'un utilisateur administrateur spécifique 'tojo'
Ce script permet de créer un utilisateur administrateur avec les identifiants demandés
(login: tojo, mot de passe: admin123) avec tous les privilèges nécessaires.
"""
import sys
import os
import uuid

# Ajouter le chemin du backend pour pouvoir importer les modules
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def create_admin_user_tojo():
    """Crée un utilisateur administrateur 'tojo' avec tous les privilèges"""
    
    # Charger les modules après avoir ajouté le chemin
    from config.config import settings
    from models.structures import Utilisateur, Profil, ProfilPermission, Permission, Module, Pays, Compagnie
    from services.auth_service import AuthentificationService
    from services.rbac_service import RBACService

    # Créer une session de base de données
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Vérifier ou créer un pays par défaut (Madagascar)
        pays = db.query(Pays).filter(Pays.code_pays == 'MDG').first()
        if not pays:
            pays = Pays(
                code_pays='MDG',
                nom_pays='Madagascar',
                devise_principale='MGA',
                taux_tva_par_defaut=20.0,
                systeme_comptable='OHADA',
                statut='Actif'
            )
            db.add(pays)
            db.commit()
            print("Pays 'Madagascar' créé avec succès")
        else:
            print("Pays 'Madagascar' existe déjà")

        # 2. Vérifier ou créer une compagnie par défaut
        compagnie = db.query(Compagnie).filter(Compagnie.code == 'ADMIN').first()
        if not compagnie:
            compagnie = Compagnie(
                code='ADMIN',
                nom='Administrateur',
                adresse='Quartier Administratif',
                telephone='+261 34 123 4567',
                email='admin@successfuel.mg',
                nif='123456789',
                statut='Actif',
                pays_id=pays.id
            )
            db.add(compagnie)
            db.commit()
            print("Compagnie 'Administrateur' créée avec succès")
        else:
            print("Compagnie 'Administrateur' existe déjà")

        # 3. Vérifier ou créer un profil administrateur système avec tous les privilèges
        profil_admin = db.query(Profil).filter(Profil.code == 'ADMIN_TOJO').first()
        if not profil_admin:
            profil_admin = Profil(
                code='ADMIN_TOJO',
                libelle='Administrateur Système Tojo',
                description='Profil avec tous les droits d\'administration système pour Tojo',
                statut='Actif',
                compagnie_id=compagnie.id
            )
            db.add(profil_admin)
            db.commit()
            print("Profil 'Administrateur Tojo' créé avec succès")
        else:
            print("Profil 'Administrateur Tojo' existe déjà")

        # 4. Récupérer ou créer toutes les permissions existantes
        all_permissions = db.query(Permission).all()
        
        # Si aucune permission n'existe, créer un ensemble de permissions de base
        if not all_permissions:
            # Créer les modules de base
            modules_libelles = [
                'Utilisateurs', 'Profils', 'Permissions', 'Modules', 'Compagnies', 'Stations', 
                'Pays', 'Articles', 'Carburants', 'Cuvettes', 'Pompes', 'Pistolets', 
                'Clients', 'Fournisseurs', 'Employés', 'Trésoreries', 'Ventes', 'Achats', 
                'Stocks', 'Comptabilité', 'Rapports', 'Sécurité'
            ]
            
            for libelle_module in modules_libelles:
                module_existant = db.query(Module).filter(Module.libelle == libelle_module).first()
                if not module_existant:
                    module = Module(libelle=libelle_module, statut='Actif')
                    db.add(module)
                    db.commit()
                    print(f"Module '{libelle_module}' créé")
            
            # Créer un ensemble de permissions de base pour chaque module
            permissions_libelles = [
                # Utilisateurs
                'lire_utilisateurs', 'creer_utilisateurs', 'modifier_utilisateurs', 'supprimer_utilisateurs',
                # Profils
                'lire_profils', 'creer_profils', 'modifier_profils', 'supprimer_profils',
                # Permissions
                'lire_permissions', 'creer_permissions', 'modifier_permissions', 'supprimer_permissions',
                # Modules
                'lire_modules', 'creer_modules', 'modifier_modules', 'supprimer_modules',
                # Compagnies
                'lire_compagnies', 'creer_compagnies', 'modifier_compagnies', 'supprimer_compagnies',
                # Stations
                'lire_stations', 'creer_stations', 'modifier_stations', 'supprimer_stations',
                # Pays
                'lire_pays', 'creer_pays', 'modifier_pays', 'supprimer_pays',
                # Articles
                'lire_articles', 'creer_articles', 'modifier_articles', 'supprimer_articles',
                # Carburants
                'lire_carburants', 'creer_carburants', 'modifier_carburants', 'supprimer_carburants',
                # Cuvettes
                'lire_cuves', 'creer_cuves', 'modifier_cuves', 'supprimer_cuves',
                # Pompes
                'lire_pompes', 'creer_pompes', 'modifier_pompes', 'supprimer_pompes',
                # Pistolets
                'lire_pistolets', 'creer_pistolets', 'modifier_pistolets', 'supprimer_pistolets',
                # Clients
                'lire_clients', 'creer_clients', 'modifier_clients', 'supprimer_clients',
                # Fournisseurs
                'lire_fournisseurs', 'creer_fournisseurs', 'modifier_fournisseurs', 'supprimer_fournisseurs',
                # Employés
                'lire_employes', 'creer_employes', 'modifier_employes', 'supprimer_employes',
                # Trésoreries
                'lire_tresoreries', 'creer_tresoreries', 'modifier_tresoreries', 'supprimer_tresoreries',
                # Ventes
                'lire_ventes', 'creer_ventes', 'modifier_ventes', 'supprimer_ventes',
                # Achats
                'lire_achats', 'creer_achats', 'modifier_achats', 'supprimer_achats',
                # Stocks
                'lire_stocks', 'creer_stocks', 'modifier_stocks', 'supprimer_stocks',
                # Comptabilité
                'lire_comptabilite', 'creer_comptabilite', 'modifier_comptabilite', 'supprimer_comptabilite',
                # Rapports
                'lire_rapports', 'generer_rapports',
                # Sécurité
                'consulter_logs', 'gerer_securite'
            ]
            
            for libelle_permission in permissions_libelles:
                # Extraire le module à partir du libellé de la permission
                module_libelle = libelle_permission.split('_')[1].title() if '_' in libelle_permission else 'Sécurité'
                
                # Trouver le module correspondant
                module = db.query(Module).filter(Module.libelle == module_libelle).first()
                if not module:
                    # Si le module n'existe pas, en créer un par défaut
                    module = Module(libelle=module_libelle, statut='Actif')
                    db.add(module)
                    db.commit()
                
                # Créer la permission
                permission = Permission(
                    libelle=libelle_permission,
                    description=f'Autorisation pour {libelle_permission}',
                    module_id=module.id,
                    statut='Actif'
                )
                db.add(permission)
            
            db.commit()
            print("Permissions de base créées")
            
            # Récupérer à nouveau toutes les permissions après les avoir créées
            all_permissions = db.query(Permission).all()
        
        # 5. Associer toutes les permissions au profil administrateur
        # Supprimer les associations existantes pour ce profil
        db.query(ProfilPermission).filter(ProfilPermission.profil_id == profil_admin.id).delete()
        
        # Associer toutes les permissions au profil administrateur
        for permission in all_permissions:
            profil_permission = ProfilPermission(
                profil_id=profil_admin.id,
                permission_id=permission.id
            )
            db.add(profil_permission)
        
        db.commit()
        print(f"Toutes les permissions ({len(all_permissions)} permissions) ont été associées au profil administrateur")

        # 6. Vérifier si l'utilisateur 'tojo' existe déjà
        admin_user = db.query(Utilisateur).filter(Utilisateur.login == 'tojo').first()
        if admin_user:
            print("L'utilisateur 'tojo' existe déjà")
            print(f"ID de l'utilisateur: {admin_user.id}")
            print("Mise à jour du mot de passe...")
            
            # Mettre à jour le mot de passe
            hashed_password = AuthentificationService.get_password_hash('admin123')
            admin_user.mot_de_passe = hashed_password
            db.commit()
            print("Mot de passe mis à jour pour l'utilisateur 'tojo' (tojo / admin123)")
        else:
            # Créer l'utilisateur administrateur 'tojo'
            hashed_password = AuthentificationService.get_password_hash('admin123')

            nouvel_admin = Utilisateur(
                login='tojo',
                mot_de_passe=hashed_password,
                nom='Administrateur Tojo',
                profil_id=profil_admin.id,
                email='tojo@successfuel.mg',
                telephone='+261 34 123 4567',
                statut='Actif',
                compagnie_id=compagnie.id
            )

            db.add(nouvel_admin)
            db.commit()
            db.refresh(nouvel_admin)

            print("Utilisateur administrateur 'tojo' créé avec succès")
            print(f"ID de l'utilisateur: {nouvel_admin.id}")
            print("Identifiants de connexion:")
            print("  Login: tojo")
            print("  Mot de passe: admin123")

        print("\nL'utilisateur administrateur 'tojo' est maintenant prêt à être utilisé.")
        print("Vous pouvez vous connecter avec ces identifiants pour accéder à toutes les fonctionnalités du système.")

    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur administrateur 'tojo': {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user_tojo()