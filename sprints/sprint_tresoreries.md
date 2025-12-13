# Sprint: Module Trésoreries

## Objectif
Implémenter la gestion des trésoreries (caisse, banque, coffre, fonds divers) globales à la compagnie, avec suivi des soldes initiaux.

## Contexte
Dans le système, la trésorerie représente un **moyen de paiement** ou un **compte de liquidités** utilisé par la compagnie et ses stations-service.

Une compagnie peut disposer de plusieurs trésoreries globales :
- Caisse
- Mobile money
- Banque
- Note de crédits
- Coffre
- Fonds divers
- Configuration des paramètres spécifiques par type

Chaque trésorerie appartient à la **compagnie**, et non à une station.
Chaque trésorerie station possède son propre solde initial.

## Spécifications détaillées

### 1. Types de trésoreries
- Caisse principale
- Banque (comptes bancaires)
- Mobile Money
- Note de crédits
- Coffre-fort
- Fonds divers
- Configuration des paramètres spécifiques par type

### 1.1 Trésoreries station
- Chaque trésorerie globale est instanciée pour chaque station
- Chaque trésorerie station possède son propre solde initial
- Les trésoreries station permettent un suivi précis par station

### 2. Paramétrage des trésoreries
- Création, modification et suppression des trésoreries
- Champs: nom, type, solde initial, statut
- Configuration des informations bancaires (pour les comptes bancaires)
- Validation de l'unicité du nom par type
- Gestion des méthodes de paiement associées à chaque trésorerie
- Configuration des méthodes de paiement spécifiques par type de trésorerie
- Activation/désactivation des méthodes de paiement
- Gestion des droits d'accès aux méthodes de paiement par utilisateur

### 3. Soldes initiaux
- Saisie du solde initial pour chaque trésorerie station
- Validation du solde initial
- Création des écritures comptables de départ
- Historique des soldes initiaux via la table `etat_initial_tresorerie` qui enregistre la situation exacte de départ de chaque trésorerie
- Le solde de départ pour tous les mouvements de trésorerie est établi à partir de cette table
- Uniquement une seule entrée par trésorerie station autorisée dans la table `etat_initial_tresorerie`

### 4. Transferts entre trésoreries
- Création, modification et suppression de transferts entre trésoreries
- Champs: trésorerie source, trésorerie destination, montant, date, description
- Validation que la trésorerie source a un solde suffisant
- Mise à jour automatique des soldes des deux trésoreries concernées
- Historique des transferts pour chaque trésorerie
- Génération d'une écriture comptable (double entrée) pour chaque transfert

### 5. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations

## Nouvelle approche technique

### 1. Structure de base de données optimisée

#### A. Tables principales
- **tresorerie**: Trésorerie globale par type (caisse, banque, etc.)
  - id: UUID
  - nom: VARCHAR(255)
  - type: VARCHAR(50) (caisse, banque, mobile_money, note_credit, coffre, fonds_divers)
  - solde_initial: DECIMAL(15,2)
  - devise: VARCHAR(10) DEFAULT 'XOF'
  - informations_bancaires: JSONB
  - statut: VARCHAR(20) DEFAULT 'actif'
  - created_at, updated_at: TIMESTAMP

- **tresorerie_station**: Instance de trésorerie par station
  - id: UUID
  - trésorerie_id: UUID (référence à tresorerie)
  - station_id: UUID (référence à station)
  - solde_initial: DECIMAL(15,2)
  - solde_actuel: DECIMAL(15,2) DEFAULT 0
  - created_at: TIMESTAMP

- **etat_initial_tresorerie**: Historique des soldes initiaux
  - id: UUID
  - tresorerie_station_id: UUID (référence à tresorerie_station)
  - date_enregistrement: DATE
  - montant: DECIMAL(15,2)
  - commentaire: TEXT
  - enregistre_par: UUID (référence à utilisateur)
  - created_at, updated_at: TIMESTAMP
  - CONSTRAINT: unique_solde_initial_par_station

