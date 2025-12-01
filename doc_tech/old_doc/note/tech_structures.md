# Technical Specification - Gestion des structures

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant la gestion des éléments physiques et organisationnels d'une station-service. Ce module se concentre sur les entités opérationnelles spécifiques à une station-service, basées sur les structures de base créées dans la phase 1. Cela inclut la gestion des cuves de stockage, des carburants, des pistolets de distribution, des produits, des fournisseurs, des clients, des employés et des trésoreries.

### Problème à résoudre
Le système SuccessFuel a besoin d'un module complet pour gérer les structures physiques et organisationnelles d'une station-service, y compris :
- Suivi des stocks et du volume dans les cuves
- Gestion des prix des carburants et produits
- Contrôle des équipements (pistolets, cuves)
- Gestion des fournisseurs, clients et employés
- Suivi des modes de paiement et des trésoreries

### Définition du périmètre
Le périmètre inclut :
- Gestion des cuves de stockage avec barème de jauge
- Gestion des carburants et historique des prix
- Gestion des pistolets de distribution
- Gestion des familles de produits et des produits
- Gestion des fournisseurs et clients
- Gestion des employés
- Gestion des trésoreries et modes de paiement
- Suivi des indices de performance et des indicateurs

## 2. User Stories & Critères d'acceptation

### US-STR-001: En tant que gestionnaire, je veux gérer les cuves de stockage
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des cuves
  - Chaque cuve est associée à une station spécifique
  - Chaque cuve a un type de carburant et une capacité en litres
  - Pouvoir définir un barème de jauge pour le calcul du volume selon la hauteur
  - Pouvoir suivre la température pour correction volumétrique

### US-STR-002: En tant que gestionnaire, je veux gérer les carburants
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des types de carburant
  - Chaque carburant a un code unique, libellé, type (essence, gasoil, pétrole)
  - Suivre les prix d'achat et de vente
  - Conserver un historique des évolutions de prix
  - Pouvoir suivre la qualité du carburant

### US-STR-003: En tant que gestionnaire, je veux gérer les pistolets de distribution
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des pistolets
  - Chaque pistolet est numéroté et associé à une cuve spécifique
  - Pouvoir suivre l'index initial et les relevés d'index
  - Pouvoir contrôler l'accès aux pistolets

### US-STR-004: En tant que gestionnaire, je veux gérer les familles de produits
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des familles de produits
  - Chaque famille est rattachée à une compagnie
  - Pouvoir définir une hiérarchie entre familles (parent/enfant)
  - Pouvoir gérer des familles pour produits de boutique et services annexes

### US-STR-005: En tant que gestionnaire, je veux gérer les produits
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des produits
  - Chaque produit a un code, libellé, code-barres, famille, prix d'achat, prix de vente
  - Gérer les stocks (quantité, unité de mesure, stock minimal)
  - Gérer les taxes applicables et la TVA
  - Pouvoir gérer des additifs et mélanges

### US-STR-006: En tant que gestionnaire, je veux gérer les fournisseurs
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des fournisseurs
  - Chaque fournisseur a un code unique, nom, coordonnées
  - Pouvoir suivre le solde et les dettes
  - Conserver un historique des transactions
  - Pouvoir associer un fournisseur à une ou plusieurs stations
  - Pouvoir suivre l'historique de qualité des livraisons

### US-STR-007: En tant que gestionnaire, je veux gérer les clients
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des clients
  - Chaque client a un code unique, nom, coordonnées
  - Pouvoir suivre le solde et les créances
  - Conserver un historique des paiements
  - Pouvoir associer un client à une ou plusieurs stations
  - Pouvoir gérer des cartes de carburant
  - Pouvoir gérer des contrats de ravitaillement

### US-STR-008: En tant que gestionnaire, je veux gérer les employés
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des employés
  - Chaque employé a un code unique, nom, prénom, poste, salaire de base
  - Pouvoir associer un employé à une ou plusieurs stations
  - Pouvoir suivre les avances et créances sur salaire
  - Pouvoir suivre la productivité et les indicateurs de performance

