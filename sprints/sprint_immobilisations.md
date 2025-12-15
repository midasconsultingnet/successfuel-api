# Sprint: Module Immobilisations

## Objectif
Implémenter la gestion des immobilisations par station, incluant leur affectation, valeur d'origine et suivi des opérations liées.

## Spécifications détaillées

### 1. Gestion des immobilisations
- Création, modification et suppression d'immobilisations
- Champs: nom, description, code, date d'acquisition, valeur d'origine
- Type d'immobilisation (matériel, véhicule, bâtiment, etc.)
- Lieu d'affectation (station spécifique)

### 2. Affectation des immobilisations
- Attribution des immobilisations à une station spécifique
- Historique des changements d'affectation
- Validation de l'affectation à une seule station à la fois

### 3. Valeur d'origine et historique
- Enregistrement de la valeur d'origine
- Suivi des réévaluations et modifications de valeur
- Historique des opérations affectant la valeur

### 4. Suivi des opérations liées
- Acquisition (achat, don, etc.)
- Améliorations et réparations majeures
- Cessions et sorties
- Dotation aux amortissements (si applicable)

### 5. Recherche et filtres
- Recherche par station, type, valeur, période
- Filtres avancés pour le reporting
- Export des données

### 6. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des modifications importantes

## Livrables
- API RESTful pour la gestion des immobilisations
- Modèles de données pour les immobilisations et les opérations
- Interface d'administration des immobilisations
- Système de recherche et de filtres
- Fonctionnalités d'export
- Tests unitaires et d'intégration