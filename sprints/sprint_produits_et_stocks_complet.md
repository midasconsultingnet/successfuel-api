# Sprint: Module Produits et Stocks Complet

## Objectif
Implémenter la gestion unifiée des produits de boutique, lubrifiants, gaz et services (sans stock) par station, incluant les familles de produits, coûts moyens et prix de vente. Intégration avec la structure organisationnelle de la compagnie via les modules appropriés.

## Spécifications détaillées

### 1. Gestion des familles de produits
- Création, modification et suppression des familles de produits
- Hiérarchie des familles (famille parente, sous-familles)
- Champs: nom, description, code
- Classification des types de produits (boutique, lubrifiants, gaz, produits service)

### 2. Gestion des produits
- Création, modification et suppression des produits
- Champs: nom, code, description, unité de mesure, famille, type (boutique, lubrifiant, gaz, service)
- Prix de vente (obligatoire pour tous les types), seuils de stock minimum (pour les produits avec stock)
- Coût moyen pondéré (pour les produits avec stock)
- Classification: boutique, lubrifiants, gaz, produits service
- Association avec une station
- Distinction: produits avec stock (boutique, lubrifiants, gaz) et produits sans stock (services: lavage, réparation pneu, etc.)
- Interface d'administration modulaire selon le type de produit

### 3. Gestion des unités de mesure
- Prise en charge de différentes unités de mesure pour un même produit (litre, unité, kg, etc.)
- Système de conversion entre unités pour les produits avec stock
- Affichage cohérent des unités dans les interfaces et les rapports

### 4. Gestion des lots et DLC (Date Limite de Consommation)
- Système de gestion des lots pour les produits avec DLC (aliments, certains lubrifiants)
- Suivi de la DLC pour gérer les produits périmés
- Alertes automatiques pour les produits proches de leur DLC
- Priorisation de la vente des produits avec DLC proche (FIFO - First In, First Out)

### 5. Stocks initiaux
- Saisie des stocks initiaux pour produits avec stock (boutique, lubrifiants, gaz)
- Association avec les stations pour les produits avec stock
- Validation des quantités initiales
- Création des écritures comptables de départ
- Historique des mouvements à partir des stocks initiaux
- Les produits service (lavage, réparation pneu, etc.) n'ont pas de stock initial

### 6. Coût moyen et prix de vente
- Calcul du coût moyen pondéré pour les produits avec stock (boutique, lubrifiants, gaz)
- Gestion des prix de vente pour tous les types de produits
- Calcul automatique des coûts après chaque mouvement pour les produits avec stock
- Stockage des mouvements des prix d'achat pour les produits avec stock (achats)
- Association avec les stations et les produits correspondants
- Contrôle d'accès pour les modifications de prix de vente (seulement par les rôles autorisés)
- Journalisation des modifications de prix (qui a modifié, quand, ancien prix, nouveau prix)
- Gestion des promotions et remises spécifiques par produit

### 7. Historique des mouvements
- Suivi des mouvements de stock (achats, livraisons, ventes, inventaires) pour les produits avec stock
- Date, quantité, type d'opération, produit concerné
- Impact sur le stock et le coût moyen (uniquement pour les produits avec stock)
- Lien avec les stations selon le type de produit
- Les produits service (lavage, réparation pneu, etc.) n'ont pas de mouvements de stock mais peuvent avoir des historiques de ventes

### 6. Gestion des pertes et ajustements
- Système de gestion des produits périmés, cassés ou détériorés
- Opérations spéciales de sortie de stock avec motif (périmé, cassé, volé, etc.)
- Historique des ajustements pour des raisons de traçabilité et de reporting
- Seuils d'alerte pour prévenir les pertes importantes
- Impact sur le coût moyen et les états financiers

### 7. Transferts inter-station
- Système de mouvement de stock entre stations de la même compagnie
- Opération de transfert avec une station d'origine et une station de destination
- Mise à jour du stock des deux stations (sortie à l'origine, entrée à destination)
- Historique des transferts pour la traçabilité
- Validation des droits d'accès pour les transferts (rôles autorisés)
- Conservation des coûts moyens lors des transferts

### 8. Gestion des retours et échanges
- Système pour gérer les retours de produits par les clients
- Création automatique d'avoirs ou remboursements suite aux retours
- Traitement des échanges de produits défectueux
- Historique des retours et échanges pour le reporting

### 9. Transferts inter-station
- Système de mouvement de stock entre stations de la même compagnie
- Opération de transfert avec une station d'origine et une station de destination
- Mise à jour du stock des deux stations (sortie à l'origine, entrée à destination)
- Historique des transferts pour la traçabilité
- Validation des droits d'accès pour les transferts (rôles autorisés)
- Conservation des coûts moyens lors des transferts

### 10. Relations avec les modules externes
- Intégration avec le module Structure de la Compagnie pour la gestion des stations
- Les produits service sont inclus dans le module Ventes Boutique mais exclus des modules de gestion de stock
- Intégration avec le module Ventes Boutique pour les opérations de vente (produits et services)
- Intégration avec le module Inventaires Boutique pour les opérations de rapprochement
- Intégration avec le module Mouvements Financiers pour les transactions liées aux produits et services

### 11. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des mouvements critiques
- Contrôle d'accès strict pour les modifications de prix de vente (seuls certains rôles peuvent modifier)
- Intégration avec le système de sécurité du module Structure de la Compagnie

## Livrables
- API RESTful pour la gestion des familles de produits
- API RESTful pour la gestion des produits (boutique, lubrifiants, gaz, services)
- API RESTful pour la gestion des stocks et mouvements (pour produits avec stock)
- API RESTful pour la gestion des ajustements de stock (pertes, casses)
- API RESTful pour la gestion des transferts inter-station
- API RESTful pour la gestion des retours et échanges
- Modèles de données pour les familles, produits et mouvements
- Interface d'administration des familles, produits et stocks (modulaire selon le type de produit)
- Système de calcul du coût moyen (pour produits avec stock)
- Système de suivi des mouvements de stock (pour produits avec stock)
- Système de contrôle d'accès pour les modifications de prix
- Système de journalisation des modifications de prix
- Système de gestion des pertes et ajustements
- Système de gestion des transferts inter-station
- Système de gestion des lots et des DLC
- Système de gestion des unités de mesure
- Système de gestion des retours et échanges
- Documentation des relations avec les modules externes