### US-STR-009: En tant que gestionnaire, je veux gérer les trésoreries et modes de paiement
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des trésoreries
  - Chaque trésorerie a un code unique, libellé, solde, devise
  - Pouvoir associer une trésorerie à une ou plusieurs stations
  - Pouvoir gérer les fournisseurs de trésoreries (banques, etc.)
  - Pouvoir configurer les modes de paiement acceptés
  - Pouvoir suivre les incidents de sécurité

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: cuves
```sql
CREATE TABLE cuves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL,
    capacite NUMERIC(18,3) NOT NULL CHECK (capacite >= 0),
    carburant_id UUID REFERENCES carburants(id) ON DELETE SET NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la cuve appartient (via la station)
    temperature NUMERIC(5,2) DEFAULT 0, -- Température pour correction volumétrique
    UNIQUE (station_id, code),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_cuves_station ON cuves(station_id);
CREATE INDEX idx_cuves_carburant ON cuves(carburant_id);
CREATE INDEX idx_cuves_compagnie ON cuves(compagnie_id);
CREATE INDEX idx_cuves_statut ON cuves(statut);
```

#### Table: barremage_cuves
```sql
CREATE TABLE barremage_cuves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    hauteur NUMERIC(18,3) NOT NULL CHECK (hauteur >= 0),
    volume NUMERIC(18,3) NOT NULL CHECK (volume >= 0),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    compagnie_id UUID REFERENCES compagnies(id)
);

-- Index pour les performances
CREATE INDEX idx_barremage_cuve ON barremage_cuves(cuve_id);
CREATE INDEX idx_barremage_station ON barremage_cuves(station_id);
CREATE INDEX idx_barremage_statut ON barremage_cuves(statut);
```

#### Table: carburants
```sql
CREATE TABLE carburants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) UNIQUE NOT NULL,
    libelle VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- Ex: "Essence", "Gasoil", "Pétrole"
    compagnie_id UUID REFERENCES compagnies(id),
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    qualite NUMERIC(3,2) DEFAULT 1.00, -- Note de qualité sur 10
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_carburants_code ON carburants(code);
CREATE INDEX idx_carburants_type ON carburants(type);
CREATE INDEX idx_carburants_compagnie ON carburants(compagnie_id);
CREATE INDEX idx_carburants_statut ON carburants(statut);
```

#### Table: historique_prix_carburants
```sql
CREATE TABLE historique_prix_carburants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID NOT NULL REFERENCES carburants(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_carburant ON historique_prix_carburants(carburant_id);
CREATE INDEX idx_historique_date ON historique_prix_carburants(date_application);
```

#### Table: pompes
```sql
CREATE TABLE pompes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL UNIQUE,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la pompe appartient (via la cuve/station)
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_pompes_station ON pompes(station_id);
CREATE INDEX idx_pompes_compagnie ON pompes(compagnie_id);
CREATE INDEX idx_pompes_statut ON pompes(statut);
```

#### Table: pistolets
```sql
CREATE TABLE pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) NOT NULL,
    pompe_id UUID REFERENCES pompes(id),
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    index_initiale NUMERIC(18,3) DEFAULT 0, -- Index initial du pistolet
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le pistolet appartient (via la cuve/station)
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_pistolets_pompe ON pistolets(pompe_id);
CREATE INDEX idx_pistolets_cuve ON pistolets(cuve_id);
CREATE INDEX idx_pistolets_compagnie ON pistolets(compagnie_id);
CREATE INDEX idx_pistolets_statut ON pistolets(statut);
```

#### Table: historique_index_pistolets
```sql
CREATE TABLE historique_index_pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pistolet_id UUID REFERENCES pistolets(id),
    index_releve NUMERIC(18,3) NOT NULL,
    date_releve DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_pistolets_pistolet ON historique_index_pistolets(pistolet_id);
CREATE INDEX idx_historique_pistolets_date ON historique_index_pistolets(date_releve);
```

