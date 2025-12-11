# 🎯 CONTEXTE GLOBAL — Système de Gestion Intégré pour Compagnie de Stations-Service

## 1. Objectif général
Le système est une plateforme ERP complète destinée aux compagnies gérant plusieurs stations-service.  
Chaque **compagnie est liée à un pays**
Il centralise toutes les opérations : utilisateurs, stations, trésoreries, carburant, boutique, tiers, immobilisations, stocks et comptabilité.  

Chaque station fonctionne comme une entité autonome pour ses opérations quotidiennes, tout en étant intégrée dans une structure centrale pour la gestion globale de la compagnie.

---

# 2. Gestion des accès et structure organisationnelle

## 2.1 Utilisateurs et permissions
- Création et gestion des utilisateurs internes.
- Affectation d’un utilisateur à une ou plusieurs stations.
- Permissions granulaires basées sur les stations.
- RBAC étendu : l’utilisateur ne consulte que les données autorisées.

## 2.2 Structure de la compagnie
- Gestion de toutes les stations-service de la compagnie.
- Identification unique des stations.
- Activation/désactivation et mise à jour des stations.
- **Lorsqu’une station est entièrement configurée (structure + soldes + stocks + immobilisations), le système peut générer un *Bilan Initial de Départ*.**

---

# 3. Tiers et trésoreries (Disponibles pour toute la compagnie)

## 3.1 Tiers (globaux à la compagnie)
Les tiers sont communs à toutes les stations :
- Clients
- Fournisseurs
- Employés

Fonctionnalités :
- Création et mise à jour des fiches tiers.
- Gestion des soldes initiales.
- Suivi des dettes, créances et règlements.
- Historique complet des mouvements tiers.
- Utilisables dans toutes les stations (pas de duplication locale).

## 3.2 Trésoreries (globales à la compagnie)
Les trésoreries sont centralisées et utilisables dans toutes les stations :
- Caisse
- Banque
- Coffre
- Fonds divers

Fonctionnalités :
- Paramétrage des trésoreries globales.
- Gestion des soldes initiales.
- Enregistrement des mouvements par station.
- Consultation des soldes et historiques consolidés ou station par station.

---

# 4. Stocks initiaux et immobilisations

## 4.1 Stocks initiaux
- Stocks initiaux carburant (par cuve, par station).
- Stocks initiaux boutique (par produit, par station).
- Stocks initiaux généraux.
- Préparation des écritures comptables de démarrage.

## 4.2 Immobilisations
- Enregistrement des immobilisations par station.
- Affectation, valeur d’origine et suivi.
- Gestion des investissements et opérations liées.

---

# 5. Gestion carburant (par station)

## 5.1 Achats carburant
- Saisie des achats auprès des fournisseurs.
- Suivi des quantités, prix, BL et factures.
- Intégration au stock carburant.

## 5.2 Livraisons carburant (par cuve)
- Affectation de chaque livraison à une cuve spécifique.
- Mise à jour automatique du stock cuve.
- Historique détaillé.

## 5.3 Ventes carburant
- Gestion des ventes par station.
- Informations supportées : pompes, compteurs, volumes, prix.
- Intégration possible via API avec équipements.

## 5.4 Inventaires carburant
- Inventaire physique par cuve.
- Comparaison stock théorique vs réel.
- Gestion des écarts (pertes, évaporation, anomalies).

---

# 6. Gestion boutique (par station)

## 6.1 Familles et produits
- Familles produits par station.
- Liste des produits boutique associée à chaque famille.
- Gestion des caractéristiques produit : prix, unité, coût moyen, etc.

## 6.2 Achats boutique
- Saisie des achats.
- Mise à jour du stock et des coûts d'acquisition.

## 6.3 Ventes boutique
- Enregistrement des ventes.
- Gestion remises, promotions, ventes en lot.

## 6.4 Inventaires boutique
- Inventaires physiques par produit.
- Calcul des écarts et ajustements.

---

# 7. Gestion avancée des opérations hors achats et ventes (par station)

## 7.1 Charges de fonctionnement
- Gestion des catégories de charges.
- Suivi des charges courantes (électricité, eau, fournitures, maintenance…).

