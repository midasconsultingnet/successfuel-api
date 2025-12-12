# Modèle de données - Module Structure de la Compagnie

## Entités principales

### Compagnie
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - pays_id (UUID, référence à la table Pays)
  - adresse (string)
  - telephone (string)
  - email (string)
  - devise (string, default "XOF")
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - 1..* avec Station
  - 1..* avec Utilisateur (un utilisateur appartient à une seule compagnie)
  - 1..* avec Tiers (Clients, Fournisseurs, Employés)
  - 1..* avec Trésorerie

### Station
- **Champs**:
  - id (UUID)
  - compagnie_id (UUID, référence à Compagnie)
  - nom (string, obligatoire)
  - code (string, obligatoire, unique par compagnie)
  - adresse (string)
  - coordonnees_gps (jsonb: {lat: float, lng: float})
  - statut (string: "actif", "inactif", default "actif")
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Compagnie
  - 1..* avec Cuve
  - 1..* avec Immobilisation
  - 1..* avec Trésorerie_Station
  - 1..* avec Produit
  - 1..* avec Affectation_Utilisateur_Station

### Cuve
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - nom (string, obligatoire)
  - code (string, obligatoire)
  - capacite_maximale (float, obligatoire)
  - niveau_actuel (float, default 0)
  - carburant_id (UUID, référence à Carburant)
  - statut (string: "actif", "inactif", default "actif")
  - barremage (jsonb: [{hauteur_cm: float, volume_litre: float}, ...])
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Carburant
  - 1..* avec Mouvement_Stock_Cuve (via module Livraisons et Ventes Carburant)
  - 1..* avec Pistolet (via module Ventes Carburant)

### Pistolet
- **Champs**:
  - id (UUID)
  - cuve_id (UUID, référence à Cuve)
  - numero (string, obligatoire)
  - statut (string: "actif", "inactif", "maintenance", default "actif")
  - index_initial (float, default 0)
  - index_final (float)
  - date_derniere_utilisation (datetime)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Cuve
  - 1..* avec Vente_Carburant

## Relations avec d'autres modules
- **Module Tiers**: Les employés de la station sont des tiers de type employé
- **Module Trésoreries**: Chaque station a des trésoreries associées
- **Module Produits et Stocks**: Les produits sont associés à une station
- **Module Utilisateurs**: Les utilisateurs appartiennent à une compagnie et sont affectés aux stations
- **Module Immobilisations**: Les immobilisations sont affectées à une station
- **Module Ventes Carburant**: Les pistolets sont utilisés pour les ventes de carburant
- **Module Livraisons Carburant**: Les cuves reçoivent des livraisons de carburant

## Contraintes d'intégrité
- Le code de la station doit être unique par compagnie
- Une cuve appartient à une seule station
- Une cuve ne peut stocker qu'un seul type de carburant
- Le niveau actuel d'une cuve ne peut pas dépasser sa capacité maximale
- L'index final d'un pistolet doit être supérieur ou égal à l'index initial