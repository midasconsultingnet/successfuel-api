# Succès Fuel - Projet de Gestion des Utilisateurs

## Description du projet

Ce projet est une application de gestion des utilisateurs pour l'entreprise Succès Fuel. Il permet de gérer différents types d'utilisateurs : administrateurs, gérants compagnie et utilisateurs compagnie, chacun ayant des droits et accès spécifiques.

## Technologies utilisées

- **Backend** : Python, FastAPI
- **Base de données** : PostgreSQL (avec psycopg2-binary)
- **Authentification** : PyJWT (v2.8.0), bcrypt
- **Déploiement** : Gunicorn (v22.0.0)
- **Sécurité** : Flask-CORS (v4.0.2)
- **Formatage** : autopep8
- **API** : RESTful

## Architecture du projet

### Modèle architectural : Architecture Hexagonale (Ports and Adapters)

L'application suit l'architecture hexagonale qui se compose de 3 couches principales :

1. **Core (Noyau métier)** : Contient la logique métier pure sans dépendances externes
2. **Ports (Interfaces)** : Définit les interfaces d'entrée et de sortie pour interagir avec le noyau
3. **Adapters (Adaptateurs)** : Implémente les ports pour interagir avec des frameworks, bases de données, etc.

### Structure des modules

Chaque module de l'application suit la structure suivante :

```
module/
├── router.py          # Gestion des routes HTTP
├── schemas.py         # Modèles de validation Pydantic
├── __init__.py        # Export des éléments du module
└── services/          # Logique métier
    ├── __init__.py    # Export des services
    └── module_service.py  # Services du module
```

### Modèle de données

- Les modèles SQLAlchemy sont dans le répertoire `api/models/`
- Chaque entité a son propre fichier de modèle
- Les relations sont gérées via des associations SQLAlchemy

### Services (Couche métier)

- Tous les services sont dans `api/services/`
- Organisés par module fonctionnel
- Contiennent toute la logique métier
- Recevant la session de base de données et l'utilisateur courant
- Les services sont importés dans les routeurs

### Contrôles d'accès (RBAC)

- Le système RBAC (Role-Based Access Control) est implémenté via des décorateurs
- Les permissions sont définies au niveau des modules
- Les gérants de compagnie ont un accès automatique à tous les modules
- Les autres utilisateurs doivent avoir des permissions explicites

### Gestion des erreurs

- Gestion centralisée via des gestionnaires d'exceptions
- Utilisation de codes HTTP appropriés
- Messages d'erreurs localisés

### Authentification et sécurité

- JWT pour la gestion des sessions
- Hachage des mots de passe avec bcrypt
- Gestion des rôles utilisateurs
- Contrôles RBAC sur les endpoints
- Utilisation uniforme de get_current_user_security pour la validation des droits
- Limitation de débit (rate limiting) pour les endpoints critiques
- Validation poussée des données entrantes via des validateurs Pydantic

## Règles de codage

### Modèles

1. **Structure** : Chaque modèle est dans son propre fichier dans `api/models/`
2. **Héritage** : Tous les modèles héritent de la classe de base `BaseModel` du module `.models.base_model` pour bénéficier des fonctionnalités standardisées
3. **Nom des tables** : Utiliser des noms explicites et en minuscules avec underscore
4. **Types de données** : Utiliser des types SQLAlchemy spécifiques
5. **UUID** : Utiliser `UUID(as_uuid=True)` pour les identifiants uniques
6. **Dates de gestion** : Utiliser les champs `date_creation` et `date_modification` fournis par `BaseModel` pour la gestion des dates
7. **Soft delete** : Utiliser le champ `est_actif` fourni par `BaseModel` pour le soft delete
8. **Relations** : Définir les relations avec des attributs explicites

```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base_model import BaseModel
import uuid

class ExempleModel(BaseModel):
    __tablename__ = "exemple_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)

    # relations
    relation = relationship("AutreModel", back_populates="reverse_relation")
```

### Services

