# Endpoints Compagnie

## Introduction

Cette documentation décrit tous les endpoints destinés aux utilisateurs des compagnies dans l'API SuccessFuel. Ces endpoints sont accessibles via le préfixe `/api/v1` et sont destinés aux gérants de compagnie et aux utilisateurs de compagnie.

## Authentification

Pour accéder à ces endpoints, vous devez inclure un en-tête d'autorisation JWT au format suivant :
```
Authorization: Bearer <votre_token>
```

Tous les endpoints dans cette section sont protégés et nécessitent une authentification valide.

## Types d'Utilisateurs de Compagnie

Le système distingue deux types d'utilisateurs de compagnie :

### 1. Gérant Compagnie
- **Accès** : `/api/v1`
- **Rôle principal** : Accès à toutes les opérations de sa compagnie
- **Responsabilités** :
  - Gestion complète des opérations de sa compagnie (achats, ventes, stocks, trésorerie, comptabilité, etc.)
  - Supervision de toutes les stations de sa compagnie
  - Gestion des utilisateurs de sa compagnie
  - Accès à tous les modules fonctionnels pour sa compagnie
- **Permissions** : Accès à toutes les fonctionnalités mais limité aux données de sa propre compagnie

### 2. Utilisateur Compagnie
- **Accès** : `/api/v1`
- **Rôle principal** : Accès limité selon ses permissions spécifiques
- **Responsabilités** :
  - Opérations quotidiennes selon ses droits
  - Saisie et traitement des données selon ses permissions
  - Responsabilité limitée à ses tâches assignées

## Liste des Endpoints

### 1. Authentification et Profil
- `POST /api/v1/login` - Authentification utilisateur
- `POST /api/v1/register` - Inscription d'un utilisateur
- `GET /api/v1/profile` - Récupérer le profil de l'utilisateur connecté
- `GET /api/v1/users/{user_id}` - Récupérer les détails d'un utilisateur
- `POST /api/v1/refresh-token` - Renouveler le jeton d'authentification
- `POST /api/v1/logout` - Déconnexion
- `POST /api/v1/logout-all` - Déconnexion de toutes les sessions

### 2. Gestion des Structures Physiques de la Station
- `GET /api/v1/cuves` - Récupérer la liste des cuves
- `POST /api/v1/cuves` - Créer une cuve
- `GET /api/v1/cuves/{cuve_id}` - Récupérer les détails d'une cuve
- `GET /api/v1/pistolets` - Récupérer la liste des pistolets
- `POST /api/v1/pistolets` - Créer un pistolet
- `GET /api/v1/pistolets/{pistolet_id}` - Récupérer les détails d'un pistolet
- `GET /api/v1/barremage-cuves` - Récupérer la liste des barémages de cuves
- `POST /api/v1/barremage-cuves` - Créer un barémage de cuve
- `GET /api/v1/pompes` - Récupérer la liste des pompes
- `POST /api/v1/pompes` - Créer une pompe

### 3. Gestion des Produits et Services
- `GET /api/v1/carburants` - Récupérer la liste des carburants
- `POST /api/v1/carburants` - Créer un carburant
- `GET /api/v1/carburants/{carburant_id}` - Récupérer les détails d'un carburant
- `GET /api/v1/articles` - Récupérer la liste des articles
- `POST /api/v1/articles` - Créer un article
- `GET /api/v1/familles-articles` - Récupérer la liste des familles d'articles
- `POST /api/v1/familles-articles` - Créer une famille d'articles

### 4. Gestion des Prix
- `GET /api/v1/historique-prix-carburants` - Récupérer l'historique des prix des carburants
- `POST /api/v1/historique-prix-carburants` - Créer un historique de prix de carburant
- `GET /api/v1/historique-prix-articles` - Récupérer l'historique des prix des articles
- `POST /api/v1/historique-prix-articles` - Créer un historique de prix d'article

### 5. Gestion des Relevés et Indices
- `GET /api/v1/historique-index-pistolets` - Récupérer l'historique des indices de pistolets
- `POST /api/v1/historique-index-pistolets` - Créer un historique d'indice de pistolet

### 6. Gestion des Tiers (Clients, Fournisseurs, Employés)
- `GET /api/v1/clients` - Récupérer la liste des clients
- `POST /api/v1/clients` - Créer un client
- `GET /api/v1/clients/{client_id}` - Récupérer les détails d'un client
- `GET /api/v1/fournisseurs` - Récupérer la liste des fournisseurs
- `POST /api/v1/fournisseurs` - Créer un fournisseur
- `GET /api/v1/fournisseurs/{fournisseur_id}` - Récupérer les détails d'un fournisseur
- `GET /api/v1/employes` - Récupérer la liste des employés
- `POST /api/v1/employes` - Créer un employé
- `GET /api/v1/employes/{employe_id}` - Récupérer les détails d'un employé
- `GET /api/v1/type-tiers` - Récupérer la liste des types de tiers

### 7. Gestion des Stocks
- `GET /api/v1/stocks` - Récupérer la liste des stocks
- `POST /api/v1/stocks` - Créer un stock
- `GET /api/v1/stocks-mouvements` - Récupérer la liste des mouvements de stock
- `POST /api/v1/stocks-mouvements` - Créer un mouvement de stock

### 8. Initialisation des Stocks
- `GET /api/v1/stocks-initialisation/qualites-carburant` - Récupérer la liste des analyses de qualité du carburant initial
- `POST /api/v1/stocks-initialisation/qualites-carburant` - Créer une analyse de qualité du carburant initial
- `PUT /api/v1/stocks-initialisation/qualites-carburant/{qualite_id}` - Mettre à jour une analyse de qualité du carburant initial
- `GET /api/v1/stocks-initialisation/couts-logistiques` - Récupérer la liste des coûts logistiques initiaux
- `POST /api/v1/stocks-initialisation/couts-logistiques` - Créer un coût logistique initial
- `GET /api/v1/stocks-initialisation/bilans-initial` - Récupérer la liste des bilans initiaux
- `POST /api/v1/stocks-initialisation/bilans-initial` - Créer un bilan initial

### 9. Gestion des Modules RBAC
- `GET /api/v1/profiles` - Récupérer la liste des profils
- `POST /api/v1/profiles` - Créer un profil
- `GET /api/v1/profiles/{profile_id}` - Récupérer les détails d'un profil
- `GET /api/v1/users` - Récupérer la liste des utilisateurs
- `POST /api/v1/users` - Créer un utilisateur
- `GET /api/v1/users/{user_id}` - Récupérer les détails d'un utilisateur
- `GET /api/v1/modules` - Récupérer la liste des modules
- `POST /api/v1/modules` - Créer un module
- `GET /api/v1/permissions` - Récupérer la liste des permissions
- `POST /api/v1/permissions` - Créer une permission
- `GET /api/v1/access-control/user-permissions/{user_id}` - Récupérer les permissions d'un utilisateur
- `POST /api/v1/access-control/check-permission` - Vérifier une permission pour un utilisateur

### 10. Gestion des Structures de Base (Lecture)
- `GET /api/v1/pays` - Récupérer la liste des pays
- `GET /api/v1/companies` - Récupérer la liste des compagnies
- `GET /api/v1/stations` - Récupérer la liste des stations
- `GET /api/v1/stations/{station_id}` - Récupérer les détails d'une station

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