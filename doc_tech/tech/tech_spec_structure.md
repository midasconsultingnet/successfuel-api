# Technical Specification - Module de gestion des structures

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de gestion des structures constitue les fondations du système ERP SuccessFuel. Il permet de créer et gérer les éléments physiques et organisationnels d'une station-service : stations, cuves, carburants, pistolets, produits, employés, clients, fournisseurs, trésoreries. Ce module est essentiel car toutes les autres fonctionnalités (achats, ventes, inventaires, etc.) dépendent de ces structures de base.

### Problème à résoudre
Sans une gestion rigoureuse des structures de base, le système ERP ne pourrait pas fonctionner correctement. Il est nécessaire de disposer d'un système d'administration permettant de créer, modifier, activer/désactiver les entités de base avec un suivi de leur statut, des contrôles de sécurité et des validations de données.

### Définition du périmètre
Le périmètre du sprint couvre la création de toutes les structures de base :
- Stations-service avec leurs caractéristiques
- Cuves avec capacités et associations
- Carburants avec historique des prix
- Pistolets avec suivi des index
- Produits et familles de produits
- Clients et fournisseurs
- Employés et leurs postes
- Trésoreries et modes de paiement

## 2. User Stories & Critères d'acceptation

### US-STRUC-001: En tant que gestionnaire, je veux créer et gérer une station-service
**Critères d'acceptation :**
- Possibilité de créer une station avec un code unique, nom, adresse, responsable
- Gestion des coordonnées de contact (téléphone, email)
- Association à une compagnie
- Statut actif/inactif/géré
- Affichage des KPIs et indicateurs de performance
- Historique des modifications

### US-STRUC-002: En tant que gestionnaire, je veux gérer les cuves de stockage
**Critères d'acceptation :**
- Création de cuves avec code, capacité, type de carburant
- Association à une station spécifique
- Gestion du barème de jauge (hauteur/volume)
- Suivi de la température pour correction volumétrique
- Contrôle d'accès limité aux opérateurs autorisés
- Historique des mesures de contenance

### US-STRUC-003: En tant que gestionnaire, je veux gérer les carburants et leurs caractéristiques
**Critères d'acceptation :**
- Création de carburants avec type (essence, gazole, etc.)
- Suivi des prix d'achat et de vente
- Historique des variations de prix
- Suivi de la qualité du carburant
- Historique des coûts logistiques
- Gestion des spécifications techniques

### US-STRUC-004: En tant que gestionnaire, je veux gérer les pistolets de distribution
**Critères d'acceptation :**
- Numérotation unique des pistolets
- Association à une pompe puis à une cuve
- Suivi des index initiaux et des relevés
- Contrôle d'accès aux opérateurs autorisés
- Historique des index et des utilisations

### US-STRUC-005: En tant que gestionnaire, je veux gérer les produits et familles
**Critères d'acceptation :**
- Création de familles de produits (alimentation, lubrifiants, etc.)
- Gestion des produits avec prix d'achat/vente, stock minimal, TVA
- Gestion des codes internes et des codes-barres
- Gestion des additifs et mélanges
- Association à une unité de mesure

### US-STRUC-006: En tant que gestionnaire, je veux gérer les clients
**Critères d'acceptation :**
- Gestion des informations générales (nom, adresse, contacts)
- Suivi des soldes et historique des paiements
- Gestion des programmes de fidélisation
- Gestion des cartes de carburant
- Gestion des contrats de ravitaillement
- Système de notation et de classement

### US-STRUC-007: En tant que gestionnaire, je veux gérer les fournisseurs
**Critères d'acceptation :**
- Gestion des informations générales (nom, adresse, contacts)
- Suivi du solde et historique des transactions
- Évaluation de la qualité des livraisons
- Analyse de performance
- Historique des relations commerciales

### US-STRUC-008: En tant que gestionnaire, je veux gérer les employés
**Critères d'acceptation :**
- Gestion des informations générales (nom, poste, contact)
- Suivi des salaires, avances et créances
- Indicateurs de performance
- Suivi de la productivité
- Gestion des affectations aux stations

