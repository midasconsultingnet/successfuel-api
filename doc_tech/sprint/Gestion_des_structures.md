# Sprint - Module 1 : Gestion des structures

## Objectif
Développer les fonctionnalités de base permettant la gestion des éléments physiques et organisationnels d'une station-service.

## Étapes du sprint
1. **Stations-service**
   - Création / édition des stations
   - Gestion des adresses, responsables et contacts
   - Association des trésoreries
   - KPIs et indicateurs de performance
   - Suivi des performances

2. **Cuves de stockage**
   - Enregistrement de chaque cuve (type de carburant, capacité en litres)
   - Barème de jauge pour le calcul du volume selon la hauteur
   - Suivi de la température pour correction volumétrique
   - Contrôle d'accès aux cuves

3. **Carburants**
   - Gestion des différents types de carburant (essence, gasoil, pétrole)
   - Suivi des prix d'achat et de vente
   - Historique des évolutions de prix
   - Suivi de la qualité du carburant
   - Historique des coûts liés à la logistique

4. **Pistolets de distribution**
   - Numérotation et association à une cuve spécifique
   - Suivi de l'index initial et des relevés
   - Contrôle d'accès aux pistolets

5. **Familles de produits**
   - Gestion des produits de la boutique (alimentation, lubrifiants, etc.)
   - Services annexes (lavage, atelier, restaurant)

6. **Produits**
   - Suivi des prix d'achat et de vente
   - Stock minimal configuré
   - Gestion de la TVA
   - Code interne pour chaque produit
   - Gestion des additifs et mélanges

7. **Fournisseurs**
   - Informations générales sur les fournisseurs
   - Suivi du solde et des dettes
   - Historique des transactions
   - Historique de qualité des livraisons
   - Analyse de performance des fournisseurs

8. **Clients**
   - Suivi du solde et des créances
   - Historique des paiements
   - Programme de fidélisation
   - Cartes de carburant
   - Contrats de ravitaillement
   - Système de notation

9. **Employés**
   - Gestion des postes (pompiste, caissier, QM, admin, etc.)
   - Suivi des salaires, avances et créances
   - Indicateurs de performance
   - Suivi de la productivité

10. **Trésoreries et modes de paiement**
    - Gestion des comptes (Banque BNI, BMOI, Caisse station, etc.)
    - Modes de paiement acceptés (espèces, chèque, virement, mobile money, carte bancaire)
    - Gestion des assurances
    - Suivi des incidents de sécurité

## Livrables
- Interface d'administration des stations
- Gestion des cuves avec barème de jauge
- Interface de gestion des carburants
- Interface de gestion des pistolets
- Interface de gestion des produits et familles
- Interface de gestion des fournisseurs
- Interface de gestion des clients
- Interface de gestion des employés
- Interface de gestion des trésoreries

## Tests
- Tests unitaires pour chaque entité
- Tests d'intégration des relations entre entités
- Tests de validation des données
- Tests d'interface utilisateur