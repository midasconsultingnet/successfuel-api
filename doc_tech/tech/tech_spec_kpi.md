# Technical Specification - Module de Gestion des Indicateurs de Performance (KPIs)

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de gestion des indicateurs de performance (KPIs) permet de suivre, analyser et prévoir les performances opérationnelles, fiscales, réglementaires et commerciales d'une station-service. Il fournit des outils d'analyse avancée pour optimiser les opérations, garantir la conformité, gérer les risques et améliorer les relations avec les clients. Le module permet de créer, calculer, surveiller et analyser un large éventail d'indicateurs clés de performance.

### Problème à résoudre
Sans un module dédié à la gestion des indicateurs de performance, les stations-service ne pourraient pas:
- Suivre efficacement leurs performances opérationnelles
- Respecter les obligations fiscales et réglementaires
- Identifier et gérer les risques opérationnels
- Optimiser leur performance commerciale
- Suivre l'efficacité de leur gestion de carburant
- Mettre en place des contrôles internes appropriés
- Gérer efficacement les relations clients
- Prendre des décisions éclairées basées sur des données précises

### Définition du périmètre
Le périmètre du sprint couvre:
- KPIs opérationnels (litres vendus, marge brute, rendement pompiste)
- Gestion fiscale et réglementaire
- Gestion des risques opérationnels
- Analyse et prévision commerciale
- Gestion des services annexes
- Gestion des contrôles internes
- Gestion des relations clients avancées
- Optimisation de la gestion de carburant

## 2. User Stories & Critères d'acceptation

### US-KPI-001: En tant que gestionnaire, je veux calculer les KPIs opérationnels
**Critères d'acceptation :**
- Calcul des litres vendus par type de carburant
- Calcul de la marge brute par produit
- Calcul de l'indicateur de rendement des pompistes
- Calcul de l'indicateur de productivité
- Affichage des analyses comparatives
- Export des données pour analyse
- Suivi évolutif des KPIs

### US-KPI-002: En tant que gestionnaire, je veux gérer les obligations fiscales
**Critères d'acceptation :**
- Calcul automatique de la TVA et autres taxes
- Intégration des obligations de déclaration
- Génération préparatoire des rapports fiscaux
- Suivi des échéances fiscales
- Alertes pour les obligations en retard
- Historique des déclarations

### US-KPI-003: En tant que gestionnaire, je veux suivre la conformité réglementaire
**Critères d'acceptation :**
- Suivi des normes de sécurité
- Suivi des réglementations applicables
- Génération des rapports exigés par les autorités
- Alertes de non-conformité
- Historique des contrôles
- Documentation des actions correctives

### US-KPI-004: En tant que gestionnaire, je veux gérer les risques opérationnels
**Critères d'acceptation :**
- Suivi des écarts anormaux
- Gestion des assurances
- Suivi des incidents de sécurité
- Contrôle des accès aux cuves et pompes
- Analyse des tendances de risque
- Alertes automatiques pour les seuils critiques

### US-KPI-005: En tant que gestionnaire, je veux faire de l'analyse et prévision commerciale
**Critères d'acceptation :**
- Analyse des tendances de vente
- Prévision de la demande
- Optimisation des prix
- Analyse de la clientèle fidèle vs occasionnelle
- Modèles de prévision configurables
- Représentation graphique des tendances

### US-KPI-006: En tant que gestionnaire, je veux gérer les services annexes
**Critères d'acceptation :**
- Gestion des services de station-service
- Comptabilisation des services rendus
- Suivi des contrats de maintenance
- Calcul des revenus des services
- Analyse de la rentabilité des services
- Historique des services rendus

### US-KPI-007: En tant que gestionnaire, je veux gérer les contrôles internes
**Critères d'acceptation :**
- Contrôle des écarts de caisse automatiques
- Suivi des opérations suspectes
- Validation hiérarchisée des transactions importantes
- Journalisation des modifications critiques
- Alertes de contrôle interne
- Rapports de conformité interne

### US-KPI-008: En tant que gestionnaire, je veux gérer les relations clients avancées
**Critères d'acceptation :**
- Programmes de fidélisation
- Cartes de carburant
- Contrats de ravitaillement à long terme
- Système de notation des clients
- Analyse du comportement des clients
- Suivi des préférences client

