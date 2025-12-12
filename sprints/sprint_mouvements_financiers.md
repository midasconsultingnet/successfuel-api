# Sprint: Module Mouvements Financiers

## Objectif
Implémenter la gestion complète des mouvements financiers (règlements de dettes, recouvrements de créances, opérations diverses, avoirs, pénalités) avec mise à jour des soldes dans le module Tiers, y compris les employés, et intégration avec les trésoreries et les états financiers.

## Spécifications détaillées

### 1. Gestion des règlements de dettes
- Création, modification et suppression de règlements
- Champs: tiers (fournisseur, employé), montant, date, méthode de paiement, statut, numéro pièce comptable, date échéance, pénalités éventuelles
- Historique des paiements par tiers
- Suivi des échéances
- Workflow de validation pour les montants supérieurs à un seuil défini

### 2. Gestion des recouvrements de créances
- Création, modification et suppression de recouvrements
- Champs: tiers (client, employé), montant, date, méthode de paiement, statut, numéro pièce comptable, date échéance, pénalités éventuelles
- Historique des paiements par tiers
- Suivi des créances en retard
- Système de relances automatiques selon les seuils configurés

### 3. Gestion des avoirs et notes de crédit
- Création, modification et suppression d'avoirs
- Champs: tiers concerné, montant, motif, date, statut (émis, utilisé, partiellement utilisé, expiré)
- Suivi des avoirs émis et utilisés
- Validation automatique des avoirs lors de transactions futures
- Génération d'avoirs pour les modules Ventes (annulations) et Achats (compensations financières)
- Coordination avec les modules Ventes et Achats pour l'utilisation des avoirs

### 4. Lien avec les tiers
- Association avec les tiers de type fournisseur, client ou employé
- Historique des règlements, recouvrements, avoirs par tiers
- Calcul des soldes nets dans le module Mouvements Financiers
- Mise à jour automatique des soldes dans le module Tiers

### 5. Gestion des échéances et retards
- Identification automatique des factures échéantes
- Système d'alertes (notifications, rappels) avec configuration des seuils
- Historique des paiements effectués
- Calcul et application automatique des pénalités selon les règles configurées

### 6. Impact sur les trésoreries
- Lien avec les trésoreries pour les paiements
- Suivi de l'impact sur les soldes
- Historique des mouvements liés aux règlements et recouvrements
- Génération automatique des écritures de trésorerie

### 7. Gestion des cas spécifiques
- Pompiste avec versement insuffisant : la différence devient une créance employé (gérée via le module Salaires)
- Client avec achat à crédit : génère une créance client
- Client avec paiement anticipé : génère une dette envers le client
- Fournisseur de carburant : peut avoir des relations de créance ou de dette
- Employés : gestion des avances, prêts, retenues de salaire, créances diverses (coordonnée avec le module Salaires)

### 8. Calcul des soldes nets dynamiques
- Chaque tiers a un solde net calculé dynamiquement à partir de l'ensemble de ses transactions
- Le solde net = Σ(mouvements de trésorerie) pour chaque tiers
- Les mouvements peuvent être des créances (positifs) ou des dettes (négatives)
- Le solde est mis à jour à chaque nouvelle transaction liée au tiers
- Calcul des sous-totaux par type de mouvement
- Mise à jour automatique des soldes dans le module Tiers

### 9. Intégration avec les autres modules
- Intégration avec le module Tiers pour la gestion des soldes
- Intégration avec le module Trésoreries pour les impacts financiers
- Intégration avec le module États, Bilans et Comptabilité pour les rapports
- Intégration avec le module Salaires pour la gestion des créances employés
- Intégration avec le module Achats pour les compensations financières
- Intégration avec le module Ventes pour les avoirs d'annulation

### 10. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes
- Contrôles supplémentaires pour les montants élevés ou les modifications sensibles

## Livrables
- API RESTful pour la gestion des règlements de dettes
- API RESTful pour la gestion des recouvrements de créances
- API RESTful pour la gestion des avoirs et notes de crédit
- Modèles de données pour les règlements, recouvrements, avoirs et mouvements
- Interface d'administration des règlements, recouvrements et avoirs
- Système de suivi des échéances et créances en retard
- Système de gestion des pénalités et frais
- Système de gestion des avoirs et notes de crédit
- Système de liaison avec les trésoreries
- Système de mise à jour des soldes tiers
- Système d'intégration avec les modules Tiers, Trésoreries, États Bilans et Salaires
- Tests unitaires et d'intégration