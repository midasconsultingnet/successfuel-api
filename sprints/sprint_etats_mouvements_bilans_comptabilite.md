# Sprint: Module États, Bilans et Comptabilité

## Objectif
Implémenter la génération d'états financiers, de bilans (opérationnels et comptables) et des journaux comptables en tant que module de reporting. Les données sont fournies par les autres modules opérationnels.

## Spécifications détaillées

### 1. États de trésorerie
- Solde par trésorerie et par station
- Historique des entrées/sorties
- Filtres par période, station ou type
- Affichage consolidé ou détaillé
- Données fournies par les modules de ventes, achats et règlements

### 2. États des tiers
- Suivi des soldes clients, fournisseurs, employés
- Détail des opérations et historiques
- Dettes et créances en temps réel
- Filtres par période ou type de tiers
- Données fournies par les modules de ventes, achats et salaires

### 3. États de stocks
- Mouvements complets (achats, livraisons, ventes, inventaires, ajustements)
- Stock réel vs théorique
- Par cuve, par station ou consolidé
- Historique détaillé
- Données fournies par les modules d'achats, de ventes et d'inventaires

### 4. Bilan des opérations
- Situation des trésoreries
- Immobilisations
- Stocks carburant
- Stocks boutique
- Dettes et créances
- Résumé comptable
- Résultat des opérations
- Par station ou consolidé global
- Données consolidées à partir des autres modules opérationnels

### 5. Bilan Initial de Départ
- Génération automatique une fois la configuration terminée
- Situation exacte de départ de la station
- Basé sur la structure, trésoreries, soldes, stocks et immobilisations
- Inclut : situation des trésoreries (à partir de la table etat_initial_tresorerie), immobilisations, stocks carburant (à partir de la table etat_initial_cuve), stocks boutique, dettes et créances
- Ce bilan représente la situation exacte de départ de la station
- Déclenché automatiquement lorsque toutes les conditions de configuration sont remplies
- Données consolidées à partir des modules de configuration initiale
- Format et structure basés sur le modèle défini dans `exemple_bilan_initial.md`

### 6. Journal des opérations
- Historique chronologique des opérations par station
- Données consolidées à partir de tous les modules opérationnels
- Filtrage par type d'opération
- Export des données

### 8. Journal comptable
- Génération automatique d'écritures comptables
- Pour chaque achat, vente, charge, salaire, mouvement de trésorerie, etc.
- Export : CSV, Excel, XML, etc.

### 9. Sécurité
- Accès restreint selon les rôles et stations
- Validation des droits d'accès avant les consultations
- Audit des exports importants

## Livrables
- API RESTful pour la génération d'états financiers
- Modèles de données pour les différents types d'états
- Interface de consultation des états
- Système de génération du bilan des opérations
- Système de génération du journal des opérations
- Système de génération du journal comptable
- Fonctionnalités d'export
- Tests unitaires et d'intégration