## 7.2 Salaires et rémunérations
- Gestion des salaires, paiements, primes, avances et retenues.

## 7.3 Immobilisations et investissements
- Gestion des acquisitions, réparations, entretiens et investissements.

## 7.4 Recouvrements de créances
- Encaissement des paiements clients.
- Gestion des créances en retard.
- Historique détaillé.

## 7.5 Règlements des dettes
- Paiements fournisseurs.
- Suivi des échéances.
- Impact sur les trésoreries.

---

# 8. États, mouvements, bilans et comptabilité

## 8.1 Mouvements et soldes de trésorerie
- Solde par trésorerie et par station.
- Historique des entrées/sorties.
- Filtres par période, station ou type.

## 8.2 Mouvements et soldes tiers
- Suivi des soldes clients, fournisseurs, employés.
- Détail des opérations et historiques.
- Dettes et créances en temps réel.

## 8.3 Stocks carburant (par cuve)
- Mouvements complets :
  - achats
  - livraisons
  - ventes
  - inventaires
  - ajustements
- Stock réel vs théorique.

## 8.4 Stocks boutique
- Mouvements d’achats, ventes, inventaires, régularisations.
- Stock par produit, par station.

## 8.5 Bilan des opérations (à une date donnée)
### Par station :
- Situation des trésoreries
- Immobilisations
- Stocks carburant
- Stocks boutique
- Dettes et créances
- Résumé comptable
- Résultat des opérations

### Global compagnie :
- Consolidation de toutes les stations.

## 8.6 Bilan Initial de Départ
Une fois les étapes suivantes terminées :
- création de la structure de la station
- définition des trésoreries
- saisie des soldes initiaux
- saisie des stocks initiaux
- enregistrement des immobilisations

Le système génère automatiquement le **Bilan Initial de Départ** de la station.
Ce bilan représente la situation exacte de départ de la station.

## 8.7 Journal des opérations
- Historique chronologique des opérations par station.
- Filtrage par type d’opération.

## 8.8 Journal comptable
- Génération automatique d’écritures comptables.
- Pour chaque achat, vente, charge, salaire, mouvement de trésorerie, inventaire, immobilisation.
- Export : CSV, Excel, XML, etc.

---

# 9. Fonctionnalités avancées futures

## 9.1 Dashboard de supervision
- Tableau de bord global pour la compagnie permettant de surveiller les performances de toutes les stations en temps réel.
- Indicateurs clés de performance (KPI) personnalisables.
- Alertes visuelles pour les seuils critiques.

## 9.2 Système d'alertes automatisées
- Seuils d'alerte paramétrables pour :
  - Stocks bas
  - Écarts de carburant
  - Retards de paiement
  - Anomalies de fonctionnement
- Notifications push et email.

## 9.3 Intégration API étendue
- Connecteurs pour systèmes externes (ERP, systèmes comptables, etc.)
- API ouverte pour intégration avec équipements de station-service
- Documentation technique complète

## 9.4 Modes de fonctionnement avancés
- Mode déconnecté pour les stations avec des problèmes de connectivité
- Synchronisation automatique des données une fois la connexion rétablie
- Gestion des conflits de données

## 9.5 Sécurité et conformité
- Sauvegardes automatisées et redondance des données
- Chiffrement des données sensibles
- Conformité aux normes RGPD et locales

## 9.6 Export et reporting avancé
- Formats d'export multiples : CSV, Excel, XML, PDF
- Rapports personnalisables
- Programmation d'envoi automatique de rapports

---

# 🔥 Résumé ultra-synthétique
ERP complet multi-stations-service couvrant :
- utilisateurs & permissions
- carburant : achats, cuves, ventes, inventaires
- boutique : familles, produits, achats, ventes, inventaires
- tiers globaux & trésoreries globales
- immobilisations, investissements, charges, salaires
- stocks initiaux & mouvements
- bilans, journaux, comptabilité
- **bilan initial automatique dès la fin de la configuration d’une station**

Chaque station est autonome, mais tout est centralisé au niveau compagnie.