- **mouvement_tresorerie**: Entrées/sorties de fonds
  - id: UUID
  - trésorerie_station_id: UUID (référence à tresorerie_station)
  - type_mouvement: VARCHAR(10) (entrée, sortie)
  - montant: DECIMAL(15,2)
  - date_mouvement: TIMESTAMP
  - description: TEXT
  - module_origine: VARCHAR(100)
  - reference_origine: VARCHAR(100)
  - utilisateur_id: UUID (référence à utilisateur)
  - numero_piece_comptable: VARCHAR(50)
  - statut: VARCHAR(20) DEFAULT 'validé' (validé, annulé)

- **transfert_tresorerie**: Transferts entre trésoreries
  - id: UUID
  - trésorerie_source_id: UUID (référence à tresorerie_station)
  - trésorerie_destination_id: UUID (référence à tresorerie_station)
  - montant: DECIMAL(15,2)
  - date_transfert: TIMESTAMP
  - description: TEXT
  - utilisateur_id: UUID (référence à utilisateur)
  - statut: VARCHAR(20) DEFAULT 'validé' (validé, annulé)

#### B. Améliorations apportées
- Ajout de contraintes pour garantir l'unicité d'un solde initial par trésorerie station
- Ajout d'index sur `(trésorerie_station_id, statut, date_mouvement)` pour la table `mouvement_tresorerie`
- Ajout d'index sur `(date_transfert, statut)` pour la table `transfert_tresorerie`

### 2. Calcul et synchronisation des soldes

#### A. Approche hybride
- Maintien de la colonne `solde_actuel` pour des opérations rapides
- Création d'une vue matérialisée `vue_materia_sldes_tresorerie` pour les rapports et analyses
- Calcul en temps réel pour vérification : `solde_initial + Σ(entrées) - Σ(sorties) + Σ(recus) - Σ(envoyes)`
- Fonction `mettre_a_jour_solde_tresorerie()` pour le calcul et la mise à jour du solde

#### B. Calcul du solde
Le solde actuel de chaque trésorerie station est calculé comme suit :
```
solde_actuel = solde_initial + Σ(montants des mouvements "entrée") - Σ(montants des mouvements "sortie") 
             + Σ(montants reçus en transfert) - Σ(montants envoyés en transfert)
```

### 3. Gestion des données

#### A. Procédures pour la gestion des soldes
- Création de la fonction PostgreSQL `enregistrer_mouvement_trésorerie()` pour gérer les mouvements
- Mise en place de triggers pour maintenir la cohérence
- Validation automatique des soldes avant les opérations de sortie

#### B. Gestion des transferts
- Lors d'un transfert, deux mouvements sont automatiquement créés :
  - Un mouvement de "sortie" dans la trésorerie source
  - Un mouvement d'"entrée" dans la trésorerie destination
- Numérotation automatique des références (TRANS-{id_transfert})

### 4. Contrôles et vérifications

#### A. Mécanismes de vérification
- Fonction `verifier_soldes_tresorerie()` pour détecter les écarts entre solde réel et enregistré
- Tolérance de 0.01 pour les arrondis
- Mise en place de tâches planifiées pour la vérification périodique

#### B. Contrôles de sécurité
- Vérification que les trésoreries appartiennent à la même compagnie
- Contrôle d'accès basé sur l'appartenance à la compagnie
- Historique conservé même lors des suppressions (statut "supprimé")

### 5. API RESTful

#### A. Endpoints implémentés
- `/tresoreries` : Gestion des trésoreries globales
- `/tresoreries-station` : Gestion des trésoreries par station
- `/etats-initiaux` : Gestion des soldes initiaux
- `/mouvements` : Gestion des entrées/sorties
- `/transferts` : Gestion des transferts entre trésoreries

#### B. Fonctionnalités
- Validation des données entrantes
- Contrôle des permissions
- Calcul automatique des soldes
- Historique des opérations

## Livrables
- API RESTful pour la gestion des trésoreries
- Modèles de données pour les trésoreries
- Interface d'administration des trésoreries
- Système de configuration des soldes initiaux
- Système de transfert entre trésoreries
- Tests unitaires et d'intégration