### US-STRUC-009: En tant que gestionnaire, je veux gérer les trésoreries
**Critères d'acceptation :**
- Création de trésoreries avec types (banque, caisse, etc.)
- Gestion des soldes théorique et réel
- Association à une ou plusieurs stations
- Gestion des modes de paiement acceptés
- Suivi des incidents de sécurité

## 3. Modèle de Données

### Tables existantes (utilisation et potentielles mises à jour)

```sql
-- Table des stations (déjà existante)
-- Modifications potentielles :
-- Ajout de champs pour KPIs et indicateurs de performance
ALTER TABLE stations ADD COLUMN IF NOT EXISTS kpi_rendement NUMERIC(5,2);
ALTER TABLE stations ADD COLUMN IF NOT EXISTS kpi_croissance NUMERIC(5,2);
ALTER TABLE stations ADD COLUMN IF NOT EXISTS indicateur_performance JSONB;

-- Table des cuves (existantes)
-- Modifications pour ajouter le suivi de température
ALTER TABLE cuves ADD COLUMN IF NOT EXISTS temperature_correction NUMERIC(5,2);
ALTER TABLE cuves ADD COLUMN IF NOT EXISTS coefficient_temperature NUMERIC(10,6);

-- Table des carburants (existantes)
-- Ajout de champs pour la qualité et la logistique
ALTER TABLE carburants ADD COLUMN IF NOT EXISTS qualite_carburant TEXT;
ALTER TABLE carburants ADD COLUMN IF NOT EXISTS cout_logistique NUMERIC(18,4);
ALTER TABLE carburants ADD COLUMN IF NOT EXISTS specification_technique TEXT;

-- Table des pistolets (existantes)
-- Ajout de champ pour le contrôle d'accès
ALTER TABLE pistolets ADD COLUMN IF NOT EXISTS acces_autorise JSONB; -- Liste d'UUID des utilisateurs autorisés

-- Table des articles (produits existants)
-- Ajout de champ pour additifs et mélanges
ALTER TABLE articles ADD COLUMN IF NOT EXISTS additifs JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS melanges JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS unite_principale VARCHAR(10);

-- Table des clients (existante)
-- Ajout de champs pour les programmes de fidélisation
ALTER TABLE clients ADD COLUMN IF NOT EXISTS programme_fidelize_id UUID;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS carte_carburant_id UUID;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS contrat_ravitaille_id UUID;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS score_fidelize NUMERIC(5,2);

-- Table des fournisseurs (existante)
-- Ajout de champs pour la qualité et l'analyse de performance
ALTER TABLE fournisseurs ADD COLUMN IF NOT EXISTS historique_qualite JSONB;
ALTER TABLE fournisseurs ADD COLUMN IF NOT EXISTS score_performance NUMERIC(5,2);

-- Table des employés (existante)
-- Ajout de champs pour indicateurs de performance
ALTER TABLE employes ADD COLUMN IF NOT EXISTS kpi_productivite NUMERIC(5,2);
ALTER TABLE employes ADD COLUMN IF NOT EXISTS historique_performance JSONB;

-- Table des trésoreries (existante)
-- Ajout de champs pour la gestion des assurances et incidents
ALTER TABLE tresoreries ADD COLUMN IF NOT EXISTS gestion_assurances JSONB;
ALTER TABLE tresoreries ADD COLUMN IF NOT EXISTS incidents_securite JSONB;
```

### Nouvelles tables à créer si non existantes

