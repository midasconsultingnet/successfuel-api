# Sprint: Module Structure de la Compagnie

## Objectif
Implémenter la gestion des compagnies, de leurs stations et des équipements associés (cuves et pistolets), intégré avec la gestion des produits (carburant et boutique) et de leurs stocks. Chaque station fonctionne comme une entité autonome pour ses opérations quotidiennes, tout en étant intégrée dans une structure centrale pour la gestion globale de la compagnie.

## Spécifications détaillées

### 1. Gestion des compagnies
- Récupération des informations de la compagnie de l'utilisateur connecté
- Champs: nom, pays_id (référence à la table pays), adresse, téléphone, email, devise
- Validation des droits d'accès à la compagnie
- Association avec un pays (pour les règles locales) via la table pays
- Chaque utilisateur appartient à une seule compagnie

### 2. Gestion des stations
- Création, modification et suppression des stations
- Champs: nom, code, adresse, coordonnées GPS, statut (actif/inactif)
- Association avec une compagnie
- Validation de l'unicité du code de station par compagnie

### 3. Association compagnie-station
- Une compagnie peut avoir plusieurs stations
- Une station appartient à une seule compagnie
- Contraintes d'intégrité référentielle

### 4. Configuration de base
- Configuration initiale d'une station (paramètres par défaut)
- Activation/désactivation des stations
- Historique des modifications de statut

### 5. Gestion des cuves
- Création, modification et suppression de cuves
- Champs: nom, code, capacité maximale, niveau actuel de carburant, carburant_id (UUID référençant le type de carburant), statut (actif/inactif)
- Barremage: tableau de correspondance hauteur (cm) / volume (litres) spécifique à chaque cuve (facultatif à la création)
- Association avec une station et un type de carburant spécifique (via carburant_id)
- Chaque cuve ne peut contenir qu'un seul type de carburant à la fois
- Validation: une cuve ne peut être associée qu'à un seul carburant
- Suivi de la jauge (niveau actuel, capacité totale) avec historique des changements
- Prise en charge des pistolets associés à la cuve
- Contraintes d'intégrité référentielle
- Intégration avec le module Produits et Stocks pour la gestion des mouvements de carburant
- Historique des mouvements de stock par cuve (entrée, sortie, stock initial)
- Calcul du stock disponible après chaque mouvement
- Avant l'initialisation du stock, validation que le barremage est correctement renseigné

### 6. Initialisation des stocks de carburant
- Interface pour la saisie des quantités initiales par cuve (nom, code, niveau de la cuve en cm, date)
- Calcul automatique du volume en litres en utilisant le barremage spécifique à chaque cuve
- Validation des quantités initiales (vérification de la capacité de la cuve)
- Association avec les types de carburant prédéfinis
- Création des écritures comptables de départ
- Historique des mouvements à partir des stocks initiaux
- Synchronisation avec le module Produits et Stocks pour les aspects liés au stock

### 7. Suivi des mouvements de stock par cuve
- Enregistrement des mouvements (entrée, sortie) avec date, quantité, type d'opération
- Calcul automatique du stock disponible après chaque mouvement
- Historique des mouvements par cuve
- Association avec les types de mouvements (achats, livraisons, ventes, pertes, invendus)
- Contraintes pour empêcher les sorties supérieures au stock disponible
- Intégration avec les données des pistolets pour les ventes de carburant

### 8. Gestion des carburants
- Consultation des types de carburant prédéfinis (gérés au niveau système)
- Champs: nom, code, description, UUID unique
- Association avec les cuves (chaque cuve contient un type spécifique de carburant)
- Les utilisateurs de compagnie ne peuvent pas créer, modifier ou supprimer les types de carburant
- Intégration avec les modules Achats Carburant et Produits et Stocks pour la gestion du prix de vente et de l'historique des prix
- Ce module ne gère pas directement les prix de vente ou d'achat, mais fournit les informations nécessaires aux modules spécialisés

### 9. Gestion des pistolets
- Création, modification et suppression de pistolets
- Champs: numéro de série, statut (actif/inactif), débitmètre
- Index initial pour chaque pistolet
- Historiques de l'index de chaque pistolet
- Association avec une cuve
- Contraintes d'intégrité référentielle
- Suivi des volumes délivrés par pistolet pour la gestion des ventes de carburant

### 10. Gestion des produits boutique
- Intégration avec les produits gérés dans le module Produits et Stocks
- Association avec une station spécifique
- Gestion des stocks, seuils minimum et prix de vente
- Historique des mouvements de stock

### 11. Relations entre entités
- Une compagnie peut avoir plusieurs stations
- Une station peut avoir plusieurs cuves
- Une cuve peut avoir un ou plusieurs pistolets
- Chaque cuve contient un seul type de carburant
- Chaque station peut gérer plusieurs produits de boutique
- Contraintes d'intégrité pour assurer la cohérence des relations
- Intégration complète avec le module Produits et Stocks

### 12. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie)
- Validation des droits d'accès aux données de la compagnie/station/cuve/pistolet
- Contrôle d'accès aux ressources selon la hiérarchie (compagnie → station → cuve → pistolet)
- Audit des mouvements critiques
- Intégration avec le système de sécurité des autres modules

### 13. Intégration avec les modules opérationnels
- Système d'origine unique pour tous les aspects liés aux carburants
- Les modules Achats Carburant, Livraisons Carburant, Ventes Carburant et Inventaires Carburant interagissent avec ce module via des API dédiées
- Toutes les modifications de stock de carburant doivent passer par ce module
- Ce module fournit l'historique des mouvements, les calculs de stock disponible et les vérifications de capacité
- Les modules opérationnels ne gèrent pas directement les stocks de carburant, mais effectuent des appels API vers ce module pour les mettre à jour

## Livrables
- API RESTful pour la consultation des informations de la compagnie de l'utilisateur connecté
- API RESTful pour la gestion des stations (lecture/écriture selon les droits)
- API RESTful pour la gestion des cuves (lecture/écriture selon les droits)
- API RESTful pour la gestion des pistolets (lecture/écriture selon les droits)
- API RESTful pour la gestion des produits boutique (lecture/écriture selon les droits)
- API RESTful pour l'initialisation des stocks de carburant (lecture/écriture selon les droits)
- API RESTful pour le suivi des mouvements de stock par cuve (lecture/écriture selon les droits)
- Interface d'administration pour les structures (stations, cuves, pistolets)
- Interface pour la saisie des stocks initiaux de carburant
- Interface pour le suivi des mouvements de stock par cuve
- Modèles de données pour les relations
- Tests unitaires et d'intégration
- Documentation des relations entre entités
- Documentation de l'API pour l'intégration avec d'autres modules