#### Table: familles_articles
```sql
CREATE TABLE familles_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la famille d'articles appartient
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    parent_id UUID NULL REFERENCES familles_articles(id), -- Référence à la famille parente (NULL si racine)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_familles_articles_code ON familles_articles(code);
CREATE INDEX idx_familles_articles_compagnie ON familles_articles(compagnie_id);
CREATE INDEX idx_familles_articles_parent ON familles_articles(parent_id);
```

#### Table: articles
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) UNIQUE NOT NULL,
    libelle VARCHAR(150) NOT NULL,
    codebarre VARCHAR(100) UNIQUE,
    famille_id UUID REFERENCES familles_articles(id) ON DELETE SET NULL,
    unite VARCHAR(20) DEFAULT 'Litre',
    unite_principale VARCHAR(10) REFERENCES unites_mesure(code_unite),
    unite_stock VARCHAR(10) REFERENCES unites_mesure(code_unite),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'article appartient
    type_article VARCHAR(20) DEFAULT 'produit' CHECK (type_article IN ('produit', 'service')),
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    tva NUMERIC(5,2) DEFAULT 0,
    taxes_applicables JSONB DEFAULT '[]'::jsonb, -- Liste des IDs de taxes
    stock_minimal NUMERIC(18,3) DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_articles_code ON articles(code);
CREATE INDEX idx_articles_codebarre ON articles(codebarre);
CREATE INDEX idx_articles_famille ON articles(famille_id);
CREATE INDEX idx_articles_compagnie ON articles(compagnie_id);
CREATE INDEX idx_articles_statut ON articles(statut);
```

#### Table: historique_prix_articles
```sql
CREATE TABLE historique_prix_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_articles ON historique_prix_articles(article_id);
CREATE INDEX idx_historique_articles_date ON historique_prix_articles(date_application);
```

#### Table: fournisseurs
```sql
CREATE TABLE fournisseurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(30),
    nif VARCHAR(50),
    email VARCHAR(150),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le fournisseur appartient
    station_ids JSONB DEFAULT '[]'::jsonb, -- Optionnel : station à laquelle le fournisseur est rattaché
    type_tiers_id UUID REFERENCES type_tiers(id) ON DELETE SET NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    nb_jrs_creance INTEGER DEFAULT 0,
    solde_comptable NUMERIC(18,2) DEFAULT 0, -- Solde actuel du fournisseur
    solde_confirme NUMERIC(18,2) DEFAULT 0, -- Solde confirmé lors des rapprochements
    date_dernier_rapprochement TIMESTAMPTZ, -- Dernière date de rapprochement
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_fournisseurs_code ON fournisseurs(code);
CREATE INDEX idx_fournisseurs_compagnie ON fournisseurs(compagnie_id);
CREATE INDEX idx_fournisseurs_statut ON fournisseurs(statut);
```

#### Table: clients
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(30),
    nif VARCHAR(50),
    email VARCHAR(150),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le client appartient
    station_ids JSONB DEFAULT '[]'::jsonb, -- Optionnel : station à laquelle le client est rattaché
    type_tiers_id UUID REFERENCES type_tiers(id) ON DELETE SET NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    nb_jrs_creance INTEGER DEFAULT 0,
    solde_comptable NUMERIC(18,2) DEFAULT 0, -- Solde actuel du client
    solde_confirme NUMERIC(18,2) DEFAULT 0, -- Solde confirmé lors des rapprochements
    date_dernier_rapprochement TIMESTAMPTZ, -- Dernière date de rapprochement
    devise_facturation VARCHAR(3) DEFAULT 'MGA',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_clients_code ON clients(code);
CREATE INDEX idx_clients_compagnie ON clients(compagnie_id);
CREATE INDEX idx_clients_statut ON clients(statut);
```

#### Table: employes
```sql
CREATE TABLE employes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    prenom VARCHAR(150),
    adresse TEXT,
    telephone VARCHAR(30),
    poste VARCHAR(100), -- Poste occupé (ex: pompiste, caissier, etc.)
    salaire_base NUMERIC(18,2) DEFAULT 0,
    avances NUMERIC(18,2) DEFAULT 0, -- Avances sur salaire
    creances NUMERIC(18,2) DEFAULT 0, -- Créances sur salaire
    station_ids JSONB DEFAULT '[]'::jsonb, -- Liste des stations auxquelles l'employé est rattaché
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'employé appartient
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_employes_code ON employes(code);
CREATE INDEX idx_employes_compagnie ON employes(compagnie_id);
CREATE INDEX idx_employes_statut ON employes(statut);
```