```sql
-- Table pour les programmes de fidélisation
CREATE TABLE IF NOT EXISTS programmes_fidelite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    type_programme VARCHAR(50) NOT NULL, -- 'points', 'reduction', etc.
    seuil_activation NUMERIC(18,2) DEFAULT 0,
    benefice TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Expiré')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les cartes de carburant
CREATE TABLE IF NOT EXISTS cartes_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_carte VARCHAR(50) UNIQUE NOT NULL,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    date_activation DATE NOT NULL,
    date_expiration DATE,
    solde_carte NUMERIC(18,2) DEFAULT 0,
    plafond_mensuel NUMERIC(18,2),
    statut VARCHAR(20) DEFAULT 'Active' CHECK (statut IN ('Active', 'Inactive', 'Bloquee', 'Perdue', 'Remplacee')),
    utilisateur_creation_id UUID REFERENCES utilisateurs(id),
    utilisateur_blocage_id UUID REFERENCES utilisateurs(id),
    motif_blocage TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les contrats de ravitaillement
CREATE TABLE IF NOT EXISTS contrats_ravitaillement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    type_contrat VARCHAR(50) NOT NULL, -- 'ravitaillement', 'stationnement', etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    volume_garanti NUMERIC(18,3), -- En litres
    prix_contractuel NUMERIC(18,4), -- Prix convenu
    frequence_livraison INTEGER, -- En jours
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé', 'Suspendu')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour la qualité du carburant
CREATE TABLE IF NOT EXISTS qualite_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID REFERENCES carburants(id),
    cuve_id UUID REFERENCES cuves(id),
    date_controle DATE NOT NULL,
    utilisateur_controle_id UUID REFERENCES utilisateurs(id),
    type_controle VARCHAR(50) NOT NULL, -- 'densite', 'octane', etc.
    valeur_relevee VARCHAR(50), -- Valeur mesurée
    valeur_standard VARCHAR(50), -- Valeur attendue
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Non conforme')),
    observation TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les coûts logistique
CREATE TABLE IF NOT EXISTS couts_logistique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_cout VARCHAR(50) NOT NULL, -- 'transport', 'stockage', 'assurance', etc.
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_cout DATE NOT NULL,
    carburant_id UUID REFERENCES carburants(id),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    utilisateur_saisie_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les stations
CREATE INDEX IF NOT EXISTS idx_stations_compagnie ON stations(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_stations_statut ON stations(statut);

-- Index pour les cuves
CREATE INDEX IF NOT EXISTS idx_cuves_station ON cuves(station_id);
CREATE INDEX IF NOT EXISTS idx_cuves_carburant ON cuves(carburant_id);

-- Index pour les carburants
CREATE INDEX IF NOT EXISTS idx_carburants_compagnie ON carburants(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_carburants_type ON carburants(type);

-- Index pour les articles
CREATE INDEX IF NOT EXISTS idx_articles_famille ON articles(famille_id);
CREATE INDEX IF NOT EXISTS idx_articles_compagnie ON articles(compagnie_id);

-- Index pour les clients
CREATE INDEX IF NOT EXISTS idx_clients_compagnie ON clients(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_clients_statut ON clients(statut);

-- Index pour les fournisseurs
CREATE INDEX IF NOT EXISTS idx_fournisseurs_compagnie ON fournisseurs(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_fournisseurs_statut ON fournisseurs(statut);

-- Index pour les employés
CREATE INDEX IF NOT EXISTS idx_employes_compagnie ON employes(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_employes_poste ON employes(poste);

-- Index pour les trésoreries
CREATE INDEX IF NOT EXISTS idx_tresoreries_compagnie ON tresoreries(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_tresoreries_statut ON tresoreries(statut);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour s'assurer qu'une station a une compagnie
CREATE OR REPLACE FUNCTION validate_station_compagnie()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.compagnie_id IS NULL THEN
        RAISE EXCEPTION 'Une station doit être associée à une compagnie';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_station_compagnie
    BEFORE INSERT OR UPDATE ON stations
    FOR EACH ROW EXECUTE FUNCTION validate_station_compagnie();

-- Trigger pour valider la capacité des cuves
CREATE OR REPLACE FUNCTION validate_cuve_capacite()
RETURNS TRIGGER AS $$
DECLARE
    total_capacite NUMERIC(18,3);
    capacite_max NUMERIC(18,3);
BEGIN
    -- Vérifier que la capacité est positive
    IF NEW.capacite <= 0 THEN
        RAISE EXCEPTION 'La capacité de la cuve doit être positive';
    END IF;
    
    -- Vérifier que la somme des capacités ne dépasse pas la limite (si applicable)
    SELECT COALESCE(SUM(capacite), 0) INTO total_capacite
    FROM cuves
    WHERE station_id = NEW.station_id AND id != NEW.id;
    
    -- Supposons une limite de 100000 litres par station (à adapter selon les besoins)
    capacite_max := 100000;
    
    IF total_capacite + NEW.capacite > capacite_max THEN
        RAISE EXCEPTION 'La capacité totale de la station dépasserait la limite de % litres', capacite_max;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_cuve_capacite
    BEFORE INSERT OR UPDATE ON cuves
    FOR EACH ROW EXECUTE FUNCTION validate_cuve_capacite();
```

