# Endpoints Administrateurs

## Introduction

Cette documentation décrit tous les endpoints réservés aux administrateurs dans l'API SuccessFuel. Ces endpoints sont accessibles via le préfixe `/api/v1/admin` et sont destinés aux super administrateurs et administrateurs du système.

## Authentification

Pour accéder à ces endpoints, vous devez inclure un en-tête d'autorisation JWT au format suivant :
```
Authorization: Bearer <votre_token>
```

Tous les endpoints dans cette section sont protégés et nécessitent une authentification valide.

## Types d'Administrateurs

Le système distingue deux types d'administrateurs :

### 1. Super Administrateur
- **Accès** : `/api/v1/admin`
- **Rôle principal** : Gestion globale du système et gestion des administrateurs et gérants de compagnie
- **Responsabilités** :
  - Gestion globale du système
  - Création et gestion des administrateurs
  - Gestion des gérants de compagnie
  - Gestion des pays
  - Gestion des compagnies
  - Gestion des modules
  - Gestion des types tiers
  - Gestion des configurations_pays et specifications_locales
  - Gestion du plan comptable
  - Configuration des paramètres système
  - Surveillance globale du système
- **Permissions** : Accès à toutes les fonctionnalités de gestion globale mais PAS aux opérations propres à chaque compagnie (structures, bilan initial, achats, ventes, stocks, trésorerie, etc.)

### 2. Administrateur
- **Accès** : `/api/v1/admin`
- **Rôle principal** : Gestion selon les permissions définies par le super administrateur
- **Responsabilités** :
  - Gestion des aspects opérationnels selon ses permissions
  - Supervision des stations selon ses droits
  - Gestion des utilisateurs en fonction de ses autorisations

## Liste des Endpoints

### 1. Gestion des Utilisateurs et Permissions
- `POST /api/v1/admin/login` - Authentification administrateur
- `GET /api/v1/admin/users` - Récupérer la liste des utilisateurs
- `POST /api/v1/admin/users` - Créer un utilisateur
- `PUT /api/v1/admin/users/{user_id}` - Mettre à jour un utilisateur
- `DELETE /api/v1/admin/users/{user_id}` - Supprimer un utilisateur
- `PUT /api/v1/admin/users/{user_id}/activate` - Activer un utilisateur
- `PUT /api/v1/admin/users/{user_id}/deactivate` - Désactiver un utilisateur

### 2. Gestion des Profils et Permissions
- `GET /api/v1/admin/profiles` - Récupérer la liste des profils
- `POST /api/v1/admin/profiles` - Créer un profil
- `PUT /api/v1/admin/profiles/{profile_id}` - Mettre à jour un profil
- `DELETE /api/v1/admin/profiles/{profile_id}` - Supprimer un profil

### 3. Gestion des Structures de Base
- `GET /api/v1/admin/companies` - Récupérer la liste des compagnies
- `POST /api/v1/admin/companies` - Créer une compagnie
- `PUT /api/v1/admin/companies/{company_id}` - Mettre à jour une compagnie
- `DELETE /api/v1/admin/companies/{company_id}` - Supprimer une compagnie
- `GET /api/v1/admin/stations` - Récupérer la liste des stations
- `POST /api/v1/admin/stations` - Créer une station
- `PUT /api/v1/admin/stations/{station_id}` - Mettre à jour une station
- `DELETE /api/v1/admin/stations/{station_id}` - Supprimer une station
- `GET /api/v1/admin/countries` - Récupérer la liste des pays

### 4. Gestion des Modules et Permissions
- `GET /api/v1/admin/modules` - Récupérer la liste des modules
- `POST /api/v1/admin/modules` - Créer un module
- `PUT /api/v1/admin/modules/{module_id}` - Mettre à jour un module
- `GET /api/v1/admin/permissions` - Récupérer la liste des permissions
- `POST /api/v1/admin/permissions` - Créer une permission
- `PUT /api/v1/admin/permissions/{permission_id}` - Mettre à jour une permission

## Contrôles de Sécurité
- Validation hiérarchique selon le montant ou le type d'opération
- Journalisation des tentatives d'accès non autorisés
- Contrôle d'accès basé sur les rôles (RBAC)
- Gestion fine des données auxquelles chaque utilisateur a accès (limité par compagnie)
- Le gérant de compagnie bénéficie de toutes les permissions fonctionnelles mais ne peut accéder qu'aux données de sa propre compagnie

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