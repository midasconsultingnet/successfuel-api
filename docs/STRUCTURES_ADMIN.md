# Documentation du Module Structures - Administrateurs

## Introduction

Cette documentation décrit les endpoints du module Structures accessibles aux administrateurs (super administrateurs et administrateurs) dans le système SuccessFuel. Ce module permet de gérer les éléments de base du système tels que les pays, les compagnies et les stations-service.

## Authentification

Les endpoints de ce module nécessitent une authentification administrative. Pour accéder à ces endpoints, vous devez inclure un en-tête d'autorisation au format suivant :

```
Authorization: Bearer <votre_token_admin>
```

### Types d'utilisateurs autorisés

- **Super Administrateur** : Accès complet à toutes les fonctionnalités de gestion des structures
- **Administrateur** : Accès selon les permissions spécifiques définies

## Endpoints Administrateurs - Gestion des Structures

### 1. Gestion des Pays

Les pays sont des entités de base utilisées pour les spécifications locales et la gestion par région.

#### Récupérer la liste des pays
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/admin/countries`
- **Description** : Récupère la liste de tous les pays dans le système
- **Paramètres** : 
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif)
  - `search` (optionnel) : Recherche par nom de pays
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 10)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `pays.lire`
- **Retour** : Liste paginée des pays avec leurs détails

#### Créer un nouveau pays
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/admin/countries`
- **Description** : Crée un nouveau pays dans le système
- **Permissions requises** : `pays.creer`
- **Corps de la requête** :
```json
{
  "code_pays": "string (3 caractères)",
  "nom_pays": "string",
  "devise_principale": "string (3 caractères)",
  "taux_tva_par_defaut": "number",
  "systeme_comptable": "string",
  "date_application_tva": "string (YYYY-MM-DD)",
  "statut": "string (Actif/Inactif)"
}
```
- **Retour** : Détails du pays créé

### 2. Gestion des Compagnies

Les compagnies sont des regroupements d'entités (stations, utilisateurs, etc.) dans le système.

#### Récupérer la liste des compagnies
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/admin/companies`
- **Description** : Récupère la liste de toutes les compagnies dans le système
- **Paramètres** : Aucun
- **Permissions requises** : Aucune (accès restreint automatiquement)
- **Retour** : Liste des compagnies avec leurs détails

#### Créer une nouvelle compagnie
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/admin/companies`
- **Description** : Crée une nouvelle compagnie dans le système
- **Permissions requises** : Accès aux endpoints administrateurs
- **Corps de la requête** :
```json
{
  "code": "string",
  "nom": "string",
  "adresse": "string (optionnel)",
  "telephone": "string (optionnel)",
  "email": "string (optionnel)",
  "nif": "string (optionnel)",
  "pays_id": "string (UUID)",
  "devise_principale": "string (3 caractères)"
}
```
- **Retour** : Détails de la compagnie créée

### 3. Gestion des Stations

Les stations-service appartiennent à une compagnie spécifique et constituent les unités opérationnelles du système.

#### Récupérer la liste des stations
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/admin/stations`
- **Description** : Récupère la liste de toutes les stations dans le système
- **Paramètres** : Aucun
- **Permissions requises** : Accès aux endpoints administrateurs
- **Retour** : Liste des stations avec leurs détails

#### Créer une nouvelle station
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/admin/stations`
- **Description** : Crée une nouvelle station dans le système
- **Permissions requises** : Accès aux endpoints administrateurs
- **Corps de la requête** :
```json
{
  "compagnie_id": "string (UUID)",
  "code": "string",
  "nom": "string",
  "adresse": "string (optionnel)",
  "telephone": "string (optionnel)",
  "email": "string (optionnel)",
  "pays_id": "string (UUID)"
}
```
- **Retour** : Détails de la station créée

## Contrôles d'Accès

### Permissions
- Les administrateurs ont accès selon leurs permissions spécifiques
- Les super administrateurs ont un accès complet aux fonctionnalités de gestion des structures
- Les endpoints sont protégés par le système RBAC

### Contrôle des données
- Les administrateurs peuvent accéder à toutes les données selon leurs permissions
- Les super administrateurs ont un accès global mais pas aux opérations quotidiennes

## Erreurs

L'API renvoie des réponses d'erreur standardisées :

- `401 Unauthorized` - Jeton invalide ou expiré
- `403 Forbidden` - Permissions insuffisantes pour l'action demandée
- `404 Not Found` - Ressource demandée introuvable
- `400 Bad Request` - Paramètres invalides ou requête mal formée
- `500 Internal Server Error` - Erreur interne du serveur

## Sécurité

- Toutes les communications doivent utiliser HTTPS
- Les jetons ont une durée de vie limitée
- Les actions critiques sont journalisées