### US-KPI-009: En tant que gestionnaire, je veux optimiser la gestion de carburant
**Critères d'acceptation :**
- Suivi des températures pour correction volumétrique
- Gestion des mélanges d'additifs
- Suivi de la qualité du carburant
- Analyse des coûts de transport et de stockage
- Indicateurs de performance de la gestion de carburant
- Suivi des pertes et gains de carburant

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `utilisateurs` - données des utilisateurs
- `stations` - données des stations
- `carburants` - données des carburants
- `pompistes` - données des pompistes
- `ventes` - données des ventes
- `achats` - données des achats
- `stocks` - données des stocks
- `ecritures_comptables` - données des écritures comptables
- `clients` - données des clients
- `fournisseurs` - données des fournisseurs
- `cuves` - données des cuves
- `pistolets` - données des pistolets
- `articles` - données des articles de boutique
- `tresoreries` - données des trésoreries
- `mode_paiements` - données des modes de paiement
- `contrats_ravitaillement` - données des contrats de ravitaillement
- `cartes_carburant` - données des cartes de carburant
- `programmes_fidelite` - données des programmes de fidélisation

### Nouvelles tables à créer

```sql
-- Table pour les indicateurs de performance (KPIs)
CREATE TABLE IF NOT EXISTS indicateurs_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_kpi VARCHAR(50) UNIQUE NOT NULL,
    libelle_kpi VARCHAR(100) NOT NULL,
    description TEXT,
    categorie_kpi VARCHAR(50) NOT NULL, -- 'operationnel', 'commercial', 'financier', 'logistique', 'fiscal', etc.
    unite_mesure VARCHAR(20), -- '%', 'litres', 'ariary', 'nombre', etc.
    calcul_kpi TEXT, -- Expression SQL ou formule de calcul
    seuil_alerte_bas NUMERIC(18,4), -- Seuil bas d'alerte
    seuil_alerte_haut NUMERIC(18,4), -- Seuil haut d'alerte
    statut VARCHAR(15) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Archive')),
    est_personnalise BOOLEAN DEFAULT FALSE, -- TRUE si KPI personnalisé
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les valeurs des indicateurs de performance
CREATE TABLE IF NOT EXISTS valeurs_indicateurs_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicateur_kpi_id UUID REFERENCES indicateurs_performance(id),
    valeur NUMERIC(18,4) NOT NULL,
    periode DATE NOT NULL, -- Date de référence pour la valeur
    station_id UUID REFERENCES stations(id),
    utilisateur_calcul_id UUID REFERENCES utilisateurs(id),
    date_calcul TIMESTAMPTZ NOT NULL DEFAULT now(),
    commentaire TEXT,
    est_previsionnel BOOLEAN DEFAULT FALSE,
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les obligations fiscales et réglementaires
CREATE TABLE IF NOT EXISTS obligations_fiscales_reglementaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_obligation VARCHAR(100) NOT NULL, -- 'TVA', 'déclaration fiscale', 'norme sécurité', etc.
    libelle_obligation VARCHAR(200) NOT NULL,
    description TEXT,
    frequence VARCHAR(20) NOT NULL, -- 'mensuelle', 'trimestrielle', 'annuelle'
    periode_obligation DATE NOT NULL, -- Mois/Trimestre/Année concernée
    date_echeance DATE NOT NULL,
    date_realisation DATE,
    utilisateur_responsable_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    statut VARCHAR(20) DEFAULT 'EnAttente' CHECK (statut IN ('EnAttente', 'Ajour', 'Realise', 'EnRetard', 'Exempte')),
    priorite INTEGER DEFAULT 1 CHECK (priorite BETWEEN 1 AND 5), -- 1 = basse, 5 = haute
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi des risques opérationnels
CREATE TABLE IF NOT EXISTS suivi_risques_operationnels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_risque VARCHAR(50) NOT NULL, -- 'ecart_anormal', 'incident_securite', 'assurance', 'acces_non_autorise'
    libelle_risque VARCHAR(100) NOT NULL,
    description TEXT,
    date_detection DATE NOT NULL,
    date_resolution DATE,
    utilisateur_detecteur_id UUID REFERENCES utilisateurs(id),
    utilisateur_traitant_id UUID REFERENCES utilisateurs(id),
    niveau_risque INTEGER CHECK (niveau_risque BETWEEN 1 AND 5), -- 1 = faible, 5 = élevé
    statut VARCHAR(20) DEFAULT 'Detecte' CHECK (statut IN ('Detecte', 'Enquete', 'Traite', 'Ferme', 'EnAttente')),
    impact_potentiel NUMERIC(18,2), -- Estimation de l'impact financier
    probabilite_risque INTEGER CHECK (probabilite_risque BETWEEN 1 AND 5), -- 1 = improbable, 5 = certain
    score_risque NUMERIC(5,2) GENERATED ALWAYS AS (niveau_risque * probabilite_risque) STORED,
    action_corrective TEXT,
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les analyses et prévisions commerciales
CREATE TABLE IF NOT EXISTS analyses_previsions_commerciales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_analyse VARCHAR(50) NOT NULL, -- 'tendance_vente', 'prevision_demande', 'optimisation_prix', 'analyse_client'
    libelle_analyse VARCHAR(100) NOT NULL,
    description TEXT,
    periode_analyse_debut DATE NOT NULL,
    periode_analyse_fin DATE NOT NULL,
    donnees_entrees JSONB, -- Données brutes de l'analyse
    resultats_analyse JSONB, -- Résultats de l'analyse
    interpretations TEXT, -- Interprétations des résultats
    modele_utilise VARCHAR(100), -- Nom du modèle de prévision
    precision_modele NUMERIC(5,2), -- Précision du modèle (en %)
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Termine' CHECK (statut IN ('EnCours', 'Termine', 'Archive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les indicateurs de gestion de carburant
CREATE TABLE IF NOT EXISTS indicateurs_gestion_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_id UUID REFERENCES cuves(id),
    type_indicateur VARCHAR(100) NOT NULL, -- 'temperature_correction', 'qualite_carburant', 'cout_transport', 'cout_stockage', 'pertes_gains'
    libelle_indicateur VARCHAR(100) NOT NULL,
    valeur_indicateur NUMERIC(18,4) NOT NULL,
    unite_mesure VARCHAR(20),
    date_mesure DATE NOT NULL,
    heure_mesure TIME,
    utilisateur_operateur_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les contrôles internes
CREATE TABLE IF NOT EXISTS controles_internes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_controle VARCHAR(100) NOT NULL, -- 'ecart_caisse', 'operation_suspecte', 'modification_critique'
    libelle_controle VARCHAR(100) NOT NULL,
    description TEXT,
    date_controle DATE NOT NULL,
    heure_controle TIME NOT NULL,
    utilisateur_controleur_id UUID REFERENCES utilisateurs(id),
    utilisateur_concerne_id UUID REFERENCES utilisateurs(id), -- Utilisateur concerné par le contrôle
    objet_type VARCHAR(50), -- Type de l'objet contrôlé
    objet_id UUID, -- ID de l'objet contrôlé
    resultat_controle VARCHAR(20) CHECK (resultat_controle IN ('Conforme', 'NonConforme', 'EnAttente')),
    seuil_alerte BOOLEAN DEFAULT FALSE,
    commentaire_controle TEXT,
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Termine', 'Archive')),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi des relations clients avancées
CREATE TABLE IF NOT EXISTS suivi_relations_clients_avancees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    type_relation VARCHAR(100) NOT NULL, -- 'programme_fidelite', 'carte_carburant', 'contrat_ravitaillement', 'notation_client'
    objet_relation_id UUID, -- ID de l'objet spécifique (programme, carte, etc.)
    libelle_relation VARCHAR(100) NOT NULL,
    valeur_relation NUMERIC(18,4),
    unite_mesure VARCHAR(20),
    date_action DATE NOT NULL,
    utilisateur_action_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Resilie')),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les indicateurs de performance
CREATE INDEX IF NOT EXISTS idx_indicateurs_performance_code ON indicateurs_performance(code_kpi);
CREATE INDEX IF NOT EXISTS idx_indicateurs_performance_categorie ON indicateurs_performance(categorie_kpi);
CREATE INDEX IF NOT EXISTS idx_indicateurs_performance_actif ON indicateurs_performance(statut);

-- Index pour les valeurs des indicateurs
CREATE INDEX IF NOT EXISTS idx_valeurs_indicateurs_indicateur ON valeurs_indicateurs_performance(indicateur_kpi_id);
CREATE INDEX IF NOT EXISTS idx_valeurs_indicateurs_periode ON valeurs_indicateurs_performance(periode);
CREATE INDEX IF NOT EXISTS idx_valeurs_indicateurs_station ON valeurs_indicateurs_performance(station_id);

-- Index pour les obligations fiscales et réglementaires
CREATE INDEX IF NOT EXISTS idx_obligations_type ON obligations_fiscales_reglementaires(type_obligation);
CREATE INDEX IF NOT EXISTS idx_obligations_echeance ON obligations_fiscales_reglementaires(date_echeance);
CREATE INDEX IF NOT EXISTS idx_obligations_statut ON obligations_fiscales_reglementaires(statut);

-- Index pour le suivi des risques opérationnels
CREATE INDEX IF NOT EXISTS idx_suivi_risques_type ON suivi_risques_operationnels(type_risque);
CREATE INDEX IF NOT EXISTS idx_suivi_risques_date ON suivi_risques_operationnels(date_detection);
CREATE INDEX IF NOT EXISTS idx_suivi_risques_statut ON suivi_risques_operationnels(statut);

-- Index pour les analyses et prévisions commerciales
CREATE INDEX IF NOT EXISTS idx_analyses_previsions_type ON analyses_previsions_commerciales(type_analyse);
CREATE INDEX IF NOT EXISTS idx_analyses_previsions_periode ON analyses_previsions_commerciales(periode_analyse_debut, periode_analyse_fin);

-- Index pour les indicateurs de gestion de carburant
CREATE INDEX IF NOT EXISTS idx_indicateurs_carburant_cuve ON indicateurs_gestion_carburant(cuve_id);
CREATE INDEX IF NOT EXISTS idx_indicateurs_carburant_type ON indicateurs_gestion_carburant(type_indicateur);
CREATE INDEX IF NOT EXISTS idx_indicateurs_carburant_date ON indicateurs_gestion_carburant(date_mesure);

-- Index pour les contrôles internes
CREATE INDEX IF NOT EXISTS idx_controles_internes_type ON controles_internes(type_controle);
CREATE INDEX IF NOT EXISTS idx_controles_internes_date ON controles_internes(date_controle);
CREATE INDEX IF NOT EXISTS idx_controles_internes_resultat ON controles_internes(resultat_controle);

-- Index pour le suivi des relations clients avancées
CREATE INDEX IF NOT EXISTS idx_suivi_relations_client ON suivi_relations_clients_avancees(client_id);
CREATE INDEX IF NOT EXISTS idx_suivi_relations_type ON suivi_relations_clients_avancees(type_relation);
CREATE INDEX IF NOT EXISTS idx_suivi_relations_date ON suivi_relations_clients_avancees(date_action);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour s'assurer de la cohérence des seuils d'alerte des KPIs
CREATE OR REPLACE FUNCTION validate_seuils_kpi()
RETURNS TRIGGER AS $$
BEGIN
    -- Si les seuils sont définis, vérifier que le seuil bas est inférieur au seuil haut
    IF NEW.seuil_alerte_bas IS NOT NULL AND NEW.seuil_alerte_haut IS NOT NULL THEN
        IF NEW.seuil_alerte_bas > NEW.seuil_alerte_haut THEN
            RAISE EXCEPTION 'Le seuil d''alerte bas doit être inférieur au seuil d''alerte haut';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_seuils_kpi
    BEFORE INSERT OR UPDATE ON indicateurs_performance
    FOR EACH ROW EXECUTE FUNCTION validate_seuils_kpi();

-- Trigger pour calculer automatiquement le score de risque
CREATE OR REPLACE FUNCTION calculate_score_risque()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculer le score de risque comme le produit du niveau et de la probabilité
    NEW.score_risque := NEW.niveau_risque * NEW.probabilite_risque;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_score_risque
    BEFORE INSERT OR UPDATE ON suivi_risques_operationnels
    FOR EACH ROW EXECUTE FUNCTION calculate_score_risque();
```

