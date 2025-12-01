# Technical Specification - Module de Gestion des Dépôts de Garantie

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de gestion des dépôts de garantie permet de gérer les fonds déposés par les clients comme garantie pour des services ou produits spécifiques. Il permet d'enregistrer les dépôts, de suivre leur utilisation pour le paiement de dettes, ventes ou écarts, de gérer les remboursements, et de maintenir un historique complet avec le solde visible pour chaque client. Le module inclut également un système de suivi des contrats de fidélité liés aux dépôts de garantie.

### Problème à résoudre
Sans un module dédié à la gestion des dépôts de garantie, les stations-service ne pourraient pas suivre efficacement les fonds déposés par les clients, ce qui entraînerait:
- Des difficultés à gérer les remboursements de garantie
- Des problèmes de traçabilité des utilisations de dépôts
- Des écarts dans les soldes de garantie par client
- Des difficultés à respecter les obligations comptables
- Des lacunes dans le suivi des contrats de fidélité

### Définition du périmètre
Le périmètre du sprint couvre:
- Gestion des dépôts de garantie (enregistrement, paiement, écritures comptables)
- Gestion des utilisations de dépôts (paiement de dettes, ventes, écarts)
- Gestion des remboursements de dépôts
- Historique complet des transactions
- Affichage du solde visible client
- Suivi des contrats de fidélité

## 2. User Stories & Critères d'acceptation

### US-DG-001: En tant que gestionnaire, je veux enregistrer un dépôt de garantie
**Critères d'acceptation :**
- Saisie du client concerné
- Saisie du montant du dépôt
- Enregistrement du mode de paiement
- Génération automatique d'une écriture comptable au passif
- Historique du dépôt
- Mise à jour du solde du client
- Numérotation unique du dépôt

### US-DG-002: En tant que gestionnaire, je veux utiliser un dépôt de garantie pour payer une dette
**Critères d'acceptation :**
- Sélection du dépôt à utiliser
- Association avec la dette à payer
- Calcul automatique de l'utilisation
- Mise à jour des soldes
- Génération d'une écriture comptable
- Historique de l'utilisation
- Contrôle que l'utilisation ne dépasse pas le solde disponible

### US-DG-003: En tant que gestionnaire, je veux utiliser un dépôt de garantie pour payer une vente
**Critères d'acceptation :**
- Sélection du dépôt à utiliser
- Association avec la vente à payer
- Calcul automatique de l'utilisation
- Mise à jour des soldes
- Génération d'une écriture comptable
- Historique de l'utilisation
- Contrôle que l'utilisation ne dépasse pas le solde disponible

### US-DG-004: En tant que gestionnaire, je veux utiliser un dépôt de garantie pour couvrir un écart
**Critères d'acceptation :**
- Sélection du dépôt à utiliser
- Association avec l'écart à couvrir
- Calcul automatique de l'utilisation
- Mise à jour des soldes
- Génération d'une écriture comptable
- Historique de l'utilisation
- Contrôle que l'utilisation ne dépasse pas le solde disponible

### US-DG-005: En tant que gestionnaire, je veux rembourser un dépôt de garantie
**Critères d'acceptation :**
- Sélection du dépôt à rembourser
- Calcul du montant remboursable
- Validation du remboursement
- Génération d'une écriture comptable
- Historique du remboursement
- Mise à jour des soldes

### US-DG-006: En tant que gestionnaire, je veux consulter l'historique complet des dépôts
**Critères d'acceptation :**
- Affichage de toutes les transactions
- Filtrage par client, période, type
- Pagination des résultats
- Export des données
- Information sur les utilisations et remboursements
- Affichage du solde après chaque transaction

### US-DG-007: En tant que gestionnaire, je veux voir le solde visible du dépôt de garantie par client
**Critères d'acceptation :**
- Calcul du solde disponible
- Affichage dans la fiche client
- Affichage dans les interfaces de gestion
- Mise à jour en temps réel
- Indication des fonds bloqués
- Historique des variations de solde

### US-DG-008: En tant que gestionnaire, je veux suivre les contrats de fidélité liés aux dépôts
**Critères d'acceptation :**
- Association des dépôts à des contrats de fidélité
- Calcul des points ou avantages acquis
- Suivi des conditions de fidélité
- Historique des contrats
- Application automatique des avantages
- Notifications d'échéance

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `clients` - données des clients
- `utilisateurs` - données des utilisateurs effectuant les opérations
- `ecritures_comptables` - données des écritures comptables
- `comptes_comptables` - données des comptes comptables
- `mode_paiements` - données des modes de paiement
- `tresoreries` - données des trésoreries
- `ventes` - données des ventes (pour associations)
- `contrats_ravitaillement` - données des contrats (pour associations)