## 4. API Backend

### 4.1 Gestion des stations

#### GET /api/stations
**Description:** Récupérer toutes les stations avec filtres

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page: integer (default: 1)
- limit: integer (default: 10)
- compagnie_id: uuid (optional)
- statut: string (Actif|Inactif|Supprime)
- search: string (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "stations": [
      {
        "id": "uuid",
        "code": "string",
        "nom": "string",
        "telephone": "string",
        "email": "string",
        "adresse": "string",
        "pays_id": "uuid",
        "compagnie_id": "uuid",
        "statut": "string",
        "kpi_rendement": "decimal",
        "kpi_croissance": "decimal",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Stations récupérées
- 401: Unauthorized
- 403: Insufficient permissions

#### POST /api/stations
**Description:** Créer une nouvelle station

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "nom": "string (max 100)",
  "telephone": "string (max 30)",
  "email": "string (max 150)",
  "adresse": "string",
  "pays_id": "uuid",
  "compagnie_id": "uuid",
  "statut": "Actif|Inactif|Supprime"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "nom": "string",
    "telephone": "string",
    "email": "string",
    "adresse": "string",
    "pays_id": "uuid",
    "compagnie_id": "uuid",
    "statut": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Station créée
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code de station déjà existant

#### PUT /api/stations/{id}
**Description:** Mettre à jour une station existante

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "nom": "string (max 100)",
  "telephone": "string (max 30)",
  "email": "string (max 150)",
  "adresse": "string",
  "pays_id": "uuid",
  "statut": "Actif|Inactif|Supprime"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "nom": "string",
    "telephone": "string",
    "email": "string",
    "adresse": "string",
    "pays_id": "uuid",
    "compagnie_id": "uuid",
    "statut": "string",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Station mise à jour
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 404: Station non trouvée

### 4.2 Gestion des cuves

#### POST /api/cuves
**Description:** Créer une nouvelle cuve

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (max 40)",
  "station_id": "uuid",
  "carburant_id": "uuid",
  "capacite": "decimal (max 18.3)",
  "temperature_correction": "decimal",
  "coefficient_temperature": "decimal"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "station_id": "uuid",
    "carburant_id": "uuid",
    "capacite": "decimal",
    "temperature_correction": "decimal",
    "coefficient_temperature": "decimal",
    "compagnie_id": "uuid",
    "statut": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Cuve créée
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code de cuve déjà existant pour cette station

### 4.3 Gestion des carburants

#### POST /api/carburants
**Description:** Créer un nouveau carburant

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 40)",
  "libelle": "string (max 150)",
  "type": "string (max 50)",  -- Essence, Gazole, etc.
  "compagnie_id": "uuid",
  "prix_achat": "decimal (max 18,4)",
  "prix_vente": "decimal (max 18,4)",
  "qualite_carburant": "string",
  "cout_logistique": "decimal (max 18,4)",
  "specification_technique": "text",
  "statut": "Actif|Inactif|Supprime"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "libelle": "string",
    "type": "string",
    "compagnie_id": "uuid",
    "prix_achat": "decimal",
    "prix_vente": "decimal",
    "qualite_carburant": "string",
    "cout_logistique": "decimal",
    "specification_technique": "string",
    "statut": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Carburant créé
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code de carburant déjà existant

### 4.4 Gestion des produits

#### POST /api/articles
**Description:** Créer un nouvel article

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 40)",
  "libelle": "string (max 150)",
  "codebarre": "string (max 100)",
  "famille_id": "uuid",
  "compagnie_id": "uuid",
  "type_article": "produit|service",
  "prix_achat": "decimal (max 18,4)",
  "prix_vente": "decimal (max 18,4)",
  "tva": "decimal (max 5,2)",
  "taxes_applicables": ["uuid"],
  "stock_minimal": "decimal (max 18,3)",
  "unite": "string (max 20)",
  "unite_principale": "string (max 10)",
  "additifs": "json",
  "melanges": "json",
  "statut": "Actif|Inactif|Supprime"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "libelle": "string",
    "codebarre": "string",
    "famille_id": "uuid",
    "compagnie_id": "uuid",
    "type_article": "string",
    "prix_achat": "decimal",
    "prix_vente": "decimal",
    "tva": "decimal",
    "taxes_applicables": ["uuid"],
    "stock_minimal": "decimal",
    "unite": "string",
    "unite_principale": "string",
    "additifs": "json",
    "melanges": "json",
    "statut": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Article créé
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code d'article déjà existant

### 4.5 Gestion des clients

#### POST /api/clients
**Description:** Créer un nouveau client

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "nom": "string (max 150)",
  "adresse": "text",
  "telephone": "string (max 30)",
  "nif": "string (max 50)",
  "email": "string (max 150)",
  "compagnie_id": "uuid",
  "station_ids": ["uuid"],
  "type_tiers_id": "uuid",
  "statut": "Actif|Inactif|Supprime",
  "devise_facturation": "string (max 3)",
  "programme_fidelize_id": "uuid",
  "carte_carburant_id": "uuid",
  "contrat_ravitaille_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "nom": "string",
    "adresse": "string",
    "telephone": "string",
    "nif": "string",
    "email": "string",
    "compagnie_id": "uuid",
    "station_ids": ["uuid"],
    "type_tiers_id": "uuid",
    "statut": "string",
    "nb_jrs_creance": 0,
    "solde_comptable": "decimal",
    "solde_confirme": "decimal",
    "date_dernier_rapprochement": "datetime",
    "devise_facturation": "string",
    "programme_fidelize_id": "uuid",
    "carte_carburant_id": "uuid",
    "contrat_ravitaille_id": "uuid",
    "score_fidelize": "decimal",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Client créé
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code de client déjà existant

### 4.6 Gestion des fournisseurs

#### POST /api/fournisseurs
**Description:** Créer un nouveau fournisseur

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "nom": "string (max 150)",
  "adresse": "text",
  "telephone": "string (max 30)",
  "nif": "string (max 50)",
  "email": "string (max 150)",
  "compagnie_id": "uuid",
  "station_ids": ["uuid"],
  "type_tiers_id": "uuid",
  "statut": "Actif|Inactif|Supprime",
  "historique_qualite": "json",
  "score_performance": "decimal"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "nom": "string",
    "adresse": "string",
    "telephone": "string",
    "nif": "string",
    "email": "string",
    "compagnie_id": "uuid",
    "station_ids": ["uuid"],
    "type_tiers_id": "uuid",
    "statut": "string",
    "nb_jrs_creance": 0,
    "solde_comptable": "decimal",
    "solde_confirme": "decimal",
    "date_dernier_rapprochement": "datetime",
    "historique_qualite": "json",
    "score_performance": "decimal",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Fournisseur créé
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code de fournisseur déjà existant

### 4.7 Gestion des employés

#### POST /api/employes
**Description:** Créer un nouvel employé

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "nom": "string (max 150)",
  "prenom": "string (max 150)",
  "adresse": "text",
  "telephone": "string (max 30)",
  "poste": "string (max 100)",
  "salaire_base": "decimal (max 18,2)",
  "station_ids": ["uuid"],
  "compagnie_id": "uuid",
  "statut": "Actif|Inactif|Supprime",
  "kpi_productivite": "decimal"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "nom": "string",
    "prenom": "string",
    "adresse": "string",
    "telephone": "string",
    "poste": "string",
    "salaire_base": "decimal",
    "station_ids": ["uuid"],
    "compagnie_id": "uuid",
    "statut": "string",
    "kpi_productivite": "decimal",
    "historique_performance": "json",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Employé créé
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code d'employé déjà existant

### 4.8 Gestion des trésoreries

#### POST /api/tresoreries
**Description:** Créer une nouvelle trésorerie

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "libelle": "string (max 100)",
  "compagnie_id": "uuid",
  "station_ids": ["uuid"],
  "solde": "decimal (max 18,2)",
  "devise_code": "string (max 3)",
  "taux_change": "decimal (max 15,6)",
  "fournisseur_id": "uuid",
  "type_tresorerie": "uuid",
  "methode_paiement": "json",
  "statut": "Actif|Inactif|Supprime",
  "type_tresorerie_libelle": "string (max 50)",
  "gestion_assurances": "json",
  "incidents_securite": "json"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "string",
    "libelle": "string",
    "compagnie_id": "uuid",
    "station_ids": ["uuid"],
    "solde": "decimal",
    "devise_code": "string",
    "taux_change": "decimal",
    "fournisseur_id": "uuid",
    "type_tresorerie": "uuid",
    "methode_paiement": "json",
    "statut": "string",
    "solde_theorique": "decimal",
    "solde_reel": "decimal",
    "date_dernier_rapprochement": "datetime",
    "utilisateur_dernier_rapprochement": "uuid",
    "type_tresorerie_libelle": "string",
    "gestion_assurances": "json",
    "incidents_securite": "json",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Trésorerie créée
- 400: Données invalides
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Code de trésorerie déjà existant

## 5. Logique Métier

### 5.1 Validation des données

**Processus de validation :**
1. Validation des types de données (UUID, NUMERIC, VARCHAR avec limites)
2. Validation des contraintes d'intégrité (clé étrangère existante)
3. Validation des longueurs maximales des champs
4. Validation des formats (email, téléphone)
5. Validation des valeurs dans les domaines autorisés (CHECK constraints)
6. Validation des contraintes de unicité (codes uniques)

**Exemples spécifiques :**
- Un code de station doit être unique par compagnie
- Une cuve doit être associée à une station existante
- Un utilisateur ne peut créer des entités que pour sa propre compagnie
- Les montants ne peuvent être négatifs
- Les dates doivent être valides

### 5.2 Gestion des relations

**Contraintes relationnelles :**
- Chaque entité appartient à une compagnie
- Les stations, cuves, etc. sont limités à la compagnie propriétaire
- Les employés peuvent être affectés à plusieurs stations
- Les clients/fournisseurs peuvent être rattachés à plusieurs stations
- Les pistolets ne peuvent être associés qu'à une seule cuve
- Les articles appartiennent à une seule famille

### 5.3 Contrôles d'accès

**Niveaux de permissions :**
- Gestion des entités liées à sa propre compagnie
- Accès limité aux stations spécifiées dans l'utilisateur
- Contrôle des modifications critiques (montant élevé, suppression)
- Validation hiérarchique pour certaines opérations

### 5.4 Calculs et traitements automatiques

**Processus automatisés :**
- Calcul automatique des KPIs pour les stations et employés
- Historisation des variations de prix
- Mise à jour des soldes en temps réel
- Suivi des écarts entre théorique et réel
- Génération des alertes pour les valeurs seuils

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)

