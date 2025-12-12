# Modèle de données - Module Trésoreries

## Entités principales

### Trésorerie
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - type (string: "caisse", "banque", "mobile_money", "note_credit", "coffre", "fonds_divers", obligatoire)
  - solde_initial (decimal, obligatoire)
  - devise (string, default "XOF")
  - informations_bancaires (jsonb: {banque: string, compte: string, etc.}, optionnel)
  - statut (string: "actif", "inactif", default "actif")
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - 1..* avec Trésorerie_Station
  - 1..* avec Mouvement_Tresorerie

### Trésorerie_Station
- **Champs**:
  - id (UUID)
  - trésorerie_id (UUID, référence à Trésorerie)
  - station_id (UUID, référence à Station)
  - solde_initial (decimal, obligatoire)
  - solde_actuel (decimal, calculé)
  - date_creation (datetime)

- **Relations**:
  - N..1 avec Trésorerie
  - N..1 avec Station
  - 1..* avec Mouvement_Tresorerie

### Mouvement_Tresorerie
- **Champs**:
  - id (UUID)
  - trésorerie_station_id (UUID, référence à Trésorerie_Station)
  - type_mouvement (string: "entrée", "sortie", obligatoire)
  - montant (decimal, obligatoire)
  - date_mouvement (datetime, obligatoire)
  - description (text)
  - module_origine (string, obligatoire)
  - reference_origine (string, obligatoire)
  - utilisateur_id (UUID, référence à Utilisateur)
  - numero_piece_comptable (string)
  - statut (string: "validé", "annulé", default "validé")

- **Relations**:
  - N..1 avec Trésorerie_Station
  - N..1 avec Utilisateur

### Transfert_Tresorerie
- **Champs**:
  - id (UUID)
  - trésorerie_source_id (UUID, référence à Trésorerie_Station)
  - trésorerie_destination_id (UUID, référence à Trésorerie_Station)
  - montant (decimal, obligatoire)
  - date_transfert (datetime, obligatoire)
  - description (text)
  - utilisateur_id (UUID, référence à Utilisateur)
  - statut (string: "validé", "annulé", default "validé")

- **Relations**:
  - N..1 avec Trésorerie_Station (source)
  - N..1 avec Trésorerie_Station (destination)
  - N..1 avec Utilisateur

## Relations avec d'autres modules
- **Module Structure de la Compagnie**: Trésorerie_Station liée à Station
- **Module Utilisateurs**: Utilisateur effectue les mouvements et transferts
- **Module Ventes Boutique**: Les ventes affectent les trésoreries
- **Module Ventes Carburant**: Les ventes affectent les trésoreries
- **Module Achats Boutique**: Les achats affectent les trésoreries
- **Module Achats Carburant**: Les achats affectent les trésoreries
- **Module Salaires**: Les paiements de salaires affectent les trésoreries
- **Module Charges de Fonctionnement**: Les paiements affectent les trésoreries
- **Module Mouvements Financiers**: Les règlements affectent les trésoreries

## Contraintes d'intégrité
- Le solde d'une trésorerie ne peut pas être négatif sauf si spécifiquement autorisé
- Dans un transfert, la trésorerie source et destination doivent être différentes
- Le montant d'un transfert ne peut pas dépasser le solde disponible de la trésorerie source
- Les mouvements sont liés à une trésorerie station spécifique et non à une trésorerie globale

## Vues de reporting

### vue_mouvements_tresorerie
- **Description**: Vue consolidée des mouvements de trésorerie avec détails des stations, trésoreries et utilisateurs
- **Jointures**:
  - mouvement_tresorerie JOIN trésorerie_station ON (mouvement_tresorerie.trésorerie_station_id = trésorerie_station.id)
  - trésorerie_station JOIN trésorerie ON (trésorerie_station.trésorerie_id = trésorerie.id)
  - trésorerie_station JOIN station ON (trésorerie_station.station_id = station.id)
  - mouvement_tresorerie JOIN utilisateur ON (mouvement_tresorerie.utilisateur_id = utilisateur.id)
- **Champs**:
  - mt.id
  - mt.trésorerie_station_id
  - trs.nom AS trésorerie_nom
  - st.nom AS station_nom
  - mt.type_mouvement
  - mt.montant
  - mt.date_mouvement
  - mt.description
  - mt.module_origine
  - mt.reference_origine
  - mt.utilisateur_id
  - u.nom AS utilisateur_nom
  - u.prenom AS utilisateur_prenom
  - mt.numero_piece_comptable
  - mt.statut