### Nouvelles tables à créer

```sql
-- Table pour les dépôts de garantie
CREATE TABLE IF NOT EXISTS depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_depot VARCHAR(50) UNIQUE NOT NULL,
    client_id UUID REFERENCES clients(id),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    date_depot DATE NOT NULL,
    montant_depot NUMERIC(18,2) NOT NULL,
    montant_utilise NUMERIC(18,2) DEFAULT 0,
    montant_rembourse NUMERIC(18,2) DEFAULT 0,
    solde_disponible NUMERIC(18,2) GENERATED ALWAYS AS (montant_depot - montant_utilise - montant_rembourse) STORED,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Rembourse', 'Utilise', 'Expiré')),
    date_expiration DATE, -- Date à laquelle le dépôt expire
    commentaire TEXT,
    ecriture_comptable_id UUID REFERENCES ecritures_comptables(id), -- Écriture de création du dépôt
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les utilisations des dépôts de garantie
CREATE TABLE IF NOT EXISTS utilisations_depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    depot_garantie_id UUID REFERENCES depot_garantie(id),
    type_utilisation VARCHAR(50) NOT NULL CHECK (type_utilisation IN ('paiement_dette', 'paiement_vente', 'couverture_ecart', 'autre')),
    objet_type VARCHAR(50), -- Type de l'objet utilisé (facture, vente, etc.)
    objet_id UUID, -- ID de l'objet utilisé
    montant_utilise NUMERIC(18,2) NOT NULL,
    date_utilisation DATE NOT NULL,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    ecriture_comptable_id UUID REFERENCES ecritures_comptables(id), -- Écriture de l'utilisation
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les remboursements des dépôts de garantie
CREATE TABLE IF NOT EXISTS remboursements_depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    depot_garantie_id UUID REFERENCES depot_garantie(id),
    montant_rembourse NUMERIC(18,2) NOT NULL,
    date_remboursement DATE NOT NULL,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    mode_paiement_id UUID REFERENCES mode_paiements(id),
    tresorerie_paiement_id UUID REFERENCES tresoreries(id),
    reference_paiement VARCHAR(100), -- Numéro de chèque, virement, etc.
    commentaire TEXT,
    ecriture_comptable_id UUID REFERENCES ecritures_comptables(id), -- Écriture du remboursement
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les contrats de fidélité liés aux dépôts de garantie
CREATE TABLE IF NOT EXISTS contrats_fidélite_depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    depot_garantie_id UUID REFERENCES depot_garantie(id),
    type_contrat VARCHAR(50) NOT NULL, -- 'fidelisation', 'avantages', etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    points_acquis_initial NUMERIC(10,2) DEFAULT 0,
    points_utilises NUMERIC(10,2) DEFAULT 0,
    points_restants NUMERIC(10,2) GENERATED ALWAYS AS (points_acquis_initial - points_utilises) STORED,
    taux_conversion_points_valeur NUMERIC(8,4) DEFAULT 1.0000, -- Combien de points = 1 unité monétaire
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Utilisé', 'Annulé')),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les utilisations des contrats de fidélité
CREATE TABLE IF NOT EXISTS utilisations_contrat_fidélite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contrat_fidélite_id UUID REFERENCES contrats_fidélite_depot_garantie(id),
    depot_garantie_id UUID REFERENCES depot_garantie(id),
    type_utilisation VARCHAR(50) NOT NULL, -- 'reduction', 'avantage', 'credit', etc.
    points_utilises NUMERIC(10,2) NOT NULL,
    valeur_equivalente NUMERIC(18,2) GENERATED ALWAYS AS (points_utilises * (SELECT taux_conversion_points_valeur FROM contrats_fidélite_depot_garantie WHERE id = contrat_fidélite_id)) STORED,
    date_utilisation DATE NOT NULL,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les dépôts de garantie
CREATE INDEX IF NOT EXISTS idx_depot_garantie_client ON depot_garantie(client_id);
CREATE INDEX IF NOT EXISTS idx_depot_garantie_date ON depot_garantie(date_depot);
CREATE INDEX IF NOT EXISTS idx_depot_garantie_statut ON depot_garantie(statut);
CREATE INDEX IF NOT EXISTS idx_depot_garantie_expiration ON depot_garantie(date_expiration);
CREATE INDEX IF NOT EXISTS idx_depot_garantie_solde ON depot_garantie(solde_disponible);

-- Index pour les utilisations des dépôts
CREATE INDEX IF NOT EXISTS idx_utilisations_depot_depot ON utilisations_depot_garantie(depot_garantie_id);
CREATE INDEX IF NOT EXISTS idx_utilisations_depot_date ON utilisations_depot_garantie(date_utilisation);
CREATE INDEX IF NOT EXISTS idx_utilisations_depot_type ON utilisations_depot_garantie(type_utilisation);

-- Index pour les remboursements
CREATE INDEX IF NOT EXISTS idx_remboursements_depot ON remboursements_depot_garantie(depot_garantie_id);
CREATE INDEX IF NOT EXISTS idx_remboursements_date ON remboursements_depot_garantie(date_remboursement);

-- Index pour les contrats de fidélité
CREATE INDEX IF NOT EXISTS idx_contrats_fidelite_depot ON contrats_fidélite_depot_garantie(depot_garantie_id);
CREATE INDEX IF NOT EXISTS idx_contrats_fidelite_statut ON contrats_fidélite_depot_garantie(statut);
CREATE INDEX IF NOT EXISTS idx_contrats_fidelite_points ON contrats_fidélite_depot_garantie(points_restants);

-- Index pour les utilisations des contrats de fidélité
CREATE INDEX IF NOT EXISTS idx_utilisations_fidelite_contrat ON utilisations_contrat_fidélite(contrat_fidélite_id);
CREATE INDEX IF NOT EXISTS idx_utilisations_fidelite_depot ON utilisations_contrat_fidélite(depot_garantie_id);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour générer automatiquement le numéro de dépôt
CREATE OR REPLACE FUNCTION generate_numero_depot()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : DG-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_depot, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_depot FROM 4 FOR 8) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM depot_garantie
    WHERE SUBSTRING(numero_depot FROM 4 FOR 8) = date_str;
    
    numero := 'DG-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    NEW.numero_depot := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_depot
    BEFORE INSERT ON depot_garantie
    FOR EACH ROW EXECUTE FUNCTION generate_numero_depot();

-- Trigger pour empêcher l'utilisation d'un dépôt dépassant le solde disponible
CREATE OR REPLACE FUNCTION prevent_depot_exceedance()
RETURNS TRIGGER AS $$
DECLARE
    solde_disponible NUMERIC(18,2);
BEGIN
    -- Obtenir le solde disponible du dépôt
    SELECT montant_depot - montant_utilise - montant_rembourse
    INTO solde_disponible
    FROM depot_garantie
    WHERE id = NEW.depot_garantie_id;
    
    -- Vérifier que le montant à utiliser ne dépasse pas le solde disponible
    IF NEW.montant_utilise > solde_disponible THEN
        RAISE EXCEPTION 'Le montant à utiliser (% AR) dépasse le solde disponible (% AR)', 
                        NEW.montant_utilise, solde_disponible;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_depot_exceedance
    BEFORE INSERT ON utilisations_depot_garantie
    FOR EACH ROW EXECUTE FUNCTION prevent_depot_exceedance();

-- Trigger pour mettre à jour le montant utilisé dans le dépôt après une utilisation
CREATE OR REPLACE FUNCTION update_depot_montant_utilise()
RETURNS TRIGGER AS $$
BEGIN
    -- Mettre à jour le montant utilisé dans le dépôt de garantie
    UPDATE depot_garantie
    SET montant_utilise = montant_utilise + NEW.montant_utilise
    WHERE id = NEW.depot_garantie_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_depot_montant_utilise
    AFTER INSERT ON utilisations_depot_garantie
    FOR EACH ROW EXECUTE FUNCTION update_depot_montant_utilise();

-- Trigger pour empêcher le remboursement d'un dépôt dépassant le solde disponible
CREATE OR REPLACE FUNCTION prevent_remboursement_exceedance()
RETURNS TRIGGER AS $$
DECLARE
    solde_disponible NUMERIC(18,2);
BEGIN
    -- Obtenir le solde disponible du dépôt
    SELECT montant_depot - montant_utilise - montant_rembourse
    INTO solde_disponible
    FROM depot_garantie
    WHERE id = NEW.depot_garantie_id;
    
    -- Vérifier que le montant à rembourser ne dépasse pas le solde disponible
    IF NEW.montant_rembourse > solde_disponible THEN
        RAISE EXCEPTION 'Le montant à rembourser (% AR) dépasse le solde disponible (% AR)', 
                        NEW.montant_rembourse, solde_disponible;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_remboursement_exceedance
    BEFORE INSERT ON remboursements_depot_garantie
    FOR EACH ROW EXECUTE FUNCTION prevent_remboursement_exceedance();

-- Trigger pour mettre à jour le montant remboursé dans le dépôt après un remboursement
CREATE OR REPLACE FUNCTION update_depot_montant_rembourse()
RETURNS TRIGGER AS $$
BEGIN
    -- Mettre à jour le montant remboursé dans le dépôt de garantie
    UPDATE depot_garantie
    SET montant_rembourse = montant_rembourse + NEW.montant_rembourse
    WHERE id = NEW.depot_garantie_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_depot_montant_rembourse
    AFTER INSERT ON remboursements_depot_garantie
    FOR EACH ROW EXECUTE FUNCTION update_depot_montant_rembourse();
```

