# Documentation du Module Structures - Utilisateurs des Compagnies

## Introduction

Cette documentation décritte les endpoints du module Structures accessibles aux utilisateurs des compagnies (gérants de compagnie et utilisateurs de compagnie) dans le système SuccessFuel. Ce module permet de gérer les éléments opérationnels des stations-service tels que les cuves, les carburants, les pistolets, les articles, les clients, les fournisseurs et les employés.

## Authentification

Les endpoints de ce module nécessitent une authentification standard. Pour accéder à ces endpoints, vous devez inclure un en-tête d'autorisation au format suivant :

```
Authorization: Bearer <votre_token_utilisateur>
```

### Types d'utilisateurs autorisés

- **Gérant de Compagnie** : Accès complet à toutes les fonctionnalités de gestion des structures pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

## Endpoints Utilisateurs - Gestion des Structures

### 1. Gestion des Cuves

Les cuves sont des réservoirs de stockage pour les carburants dans les stations-service.

#### Récupérer la liste des cuves
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/cuves`
- **Description** : Récupère la liste des cuves de la compagnie de l'utilisateur
- **Paramètres** :
  - `station_id` (optionnel) : Filtre par station
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `cuves.lire`
- **Retour** : Liste paginée des cuves avec leurs détails

#### Créer une nouvelle cuve
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/cuves`
- **Description** : Crée une nouvelle cuve dans la station spécifiée
- **Permissions requises** : `cuves.creer`
- **Corps de la requête** :
```json
{
  "station_id": "string (UUID)",
  "code": "string",
  "capacite": "number",
  "carburant_id": "string (UUID, optionnel)",
  "temperature": "number (optionnel)"
}
```
- **Retour** : Détails de la cuve créée

#### Récupérer les détails d'une cuve spécifique
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/cuves/{cuve_id}`
- **Description** : Récupère les détails d'une cuve spécifique
- **Permissions requises** : `cuves.lire`
- **Retour** : Détails de la cuve spécifiée

### 2. Gestion des Carburants

Les carburants sont les différents types de produits pétroliers vendus dans les stations-service.

#### Récupérer la liste des carburants
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/carburants`
- **Description** : Récupère la liste des carburants de la compagnie de l'utilisateur
- **Paramètres** :
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `carburants.lire`
- **Retour** : Liste paginée des carburants avec leurs détails

#### Créer un nouveau carburant
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/carburants`
- **Description** : Crée un nouveau type de carburant
- **Permissions requises** : `carburants.creer`
- **Corps de la requête** :
```json
{
  "code": "string",
  "libelle": "string",
  "type": "string (Essence/Gasoil/Pétrole)",
  "prix_achat": "number (optionnel)",
  "prix_vente": "number (optionnel)",
  "qualite": "number (optionnel)"
}
```
- **Retour** : Détails du carburant créé

#### Récupérer les détails d'un carburant spécifique
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/carburants/{carburant_id}`
- **Description** : Récupère les détails d'un carburant spécifique
- **Permissions requises** : `carburants.lire`
- **Retour** : Détails du carburant spécifié

### 3. Gestion des Pistolets

Les pistolets sont les équipements de distribution de carburant dans les stations-service.

#### Récupérer la liste des pistolets
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/pistolets`
- **Description** : Récupère la liste des pistolets de la compagnie de l'utilisateur
- **Paramètres** :
  - `pompe_id` (optionnel) : Filtre par pompe
  - `cuve_id` (optionnel) : Filtre par cuve
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `pistolets.lire`
- **Retour** : Liste paginée des pistolets avec leurs détails

#### Créer un nouveau pistolet
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/pistolets`
- **Description** : Crée un nouveau pistolet dans la pompe et cuve spécifiées
- **Permissions requises** : `pistolets.creer`
- **Corps de la requête** :
```json
{
  "code": "string",
  "pompe_id": "string (UUID)",
  "cuve_id": "string (UUID)",
  "index_initiale": "number (optionnel)"
}
```
- **Retour** : Détails du pistolet créé

