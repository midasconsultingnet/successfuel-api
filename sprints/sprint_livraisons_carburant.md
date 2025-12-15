# Sprint: Module Livraisons Carburant

## Objectif
Implémenter la gestion des livraisons de carburant vers les cuves des stations, incluant l'affectation à une cuve spécifique et la mise à jour automatique du stock.

## Spécifications détaillées

### 1. Gestion des livraisons
- Création, modification et suppression de livraisons de carburant
- Champs: station, cuve, carburant, quantité livrée, date/heure
- Informations sur le fournisseur (optionnel)
- Historique des livraisons par cuve

### 2. Affectation aux cuves
- Association directe avec une cuve spécifique via l'API du module Structure de la Compagnie
- Validation que la cuve accepte le type de carburant via l'API du module Structure de la Compagnie
- Calcul automatique de l'impact sur le stock de la cuve via l'API du module Structure de la Compagnie

### 3. Historique détaillé
- Suivi des quantités livrées par période
- Historique des modifications
- Données de jauge avant et après livraison

### 4. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes

## Livrables
- API RESTful pour la gestion des livraisons carburant
- Modèles de données pour les livraisons
- Interface d'administration des livraisons carburant
- Système de mise à jour automatique du stock de cuve
- Calcul automatique des impacts sur le stock
- Tests unitaires et d'intégration