1. **Emplacement** : Chaque service est dans `api/services/{module}/`
2. **Nom des fichiers** : `{module}_service.py`
3. **Gestion des transactions** : Pour les opérations critiques, utiliser le module `transaction_manager` et la classe `TransactionManager` pour gérer les transactions explicitement
4. **Modèle de service de base** : Pour les opérations CRUD courantes, hériter du service `DatabaseService` qui fournit des méthodes avec gestion des transactions

Exemple d'utilisation des transactions :
```python
from ..database.transaction_manager import transaction
from ..services.database_service import DatabaseService

# Dans une fonction ou une méthode de service
def operation_critique(db: Session):
    with transaction(db) as session:
        # Effectuer des opérations dans la transaction
        entity = Model(**data)
        session.add(entity)
        # La transaction est automatiquement validée si tout se passe bien
        # ou annulée en cas d'erreur
```

### Gestion des erreurs de base de données

1. **Exception personnalisée** : Utiliser `DatabaseIntegrityException` pour les erreurs d'intégrité de base de données
2. **Gestion des erreurs SQLAlchemy** : Gérer les erreurs SQLAlchemy avec le gestionnaire approprié
3. **Transactions et erreurs** : En cas d'erreur dans une transaction, le système effectue automatiquement un rollback
4. **Journalisation** : Toutes les erreurs de base de données sont journalisées avec le logger approprié

### Routes

1. **Structure** : Chaque fonction reçoit `db: Session` et `current_user` en premier
2. **Validation** : Toutes les validations métier sont effectuées dans les services
3. **Gestion des erreurs** : Les services lèvent des exceptions HTTP si nécessaire
4. **Réutilisabilité** : Les fonctions de service sont conçues pour être réutilisables

### Routeurs

1. **Importation des services** : Importer les services nécessaires avec alias explicites
2. **Utilisation des décorateurs** : Toujours utiliser `require_permission` pour les endpoints protégés
3. **Dépendances** : Utiliser `get_current_user_security` pour l'authentification
4. **Réponses typées** : Tous les endpoints doivent avoir des types de réponse spécifiés
5. **Pagination** : Pour les listes, utiliser une pagination cohérente (skip, limit)
6. **Gestion des UUID** : Utiliser `uuid.UUID` comme type pour les paramètres d'URL UUID

### Schémas Pydantic

1. **Validation** : Définir des schémas pour la validation des entrées et sorties
2. **Modèles spécifiques** : Créer des modèles spécifiques pour la création, mise à jour et réponse
3. **Config** : Utiliser `from_attributes = True` pour la conversion SQLAlchemy vers Pydantic

### Gestion des erreurs

1. **Gestion centralisée** : Utiliser les gestionnaires d'exceptions dans `api/exception_handlers.py`
2. **Codes HTTP appropriés** : Utiliser les codes HTTP corrects selon le contexte
3. **Messages d'erreurs clairs** : Fournir des messages d'erreurs explicites et localisés

### Noms de variables

1. **Pas d'accents dans les noms de variables** : Ne pas utiliser d'accents dans les noms de variables pour éviter les problèmes de compatibilité et de codage.
2. **Utilisation de caractères ASCII uniquement** : Préférer les caractères ASCII pour les noms de variables pour assurer une compatibilité maximale.

### Noms de colonnes dans la base de données

1. **Pas d'accents dans les noms de colonnes** : Ne pas utiliser d'accents dans les noms de colonnes de la base de données pour assurer la cohérence entre le code et la base de données.
2. **Cohérence entre le code et la base de données** : Les noms de colonnes dans les modèles SQLAlchemy doivent correspondre exactement aux noms de colonnes dans la base de données.

### Sécurité

1. **Contrôles RBAC** : Tous les endpoints sensibles doivent avoir des contrôles RBAC
2. **Validation de l'utilisateur** : Vérifier que l'utilisateur a le droit d'accéder aux ressources
3. **Hachage des mots de passe** : Utiliser bcrypt pour le hachage des mots de passe
4. **JWT** : Utiliser des jetons JWT sécurisés avec une clé secrète correctement gérée
5. **Authentification uniforme** : Utiliser get_current_user_security uniformément dans tous les modules
6. **Validation poussée** : Appliquer des validateurs Pydantic personnalisés pour les données critiques
7. **Rate limiting** : Implémenter des limitations de débit pour les endpoints sensibles (connexion, création de ressources)
   - En environnement de développement (ENVIRONMENT=development), le rate limiting est désactivé ou très permissif
   - En production, les limitations sont appliquées selon les seuils définis