```
compagnies ||--o{ stations : "possède"
compagnies ||--o{ carburants : "gère"
compagnies ||--o{ articles : "possède"
compagnies ||--o{ clients : "gère"
compagnies ||--o{ fournisseurs : "gère"
compagnies ||--o{ employes : "emploie"
compagnies ||--o{ tresoreries : "possède"

stations ||--o{ cuves : "contient"
cuves ||--o{ pistolets : "alimente"
cuves ||--|| carburants : "stocke"
carburants ||--o{ historique_prix_carburants : "affecte"

articles }o--|| familles_articles : "appartient à"
articles ||--o{ historique_prix_articles : "affecte"

employes ||--o{ stations_user : "affecté à" (relation many-to-many via stations_user)
clients ||--o{ stations : "fréquente" (relation many-to-many via station_ids)
fournisseurs ||--o{ stations : "fournit à" (relation many-to-many via station_ids)

tresoreries ||--o{ fournisseurs : "paye"
tresoreries ||--o{ stations : "associée à"
```

### 6.2 Diagramme de séquence - Création d'une station

```
Gestionnaire -> Serveur: POST /api/stations
Serveur -> Serveur: Valider les permissions
Serveur -> DB: Vérifier existence companie
DB -> Serveur: Retourner résultat
Serveur -> Serveur: Valider les données d'entrée
Serveur -> DB: Créer la station
Serveur -> DB: Enregistrer dans journal d'audit
Serveur -> Gestionnaire: Retourner la station créée
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Validation des données d'entrée (formats, longueurs, types)
- Méthodes de création des entités
- Méthodes de mise à jour des entités
- Méthodes de suppression logique
- Méthodes de calcul des KPIs
- Méthodes de gestion des relations

### 7.2 Tests d'intégration
- Cycle complet de CRUD pour chaque entité
- Relations entre entités (station-cuve-article-client-fournisseur)
- Contraintes d'intégrité référentielles
- Journalisation des actions
- Contrôles d'accès selon la compagnie

### 7.3 Tests de charge/performance
- Performance des requêtes de recherche avec filtres
- Performance des insertions massives
- Impact des triggers sur la performance des opérations
- Tests de pagination pour des grandes quantités de données

### 7.4 Jeux de données de test
```sql
-- Données de test pour les structures
-- Création d'une compagnie de test
INSERT INTO compagnies (
    id, code, nom, adresse, telephone, email, nif, statut, pays_id, devise_principale
) VALUES (
    gen_random_uuid(),
    'TEST001',
    'Compagnie de test',
    'Adresse de test',
    '0123456789',
    'test@example.com',
    'NIF001',
    'Actif',
    (SELECT id FROM pays WHERE code_pays = 'MDG' LIMIT 1), -- Supposant que Madagascar existe
    'MGA'
);