#### Table: tresoreries
```sql
CREATE TABLE tresoreries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la trésorerie appartient
    station_ids JSONB DEFAULT '[]'::jsonb, -- Optionnel : station à laquelle la trésorerie est rattachée
    solde NUMERIC(18,2) DEFAULT 0 CHECK (solde >= -1000000000),
    devise_code VARCHAR(3) DEFAULT 'MGA',
    taux_change NUMERIC(15,6) DEFAULT 1.000000,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL, -- Référence corrigée
    type_tresorerie UUID REFERENCES methode_paiment(id),
    methode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    solde_theorique NUMERIC(18,2) DEFAULT 0,  -- Solde recalculé à partir des mouvements
    solde_reel NUMERIC(18,2) DEFAULT 0,        -- Solde réel vérifié (par exemple lors des rapprochements)
    date_dernier_rapprochement TIMESTAMPTZ,    -- Dernière date de rapprochement
    utilisateur_dernier_rapprochement UUID REFERENCES utilisateurs(id),  -- Référence corrigée
    type_tresorerie_libelle VARCHAR(50),      -- Pour identifier la caisse boutique/principale, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_tresoreries_code ON tresoreries(code);
CREATE INDEX idx_tresoreries_compagnie ON tresoreries(compagnie_id);
CREATE INDEX idx_tresoreries_statut ON tresoreries(statut);
```

### 3.2 Relations
- `stations.id` → `cuves.station_id` (One-to-Many)
- `carburants.id` → `cuves.carburant_id` (One-to-Many)
- `compagnies.id` → `cuves.compagnie_id` (One-to-Many)
- `cuves.id` → `barremage_cuves.cuve_id` (One-to-Many)
- `stations.id` → `barremage_cuves.station_id` (One-to-Many)
- `compagnies.id` → `barremage_cuves.compagnie_id` (One-to-Many)
- `compagnies.id` → `carburants.compagnie_id` (One-to-Many)
- `carburants.id` → `historique_prix_carburants.carburant_id` (One-to-Many)
- `utilisateurs.id` → `historique_prix_carburants.utilisateur_id` (One-to-Many)
- `stations.id` → `pompes.station_id` (One-to-Many)
- `compagnies.id` → `pompes.compagnie_id` (One-to-Many)
- `pompes.id` → `pistolets.pompe_id` (One-to-Many)
- `cuves.id` → `pistolets.cuve_id` (One-to-Many)
- `compagnies.id` → `pistolets.compagnie_id` (One-to-Many)
- `pistolets.id` → `historique_index_pistolets.pistolet_id` (One-to-Many)
- `utilisateurs.id` → `historique_index_pistolets.utilisateur_id` (One-to-Many)
- `compagnies.id` → `familles_articles.compagnie_id` (One-to-Many)
- `familles_articles.id` → `familles_articles.parent_id` (Self-referencing)
- `familles_articles.id` → `articles.famille_id` (One-to-Many)
- `unites_mesure.code_unite` → `articles.unite_principale` (One-to-Many)
- `unites_mesure.code_unite` → `articles.unite_stock` (One-to-Many)
- `compagnies.id` → `articles.compagnie_id` (One-to-Many)
- `articles.id` → `historique_prix_articles.article_id` (One-to-Many)
- `utilisateurs.id` → `historique_prix_articles.utilisateur_id` (One-to-Many)
- `compagnies.id` → `fournisseurs.compagnie_id` (One-to-Many)
- `type_tiers.id` → `fournisseurs.type_tiers_id` (One-to-Many)
- `compagnies.id` → `clients.compagnie_id` (One-to-Many)
- `type_tiers.id` → `clients.type_tiers_id` (One-to-Many)
- `compagnies.id` → `employes.compagnie_id` (One-to-Many)
- `compagnies.id` → `tresoreries.compagnie_id` (One-to-Many)
- `fournisseurs.id` → `tresoreries.fournisseur_id` (One-to-Many)
- `methode_paiment.id` → `tresoreries.type_tresorerie` (One-to-Many)
- `utilisateurs.id` → `tresoreries.utilisateur_dernier_rapprochement` (One-to-Many)

