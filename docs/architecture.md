# Architecture du système SuccessFuel

## Vue d'ensemble

SuccessFuel est un système d'information ERP (Enterprise Resource Planning) modulaire conçu pour la gestion complète des stations-service. L'architecture est organisée selon une structure en couches avec séparation claire des responsabilités.

## Architecture technique

### Backend

- **Langage** : Python 3.8+
- **Framework web** : FastAPI
- **Base de données** : PostgreSQL
- **ORM** : SQLAlchemy
- **Système de modèles** : Pydantic
- **Authentification** : JWT (JSON Web Tokens)
- **Sécurité** : bcrypt pour le hachage des mots de passe

### Architecture des dossiers

```
backend/
├── api/                    # Définitions des routes API
│   └── v1/                # Version 1 de l'API
├── models/                 # Modèles de données SQLAlchemy
├── services/               # Logique métier
├── utils/                  # Utilitaires et helpers
│   ├── access_control.py   # Contrôles d'accès et permissions
│   ├── dependencies.py     # Dépendances FastAPI
│   └── security.py         # Fonctions de sécurité
├── config/                 # Configuration du système
└── database/               # Gestion de la base de données
```

## Gestion des utilisateurs et des permissions

### Modèle de sécurité

Le système utilise un modèle RBAC (Role-Based Access Control) avec une extension pour la gestion par compagnie.

### Types d'utilisateurs

1. **Super Administrateur**
   - Accès total à toutes les fonctionnalités
   - Gestion des autres administrateurs
   - Supervision globale du système

2. **Administrateur**
   - Accès selon permissions spécifiques
   - Gestion des aspects délégués

3. **Gérant de Compagnie**
   - Accès complet aux opérations de sa compagnie
   - Accès limité aux données de sa compagnie
   - Bénéficie de toutes les permissions fonctionnelles

4. **Utilisateur de Compagnie**
   - Accès limité selon permissions spécifiques
   - Opérations quotidiennes

### Nouvelle règle de permissions pour le Gérant de Compagnie

Avec la mise en place de la nouvelle règle de permissions :
- Le gérant de compagnie bénéficie automatiquement de toutes les permissions fonctionnelles
- Il ne peut accéder qu'aux données appartenant à sa propre compagnie
- Le système filtre automatiquement les données selon la compagnie de l'utilisateur
- Les validations sont effectuées à chaque accès fonctionnel

### Contrôles d'accès

#### Filtres par compagnie
- Toutes les requêtes de données sont automatiquement filtrées selon la compagnie de l'utilisateur
- Le système vérifie que les entités manipulées appartiennent à la compagnie de l'utilisateur
- Les endpoints de lecture/liste sont automatiquement limités à la compagnie de l'utilisateur

#### Séparation des endpoints
- `/api/v1/admin/` : Réservé aux administrateurs (super admin et admin)
- `/api/v1/` : Réservé aux utilisateurs standards (gérant de compagnie et utilisateur de compagnie)

#### Permissions implicites
- Le gérant de compagnie a implicitement toutes les permissions fonctionnelles
- Les validations sont effectuées selon les seuils définis (par exemple pour les validations hiérarchiques)

## Modèle de données

### Entités principales

- **Pays** : Informations sur les pays où opère le système
- **Compagnie** : Groupes d'entités (stations, employés, etc.)
- **Station** : Lieux d'exploitation (généralement des stations-service)
- **Utilisateur** : Personnes qui utilisent le système
- **Profil** : Groupes d'utilisateurs avec permissions similaires
- **Permission** : Actions spécifiques autorisées dans le système
- **Module** : Fonctionnalités principales du système

### Relations importantes

- Chaque utilisateur est associé à une compagnie
- Chaque station appartient à une compagnie
- Les données métier (produits, ventes, stocks, etc.) sont liées à une station et donc à une compagnie
- Les profils définissent les permissions pour des groupes d'utilisateurs

## Services métiers

### Services disponibles

- `auth_service.py` : Gestion de l'authentification et des utilisateurs
- `rbac_service.py` : Gestion des profils et permissions
- `structures_service.py` : Gestion des structures de base (pays, compagnies, stations)
- `structure_service.py` : Gestion des éléments physiques (cuves, carburants, pistolets, etc.)
- `achat_service.py` : Gestion des achats
- `vente_service.py` : Gestion des ventes
- `stock_service.py` : Gestion des stocks
- `comptabilite_service.py` : Gestion comptable
- `tresorerie_service.py` : Gestion de trésorerie
- `rapport_service.py` : Génération des rapports

## Contrôles d'accès au code

### Fichiers clés

1. **`utils/access_control.py`** : Décorateurs et fonctions de contrôle d'accès
   - `require_permission()` : Vérifie les permissions spécifiques
   - `require_station_access()` : Vérifie l'accès à une station spécifique
   - `require_company_access()` : Vérifie l'accès à une compagnie spécifique
   - `check_company_access()` : Fonction utilitaire pour vérifier l'accès à une compagnie

2. **`utils/dependencies.py`** : Dépendances FastAPI
   - `get_current_user()` : Récupère l'utilisateur actuel à partir du token
   - `get_current_user_with_company_access()` : Récupère l'utilisateur et vérifie l'accès à la compagnie

3. **`services/rbac_service.py`** : Gestion des permissions
   - `check_user_permission()` : Vérifie si un utilisateur a une permission spécifique
   - Contient la logique pour accorder automatiquement toutes les permissions aux gérants de compagnie

### Implémentation de la nouvelle règle

La nouvelle règle pour les gérants de compagnie est implémentée dans plusieurs endroits :

1. Dans `services/rbac_service.py` - Fonction `check_user_permission()` vérifie si l'utilisateur est un gérant de compagnie et lui accorde toutes les permissions
2. Dans `utils/access_control.py` - Fonctions qui vérifient l'appartenance à la même compagnie
3. Dans les fichiers API - Validation que les données manipulées appartiennent à la compagnie de l'utilisateur
4. Dans les services de données - Filtrage par compagnie dans les fonctions de récupération de données

## Sécurité

### Protection contre les attaques

- **Injections SQL** : Utilisation de requêtes préparées et validation des entrées
- **Authentification** : Jetons JWT avec durée de vie limitée
- **Autorisation** : Vérification fine des permissions avant chaque action
- **Accès aux données** : Filtrage systématique par compagnie
- **Journalisation** : Toutes les actions critiques sont enregistrées

### Gestion des erreurs

- Messages d'erreur standardisés
- Aucune divulgation d'informations sensibles dans les erreurs
- Surveillance proactive des comportements inhabituels

## Déploiement

### Environnement de production

- Serveur WSGI : Gunicorn
- Reverse proxy : Nginx (recommandé)
- Base de données : PostgreSQL
- Mise en cache : Optionnellement Redis

### Scalabilité

- Architecture modulaire permettant l'ajout de fonctionnalités
- Gestion séparée des endpoints pour admin et utilisateurs
- Contrôles d'accès optimisés pour de multiples compagnies