## 4. API Backend

### 4.1 Gestion des indicateurs de performance

#### POST /api/kpi/indicateurs
**Description:** Créer un nouvel indicateur de performance

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "code_kpi": "string (unique, max 50)",
  "libelle_kpi": "string (max 100)",
  "description": "string (optionnel)",
  "categorie_kpi": "operationnel|commercial|financier|logistique|fiscal|reglementaire",
  "unite_mesure": "string (max 20)",
  "calcul_kpi": "text (requete SQL ou formule)",
  "seuil_alerte_bas": "decimal (optionnel)",
  "seuil_alerte_haut": "decimal (optionnel)",
  "est_personnalise": "boolean (default: false)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code_kpi": "string",
    "libelle_kpi": "string",
    "description": "string",
    "categorie_kpi": "string",
    "unite_mesure": "string",
    "calcul_kpi": "text",
    "seuil_alerte_bas": "decimal (nullable)",
    "seuil_alerte_haut": "decimal (nullable)",
    "statut": "string",
    "est_personnalise": "boolean",
    "utilisateur_createur_id": "uuid",
    "created_at": "datetime"
  },
  "message": "Indicateur de performance créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Indicateur créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 409: Code KPI déjà existant
- 500: Erreur interne du serveur

#### GET /api/kpi/indicateurs
**Description:** Obtenir la liste des indicateurs de performance

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- categorie: string (optionnel)
- statut: Actif|Inactif|Archive (optionnel)
- est_personnalise: boolean (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "indicateurs": [
      {
        "id": "uuid",
        "code_kpi": "string",
        "libelle_kpi": "string",
        "description": "string",
        "categorie_kpi": "string",
        "unite_mesure": "string",
        "seuil_alerte_bas": "decimal (nullable)",
        "seuil_alerte_haut": "decimal (nullable)",
        "statut": "string",
        "est_personnalise": "boolean"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Indicateurs de performance récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

### 4.2 Gestion des valeurs des indicateurs

#### GET /api/kpi/valeurs/{indicateur_id}
**Description:** Obtenir les valeurs d'un indicateur sur une période

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- periode_debut: date (format YYYY-MM-DD)
- periode_fin: date (format YYYY-MM-DD)
- station_id: uuid (optionnel)
- est_previsionnel: boolean (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "kpi": {
      "id": "uuid",
      "code_kpi": "string",
      "libelle_kpi": "string",
      "unite_mesure": "string"
    },
    "valeurs": [
      {
        "id": "uuid",
        "valeur": "decimal",
        "periode": "date",
        "date_calcul": "datetime",
        "commentaire": "string (nullable)",
        "est_previsionnel": "boolean"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Valeurs de l'indicateur récupérées avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Indicateur non trouvé
- 500: Erreur interne du serveur

### 4.3 Gestion des obligations fiscales et réglementaires

#### POST /api/kpi/obligations
**Description:** Créer une nouvelle obligation fiscale ou réglementaire

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_obligation": "string (max 100)",
  "libelle_obligation": "string (max 200)",
  "description": "text (optionnel)",
  "frequence": "mensuelle|trimestrielle|annuelle",
  "periode_obligation": "date (format YYYY-MM-01)",
  "date_echeance": "date (format YYYY-MM-DD)",
  "utilisateur_responsable_id": "uuid (optionnel)",
  "station_id": "uuid",
  "priorite": "integer (1-5, default: 1)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type_obligation": "string",
    "libelle_obligation": "string",
    "description": "text",
    "frequence": "string",
    "periode_obligation": "date",
    "date_echeance": "date",
    "date_realisation": "date (nullable)",
    "utilisateur_responsable_id": "uuid",
    "station_id": "uuid",
    "statut": "string",
    "priorite": "integer",
    "commentaire": "text",
    "created_at": "datetime"
  },
  "message": "Obligation fiscale ou réglementaire créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Obligation créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Utilisateur/station non trouvé
- 500: Erreur interne du serveur

#### GET /api/kpi/obligations
**Description:** Obtenir la liste des obligations fiscales et réglementaires

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- statut: EnAttente|Ajour|Realise|EnRetard|Exempte (optionnel)
- date_echeance_debut: date (format YYYY-MM-DD) (optionnel)
- date_echeance_fin: date (format YYYY-MM-DD) (optionnel)
- station_id: uuid (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "obligations": [
      {
        "id": "uuid",
        "type_obligation": "string",
        "libelle_obligation": "string",
        "frequence": "string",
        "periode_obligation": "date",
        "date_echeance": "date",
        "date_realisation": "date (nullable)",
        "utilisateur_responsable_id": "uuid",
        "station_id": "uuid",
        "statut": "string",
        "priorite": "integer",
        "commentaire": "text"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Obligations fiscales et réglementaires récupérées avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

### 4.4 Gestion des risques opérationnels

#### POST /api/kpi/risques
**Description:** Créer un nouveau suivi de risque opérationnel

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_risque": "ecart_anormal|incident_securite|assurance|acces_non_autorise",
  "libelle_risque": "string (max 100)",
  "description": "text (optionnel)",
  "niveau_risque": "integer (1-5)",
  "probabilite_risque": "integer (1-5)",
  "station_id": "uuid",
  "commentaire": "text (optionnel)",
  "action_corrective": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type_risque": "string",
    "libelle_risque": "string",
    "description": "text",
    "date_detection": "date",
    "date_resolution": "date (nullable)",
    "utilisateur_detecteur_id": "uuid",
    "utilisateur_traitant_id": "uuid (nullable)",
    "niveau_risque": "integer",
    "probabilite_risque": "integer",
    "score_risque": "decimal",
    "impact_potentiel": "decimal (nullable)",
    "statut": "string",
    "action_corrective": "text",
    "station_id": "uuid",
    "commentaire": "text",
    "created_at": "datetime"
  },
  "message": "Risque opérationnel enregistré avec succès"
}
```

**HTTP Status Codes:**
- 201: Risque enregistré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

### 4.5 Gestion des analyses et prévisions commerciales

#### POST /api/kpi/analyses-previsions
**Description:** Créer une nouvelle analyse ou prévision commerciale

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_analyse": "tendance_vente|prevision_demande|optimisation_prix|analyse_client",
  "libelle_analyse": "string (max 100)",
  "description": "text (optionnel)",
  "periode_analyse_debut": "date (format YYYY-MM-DD)",
  "periode_analyse_fin": "date (format YYYY-MM-DD)",
  "donnees_entrees": "jsonb",
  "resultats_analyse": "jsonb",
  "interpretations": "text (optionnel)",
  "modele_utilise": "string (max 100) (optionnel)",
  "precision_modele": "decimal (max 5,2) (optionnel)",
  "station_id": "uuid",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type_analyse": "string",
    "libelle_analyse": "string",
    "description": "text",
    "periode_analyse_debut": "date",
    "periode_analyse_fin": "date",
    "donnees_entrees": "jsonb",
    "resultats_analyse": "jsonb",
    "interpretations": "text",
    "modele_utilise": "string",
    "precision_modele": "decimal",
    "statut": "string",
    "utilisateur_createur_id": "uuid",
    "station_id": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "Analyse ou prévision commerciale enregistrée avec succès"
}
```

**HTTP Status Codes:**
- 201: Analyse/prévision enregistrée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

### 4.6 Gestion des contrôles internes

#### POST /api/kpi/controles
**Description:** Créer un nouveau contrôle interne

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_controle": "ecart_caisse|operation_suspecte|modification_critique|autre",
  "libelle_controle": "string (max 100)",
  "description": "text (optionnel)",
  "objet_type": "string (optionnel)",
  "objet_id": "uuid (optionnel)",
  "utilisateur_concerne_id": "uuid (optionnel)",
  "resultat_controle": "Conforme|NonConforme|EnAttente",
  "seuil_alerte": "boolean (default: false)",
  "commentaire_controle": "text (optionnel)",
  "station_id": "uuid",
  "statut": "string (default: EnCours)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type_controle": "string",
    "libelle_controle": "string",
    "description": "text",
    "date_controle": "date",
    "heure_controle": "time",
    "utilisateur_controleur_id": "uuid",
    "utilisateur_concerne_id": "uuid",
    "objet_type": "string",
    "objet_id": "uuid",
    "resultat_controle": "string",
    "seuil_alerte": "boolean",
    "commentaire_controle": "text",
    "statut": "string",
    "station_id": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "Contrôle interne enregistré avec succès"
}
```

**HTTP Status Codes:**
- 201: Contrôle enregistré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Utilisateur/station non trouvé
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de calcul des KPIs opérationnels
1. Litres vendus par type de carburant: somme des quantités vendues par carburant dans une période
2. Marge brute par produit: (prix de vente - prix d'achat) * quantité vendue
3. Indicateur de rendement des pompistes: volume total distribué / temps de travail
4. Indicateur de productivité: chiffre d'affaires / nombre d'employés
5. Analyse comparative: calcul de variation en pourcentage entre différentes périodes ou stations

### Règles de gestion fiscale et réglementaire
1. Calcul automatique des obligations fiscales selon les taux en vigueur
2. Échéances basées sur les réglementations en vigueur
3. Génération préparatoire des rapports fiscaux
4. Suivi des normes de sécurité selon les réglementations applicables
5. Documentation des actions correctives pour les non-conformités

### Règles de gestion des risques opérationnels
1. Détection automatique des écarts anormaux selon des seuils configurables
2. Classification des risques par niveau et probabilité
3. Calcul du score de risque comme le produit du niveau et de la probabilité
4. Suivi des incidents de sécurité et des mesures prises
5. Contrôle des accès avec journalisation des tentatives non autorisées

### Règles d'analyse et prévision commerciale
1. Analyse des tendances basées sur les données historiques
2. Modèles de prévision configurables selon les types d'analyses
3. Calcul de la précision des modèles de prévision
4. Optimisation des prix basée sur la demande et la concurrence
5. Analyse segmentée des clients fidèles et occasionnels

### Règles de gestion des services annexes
1. Comptabilisation des services rendus dans les indicateurs financiers
2. Suivi de la rentabilité des services
3. Gestion des contrats de maintenance selon les termes convenus
4. Calcul des revenus spécifiques aux services
5. Analyse comparative de la performance des différents services

### Règles de gestion des contrôles internes
1. Contrôle automatique des écarts de caisse selon des seuils définis
2. Suivi des opérations suspectes selon des critères prédéfinis
3. Validation hiérarchisée selon les montants et le type de transaction
4. Journalisation des modifications critiques pour traçabilité
5. Alertes automatiques pour les seuils critiques dépassés

### Règles de gestion des relations clients avancées
1. Programmes de fidélisation basés sur des critères configurables
2. Gestion des cartes de carburant selon les règles établies
3. Contrats de ravitaillement à long terme avec suivi des engagements
4. Système de notation basé sur le comportement client
5. Analyse du comportement d'achat pour personnalisation

### Règles d'optimisation de la gestion de carburant
1. Correction volumétrique basée sur la température mesurée
2. Gestion des mélanges d'additifs selon les spécifications
3. Suivi de la qualité du carburant selon les normes en vigueur
4. Analyse des coûts logistiques pour optimisation
5. Suivi des pertes et gains de carburant pour identification des anomalies

### Impacts sur d'autres modules
1. Le module KPI interagit avec tous les autres modules pour récupérer les données
2. Les indicateurs affectent les décisions dans les modules de gestion
3. Les alertes KPI peuvent déclencher des actions dans d'autres modules
4. Les calculs KPI peuvent influencer les prévisions dans d'autres modules
5. Les indicateurs sont utilisés dans les rapports des modules de reporting

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
utilisateurs ||--o{ indicateurs_performance
utilisateurs ||--o{ valeurs_indicateurs_performance
utilisateurs ||--o{ obligations_fiscales_reglementaires
utilisateurs ||--o{ suivi_risques_operationnels
utilisateurs ||--o{ analyses_previsions_commerciales
utilisateurs ||--o{ controles_internes
utilisateurs ||--o{ indicateurs_gestion_carburant
stations ||--o{ indicateurs_performance
stations ||--o{ valeurs_indicateurs_performance
stations ||--o{ obligations_fiscales_reglementaires
stations ||--o{ suivi_risques_operationnels
stations ||--o{ analyses_previsions_commerciales
stations ||--o{ indicateurs_gestion_carburant
stations ||--o{ controles_internes
indicateurs_performance ||--o{ valeurs_indicateurs_performance
suivi_risques_operationnels }o--o{ utilisateurs (utilisateur_detecteur_id)
suivi_risques_operationnels }o--o{ utilisateurs (utilisateur_traitant_id)
suivi_relations_clients_avancees }o--o{ clients
```

### Diagramme de séquence pour le calcul d'un KPI
```
Gestionnaire -> API: GET /api/kpi/valeurs/{indicateur_id}
API -> Base de données: Requête pour récupérer la formule de calcul
API -> Calculateur: Calcul de la valeur selon la formule
Calculateur -> Base de données: Récupération des données nécessaires
Calculateur -> API: Retour de la valeur calculée
API -> Base de données: Enregistrer la valeur dans valeurs_indicateurs_performance
API -> API: Générer des alertes si seuils dépassés
API -> Gestionnaire: Retourner la valeur du KPI
```

## 7. Tests Requises

### Tests unitaires
1. Test des fonctions de calcul des KPIs opérationnels
2. Test des validations de données pour les différents endpoints
3. Test des calculs de seuils d'alerte
4. Test des fonctions de prévision commerciale
5. Test des calculs de scores de risque
6. Test des fonctions de validation fiscale

### Tests d'intégration
1. Test complet du processus de création d'indicateurs
2. Test de la génération automatique des valeurs KPI
3. Test du workflow de gestion des obligations fiscales
4. Test de la détection automatique des risques
5. Test de la génération d'analyses prévisionnelles
6. Test de la gestion des contrôles internes

### Tests de charge/performance
1. Test de performance pour des calculs de KPIs sur de grandes périodes
2. Test de performance pour des analyses prévisionnelles complexes
3. Test de performance pour des calculs de risques multiples
4. Test de la génération de valeurs pour de nombreux indicateurs
5. Test de la consultation simultanée de plusieurs KPIs

### Jeux de données de test
1. Données d'indicateurs valides avec différentes catégories
2. Données de performance historique pour les tests de prévision
3. Données de risques avec différents niveaux et probabilités
4. Données d'obligations fiscales pour les tests de conformité
5. Données de contrôles internes pour les tests de sécurité
6. Données de gestion de carburant pour les tests d'optimisation

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contrôles d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de calcul des KPIs et indicateurs
6. [ ] Implémenter la logique de validation des données
7. [ ] Créer les algorithmes d'analyse et de prévision
8. [ ] Implémenter le système d'alertes automatiques
9. [ ] Créer les modules de gestion des obligations fiscales
10. [ ] Créer les tests unitaires et d'intégration
11. [ ] Implémenter la gestion des erreurs et logs
12. [ ] Créer les vues frontend pour la gestion des KPIs (si applicable)
13. [ ] Documenter les endpoints API
14. [ ] Intégrer avec les modules de reporting pour les analyses
15. [ ] Intégrer avec le module de sécurité pour les validations

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base pour les indicateurs
3. Développer les services de calcul des KPIs
4. Implémenter la gestion des obligations fiscales
5. Créer les fonctionnalités de gestion des risques
6. Développer les analyses et prévisions commerciales
7. Intégrer avec les modules existants
8. Créer les tests
9. Optimiser les performances
10. Documenter la solution

### Livrables attendus
1. Code source complet avec commentaires
2. Scripts de migration de base de données
3. Documentation API
4. Jeux de tests et résultats
5. Documentation technique détaillée
6. Guide d'installation et de déploiement

## 9. Risques & Points de vigilance

### Points sensibles
1. La complexité des calculs de KPIs et indicateurs
2. La précision des modèles de prévision
3. La sécurité des données sensibles dans les indicateurs
4. La performance des calculs pour de grands volumes de données
5. La conformité des calculs fiscaux aux réglementations en vigueur

### Risques techniques
1. Risque d'erreurs dans les calculs complexes des indicateurs
2. Risque de non-conformité aux normes fiscales et réglementaires
3. Risque de problèmes de performances avec de grands volumes
4. Risque de perte de données en cas de panne pendant les calculs
5. Risque de manipulation des données par des utilisateurs non autorisés
6. Risque d'inexactitudes dans les prévisions commerciales

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples indicateurs
2. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
3. Besoin de maintenance continue pour les formules de calcul
4. Risque de dépendance excessive à des bibliothèques tierces pour les analyses
5. Risque de complexité dans la configuration des seuils d'alerte