#### Récupérer les détails d'un pistolet spécifique
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/pistolets/{pistolet_id}`
- **Description** : Récupère les détails d'un pistolet spécifique
- **Permissions requises** : `pistolets.lire`
- **Retour** : Détails du pistolet spécifié

### 4. Gestion des Articles

Les articles sont les produits vendus dans la boutique de la station-service.

#### Récupérer la liste des articles
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/articles`
- **Description** : Récupère la liste des articles de la compagnie de l'utilisateur
- **Paramètres** :
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `articles.lire`
- **Retour** : Liste paginée des articles avec leurs détails

#### Créer un nouvel article
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/articles`
- **Description** : Crée un nouvel article dans la boutique
- **Permissions requises** : `articles.creer`
- **Corps de la requête** :
```json
{
  "code": "string",
  "libelle": "string",
  "codebarre": "string (optionnel)",
  "famille_id": "string (UUID, optionnel)",
  "unite": "string (Litre/kg/pce/etc., par défaut 'Litre')",
  "type_article": "string ('produit' ou 'service', par défaut 'produit')",
  "prix_achat": "number",
  "prix_vente": "number",
  "tva": "number (optionnel)",
  "stock_minimal": "number (optionnel)"
}
```
- **Retour** : Détails de l'article créé

### 5. Gestion des Clients

Les clients sont les personnes ou entreprises achetant des produits ou services à la station-service.

#### Récupérer la liste des clients
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/clients`
- **Description** : Récupère la liste des clients de la compagnie de l'utilisateur
- **Paramètres** :
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `clients.lire`
- **Retour** : Liste paginée des clients avec leurs détails

#### Créer un nouveau client
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/clients`
- **Description** : Crée un nouveau client
- **Permissions requises** : `clients.creer`
- **Corps de la requête** :
```json
{
  "code": "string",
  "nom": "string",
  "adresse": "string (optionnel)",
  "telephone": "string (optionnel)",
  "nif": "string (optionnel)",
  "email": "string (optionnel)",
  "station_ids": "array (optionnel)",
  "type_tiers_id": "string (UUID, optionnel)",
  "nb_jrs_creance": "number (optionnel)",
  "devise_facturation": "string (3 caractères, par défaut 'MGA')"
}
```
- **Retour** : Détails du client créé

#### Récupérer les détails d'un client spécifique
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/clients/{client_id}`
- **Description** : Récupère les détails d'un client spécifique
- **Permissions requises** : `clients.lire`
- **Retour** : Détails du client spécifié

### 6. Gestion des Fournisseurs

Les fournisseurs sont les personnes ou entreprises fournissant des produits ou services à la station-service.

#### Récupérer la liste des fournisseurs
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/fournisseurs`
- **Description** : Récupère la liste des fournisseurs de la compagnie de l'utilisateur
- **Paramètres** :
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `fournisseurs.lire`
- **Retour** : Liste paginée des fournisseurs avec leurs détails

#### Créer un nouveau fournisseur
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/fournisseurs`
- **Description** : Crée un nouveau fournisseur
- **Permissions requises** : `fournisseurs.creer`
- **Corps de la requête** :
```json
{
  "code": "string",
  "nom": "string",
  "adresse": "string (optionnel)",
  "telephone": "string (optionnel)",
  "nif": "string (optionnel)",
  "email": "string (optionnel)",
  "station_ids": "array (optionnel)",
  "type_tiers_id": "string (UUID, optionnel)",
  "nb_jrs_creance": "number (optionnel)"
}
```
- **Retour** : Détails du fournisseur créé

#### Récupérer les détails d'un fournisseur spécifique
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/fournisseurs/{fournisseur_id}`
- **Description** : Récupère les détails d'un fournisseur spécifique
- **Permissions requises** : `fournisseurs.lire`
- **Retour** : Détails du fournisseur spécifié

### 7. Gestion des Employés

Les employés sont le personnel travaillant dans les stations-service.

#### Récupérer la liste des employés
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/employes`
- **Description** : Récupère la liste des employés de la compagnie de l'utilisateur
- **Paramètres** :
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `employes.lire`
- **Retour** : Liste paginée des employés avec leurs détails

