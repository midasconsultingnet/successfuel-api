# Sprint : Gestion des Tiers - Clients, Fournisseurs et Employés

## Objectif principal
Développer une gestion séparée des différents types de tiers (clients, fournisseurs, employés) dans le système Succès Fuel, avec des interfaces spécifiques pour chaque type.

## Étude de l'existant
- Le système actuel utilise une table `tiers` unique pour gérer les clients, fournisseurs et employés
- Chaque type de tiers partage les mêmes champs, ce qui introduit des champs inutiles pour chaque type
- L'interface utilisateur gère tous les types de tiers de manière générique
- Le système est moins intuitif et plus sujet aux erreurs

## Problèmes identifiés
1. Mélange des concepts : clients, fournisseurs et employés dans une même table
2. Champs optionnels : de nombreux champs ne sont pertinents que pour un type spécifique
3. Manque de clarté : interface unique pour des entités très différentes
4. Validation insuffisante : impossibilité d'appliquer des validations spécifiques à chaque type

## Solution proposée
Séparation des endpoints et interfaces pour chaque type de tiers :
- CRUD séparé pour les clients
- CRUD séparé pour les fournisseurs
- CRUD séparé pour les employés

## Développements à réaliser

### 1. Modèle de données
- [x] Mise à jour du modèle SQLAlchemy pour utiliser des UUID
- [x] Correction des types de données pour les champs monétaires
- [x] Ajout des champs created_at et updated_at

### 2. Schémas Pydantic
- [x] Création de schémas spécifiques pour les clients
- [x] Création de schémas spécifiques pour les fournisseurs
- [x] Création de schémas spécifiques pour les employés

### 3. Endpoints API
- [x] Création d'endpoints spécifiques pour les clients
  - POST `/api/v1/tiers/clients`
  - GET `/api/v1/tiers/clients`
  - GET `/api/v1/tiers/clients/{client_id}`
  - PUT `/api/v1/tiers/clients/{client_id}`
  - DELETE `/api/v1/tiers/clients/{client_id}`
  
- [x] Création d'endpoints spécifiques pour les fournisseurs
  - POST `/api/v1/tiers/fournisseurs`
  - GET `/api/v1/tiers/fournisseurs`
  - GET `/api/v1/tiers/fournisseurs/{fournisseur_id}`
  - PUT `/api/v1/tiers/fournisseurs/{fournisseur_id}`
  - DELETE `/api/v1/tiers/fournisseurs/{fournisseur_id}`
  
- [x] Création d'endpoints spécifiques pour les employés
  - POST `/api/v1/tiers/employes`
  - GET `/api/v1/tiers/employes`
  - GET `/api/v1/tiers/employes/{employe_id}`
  - PUT `/api/v1/tiers/employes/{employe_id}`
  - DELETE `/api/v1/tiers/employes/{employe_id}`

### 4. Validation et sécurité
- [x] Validation spécifique à chaque type de tiers
- [x] Récupération automatique du compagnie_id de l'utilisateur connecté
- [x] Vérification des permissions (un utilisateur ne voit que les tiers de sa compagnie)

## Spécifications détaillées

### Clients
- Champs spécifiques : seuil_credit, conditions_paiement, categorie_client
- Pas de champ poste ou date_embauche
- Inclut les champs solde et statut

### Fournisseurs
- Champs spécifiques : conditions_livraison, delai_paiement
- Pas de champ seuil_credit, conditions_paiement ni categorie_client
- Pas de champ poste ou date_embauche

### Employés
- Champs spécifiques : poste, date_embauche
- Pas de champ seuil_credit, conditions_paiement, categorie_client, conditions_livraison ou delai_paiement

## Avantages de la nouvelle approche
1. Clarté : interfaces spécifiques pour chaque type d'entité
2. Validation : validations adaptées à chaque type
3. Maintenance : code plus modulaire et facile à maintenir
4. Sécurité : accès restreint aux informations pertinentes
5. Évolutivité : ajout de nouveaux types de tiers plus simple

## Tests à implémenter
- [x] Tests unitaires pour les schémas spécifiques
- [x] Tests fonctionnels pour les nouveaux endpoints
- [ ] Tests d'intégration pour valider le fonctionnement complet

## Documentation
- [x] Mise à jour de la documentation API
- [ ] Mise à jour du guide utilisateur
- [ ] Documentation des endpoints dans le fichier OpenAPI

## 3. Soldes initiaux
- [ ] Saisie des soldes initiaux pour chaque client, fournisseur, employé
- [ ] Validation des soldes initiaux
- [ ] Création des écritures comptables de départ
- [ ] Endpoint pour la mise à jour du solde initial
- [ ] Suivi des modifications de solde initial

## 4. Gestion des interactions
- [ ] Suivi des interactions avec chaque client, fournisseur, employé
- [ ] Type d'interaction, date, montant
- [ ] Historique des communications
- [ ] Lien avec les stations pour les opérations localisées
- [ ] Endpoint pour enregistrer une nouvelle interaction
- [ ] Endpoint pour récupérer l'historique des interactions

## 5. Suivi des dettes et créances
- [ ] Calcul des soldes actuels
- [ ] Historique des paiements et factures
- [ ] Gestion des dates d'échéance pour les créances clients
- [ ] Système de blocage automatique si dépassement du seuil de crédit
- [ ] Notifications pour les paiements en retard
- [ ] Interface de gestion des créances

## Ressources nécessaires
- Accès à la base de données pour tester les nouveaux modèles
- Environnement de développement pour tester les endpoints
- Documentation des API existantes