### 3.3 Triggers et règles d'intégrité
```sql
-- Trigger pour mettre à jour le champ updated_at sur les entités de structure
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_cuves_updated_at
    BEFORE UPDATE ON cuves
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_carburants_updated_at
    BEFORE UPDATE ON carburants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_pistolets_updated_at
    BEFORE UPDATE ON pistolets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_fournisseurs_updated_at
    BEFORE UPDATE ON fournisseurs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_employes_updated_at
    BEFORE UPDATE ON employes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_tresoreries_updated_at
    BEFORE UPDATE ON tresoreries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## 4. API Backend

### 4.1 Gestion des cuves

#### POST /api/v1/tanks
- **Description**: Créer une nouvelle cuve
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "station_id": "uuid",
    "code": "string (40 chars max)",
    "capacite": "number",
    "carburant_id": "uuid",
    "temperature": "number"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "station_id": "uuid",
        "code": "string",
        "capacite": "number",
        "carburant_id": "uuid",
        "compagnie_id": "uuid",
        "temperature": "number",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Non autorisé
  - 403: Accès interdit
  - 409: Code de cuve déjà existant pour cette station

#### GET /api/v1/tanks/{tank_id}
- **Description**: Récupérer les détails d'une cuve
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "station_id": "uuid",
        "code": "string",
        "capacite": "number",
        "carburant_id": "uuid",
        "compagnie_id": "uuid",
        "temperature": "number",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

#### PUT /api/v1/tanks/{tank_id}
- **Description**: Mettre à jour une cuve
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (40 chars max)",
    "capacite": "number",
    "carburant_id": "uuid",
    "temperature": "number",
    "statut": "string"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "station_id": "uuid",
        "code": "string",
        "capacite": "number",
        "carburant_id": "uuid",
        "compagnie_id": "uuid",
        "temperature": "number",
        "statut": "string",
        "updated_at": "timestamp"
    }
}
```

### 4.2 Gestion des carburants

#### POST /api/v1/fuels
- **Description**: Créer un nouveau carburant
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (40 chars max)",
    "libelle": "string (150 chars max)",
    "type": "string (50 chars max)",
    "prix_achat": "number",
    "prix_venue": "number"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "type": "string",
        "compagnie_id": "uuid",
        "prix_achat": "number",
        "prix_vente": "number",
        "qualite": "number",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

#### GET /api/v1/fuels
- **Description**: Lister tous les carburants
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - type: "string" (Essence, Gasoil, Pétrole, etc.)
  - statut: "string" (Actif, Inactif, Supprime)
  - limit: "integer"
  - offset: "integer"
- **Réponse**:
```json
{
    "success": true,
    "pagination": {
        "total": "integer",
        "limit": "integer",
        "offset": "integer"
    },
    "data": [
        {
            "id": "uuid",
            "code": "string",
            "libelle": "string",
            "type": "string",
            "compagnie_id": "uuid",
            "prix_achat": "number",
            "prix_vente": "number",
            "qualite": "number",
            "statut": "string",
            "created_at": "timestamp",
            "updated_at": "timestamp"
        }
    ]
}
```

### 4.3 Gestion des pistolets