## 4. API Backend

### 4.1 Gestion des dépôts de garantie

#### POST /api/depots-garantie
**Description:** Créer un nouveau dépôt de garantie

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "client_id": "uuid",
  "montant_depot": "decimal (max 18,2)",
  "date_expiration": "date (format YYYY-MM-DD) (optionnel)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_depot": "string",
    "client_id": "uuid",
    "montant_depot": "decimal",
    "montant_utilise": "decimal",
    "montant_rembourse": "decimal",
    "solde_disponible": "decimal",
    "statut": "string",
    "date_depot": "date",
    "date_expiration": "date",
    "commentaire": "string",
    "created_at": "datetime"
  },
  "message": "Dépôt de garantie créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Dépôt créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Client non trouvé
- 500: Erreur interne du serveur

#### GET /api/depots-garantie/{id}
**Description:** Obtenir les détails d'un dépôt de garantie

**Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_depot": "string",
    "client": {
      "id": "uuid",
      "nom": "string",
      "email": "string"
    },
    "montant_depot": "decimal",
    "montant_utilise": "decimal",
    "montant_rembourse": "decimal",
    "solde_disponible": "decimal",
    "statut": "string",
    "date_depot": "date",
    "date_expiration": "date",
    "commentaire": "string",
    "historique": [
      {
        "type": "depot|utilisation|remboursement",
        "montant": "decimal",
        "date": "date",
        "description": "string"
      }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "Détails du dépôt de garantie récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 404: Dépôt non trouvé
- 500: Erreur interne du serveur

### 4.2 Gestion des utilisations de dépôts

#### POST /api/depots-garantie/{id}/utilisations
**Description:** Utiliser un dépôt de garantie pour payer une dette, une vente ou couvrir un écart

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_utilisation": "paiement_dette|paiement_vente|couverture_ecart|autre",
  "objet_type": "vente|facture|dette|ecart (optionnel)",
  "objet_id": "uuid (optionnel)",
  "montant_utilise": "decimal (max 18,2)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "depot_garantie_id": "uuid",
    "type_utilisation": "string",
    "objet_type": "string",
    "objet_id": "uuid",
    "montant_utilise": "decimal",
    "date_utilisation": "date",
    "commentaire": "string",
    "created_at": "datetime"
  },
  "message": "Utilisation du dépôt de garantie enregistrée avec succès"
}
```

**HTTP Status Codes:**
- 200: Utilisation enregistrée avec succès
- 400: Données invalides ou montant trop élevé
- 401: Non autorisé
- 403: Accès refusé
- 404: Dépôt/objet non trouvé
- 409: Solde insuffisant
- 500: Erreur interne du serveur

### 4.3 Gestion des remboursements

#### POST /api/depots-garantie/{id}/remboursements
**Description:** Rembourser une partie ou la totalité d'un dépôt de garantie

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "montant_rembourse": "decimal (max 18,2)",
  "mode_paiement_id": "uuid",
  "tresorerie_paiement_id": "uuid",
  "reference_paiement": "string (optionnel)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "depot_garantie_id": "uuid",
    "montant_rembourse": "decimal",
    "date_remboursement": "date",
    "mode_paiement_id": "uuid",
    "tresorerie_paiement_id": "uuid",
    "reference_paiement": "string",
    "commentaire": "string",
    "created_at": "datetime"
  },
  "message": "Remboursement du dépôt de garantie enregistré avec succès"
}
```