-- Création d'un utilisateur de test
INSERT INTO utilisateurs (
    id, login, mot_de_passe, nom, profil_id, email, telephone, 
    stations_user, statut, compagnie_id, created_at
)
SELECT 
    gen_random_uuid(),
    'test_user',
    '$2b$12$L.RZ2T0pL.z8x1q2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n', -- Mot de passe haché
    'Test User',
    (SELECT id FROM profils WHERE code = 'ADMIN' LIMIT 1),
    'test@example.com',
    '0123456789',
    '[]',
    'Actif',
    id,
    now()
FROM compagnies 
WHERE code = 'TEST001'
LIMIT 1;

-- Création d'une station de test
INSERT INTO stations (
    id, compagnie_id, code, nom, telephone, email, adresse, pays_id, statut
)
SELECT 
    gen_random_uuid(),
    (SELECT id FROM compagnies WHERE code = 'TEST001' LIMIT 1),
    'STN001',
    'Station Test 1',
    '0123456789',
    'station@test.com',
    'Adresse Station Test',
    (SELECT id FROM pays WHERE code_pays = 'MDG' LIMIT 1),
    'Actif'
LIMIT 1;

-- Création d'une famille d'articles de test
INSERT INTO familles_articles (
    id, code, libelle, compagnie_id, statut
)
SELECT 
    gen_random_uuid(),
    'FAM001',
    'Lubrifiants',
    (SELECT id FROM compagnies WHERE code = 'TEST001' LIMIT 1),
    'Actif'