#### POST /api/v1/nozzles
- **Description**: Créer un nouveau pistolet
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (40 chars max)",
    "pompe_id": "uuid",
    "cuve_id": "uuid",
    "index_initiale": "number"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "pompe_id": "uuid",
        "cuve_id": "uuid",
        "index_initiale": "number",
        "compagnie_id": "uuid",
        "statut": "string",
        "created_at": "timestamp"
    }
}
```

### 4.4 Gestion des produits et familles

#### POST /api/v1/product-families
- **Description**: Créer une nouvelle famille de produits
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (10 chars max)",
    "libelle": "string (100 chars max)",
    "parent_id": "uuid"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "compagnie_id": "uuid",
        "parent_id": "uuid",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

#### POST /api/v1/products
- **Description**: Créer un nouveau produit
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (40 chars max)",
    "libelle": "string (150 chars max)",
    "codebarre": "string (100 chars max)",
    "famille_id": "uuid",
    "unite": "string (20 chars max)",
    "prix_achat": "number",
    "prix_vente": "number",
    "tva": "number",
    "stock_minimal": "number"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "codebarre": "string",
        "famille_id": "uuid",
        "unite": "string",
        "compagnie_id": "uuid",
        "prix_achat": "number",
        "prix_vente": "number",
        "tva": "number",
        "stock_minimal": "number",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### 4.5 Gestion des fournisseurs

#### POST /api/v1/suppliers
- **Description**: Créer un nouveau fournisseur
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (20 chars max)",
    "nom": "string (150 chars max)",
    "adresse": "string",
    "telephone": "string (30 chars max)",
    "email": "string (150 chars max)",
    "nif": "string (50 chars max)",
    "station_ids": ["uuid", ...]
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "nom": "string",
        "adresse": "string",
        "telephone": "string",
        "email": "string",
        "nif": "string",
        "compagnie_id": "uuid",
        "station_ids": ["uuid", ...],
        "statut": "string",
        "nb_jrs_creance": "integer",
        "solde_comptable": "number",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### 4.6 Gestion des clients

#### POST /api/v1/clients
- **Description**: Créer un nouveau client
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (20 chars max)",
    "nom": "string (150 chars max)",
    "adresse": "string",
    "telephone": "string (30 chars max)",
    "email": "string (150 chars max)",
    "nif": "string (50 chars max)",
    "station_ids": ["uuid", ...]
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "nom": "string",
        "adresse": "string",
        "telephone": "string",
        "email": "string",
        "nif": "string",
        "compagnie_id": "uuid",
        "station_ids": ["uuid", ...],
        "statut": "string",
        "nb_jrs_creance": "integer",
        "solde_comptable": "number",
        "devise_facturation": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### 4.7 Gestion des employés

#### POST /api/v1/employees
- **Description**: Créer un nouvel employé
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (20 chars max)",
    "nom": "string (150 chars max)",
    "prenom": "string (150 chars max)",
    "adresse": "string",
    "telephone": "string (30 chars max)",
    "poste": "string (100 chars max)",
    "salaire_base": "number",
    "station_ids": ["uuid", ...]
}
```
- **Réponse**:
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
        "salaire_base": "number",
        "avances": "number",
        "creances": "number",
        "compagnie_id": "uuid",
        "station_ids": ["uuid", ...],
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### 4.8 Gestion des trésoreries

#### POST /api/v1/treasuries
- **Description**: Créer une nouvelle trésorerie
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (20 chars max)",
    "libelle": "string (100 chars max)",
    "station_ids": ["uuid", ...],
    "devise_code": "string (3 chars max)",
    "fournisseur_id": "uuid",
    "type_tresorerie": "uuid"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "compagnie_id": "uuid",
        "station_ids": ["uuid", ...],
        "solde": "number",
        "devise_code": "string",
        "fournisseur_id": "uuid",
        "type_tresorerie": "uuid",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

## 5. Logique Métier

### 5.1 Règles de gestion des cuves
- Chaque cuve est associée à une seule station
- Une cuve ne peut contenir qu'un seul type de carburant à la fois
- La capacité d'une cuve est fixe et positive
- Le barème de jauge permet de calculer le volume réel en fonction de la hauteur
- La température est utilisée pour la correction volumétrique
- Une cuve inactive ne peut pas recevoir de livraisons ou faire l'objet de ventes

### 5.2 Règles de gestion des carburants
- Chaque carburant a un prix d'achat et de vente
- Le prix d'un carburant peut évoluer dans le temps (historisation)
- La qualité du carburant est notée sur 10
- Chaque carburant est rattaché à une seule compagnie
- Un historique des prix est conservé pour chaque carburant

