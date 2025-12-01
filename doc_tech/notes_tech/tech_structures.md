# Technical Specification - Gestion des structures (Mis à Jour)

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

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des opérations que sur les données appartenant à sa compagnie. Le **super administrateur** n'aura pas accès aux opérations quotidiennes de ce module (cuves, carburants, pistolets, produits, clients, fournisseurs, employés) et ne pourra effectuer que les opérations de gestion globale du système.

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
- Contrôles de validation selon l'importance des modifications

## 2. User Stories & Critères d'acceptation

### US-STR-001: En tant que gestionnaire, je veux gérer les cuves de stockage
- **Critères d'acceptation :**
  - Pouvoir enregistrer chaque cuve (type de carburant, capacité en litres)
  - Configurer le barème de jauge pour le calcul du volume selon la hauteur
  - Suivre la température pour correction volumétrique
  - Contrôler l'accès aux cuves
  - Enregistrer l'historique des mesures
  - Seuls les utilisateurs avec les permissions appropriées peuvent modifier les cuves
  - Les gérants de compagnie peuvent gérer toutes les cuves pour leur compagnie

### US-STR-002: En tant que gestionnaire, je veux gérer les carburants et leurs prix
- **Critères d'acceptation :**
  - Pouvoir gérer les différents types de carburant (essence, gasoil, pétrole)
  - Suivre les prix d'achat et de vente
  - Enregistrer l'historique des évolutions de prix
  - Suivre la qualité du carburant
  - Générer des rapports sur l'évolution des prix
  - Les gérants de compagnie peuvent gérer tous les carburants et prix pour leur compagnie

### US-STR-003: En tant que gestionnaire, je veux gérer les pistolets de distribution
- **Critères d'acceptation :**
  - Numéroter et associer chaque pistolet à une cuve spécifique
  - Suivre l'index initial et les relevés
  - Contrôler l'accès aux pistolets
  - Enregistrer l'historique des index
  - Suivre les performances de chaque pistolet
  - Les gérants de compagnie peuvent gérer tous les pistolets pour leur compagnie

### US-STR-004: En tant que gestionnaire, je veux gérer les produits et familles de produits
- **Critères d'acceptation :**
  - Créer et organiser les familles de produits
  - Gérer les produits de la boutique (alimentation, lubrifiants, etc.)
  - Suivre les prix d'achat et de vente
  - Enregistrer les historiques de prix
  - Les gérants de compagnie peuvent gérer tous les produits pour leur compagnie

### US-STR-005: En tant que gestionnaire, je veux gérer les clients, fournisseurs et employés
- **Critères d'acceptation :**
  - Enregistrer les informations des clients, fournisseurs et employés
  - Suivre les coordonnées et les informations contractuelles
  - Gérer les statuts (actif, inactif, etc.)
  - Mettre à jour les informations selon les changements
  - Les gérants de compagnie peuvent gérer tous les clients, fournisseurs et employés pour leur compagnie

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
```

## 4. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès aux fonctionnalités de gestion globale du système (pays, compagnies, stations, modules, profils, administrateurs, gérants de compagnie, plan comptable, configurations_pays, specifications_locales, paramètres système) mais PAS aux opérations quotidiennes de ce module (cuves, carburants, pistolets, produits, clients, fournisseurs, employés)
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations de gestion des structures pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les stations, employés, clients et fournisseurs concernés doivent appartenir à la même compagnie que l'utilisateur
- Les super administrateurs n'ont pas accès aux données opérationnelles quotidiennes des compagnies

## 5. Dépendances avec d'autres modules

### Module de sécurité
- Les structures sont soumises aux contrôles d'accès par compagnie
- Les validations de permissions sont requises pour les modifications

### Module des stocks
- Les cuves et carburants sont liés à la gestion des stocks
- Les produits sont utilisés dans les modules de vente et d'inventaire

### Module des ventes et achats
- Les structures fournissent les bases pour les opérations d'achat et de vente
- Les clients et fournisseurs sont gérés dans ce module

## 6. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités de gestion des structures pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les modifications respectent les limites de permissions