LIMIT 1;

-- Création d'un article de test
INSERT INTO articles (
    id, code, libelle, famille_id, compagnie_id, type_article, prix_achat, prix_vente
)
SELECT 
    gen_random_uuid(),
    'ART001',
    'Huile moteur 10W40',
    (SELECT id FROM familles_articles WHERE code = 'FAM001' LIMIT 1),
    (SELECT id FROM compagnies WHERE code = 'TEST001' LIMIT 1),
    'produit',
    5000.00,
    6500.00
LIMIT 1;

-- Création d'un client de test
INSERT INTO clients (
    id, code, nom, adresse, telephone, email, compagnie_id, statut
)
SELECT 
    gen_random_uuid(),
    'CLI001',
    'Client Test',
    'Adresse Client Test',
    '0123456789',
    'client@test.com',
    (SELECT id FROM compagnies WHERE code = 'TEST001' LIMIT 1),
    'Actif'
LIMIT 1;
```

## 8. Checklist Développeur

### Tâches techniques détaillées

**Phase 1 - Stations et cuves (jours 1-2)**
- [ ] Créer les services de gestion des stations
- [ ] Créer les endpoints API pour les stations
- [ ] Implémenter la validation des données
- [ ] Créer les services de gestion des cuves
- [ ] Créer les endpoints API pour les cuves
- [ ] Implémenter le barème de jauge (tables et API pour les mesures)
- [ ] Tester les relations station-cuve
- [ ] Tester les contrôles d'accès

**Phase 2 - Carburants et pistolets (jours 3-4)**
- [ ] Créer les services de gestion des carburants
- [ ] Créer les endpoints API pour les carburants
- [ ] Implémenter l'historique des prix des carburants
- [ ] Créer les services de gestion des pistolets
- [ ] Créer les endpoints API pour les pistolets
- [ ] Implémenter le suivi des index
- [ ] Tester les flux complets de gestion

**Phase 3 - Produits et familles (jours 5-6)**
- [ ] Créer les services de gestion des familles d'articles
- [ ] Créer les endpoints API pour les familles
- [ ] Créer les services de gestion des articles
- [ ] Créer les endpoints API pour les articles
- [ ] Implémenter la gestion des TVA et taxes
- [ ] Tester les relations famille-article
- [ ] Tester la gestion des unités de mesure

**Phase 4 - Clients, fournisseurs et employés (jours 7-8)**
- [ ] Créer les services de gestion des clients
- [ ] Créer les endpoints API pour les clients
- [ ] Implémenter les programmes de fidélisation
- [ ] Créer les services de gestion des fournisseurs
- [ ] Créer les endpoints API pour les fournisseurs
- [ ] Créer les services de gestion des employés
- [ ] Créer les endpoints API pour les employés
- [ ] Tester les fonctionnalités de suivi de performance

**Phase 5 - Trésoreries et modes de paiement (jour 9)**
- [ ] Créer les services de gestion des trésoreries
- [ ] Créer les endpoints API pour les trésoreries
- [ ] Implémenter les modes de paiement
- [ ] Tester l'association avec les stations
- [ ] Tester la gestion des assurances et incidents

**Phase 6 - Intégration et tests (jour 10)**
- [ ] Tester les flux complets
- [ ] Valider les contrôles d'accès
- [ ] Valider les contraintes d'intégrité
- [ ] Effectuer les tests d'intégration
- [ ] Documenter les API
- [ ] Finaliser la documentation technique

### Ordre recommandé
1. Commencer par les entités les plus fondamentales (stations)
2. Puis les entités qui en dépendent (cuves, carburants)
3. Ensuite les articles et familles
4. Puis clients, fournisseurs, employés
5. Enfin les trésoreries qui dépendent de presque tout

### Livrables attendus
- [ ] Services backend pour chaque entité
- [ ] Endpoints API complets
- [ ] Validation des données
- [ ] Contrôles d'accès
- [ ] Tests unitaires et d'intégration
- [ ] Documentation API
- [ ] Jeux de données de test

## 9. Risques & Points de vigilance

### Points sensibles
- Gestion des contraintes d'intégrité référentielles
- Contrôles d'accès limités par compagnie
- Performance des requêtes avec jointures multiples
- Gestion des relations many-to-many (clients-stations, employés-stations)
- Historisation des données (prix, index, etc.)

### Risques techniques
- Risque de violation des contraintes d'intégrité pendant les migrations
- Risque de performances dégradées avec de grandes quantités de données
- Risque de contournement des contrôles d'accès
- Risque de perte de données sans sauvegarde adéquate
- Risque de mauvaise gestion des relations entre entités

### Dette technique potentielle
- Mise en place d'un système de cache pour les données fréquemment utilisées
- Centralisation de la gestion des validations dans un framework dédié
- Mise en place d'un système de recherche avancée avec Elasticsearch
- Intégration de systèmes de monitoring pour les performances
- Mise en place d'un système d'événements pour les traitements asynchrones