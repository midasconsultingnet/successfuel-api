# Modèle de données - Module Immobilisations

## Entités principales

### Immobilisation
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - description (text)
  - code (string, obligatoire)
  - type (string: "matériel", "véhicule", "bâtiment", "informatique", etc., obligatoire)
  - date_acquisition (date, obligatoire)
  - valeur_origine (decimal, obligatoire)
  - valeur_nette (decimal, calculé)
  - taux_amortissement (decimal, optionnel)
  - duree_vie (integer, en années, optionnel)
  - statut (string: "actif", "inactif", "cessionné", "hors_service", default "actif")
  - station_id (UUID, référence à Station)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - 1..* avec Mouvement_Immobilisation

### Mouvement_Immobilisation
- **Champs**:
  - id (UUID)
  - immobilisation_id (UUID, référence à Immobilisation)
  - type_mouvement (string: "acquisition", "amélioration", "cession", "sortie", "amortissement", obligatoire)
  - date_mouvement (datetime, obligatoire)
  - description (text)
  - valeur_variation (decimal, positif ou négatif)
  - valeur_apres_mouvement (decimal, calculé)
  - utilisateur_id (UUID, référence à Utilisateur)
  - reference_document (string)
  - statut (string: "validé", "annulé", default "validé")

- **Relations**:
  - N..1 avec Immobilisation
  - N..1 avec Utilisateur

### Historique_Affectation_Immobilisation
- **Champs**:
  - id (UUID)
  - immobilisation_id (UUID, référence à Immobilisation)
  - station_origine_id (UUID, référence à Station)
  - station_destination_id (UUID, référence à Station)
  - date_affectation (datetime, obligatoire)
  - motif_affectation (text)
  - utilisateur_id (UUID, référence à Utilisateur)

- **Relations**:
  - N..1 avec Immobilisation
  - N..1 avec Station (station_origine_id)
  - N..1 avec Station (station_destination_id)
  - N..1 avec Utilisateur

## Relations avec d'autres modules
- **Module Structure de la Compagnie**: Les immobilisations sont affectées à une station
- **Module Utilisateurs**: Les utilisateurs effectuent les mouvements d'immobilisation
- **Module États, Bilans et Comptabilité**: Pour les rapports d'immobilisations
- **Module Tiers**: Pour les fournisseurs d'immobilisations (dans le cadre des achats)

## Contraintes d'intégrité
- Une immobilisation est affectée à une seule station à la fois
- L'historique des affectations est conservé pour chaque immobilisation
- La valeur nette d'une immobilisation ne peut pas être négative
- Les mouvements d'immobilisation affectent la valeur nette de l'immobilisation
- Une immobilisation ne peut être affectée qu'à une seule station à la fois