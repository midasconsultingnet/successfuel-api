# SuccessFuel ERP

ERP pour la gestion complète des stations-service à Madagascar, construit avec FastAPI.

## Prérequis

- Python 3.11 ou supérieur
- PostgreSQL (pour la base de données de production)
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez le projet
2. Créez un environnement virtuel :
   ```bash
   python -m venv venv
   ```
3. Activez l'environnement virtuel :
   - Sous Windows :
     ```bash
     venv\Scripts\activate
     ```
   - Sous macOS/Linux :
     ```bash
     source venv/bin/activate
     ```
4. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
5. Configurez vos variables d'environnement dans un fichier `.env` à la racine du dossier `backend`. Exemple de fichier `.env` :
   ```
   SECRET_KEY=votre-cle-secrete-ici
   DATABASE_URL=postgresql://username:password@localhost/nom_de_la_base
   JWT_SECRET_KEY=votre-cle-jwt-ici
   DEBUG=True
   ```
6. Démarrez l'application :
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

## Technologies

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Strawberry-GraphQL

## Documentation

La documentation de l'API est disponible à l'adresse `/docs` une fois l'application démarrée.
Un endpoint GraphQL est disponible à l'adresse `/graphql`.

## Structure du projet

- `backend/` - Code source de l'application FastAPI
  - `api/v1/` - Définition des routes API
  - `config/` - Configuration de l'application
  - `database/` - Configuration et modèles de la base de données
  - `models/` - Modèles de données
  - `services/` - Logique métier
  - `strawberry_graphql/` - Définition du schéma GraphQL
  - `utils/` - Utilitaires divers
- `database/` - Scripts de base de données
- `docs/` - Documentation du projet
- `scripts/` - Scripts d'automatisation
- `doc_tech/` - Documentation technique
- `docker/` - Fichiers de conteneurisation (Docker)

## Développement

Pour exécuter l'application en mode développement :
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Tests

Pour exécuter les tests :
```bash
cd backend
pytest
```