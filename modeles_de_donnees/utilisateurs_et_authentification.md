# Modèle de données - Module Utilisateurs et Authentification

## Entités principales

### Utilisateur
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - prénom (string, obligatoire)
  - email (string, obligatoire, unique)
  - login (string, obligatoire, unique)
  - mot_de_passe_hash (string, obligatoire)
  - role (string: "gerant_compagnie" ou "utilisateur_compagnie", obligatoire)
  - date_creation (datetime)
  - date_modification (datetime)
  - date_derniere_connexion (datetime, optionnel)
  - actif (boolean, default true)

- **Relations**:
  - 1..* avec Station (via table intermédiaire: affectation_utilisateur_station)
  - 1..1 avec Compagnie

### Affectation_Utilisateur_Station
- **Champs**:
  - id (UUID)
  - utilisateur_id (UUID, référence à Utilisateur)
  - station_id (UUID, référence à Station)
  - date_affectation (datetime)

- **Relations**:
  - N..1 avec Utilisateur
  - N..1 avec Station

### Token_Session
- **Champs**:
  - id (UUID)
  - utilisateur_id (UUID, référence à Utilisateur)
  - token (string, obligatoire)
  - token_refresh (string, obligatoire)
  - date_expiration (datetime, obligatoire)
  - date_creation (datetime)
  - actif (boolean, default true)

- **Relations**:
  - N..1 avec Utilisateur

### Journal_Action_Utilisateur
- **Champs**:
  - id (UUID)
  - utilisateur_id (UUID, référence à Utilisateur)
  - date_action (datetime, obligatoire)
  - type_action (string, obligatoire)
  - module_concerne (string, obligatoire)
  - donnees_avant (jsonb, optionnel)
  - donnees_apres (jsonb, optionnel)
  - ip_utilisateur (string)
  - user_agent (string)

- **Relations**:
  - N..1 avec Utilisateur

## Relations avec d'autres modules
- **Module Structure de la Compagnie**: Relation 1..1 avec Compagnie, relations N..* avec Station
- **Tous les modules**: Journalisation des actions via Journal_Action_Utilisateur

## Contraintes d'intégrité
- Un utilisateur ne peut appartenir qu'à une seule compagnie
- Un utilisateur ne peut être affecté qu'une fois à une station spécifique
- L'email de l'utilisateur doit être unique
- Un utilisateur ne peut accéder qu'aux données des stations auxquelles il est affecté