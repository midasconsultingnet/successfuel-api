# Sprint: Module Achats Boutique

## Objectif
Implémenter la gestion complète des achats boutique auprès des tiers, incluant la gestion des commandes, réceptions, factures, paiements, écarts et les règles de paiement paramétrables. Le module gère l'approvisionnement des produits boutique, gaz, lubrifiants, accessoires, boissons, cigarettes avec une flexibilité maximale dans les conditions de paiement.

## Spécifications détaillées

### 1. Gestion des demandes d'achat
- Création, modification et suppression de demandes d'achat
- Champs: produits nécessaires, quantités, date de besoin, urgence
- La station est automatiquement déterminée selon l'utilisateur connecté
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Statuts: en attente, approuvée, rejetée
- Indicateurs: traitée (lorsqu'une commande a été créée à partir de la demande)

### 2. Gestion des commandes
- Création, modification et suppression des commandes à partir de demandes approuvées
- Champs: tiers, date_commande, date_livraison_prévue
- La station est automatiquement déterminée selon l'utilisateur connecté
- Détails des commandes: produit, quantité_demandée, prix_unitaire_demandé, montant
- Conditions de paiement paramétrées par tiers (prépayé, COD, différé, consignation, mixte)
- Statuts: brouillon, confirmée, en_cours, reçue, terminée
- Indicateurs: facturé, payé, en_retard (basés sur les dates et conditions de paiement)
- Actions possibles selon le statut:
  - brouillon: créer/modifier/supprimer la commande, valider/annuler la commande
  - confirmée: modifier certains détails, annuler la commande, envoyer au tiers
  - en_cours: suivre l'expédition, mettre à jour les informations de livraison
  - reçue: valider la quantité/qualité, générer la facture, mettre à jour les stocks, signaler des écarts
  - terminée: accès en lecture seule, consultation historique
- Suivi des quantités et prix:
  - Quantité commandée, quantité reçue, quantité facturée
  - Prix unitaire commandé, prix unitaire facturé
  - Calcul automatique des montants
  - Historique des prix d'achat par produit et tiers
  - Gestion des écarts de prix

### 3. Paramétrage souple du système
#### 3.1 Paramètres par tiers
- Type de paiement (prépayé, COD, différé, consignation, mixte, partiel)
- Délai de paiement (7j, 15j, 30j, 60j)
- Pourcentage d'acompte (ex: 30% avant livraison)
- Limite de crédit
- Mode de règlement accepté (cash, chèque, virement, mobile money)
- Documents requis (bon de commande, facture, etc.)
- Configuration spécifique selon le type de produit (boutique, gaz, lubrifiant)
- Règles de stock minimum/maximum
- Fréquence d'approvisionnement
- Limites de budget et de stock par station
- Niveaux de validation internes

### 4. Gestion des types de paiement
#### 4.1 Paiement à l'avance (Prépayé)
- Paiement avant toute livraison
- Nécessite une facture proforma ou un devis
- Stock livré uniquement après confirmation du paiement

#### 4.2 Paiement à la livraison (Cash On Delivery - COD)
- Paiement au moment de la livraison
- Aucun crédit tiers
- Paiement rattaché directement à la réception + facture immédiate

#### 4.3 Paiement après livraison (Paiement différé)
- Délai accordé (7j / 15j / 30j / 60j)
- Stock reçu avant paiement
- Création automatique d'une dette tiers dans l'ERP

#### 4.4 Paiement partiel (Acompte + Solde)
- Exemple : 30% avant livraison, 70% après réception
- Gestion de plusieurs échéances (acomptes, paiements restants)
- Rapprochement automatique

#### 4.5 Paiement programmé / récurrent
- Paiements planifiés selon calendrier régulier
- Utilisé pour produits récurrents (boissons, eau, gaz)

#### 4.6 Paiement en consignation (surtout Gaz)
- Stock déposé en station par le tiers
- Paiement en fonction des ventes réelles
- Le stock reste propriété du tiers jusqu'à la vente
- Factures générées automatiquement selon les sorties

### 5. Suivi des paiements
- Historique des paiements pour chaque commande
- Détails des paiements: date, montant, méthode de paiement, numéro de transaction
- Gestion des paiements partiels et complets
- Échéances de paiement basées sur les conditions de paiement
- Notifications automatiques pour les paiements en retard
- Relances automatiques selon les paramètres de retard
- Pièces justificatives des paiements (reçus, virements, chèques numérisés)
- Lien avec le module Mouvements Financiers pour les règlements de dettes

### 6. Lien avec les tiers
- Association avec les tiers de type fournisseur
- Historique des achats par tiers
- Calcul des montants dus (uniquement pour les tiers avec crédit)

### 7. Lien avec les produits et stations
- Association avec les produits boutique, gaz, lubrifiants
- Association avec la station concernée
- Validation de la disponibilité du produit dans la station
- Gestion des seuils minimums de stock

### 8. Workflow de réception
- Contrôle qualité, quantité, dates, prix facturé
- Gestion des livraisons partielles ou surplus
- Validation de la livraison (quantité et qualité)
- Mise à jour des quantités réellement reçues
- Intégration avec les documents
  - Numéro de bon de commande (BC)
  - Numéro de bon de livraison (BL)
  - Numéro de facture
  - Date de facturation
  - Lien avec les documents originaux (futur support de pièces jointes)
  - Rapprochement BC → réception → facture


### 9. Gestion des mouvements de trésorerie
- Sortie de trésorerie selon le type de paiement
- Intégration avec le module Trésoreries
- Gestion des rendus en trésorerie selon les conditions de livraison

### 10. Mise à jour des stocks et coûts
- Mise à jour automatique des stocks après validation de la réception
- Impact sur le coût moyen du produit
- Historique des mouvements de stock
- Calcul automatique des coûts après chaque mouvement

### 11. Gestion des écarts et exceptions
#### 11.1 Écarts de quantité
- Surplus, manquants, livraison partielle, substitution produit
- Traitement automatique selon seuils paramétrés

#### 11.2 Écarts de prix
- Prix livré ≠ prix commandé
- Facturation incorrecte
- Non-respect d'une remise tiers

#### 11.3 Qualité non conforme
- Produit endommagé, carton ouvert, produit périmé ou proche de la date

#### 11.4 Gestion des corrections
- Refus partiel ou total de la livraison
- Ajustement du stock
- Émission d'une réclamation tiers
- Avoir tiers
- Réédition de facture

#### 11.5 Gestion de la compensation financière
- Création automatique d'avoirs/notes de crédit suite aux écarts entre théorique et réel
- Si montant réel < montant payé → avoir reçu du tiers
- Si montant réel > montant payé → avoir dû au tiers
- Mise à jour automatique du solde du tiers
- Historique des avoirs dans une table dédiée
- Traçabilité des ajustements financiers

### 12. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes
- Contrôles selon le RBAC (demande d'achat, validation, commande, réception, paiement)
- Journalisation complète pour l'audit interne, y compris les changements de statut
- Reportings sur les écarts et exceptions
- Suivi des indicateurs facturé, payé, en_retard
- Système de rapprochement automatique entre BC, réception, facture et paiement

## Livrables
- API RESTful pour la gestion des demandes d'achat
- API RESTful pour la gestion des commandes
- API RESTful pour la gestion des réceptions
- API RESTful pour la gestion des écarts de livraison
- API RESTful pour la gestion des avoirs et retours
- API RESTful pour le suivi des paiements
- Modèles de données pour les achats, les avoirs, les mouvements de stock et leurs détails
- Interface d'administration complète pour les achats boutique
- Système d'intégration avec le stock boutique
- Système de gestion des compensations financières
- Système de gestion des mouvements de trésorerie
- Système de paramétrage souple par tiers
- Calcul automatique des impacts sur le stock et le coût moyen
- Système de gestion des types de paiement multiples
- Système de rapprochement BC/réception/facture/paiement
- Système d'audit et de reporting
- Tests unitaires et d'intégration