### 5.3 Règles de gestion des pistolets
- Chaque pistolet est associé à une seule pompe
- Chaque pistolet est associé à une seule cuve
- L'index initial est le point de départ pour le relevé des volumes distribués
- Un pistolet inactive n'est pas utilisé pour les ventes

### 5.4 Règles de gestion des produits
- Chaque produit appartient à une seule famille
- La hiérarchie des familles permet une classification fine des produits
- Les produits ont des prix d'achat et de vente
- Le stock minimal permet de déclencher des alertes de réapprovisionnement
- Les historiques de prix sont conservés pour chaque produit

### 5.5 Règles de gestion des fournisseurs
- Chaque fournisseur est rattaché à une seule compagnie
- Les fournisseurs peuvent être associés à plusieurs stations
- Le solde comptable est calculé à partir des transactions
- Les fournisseurs peuvent être classés par qualité de service

### 5.6 Règles de gestion des clients
- Chaque client est rattaché à une seule compagnie
- Les clients peuvent être associés à plusieurs stations
- Le solde comptable est calculé à partir des transactions
- Les clients peuvent avoir des contrats de ravitaillement ou des cartes de carburant

### 5.7 Règles de gestion des employés
- Chaque employé est rattaché à une seule compagnie
- Les employés peuvent être associés à plusieurs stations
- Le salaire de base peut être ajusté avec des avances et des créances
- Les indicateurs de performance peuvent être suivis par employé

### 5.8 Règles de gestion des trésoreries
- Chaque trésorerie est rattachée à une seule compagnie
- Les trésoreries peuvent être associées à plusieurs stations
- Les trésoreries ont un solde qui évolue avec les mouvements
- Les trésoreries peuvent être rattachées à des fournisseurs (banques, etc.)

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
[compagnies] 1 -- * [cuves]
[stations] 1 -- * [cuves]
[carburants] 1 -- * [cuves]

[cuves] 1 -- * [barremage_cuves]
[stations] 1 -- * [barremage_cuves]
[compagnies] 1 -- * [barremage_cuves]

[compagnies] 1 -- * [carburants]
[carburants] 1 -- * [historique_prix_carburants]
[utilisateurs] 1 -- * [historique_prix_carburants]

[stations] 1 -- * [pompes]
[compagnies] 1 -- * [pompes]

[pompes] 1 -- * [pistolets]
[cuves] 1 -- * [pistolets]
[compagnies] 1 -- * [pistolets]

[pistolets] 1 -- * [historique_index_pistolets]
[utilisateurs] 1 -- * [historique_index_pistolets]

[compagnies] 1 -- * [familles_articles]
[familles_articles] 1 -- * [familles_articles] (parent-enfant)

[familles_articles] 1 -- * [articles]
[unites_mesure] 1 -- * [articles] (unite_principale)
[unites_mesure] 1 -- * [articles] (unite_stock)
[compagnies] 1 -- * [articles]

[articles] 1 -- * [historique_prix_articles]
[utilisateurs] 1 -- * [historique_prix_articles]

[compagnies] 1 -- * [fournisseurs]
[type_tiers] 1 -- * [fournisseurs]

[compagnies] 1 -- * [clients]
[type_tiers] 1 -- * [clients]

[compagnies] 1 -- * [employes]

[compagnies] 1 -- * [tresoreries]
[fournisseurs] 1 -- * [tresoreries]
[methode_paiment] 1 -- * [tresoreries]
[utilisateurs] 1 -- * [tresoreries] (utilisateur_dernier_rapprochement)
```

### 6.2 Diagramme de séquence (création d'une cuve)
```
Gestionnaire -> API: POST /api/v1/tanks (station_id, code, capacite, carburant_id)
API -> Database: Vérifier que la station existe et appartient à la compagnie de l'utilisateur
Database -> API: Station trouvée
API -> Database: Vérifier que le code de cuve est unique pour cette station
Database -> API: Code disponible
API -> Database: Créer la cuve
Database -> API: Cuve créée
API -> Gestionnaire: {success: true, data: {...}}
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test des validations de données pour chaque modèle
- Test des triggers de mise à jour des timestamps
- Test de la logique d'association des entités
- Test des contraintes de base de données