### Internationalisation

1. **Traductions** : Utiliser le système de traduction pour les messages d'erreurs et les réponses
2. **Langues supportées** : Français et anglais (en) sont les langues supportées
3. **Localisation** : Les messages sont localisés selon l'en-tête `Accept-Language`

### Performance

1. **Optimisation des requêtes** : Éviter les problèmes N+1 en utilisant des jointures appropriées
2. **Pagination** : Tous les endpoints de liste doivent être paginés
3. **Indexation** : Les champs fréquemment recherchés doivent être indexés

## Structure technique du projet

### Architecture générale

L'application est structurée selon une architecture hexagonale avec :
- Une couche d'API (routeurs FastAPI)
- Une couche de services (logique métier)
- Une couche de modèles (ORM SQLAlchemy)
- Une couche d'infrastructure (base de données, authentification)

### Dépendances

- FastAPI : Framework web asynchrone
- SQLAlchemy : ORM pour la base de données
- Pydantic : Validation des données
- bcrypt : Hachage des mots de passe
- PyJWT : Gestion des tokens JWT
- psycopg2-binary : Pilote PostgreSQL

### Fichiers principaux

- `main.py` : Point d'entrée principal de l'application
- `database.py` : Configuration de la base de données
- `auth_handler.py` : Gestion de l'authentification
- `rbac_decorators.py` : Décorateurs RBAC
- `exception_handlers.py` : Gestion des exceptions

## Structure du projet

Le projet utilise une architecture basée sur FastAPI avec une séparation claire des responsabilités :
- `api/` : Contient la couche API et la logique métier
- `api/models/` : Modèles SQLAlchemy pour la base de données
- `api/database.py` : Configuration de la base de données et session
- `api/services/` : Services contenant la logique métier
- `api/auth/` : Gestion de l'authentification et autorisation
- `api/rbac_*.py` : Système RBAC (Role-Based Access Control)
- `api/translations/` : Système de traduction et internationalisation
- `requirements.txt` : Dépendances du projet
- `run_server.py` : Script de démarrage du serveur
- `api/base.py` : Définition de la classe Base pour les modèles SQLAlchemy
- `api/main.py` : Point d'entrée de l'application FastAPI

### Modèles de base de données

Les modèles de base de données sont organisés dans le répertoire `api/models/` et suivent la structure suivante :

- `user.py` : Modèle pour les utilisateurs du système
- `station.py` : Modèle pour les stations-service
- `compagnie.py` : Modèle pour les compagnies
- `produit.py` : Modèle pour les produits
- `stock.py` : Modèle pour la gestion des stocks
- `achat*.py` : Modèles pour les achats
- `vente*.py` : Modèles pour les ventes
- `tresorerie*.py` : Modèles pour la gestion trésorière
- `carburant*.py` : Modèles pour la gestion du carburant
- `prix_carburant.py` : Modèle pour les prix du carburant
- `cuve.py` : Modèle pour les cuves de carburant
- `pistolet.py` : Modèle pour les pistolets de distribution
- `mouvement*.py` : Modèles pour les mouvements de stock et trésorerie
- `tiers.py` : Modèle pour les tiers (clients, fournisseurs, employés)
- `methode_paiement.py` : Modèle pour les méthodes de paiement
- `charge.py` : Modèle pour les charges
- `salaire.py` : Modèle pour les salaires
- `immobilisation.py` : Modèle pour les immobilisations
- `inventaire.py` : Modèle pour les inventaires
- `livraison.py` : Modèle pour les livraisons
- `bilan.py` : Modèle pour les bilans financiers
- `mouvement_financier.py` : Modèle pour les mouvements financiers
- `token_session.py` : Modèle pour les tokens de session
- `journal_action_utilisateur.py` : Modèle pour les actions des utilisateurs
- `affectation_utilisateur_station.py` : Modèle pour l'affectation des utilisateurs aux stations
- `rbac_models.py` : Modèles pour le système RBAC

