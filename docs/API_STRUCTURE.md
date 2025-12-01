# Documentation de l'API SuccessFuel - Structure des Endpoints

## Introduction

SuccessFuel est un ERP complet conçu pour la gestion des stations-service. Cette documentation décrit la structure et l'organisation des endpoints de l'API, avec une séparation claire entre les endpoints destinés aux administrateurs et ceux destinés aux utilisateurs des compagnies.

La documentation détaillée des endpoints a été séparée en deux fichiers distincts pour une meilleure organisation :

- [Endpoints Administrateurs](admin_endpoints.md) - Tous les endpoints réservés aux administrateurs
- [Endpoints Compagnie](compagnie_endpoints.md) - Tous les endpoints destinés aux utilisateurs des compagnies

## Authentification

L'API utilise un système d'authentification basé sur des jetons JWT (JSON Web Token). Pour accéder aux endpoints protégés, vous devez inclure un en-tête d'autorisation au format suivant :

```
Authorization: Bearer <votre_token>
```

## Types d'Utilisateurs et Accès

Le système distingue 4 types d'utilisateurs avec des rôles et responsabilités spécifiques :

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

### 3. Gérant Compagnie
- **Accès** : `/api/v1`
- **Rôle principal** : Accès à toutes les opérations de sa compagnie
- **Responsabilités** :
  - Gestion complète des opérations de sa compagnie (achats, ventes, stocks, trésorerie, comptabilité, etc.)
  - Supervision de toutes les stations de sa compagnie
  - Gestion des utilisateurs de sa compagnie
  - Accès à tous les modules fonctionnels pour sa compagnie
- **Permissions** : Accès à toutes les fonctionnalités mais limité aux données de sa propre compagnie

### 4. Utilisateur Compagnie
- **Accès** : `/api/v1`
- **Rôle principal** : Accès limité selon ses permissions spécifiques
- **Responsabilités** :
  - Opérations quotidiennes selon ses droits
  - Saisie et traitement des données selon ses permissions
  - Responsabilité limitée à ses tâches assignées

## Contrôles d'Accès et Permissions

### Séparation des Endpoints
- **Endpoints administrateurs** : Réservés aux super administrateurs et administrateurs
- **Endpoints utilisateurs** : Réservés aux gérants de compagnie et utilisateurs de compagnie
- **Blocage automatique** : Les utilisateurs ne peuvent pas accéder à l'endpoint qui ne leur est pas destiné

### Contrôles de Sécurité
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