### 7.2 Tests d'intégration
- Test de la création complète d'une cuve avec son barème de jauge
- Test de la création d'un produit avec sa famille
- Test de l'association d'un fournisseur à une ou plusieurs stations
- Test de l'historisation des prix pour carburants et produits

### 7.3 Tests de charge/performance
- Test de la performance lors de la gestion de nombreuses cuves
- Test de la performance lors de la récupération des historiques de prix
- Test de la performance lors de l'accès concurrentiel aux données

### 7.4 Jeux de données de test
```sql
-- Création de données de test pour les structures
INSERT INTO carburants (code, libelle, type, compagnie_id, prix_achat, prix_vente, statut, created_at, updated_at) VALUES
('SP98', 'Super Plus 98', 'Essence', 'COMP1-UUID', 4200, 4800, 'Actif', now(), now()),
('GASOIL', 'Gasoil ordinaire', 'Gasoil', 'COMP1-UUID', 3800, 4400, 'Actif', now(), now());

INSERT INTO familles_articles (code, libelle, compagnie_id, statut, created_at, updated_at) VALUES
('CARBURANT', 'Carburants', 'COMP1-UUID', 'Actif', now(), now()),
('LUBRIFIANT', 'Lubrifiants', 'COMP1-UUID', 'Actif', now(), now()),
('ALIMENT', 'Aliments', 'COMP1-UUID', 'Actif', now(), now());
```

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Création des modèles SQLAlchemy pour les tables : cuves, barremage_cuves, carburants, historique_prix_carburants, pompes, pistolets, historique_index_pistolets, familles_articles, articles, historique_prix_articles, fournisseurs, clients, employes, tresoreries
- [ ] Mise en place des relations entre les modèles
- [ ] Développement des services pour la gestion des cuves avec barème de jauge
- [ ] Développement des services pour la gestion des carburants et historique des prix
- [ ] Développement des services pour la gestion des pistolets et relevés d'index
- [ ] Développement des services pour la gestion des familles de produits
- [ ] Développement des services pour la gestion des produits et historique des prix
- [ ] Développement des services pour la gestion des fournisseurs
- [ ] Développement des services pour la gestion des clients
- [ ] Développement des services pour la gestion des employés
- [ ] Développement des services pour la gestion des trésoreries
- [ ] Développement des endpoints API pour chaque service
- [ ] Mise en place des validations de données
- [ ] Mise en place des triggers pour les timestamps
- [ ] Tests unitaires et d'intégration
- [ ] Documentation des API

### 8.2 Ordre recommandé
1. Création des modèles et migrations des tables
2. Développement des services de base (carburants, familles de produits)
3. Développement des services pour la gestion des cuves et pistolets
4. Développement des services pour la gestion des produits
5. Développement des services pour la gestion des parties prenantes (fournisseurs, clients, employés)
6. Développement des services pour la gestion des trésoreries
7. Tests et documentation

### 8.3 Livrables attendus
- Modèles SQLAlchemy pour toutes les tables du module structures
- Services backend pour la gestion des différentes entités
- Endpoints API complets pour la gestion des structures
- Système de validation des données
- Système de gestion des historiques de prix
- Documentation API
- Jeux de tests unitaires et d'intégration

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La gestion des volumes dans les cuves avec le barème de jauge
- La synchronisation des prix historiques pour les carburants et produits
- La gestion des multiples stations pour les fournisseurs, clients et employés
- La performance du système avec un grand nombre d'entités

### 9.2 Risques techniques
- Risque de performance lié à la gestion de nombreuses cuves et pistolets
- Risque d'incohérence dans l'historique des prix
- Risque d'erreurs dans le calcul des volumes en fonction de la température
- Risque de conflits si plusieurs utilisateurs modifient les mêmes entités simultanément

### 9.3 Dette technique potentielle
- Mise en place d'un système de sauvegarde et de récupération des données
- Mise en place d'outils d'analyse et de reporting des indicateurs
- Mise en place de rôles par défaut pour la gestion des structures
- Mise en place d'une interface d'administration plus avancée