### Modules fonctionnels

Les modules fonctionnels de l'application sont organisés dans le répertoire `api/` et incluent :

- `achats/` : Gestion des achats
- `achats_carburant/` : Gestion des achats de carburant
- `ventes/` : Gestion des ventes
- `stocks/` : Gestion des stocks
- `tresoreries/` : Gestion trésorière
- `carburant/` : Gestion du carburant
- `tiers/` : Gestion des tiers (clients, fournisseurs, employés)
- `compagnie/` : Gestion des compagnies
- `config/` : Configuration de l'application
- `bilans/` : Gestion des bilans
- `charges/` : Gestion des charges
- `salaires/` : Gestion des salaires
- `immobilisations/` : Gestion des immobilisations
- `inventaires/` : Gestion des inventaires
- `livraisons/` : Gestion des livraisons
- `methode_paiement/` : Gestion des méthodes de paiement
- `mouvements_financiers/` : Gestion des mouvements financiers
- `produits/` : Gestion des produits
- `health/` : Points de terminaison de santé de l'application

- Tous les modèles étendent la classe `Base` définie dans `api/base.py`
- La classe `Base` utilise `as_declarative()` de SQLAlchemy
- Les identifiants uniques sont généralement de type UUID
- Les relations entre tables sont gérées via les clés étrangères

### Services

Chaque module fonctionnel a ses services correspondants dans le répertoire `api/services/` :

- `achats/` : Services pour la gestion des achats
- `tresoreries/` : Services pour la gestion trésorière
- `ventes/` : Services pour la gestion des ventes
- `stock_service.py` : Service pour la gestion des stocks
- `pagination_service.py` : Service pour la pagination
- Autres modules de service selon les besoins fonctionnels

Les services respectent les principes suivants :
- Chaque service est organisé dans un sous-répertoire correspondant au module
- Les services contiennent uniquement la logique métier
- Les services reçoivent la session de base de données et l'utilisateur comme paramètres
- Les services retournent des objets Pydantic ou des modèles SQLAlchemy
- Les services gèrent les validations métier et les erreurs

### Authentification et Autorisation

Le système d'authentification et d'autorisation repose sur :

- JWT (JSON Web Tokens) pour la gestion des sessions
- RBAC (Role-Based Access Control) pour la gestion des permissions
- Hachage des mots de passe avec bcrypt
- Gestion des rôles : gérant_compagnie, utilisateur_compagnie
- Système de profils et de permissions associées

### Déploiement et Environnements

- Utilisation de Gunicorn pour le déploiement en production
- Configuration via variables d'environnement
- Gestion des variables sensibles via `.env`
- Support de la localisation et de l'internationalisation
- Journalisation des actions des utilisateurs
- Variable `ENVIRONMENT` pour distinguer développement/production/test
  - `ENVIRONMENT=development` : Désactive ou rend permissif le rate limiting
  - `ENVIRONMENT=production` : Applique les limitations strictes

### Migrations de base de données

- Utilisation d'Alembic pour gérer les migrations
- Le fichier `alembic.ini` est configuré pour utiliser la variable d'environnement `DATABASE_URL`
- Les modèles sont automatiquement détectés via le `MetaData` de `BaseModel`
- Pour générer une migration : `alembic revision --autogenerate -m "Description de la migration"`
- Pour appliquer les migrations : `alembic upgrade head`
- Les migrations sont versionnées dans le dossier `alembic/versions/`
- Il est important de vérifier les migrations générées automatiquement avant de les appliquer

### Tests

- Structure prévue pour les tests dans le répertoire `tests/`
- Utilisation de pytest pour l'exécution des tests
- Séparation des tests unitaires et d'intégration
- Mocking des dépendances externes pour les tests

### Gestion des imports et dépendances

- Pour éviter les cycles d'importation, la classe `Base` est définie dans `api/base.py`
- Tous les modèles importent `Base` depuis `..base` (chemin relatif vers le répertoire parent)
- Les imports sont organisés dans un ordre cohérent : bibliothèques standard, bibliothèques tierces, imports locaux
- Les dépendances sont gérées dans `requirements.txt`
- Les chemins sont gérés de manière relative pour assurer la portabilité
- Le fichier `api/database.py` importe `Base` depuis `..base`
- Le fichier `api/models/__init__.py` expose tous les modèles pour importation globale

