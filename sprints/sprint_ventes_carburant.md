# Sprint: Module Ventes Carburant

## Objectif
Implémenter la gestion des ventes de carburant par station, incluant les informations sur les pompes, compteurs, volumes, prix et intégration possible avec les équipements via API.

## Spécifications détaillées

### 1. Gestion des ventes
- Création, modification et suppression de ventes de carburant
- Champs: carburant, quantité vendue, prix unitaire (obtenu via l'API du module Structure de la Compagnie), date/heure
- La station est automatiquement déterminée selon l'utilisateur connecté
- Informations des pistolets et compteurs (numéro, état, volume, index initial, index final)
- Validation des quantités vendues (pas de vente excédentaire)

### 2. Lien avec les cuves et produits
- Association directe avec les cuves de carburant via l'API du module Structure de la Compagnie
- Calcul automatique de l'impact sur le stock de la cuve via l'API du module Structure de la Compagnie
- Le stock théorique d'une cuve est calculé à partir de l'état initial défini dans la table etat_initial_cuve plus les mouvements ultérieurs
- Historique des ventes par carburant et par cuve

### 3. Intégration avec équipements
- Prise en charge des pompes automatiques
- Synchronisation des données de vente en temps réel

### 4. Gestion des paiements et des créances
- Lien avec le pompiste (employé non utilisateur du système)
- Lien avec le QM (Quality Marchal) qui enregistre la vente
- Modes de paiement : espèce, chèque, crédit client, note de crédit (carte carburant)
- Calcul basé sur l'écart entre index initial et final de pistolet
- Enregistrement du montant effectivement payé par le pompiste
- Si montant payé < montant dû → création automatique d'une créance employé
- Liaison avec le module Mouvements Financiers pour la gestion des créances
- Génération d'une écriture de compensation pour les écarts de paiement

### 5. Gestion des annulations et modifications
- Création d'opérations inverses pour annuler ou modifier une vente
- Validation des droits avant annulation (rôles autorisés)
- Vérification de la disponibilité des stocks pour les annulations
- Vérification de la disponibilité de trésorerie pour les remboursements
- Gestion des annulations partielles et totales
- Génération automatique des écritures de compensation pour :
  - Restauration des quantités en stock
  - Remboursement ou ajustement de trésorerie
  - Mise à jour des soldes clients/employés
- Historique complet des modifications et annulations
- Journalisation des motifs d'annulation
- Application des changements dans une transaction atomique

### 6. Historique des ventes
- Suivi des volumes vendus par période
- Historique des prix de vente
- Données de compteur (début et fin de période)

### 7. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes

## Livrables
- API RESTful pour la gestion des ventes carburant
- Modèles de données pour les ventes, les paiements, les créances et les annulations
- Interface d'administration des ventes carburant
- Système d'intégration avec les équipements de pompe
- Système de gestion des paiements et des créances
- Système de gestion des annulations et modifications
- Calcul automatique des impacts sur le stock de cuve
- Tests unitaires et d'intégration