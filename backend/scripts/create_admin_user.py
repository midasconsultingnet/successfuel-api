#!/usr/bin/env python3
"""
Script de création d'un utilisateur administrateur
Ce script permet de créer un utilisateur administrateur sans avoir besoin
d'être authentifié, ce qui est nécessaire pour l'initialisation du système.
"""
import sys
import os
import uuid

# Ajouter le chemin du backend pour pouvoir importer les modules
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Charger les modules après avoir ajouté le chemin
def create_admin_user():
    """Crée un utilisateur administrateur avec les permissions nécessaires"""

    # Charger les modules maintenant que le chemin est correct
    from config.config import settings
    from models.structures import Utilisateur, Profil, Pays, Compagnie
    from services.auth_service import AuthentificationService

    # Créer une session de base de données
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Vérifier ou créer un pays par défaut (par exemple, Madagascar)
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

        # 3. Vérifier ou créer un profil administrateur
        profil_admin = db.query(Profil).filter(Profil.code == 'ADMIN').first()
        if not profil_admin:
            profil_admin = Profil(
                code='ADMIN',
                libelle='Administrateur Système',
                description='Profil avec tous les droits d\'administration système',
                statut='Actif',
                compagnie_id=compagnie.id
            )
            db.add(profil_admin)
            db.commit()
            print("Profil 'Administrateur' créé avec succès")
        else:
            print("Profil 'Administrateur' existe déjà")

        # 4. Vérifier si l'utilisateur admin existe déjà
        admin_user = db.query(Utilisateur).filter(Utilisateur.login == 'admin').first()
        if admin_user:
            print("L'utilisateur admin existe déjà")
            print(f"ID de l'utilisateur: {admin_user.id}")
            print("Mise à jour du mot de passe...")

            # Mettre à jour le mot de passe
            hashed_password = AuthentificationService.get_password_hash('admin123')
            admin_user.mot_de_passe = hashed_password
            db.commit()
            print("Mot de passe mis à jour pour l'utilisateur admin (admin / admin123)")
        else:
            # Créer l'utilisateur administrateur
            hashed_password = AuthentificationService.get_password_hash('admin123')

            nouvel_admin = Utilisateur(
                login='admin',
                mot_de_passe=hashed_password,
                nom='Administrateur Système',
                profil_id=profil_admin.id,
                email='admin@successfuel.mg',
                telephone='+261 34 123 4567',
                statut='Actif',
                compagnie_id=compagnie.id
            )

            db.add(nouvel_admin)
            db.commit()
            db.refresh(nouvel_admin)

            print("Utilisateur administrateur créé avec succès")
            print(f"ID de l'utilisateur: {nouvel_admin.id}")
            print("Identifiants de connexion:")
            print("  Login: admin")
            print("  Mot de passe: admin123")

        print("\nL'utilisateur administrateur est maintenant prêt à être utilisé.")
        print("Vous pouvez vous connecter avec ces identifiants pour créer d'autres entités.")

    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur administrateur: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()