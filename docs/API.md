# Documentation de l'API SuccessFuel

## Introduction

SuccessFuel est un ERP complet conçu pour la gestion des stations-service. Cette API permet d'automatiser, centraliser et sécuriser toutes les opérations liées à la gestion d'une station-service, de la vente de carburant aux opérations comptables et administratives.

## Authentification

L'API utilise un système d'authentification basé sur des jetons JWT (JSON Web Token). Pour accéder aux endpoints protégés, vous devez inclure un en-tête d'autorisation au format suivant :

```
Authorization: Bearer <votre_token>
```

### Types d'utilisateurs

Le système distingue 4 types d'utilisateurs avec des rôles et responsabilités spécifiques :

1. **Super Administrateur**
   - Accès complet à toutes les fonctionnalités
   - Gestion globale du système
   - Création et gestion des autres administrateurs
   - Endpoint d'accès : `/api/v1/admin`

2. **Administrateur**
   - Accès selon les permissions définies par le super administrateur
   - Gestion des aspects opérationnels selon ses permissions
   - Endpoint d'accès : `/api/v1/admin`

3. **Gérant de Compagnie** (nouvelle règle mise en place)
   - Accès à toutes les opérations de sa propre compagnie (achats, ventes, stocks, trésorerie, comptabilité, etc.)
   - Accès limité aux données de sa propre compagnie
   - Ne peut pas accéder aux endpoints administratifs
   - Endpoint d'accès : `/api/v1`
   - **Important :** Le gérant de compagnie bénéficie automatiquement de toutes les permissions fonctionnelles mais ne peut accéder qu'aux données appartenant à sa propre compagnie

4. **Utilisateur de Compagnie**
   - Accès limité selon ses permissions spécifiques
   - Opérations quotidiennes selon ses droits
   - Endpoint d'accès : `/api/v1`

### Séparation des endpoints

- **Endpoints administrateurs** (`/api/v1/admin`) : Réservés aux super administrateurs et administrateurs
- **Endpoints utilisateurs** (`/api/v1`) : Réservés aux gérants de compagnie et utilisateurs de compagnie
- Le système bloque automatiquement les accès croisés entre les types d'utilisateurs et les endpoints

## Permissions et Contrôles d'accès

### Système RBAC (Role-Based Access Control)

Le système utilise un modèle RBAC avec :
- **Profils** : Groupes d'utilisateurs avec des permissions similaires
- **Permissions** : Actions spécifiques que les utilisateurs peuvent effectuer
- **Modules** : Fonctionnalités principales du système (achats, ventes, stocks, etc.)

### Nouvelle règle de permissions pour le Gérant de Compagnie

Avec la mise à jour récente, le **gérant de compagnie** bénéficie d'une nouvelle règle de permissions :
- Il a **automatiquement accès à toutes les fonctionnalités** du système
- Cependant, son accès est **limité aux données appartenant à sa propre compagnie**
- Il ne peut pas accéder aux endpoints administratifs
- Il bénéficie de tous les droits fonctionnels (achats, ventes, stocks, trésorerie, comptabilité, etc.) pour sa propre compagnie

### Contrôle par compagnie

Toutes les opérations métier sont filtrées par **compagnie** :
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Lors de la création/consultation d'entités (stations, produits, ventes, etc.), le système vérifie que l'entité appartient à la même compagnie que l'utilisateur
- Les endpoints de recherche/liste sont automatiquement filtrés par compagnie pour les utilisateurs non-administrateurs

## Endpoints disponibles

### Authentification

- `POST /api/v1/auth/login` - Connexion des utilisateurs standards
- `POST /api/v1/admin/login` - Connexion des administrateurs

### Gestion des structures

- `GET/POST/PUT /api/v1/pays` - Gestion des pays
- `GET/POST/PUT /api/v1/companies` - Gestion des compagnies
- `GET/POST/PUT /api/v1/stations` - Gestion des stations-service

### Gestion des profils et permissions

- `GET/POST/PUT /api/v1/profiles` - Gestion des profils
- `GET/POST /api/v1/modules` - Gestion des modules
- `GET/POST /api/v1/permissions` - Gestion des permissions
- `GET /api/v1/users` - Gestion des utilisateurs

## Exemples d'utilisation

### Exemple de requête pour un gérant de compagnie

```http
GET /api/v1/stations
Authorization: Bearer <token_gérant_compagnie>
```

Cette requête ne retournera que les stations appartenant à la même compagnie que le gérant.

### Exemple de requête pour un administrateur

```http
GET /api/v1/stations
Authorization: Bearer <token_admin>
```

Cette requête peut retourner toutes les stations ou celles filtrées par compagnie, selon les permissions de l'administrateur.

## Erreurs

L'API renvoie des réponses d'erreur standardisées :

- `401 Unauthorized` - Jeton invalide ou expiré
- `403 Forbidden` - Permissions insuffisantes pour l'action demandée
- `404 Not Found` - Ressource demandée introuvable
- `400 Bad Request` - Paramètres invalides ou requête mal formée
- `500 Internal Server Error` - Erreur interne du serveur

## Sécurité

- Toutes les communications doivent utiliser HTTPS
- Les mots de passe sont hachés avec bcrypt
- Les jetons ont une durée de vie limitée (10 heures par défaut)
- Les entrées utilisateur sont validées pour prévenir les injections SQL et XSS
- Les actions critiques sont journalisées