#### Créer un nouvel employé
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/employes`
- **Description** : Crée un nouvel employé
- **Permissions requises** : `employes.creer`
- **Corps de la requête** :
```json
{
  "code": "string",
  "nom": "string",
  "prenom": "string (optionnel)",
  "adresse": "string (optionnel)",
  "telephone": "string (optionnel)",
  "poste": "string (optionnel)",
  "salaire_base": "number",
  "avances": "number (optionnel)",
  "creances": "number (optionnel)",
  "station_ids": "array (optionnel)"
}
```
- **Retour** : Détails de l'employé créé

#### Récupérer les détails d'un employé spécifique
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/employes/{employe_id}`
- **Description** : Récupère les détails d'un employé spécifique
- **Permissions requises** : `employes.lire`
- **Retour** : Détails de l'employé spécifié

### 8. Gestion des Pompes

Les pompes sont les équipements contenant un ou plusieurs pistolets de distribution.

#### Récupérer la liste des pompes
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/pompes`
- **Description** : Récupère la liste des pompes de la compagnie de l'utilisateur
- **Paramètres** :
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `pompes.lire`
- **Retour** : Liste paginée des pompes avec leurs détails

#### Créer une nouvelle pompe
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/pompes`
- **Description** : Crée une nouvelle pompe dans la station spécifiée
- **Permissions requises** : `pompes.creer`
- **Corps de la requête** :
```json
{
  "station_id": "string (UUID)",
  "code": "string"
}
```
- **Retour** : Détails de la pompe créée

#### Récupérer les détails d'une pompe spécifique
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/pompes/{pompe_id}`
- **Description** : Récupère les détails d'une pompe spécifique
- **Permissions requises** : `pompes.lire`
- **Retour** : Détails de la pompe spécifiée

### 9. Gestion des Barémages de Cuves

Les barémages sont les relations entre la hauteur de liquide et le volume dans une cuve.

#### Récupérer la liste des barémages
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/barremage-cuves`
- **Description** : Récupère la liste des barémages de la compagnie de l'utilisateur
- **Paramètres** :
  - `cuve_id` (optionnel) : Filtre par cuve
  - `statut` (optionnel) : Filtre par statut (Actif, Inactif, Supprimé)
  - `limit` (optionnel) : Limite le nombre de résultats (1-100, par défaut 50)
  - `offset` (optionnel) : Décalage pour la pagination
- **Permissions requises** : `barremage.lire`
- **Retour** : Liste paginée des barémages avec leurs détails

#### Créer un nouveau barémage
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/barremage-cuves`
- **Description** : Crée un nouveau barémage pour une cuve spécifique
- **Permissions requises** : `barremage.creer`
- **Corps de la requête** :
```json
{
  "cuve_id": "string (UUID)",
  "station_id": "string (UUID)",
  "hauteur": "number",
  "volume": "number"
}
```
- **Retour** : Détails du barémage créé

### 10. Gestion des Historiques de Prix

Les historiques de prix conservent les évolutions de prix des carburants et articles.

#### Récupérer l'historique des prix des carburants
- **Méthode** : `GET`
- **Endpoint** : `/api/v1/historique-prix-carburants`
- **Description** : Récupère l'historique des prix des carburants pour la compagnie de l'utilisateur
- **Paramètres** : Aucun
- **Permissions requises** : `historique_prix_carburants.lire`
- **Retour** : Liste de l'historique des prix des carburants

#### Créer un historique de prix de carburant
- **Méthode** : `POST`
- **Endpoint** : `/api/v1/historique-prix-carburants`
- **Description** : Crée un nouvel historique de prix pour un carburant (généralement automatiquement lors d'un changement de prix)
- **Permissions requises** : `historique_prix_carburants.creer`
- **Corps de la requête** :
```json
{
  "carburant_id": "string (UUID)",
  "prix_achat": "number",
  "prix_vente": "number",
  "date_application": "string (YYYY-MM-DD)"
}
```
- **Retour** : Détails de l'historique de prix créé

## Contrôles d'Accès

### Permissions
- Les gérants de compagnie ont accès à toutes les fonctionnalités de structures pour leur compagnie
- Les utilisateurs de compagnie ont accès limité selon leurs permissions spécifiques
- Toutes les opérations sont automatiquement filtrées par la compagnie de l'utilisateur

### Contrôle des données
- Les utilisateurs ne peuvent accéder qu'aux données appartenant à leur propre compagnie
- Les stations, employés, clients et fournisseurs concernés doivent appartenir à la même compagnie que l'utilisateur
- Les super administrateurs n'ont pas accès aux données opérationnelles quotidiennes des compagnies

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