### Conventions de codage

1. **Nom des variables et fonctions** : Utiliser le format snake_case
2. **Nom des classes** : Utiliser le format PascalCase
3. **Nom des modules** : Utiliser le format snake_case
4. **Documentation** : Les fonctions et classes doivent être documentées avec docstrings
5. **Annotations de type** : Fournir des annotations de type pour toutes les fonctions
6. **Longueur des lignes** : Limiter à 100 caractères par ligne
7. **Importations** : Regrouper les importations par type (bibliothèques standard, tierces, locales)
8. **Noms des endpoints** : Utiliser des noms pluriels pour les collections, singuliers pour les éléments spécifiques
9. **Noms des méthodes de service** : Utiliser des verbes à l'infinitif (get_, create_, update_, delete_)
10. **Gestion des erreurs** : Utiliser des exceptions HTTP avec des messages clairs

- Les identifiants sont de type UUID pour assurer l'unicité
- Les clés étrangères utilisent le même type que les champs qu'elles référencent
- Les champs temporels utilisent DateTime avec des valeurs par défaut
- Les relations entre modèles utilisent les fonctionnalités de SQLAlchemy

## Bonnes pratiques

1. **Séparation des responsabilités** : La logique métier doit être dans les services, pas dans les routeurs
2. **Gestion des erreurs** : Utiliser des gestionnaires d'exceptions centralisés
3. **Sécurité** : Appliquer les contrôles RBAC à tous les endpoints sensibles
4. **Validation des entrées** : Utiliser des schémas Pydantic pour valider toutes les données entrantes
5. **Performance** : Éviter les N+1 queries en utilisant des jointures appropriées
6. **Testabilité** : Écrire des tests unitaires pour la logique métier dans les services
7. **Documentation** : Maintenir à jour la documentation de l'API et du code
8. **Versioning** : Utiliser des préfixes pour les versions d'API (ex: /api/v1/)
9. **Journalisation** : Enregistrer les actions importantes pour la traçabilité
10. **Gestion des transactions** : Utiliser des transactions explicites pour les opérations critiques
11. **Sécurité avancée** : Utiliser get_current_user_security uniformément, implémenter des validations poussées et appliquer du rate limiting aux endpoints critiques

## Conclusion

Ce projet met en œuvre une architecture moderne et évolutive pour une application de gestion de station-service. L'architecture hexagonale permet une séparation claire des responsabilités, facilitant la maintenance et les tests. Le système RBAC assure une sécurité fine des accès, tandis que l'internationalisation permet de supporter plusieurs langues.

L'application est conçue pour être extensible, permettant l'ajout de nouveaux modules fonctionnels tout en maintenant une cohérence architecturale.

### Corrections apportées

#### Problème d'importation résolu
- Initial : `ImportError: cannot import name 'Base' from 'api.database'`
- Cause : Cycle d'importation entre les modules
- Solution : Création d'un fichier `api/base.py` centralisant la définition de `Base`

#### Problèmes de cohérence de types résolus
- Initial : Incompatibilités de types entre clés étrangères et champs référencés
- Cause : Utilisation incohérente de types (UUID vs String) pour les mêmes entités
- Solution : Uniformisation de l'utilisation du type UUID pour tous les identifiants et clés étrangères

### Considérations pour les futures implémentations

1. Lors de la création de nouveaux modèles :
   - Toujours étendre la classe `Base` depuis `..base`
   - Utiliser le type UUID pour les identifiants uniques
   - Assurer la cohérence des types entre clés étrangères et champs référencés

2. Lors de l'ajout de relations :
   - Utiliser les fonctionnalités de relation de SQLAlchemy
   - Spécifier correctement les propriétés `back_populates` ou `backref`

3. Lors de la modification des modèles existants :
   - Vérifier l'impact sur les relations et dépendances
   - Maintenir la cohérence des types dans toutes les références