**HTTP Status Codes:**
- 200: Remboursement enregistré avec succès
- 400: Données invalides ou montant trop élevé
- 401: Non autorisé
- 403: Accès refusé
- 404: Dépôt/mode_paiement/tresorerie non trouvé
- 409: Solde insuffisant
- 500: Erreur interne du serveur

### 4.4 Historique et consultations

#### GET /api/depots-garantie
**Description:** Obtenir la liste des dépôts de garantie

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- client_id: uuid (optionnel)
- statut: Actif|Rembourse|Utilise|Expiré (optionnel)
- date_debut: date (format YYYY-MM-DD) (optionnel)
- date_fin: date (format YYYY-MM-DD) (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "depots": [
      {
        "id": "uuid",
        "numero_depot": "string",
        "client_id": "uuid",
        "client_nom": "string",
        "montant_depot": "decimal",
        "montant_utilise": "decimal",
        "montant_rembourse": "decimal",
        "solde_disponible": "decimal",
        "statut": "string",
        "date_depot": "date",
        "date_expiration": "date"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Liste des dépôts de garantie récupérée avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

### 4.5 Contrats de fidélité

#### GET /api/depots-garantie/{id}/contrats-fidelite
**Description:** Obtenir les contrats de fidélité liés à un dépôt de garantie

**Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
  "success": true,
  "data": {
    "contrats": [
      {
        "id": "uuid",
        "type_contrat": "string",
        "libelle": "string",
        "points_acquis_initial": "decimal",
        "points_utilises": "decimal",
        "points_restants": "decimal",
        "taux_conversion_points_valeur": "decimal",
        "date_debut": "date",
        "date_fin": "date",
        "statut": "string"
      }
    ]
  },
  "message": "Contrats de fidélité récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 404: Dépôt non trouvé
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de gestion des dépôts
1. Les dépôts doivent être associés à un client existant
2. Les montants des dépôts doivent être positifs
3. Les dépôts génèrent automatiquement une écriture comptable au passif
4. Les dépôts peuvent avoir une date d'expiration
5. Les soldes disponibles sont calculés dynamiquement (montant - utilisations - remboursements)

### Règles de gestion des utilisations
1. Les utilisations ne peuvent pas dépasser le solde disponible
2. Les utilisations sont classées par type (paiement de dette, vente, écart)
3. Les utilisations génèrent des écritures comptables appropriées
4. Les utilisations sont liées à des objets spécifiques si applicable
5. Les utilisations mettent à jour automatiquement le solde du dépôt

### Règles de gestion des remboursements
1. Les remboursements ne peuvent pas dépasser le solde disponible
2. Les remboursements doivent être effectués via un mode de paiement valide
3. Les remboursements génèrent des écritures comptables de clôture
4. Les remboursements mettent à jour automatiquement le solde du dépôt
5. Les remboursements peuvent nécessiter une validation supplémentaire

### Règles de gestion des contrats de fidélité
1. Les contrats de fidélité sont liés à des dépôts spécifiques
2. Les points sont calculés selon des taux de conversion configurables
3. Les contrats peuvent avoir des durées limitées
4. Les utilisations de contrats affectent les points disponibles
5. Les contrats peuvent être utilisés pour obtenir des réductions ou avantages

### Règles de validation
1. Vérification que le montant du dépôt est positif
2. Vérification que les utilisations ne dépassent pas le solde disponible
3. Vérification que les remboursements ne dépassent pas le solde disponible
4. Vérification de l'existence des objets liés (ventes, dettes, etc.)
5. Vérification des permissions d'accès pour chaque opération

### Impacts sur d'autres modules
1. Le module de dépôts affecte le module comptable (écritures de passif)
2. Le module de dépôts affecte le module de gestion des clients (soldes)
3. Le module de dépôts affecte le module de trésorerie (mouvements d'argent)
4. Le module de dépôts affecte le module de ventes (paiements)
5. Le module de dépôts fournit des données aux modules de reporting

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
clients ||--o{ depot_garantie
utilisateurs ||--o{ depot_garantie
ecritures_comptables ||--o{ depot_garantie
depot_garantie ||--o{ utilisations_depot_garantie
depot_garantie ||--o{ remboursements_depot_garantie
depot_garantie ||--o{ contrats_fidélite_depot_garantie
utilisateurs ||--o{ utilisations_depot_garantie
ecritures_comptables ||--o{ utilisations_depot_garantie
utilisateurs ||--o{ remboursements_depot_garantie
mode_paiements ||--o{ remboursements_depot_garantie
tresoreries ||--o{ remboursements_depot_garantie
ecritures_comptables ||--o{ remboursements_depot_garantie
contrats_fidélite_depot_garantie ||--o{ utilisations_contrat_fidélite
depot_garantie ||--o{ utilisations_contrat_fidélite
utilisateurs ||--o{ utilisations_contrat_fidélite
```

### Diagramme de séquence pour un dépôt de garantie
```
Client -> Gestionnaire: Demande de dépôt de garantie
Gestionnaire -> API: POST /api/depots-garantie
API -> Base de données: Créer le dépôt (statut: Actif)
API -> API: Générer l'écriture comptable au passif
API -> Base de données: Enregistrer l'écriture comptable
API -> Gestionnaire: Retourner le dépôt créé
Gestionnaire -> Client: Confirmation du dépôt
```

## 7. Tests Requises

### Tests unitaires
1. Test de la fonction de génération automatique de numéro de dépôt
2. Test des validations de données pour les différents endpoints
3. Test des calculs de soldes disponibles
4. Test des validations d'utilisation et de remboursement
5. Test des fonctions de mise à jour des soldes
6. Test des calculs de points de fidélité

### Tests d'intégration
1. Test complet du processus de dépôt de garantie
2. Test du processus d'utilisation de dépôt
3. Test du processus de remboursement
4. Test de la génération automatique des écritures comptables
5. Test du suivi des contrats de fidélité
6. Test de la consultation des soldes clients

### Tests de charge/performance
1. Test de performance pour des centaines de dépôts simultanés
2. Test de performance pour des utilisations multiples
3. Test de performance pour des calculs de soldes complexes
4. Test de la génération d'écritures comptables pour de grands volumes
5. Test des consultations historiques pour de nombreux dépôts

### Jeux de données de test
1. Données de dépôts valides avec différentes configurations
2. Données de clients avec différents profils de dépôts
3. Données d'utilisation avec différents types d'objets
4. Données de remboursement avec différents modes de paiement
5. Données de contrats de fidélité variés
6. Données historiques pour les tests d'analyse

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contrôles d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de gestion des dépôts de garantie
6. [ ] Implémenter la logique de validation des données
7. [ ] Créer les utilitaires de génération d'écritures comptables
8. [ ] Implémenter les algorithmes de calcul de soldes
9. [ ] Créer les fonctionnalités de gestion des contrats de fidélité
10. [ ] Créer les tests unitaires et d'intégration
11. [ ] Implémenter la gestion des erreurs et logs
12. [ ] Créer les vues frontend pour la gestion des dépôts (si applicable)
13. [ ] Documenter les endpoints API
14. [ ] Intégrer avec les modules de reporting pour les analyses
15. [ ] Intégrer avec le module de sécurité pour les validations

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base pour les dépôts
3. Développer les fonctionnalités d'utilisation
4. Implémenter le système de remboursement
5. Créer les fonctionnalités de contrats de fidélité
6. Développer les consultations et historiques
7. Intégrer avec les modules de comptabilité et trésorerie
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
1. La sécurité des fonds déposés par les clients
2. La précision des calculs de soldes et d'utilisations
3. La conformité comptable des écritures générées
4. La traçabilité des transactions financières
5. La performance des calculs pour de grands volumes de données

### Risques techniques
1. Risque d'erreurs dans les calculs de soldes disponibles
2. Risque de non-conformité aux normes comptables
3. Risque de problèmes de performances avec de grands volumes
4. Risque de perte de données en cas de panne pendant les processus
5. Risque de manipulation des données par des utilisateurs non autorisés
6. Risque d'incohérence entre les modules si les intégrations ne sont pas correctes

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples règles de gestion
2. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
3. Besoin de maintenance continue pour les règles comptables
4. Risque de dépendance excessive à des bibliothèques tierces pour les calculs complexes
5. Risque de complexité dans la gestion des contrats de fidélité