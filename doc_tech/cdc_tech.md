# Cahier des Charges Technique - SuccessFuel ERP

## 1. Présentation du projet

**SuccessFuel** est un ERP (Enterprise Resource Planning) spécialement conçu pour la gestion complète des stations-service. Ce système informatisé permet d'automatiser, centraliser et sécuriser toutes les opérations liées à la gestion d'une station-service, de la vente de carburant aux opérations comptables et administratives.

Le système est construit avec une architecture modulaire permettant son extension à d'autres pays africains francophones.

---

## 2. Architecture technique

### 2.1 Technologies utilisées
- **Backend**: PostgreSQL (base de données relationnelle)
- **Langage de requêtes**: SQL standard avec extensions PostgreSQL
- **Identifiants uniques**: UUID (Universally Unique Identifier)
- **Gestion des dates/heures**: TIMESTAMPTZ (avec fuseau horaire)
- **Stocker des données semi-structurées**: JSONB pour certaines données flexibles

### 2.2 Structure de base de données
- **Normalisation**: Respect des normes de normalisation relationnelle (3NF)
- **Clés primaires**: Utilisation d'UUID pour toutes les clés primaires
- **Clés étrangères**: Relations avec contraintes d'intégrité référentielle
- **Indexation**: Index appropriés pour les performances
- **Sécurité**: Contraintes de validation et de sécurité intégrées

### 2.3 Modèle de conception
- **Modèle Entité-Relation**: Relations claires entre les différentes entités
- **Normalisation**: Respect des principes de normalisation pour minimiser la redondance
- **Extensibilité**: Architecture modulaire permettant l'ajout de fonctionnalités

---

## 3. Structure détaillée des tables

### 3.1 Tables de base

#### 3.1.1 Table `pays`
```sql
CREATE TABLE pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_pays CHAR(3) UNIQUE NOT NULL, -- Ex: FRA, MDG, SEN, CIV
    nom_pays VARCHAR(100) NOT NULL,
    devise_principale VARCHAR(3) NOT NULL, -- Code ISO de la devise
    taux_tva_par_defaut NUMERIC(5,2) DEFAULT 0,
    systeme_comptable VARCHAR(50) DEFAULT 'OHADA', -- Ex: OHADA, FRANCE, etc.
    date_application_tva DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.2 Table `compagnies`
```sql
CREATE TABLE compagnies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(30),
    email VARCHAR(150),
    nif VARCHAR(50), -- Numéro d'identification fiscale
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    pays_id UUID REFERENCES pays(id),
    devise_principale VARCHAR(3) DEFAULT 'MGA',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.3 Table `modules`
```sql
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);
```

#### 3.1.4 Table `permissions`
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,        -- Ex: 'lire_ventes', 'creer_vente', 'modifier_vente', 'supprimer_vente'
    description TEXT,
    module_id UUID REFERENCES modules(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.5 Table `profils`
```sql
CREATE TABLE profils (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id) ON DELETE SET NULL,  -- La compagnie qui a créé le profil
    description TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.6 Table `profil_permissions`
```sql
CREATE TABLE profil_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profil_id UUID REFERENCES profils(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(profil_id, permission_id)
);
```

#### 3.1.7 Table `stations`
```sql
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID REFERENCES compagnies(id),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    telephone VARCHAR(30),
    email VARCHAR(150),
    adresse TEXT,
    pays_id UUID REFERENCES pays(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.8 Table `utilisateurs`
```sql
CREATE TABLE utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    nom VARCHAR(150) NOT NULL,
    profil_id UUID REFERENCES profils(id) ON DELETE SET NULL,
    email VARCHAR(150),
    telephone VARCHAR(30),
    stations_user JSONB DEFAULT '[]'::jsonb,  -- Liste des UUID des stations auxquelles l'utilisateur a accès
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    last_login TIMESTAMPTZ,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.9 Table `auth_tokens`
```sql
CREATE TABLE auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
);
```

#### 3.1.10 Table `familles_articles`
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
```

#### 3.1.11 Table `plan_comptable`
```sql
CREATE TABLE plan_comptable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero VARCHAR(20) UNIQUE NOT NULL,           -- Numéro de compte comptable (ex: 100000)
    intitule VARCHAR(255) NOT NULL,               -- Nom du compte (ex: Capital & Réserves)
    classe VARCHAR(5) NOT NULL,                   -- Classe comptable (ex: 1, 2, etc.)
    type_compte VARCHAR(100) NOT NULL,            -- Type de compte (ex: Capitaux Propres)
    sens_solde VARCHAR(10) CHECK (sens_solde IN ('D', 'C')), -- Sens de solde
    compte_parent_id UUID REFERENCES plan_comptable(id) ON DELETE SET NULL, -- Lien vers le compte parent
    description TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    est_compte_racine BOOLEAN DEFAULT FALSE,
    est_compte_de_resultat BOOLEAN DEFAULT FALSE,
    est_compte_actif BOOLEAN DEFAULT TRUE,
    pays_id UUID REFERENCES pays(id),
    est_specifique_pays BOOLEAN DEFAULT FALSE,
    code_pays VARCHAR(3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.12 Table `type_tiers`
```sql
CREATE TABLE type_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    num_compte VARCHAR(10),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'article appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.13 Table `articles`
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
```

### 3.2 Tables fonctionnelles

#### 3.2.1 Table `carburants`
```sql
CREATE TABLE carburants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) UNIQUE NOT NULL,
    libelle VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- Ex: "Essence", "Gasoil", "Pétrole"
    compagnie_id UUID REFERENCES compagnies(id),
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.2 Table `cuves`
```sql
CREATE TABLE cuves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL,
    capacite NUMERIC(18,3) NOT NULL CHECK (capacite >= 0),
    carburant_id UUID REFERENCES carburants(id) ON DELETE SET NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la cuve appartient (via la station)
    UNIQUE (station_id, code),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.3 Table `barremage_cuves`
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
```

#### 3.2.4 Table `pompes`
```sql
CREATE TABLE pompes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL UNIQUE,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la pompe appartient (via la cuve/station)
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.5 Table `pistolets`
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
```

#### 3.2.6 Table `historique_index_pistolets`
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
```

#### 3.2.7 Table `reinitialisation_index_pistolets`
```sql
CREATE TABLE reinitialisation_index_pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pistolet_id UUID REFERENCES pistolets(id),
    ancien_index NUMERIC(18,3) NOT NULL,
    nouvel_index NUMERIC(18,3) NOT NULL,
    utilisateur_demande_id UUID REFERENCES utilisateurs(id),
    utilisateur_autorise_id UUID REFERENCES utilisateurs(id),
    motif TEXT NOT NULL,
    date_demande TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_autorisation TIMESTAMPTZ,
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Approuve', 'Rejete', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.8 Table `clients`
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
```

#### 3.2.9 Table `fournisseurs`
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
```

#### 3.2.10 Table `employes`
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
    station_ids JSONB DEFAULT '[]'::jsonb, -- Liste des stations auxquelles l'employé est rattaché
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'employé appartient
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.11 Table `methode_paiment`
```sql
CREATE TABLE methode_paiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_tresorerie VARCHAR(100) NOT NULL,
    mode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) NOT NULL DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 3.2.12 Table `tresoreries`
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
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    type_tresorerie UUID REFERENCES methode_paiment(id),
    methode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    solde_theorique NUMERIC(18,2) DEFAULT 0,  -- Solde recalculé à partir des mouvements
    solde_reel NUMERIC(18,2) DEFAULT 0,        -- Solde réel vérifié (par exemple lors des rapprochements)
    date_dernier_rapprochement TIMESTAMPTZ,    -- Dernière date de rapprochement
    utilisateur_dernier_rapprochement UUID REFERENCES utilisateurs(id),  -- Utilisateur qui a effectué le dernier rapprochement
    type_tresorerie_libelle VARCHAR(50),      -- Pour identifier la caisse boutique/principale, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.13 Table `tickets_caisse`
```sql
CREATE TABLE tickets_caisse (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_ticket VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    caissier_id UUID REFERENCES utilisateurs(id),
    date_ticket DATE NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME,
    montant_initial NUMERIC(18,2) DEFAULT 0,
    montant_final_theorique NUMERIC(18,2) DEFAULT 0,
    montant_final_reel NUMERIC(18,2) DEFAULT 0,
    ecart NUMERIC(18,2) DEFAULT 0, -- Différence entre théorique et réel
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    statut VARCHAR(20) DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'Ferme', 'Reconcilie')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.14 Table `arrets_compte_caissier`
```sql
CREATE TABLE arrets_compte_caissier (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_caisse_id UUID REFERENCES tickets_caisse(id),
    utilisateur_id UUID REFERENCES utilisateurs(id), -- L'utilisateur qui fait l'arrêt de compte
    date_arret DATE NOT NULL,
    heure_arret TIME NOT NULL,
    total_vente_especes NUMERIC(18,2) DEFAULT 0,
    total_vente_cb NUMERIC(18,2) DEFAULT 0,
    total_vente_chq NUMERIC(18,2) DEFAULT 0,
    total_vente_autre NUMERIC(18,2) DEFAULT 0,
    total_vente_credit NUMERIC(18,2) DEFAULT 0,
    total_vente_total NUMERIC(18,2) GENERATED ALWAYS AS (total_vente_especes + total_vente_cb + total_vente_chq + total_vente_autre + total_vente_credit) STORED,
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.15 Table `journal_entries`
```sql
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date_ecriture DATE NOT NULL,
    libelle TEXT NOT NULL,
    type_operation VARCHAR(30) CHECK (type_operation IN ('Achat','Vente','Tresorerie','Stock','Autre','Ouverture','Regul')) DEFAULT 'Autre',
    reference_operation VARCHAR(100),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'écriture appartient
    pays_id UUID REFERENCES pays(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_by UUID REFERENCES utilisateurs(id),
    est_valide BOOLEAN DEFAULT FALSE,
    valide_par UUID REFERENCES utilisateurs(id),
    date_validation TIMESTAMPTZ,
    type_document_origine VARCHAR(50),
    document_origine_id UUID,
    est_ouverture BOOLEAN DEFAULT FALSE,
    bilan_initial_id UUID REFERENCES bilan_initial(id)
);
```

#### 3.2.16 Table `journal_lines`
```sql
CREATE TABLE journal_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
    compte_num VARCHAR(20),
    compte_id UUID REFERENCES plan_comptable(id),
    debit NUMERIC(18,2) DEFAULT 0 CHECK (debit >= 0),
    credit NUMERIC(18,2) DEFAULT 0 CHECK (credit >= 0),
    sens CHAR(1) CHECK (sens IN ('D','C')) GENERATED ALWAYS AS (
        CASE WHEN debit > credit THEN 'D' WHEN credit > debit THEN 'C' ELSE 'D' END
    ) STORED
);
```

#### 3.2.17 Table `achats`
```sql
CREATE TABLE achats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    date_achat DATE NOT NULL,
    total NUMERIC(18,2) NOT NULL CHECK (total >= 0),
    reference_facture VARCHAR(100),
    observation TEXT,
    type_achat VARCHAR(20) DEFAULT 'Produits' CHECK (type_achat IN ('Produits', 'Carburants')) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'achat appartient
    pays_id UUID REFERENCES pays(id),
    devise_code VARCHAR(3) DEFAULT 'MGA',
    taux_change NUMERIC(15,6) DEFAULT 1.000000,
    journal_entry_id UUID,
    statut VARCHAR(40) DEFAULT 'En attente de livraison' CHECK (statut IN ('En attente de livraison', 'Livré','Annulé')) NOT NULL,
    date_livraison DATE, -- Nouveau champ pour la date de livraison
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.18 Table `bons_commande`
```sql
CREATE TABLE bons_commande (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_bon VARCHAR(50) UNIQUE NOT NULL,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    date_bon DATE NOT NULL,
    total NUMERIC(18,2) NOT NULL CHECK (total >= 0),
    observation TEXT,
    type_bon VARCHAR(20) DEFAULT 'Produits' CHECK (type_bon IN ('Produits', 'Carburants')) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id),
    statut VARCHAR(40) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Livre', 'Facture', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.19 Table `achats_stations`
```sql
CREATE TABLE achats_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(achat_id, station_id)  -- Empêche la duplication
);
```

#### 3.2.20 Table `achats_details`
```sql
CREATE TABLE achats_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    article_id UUID NOT NULL,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE, -- Ajout de la station
    cuve_id UUID REFERENCES cuves(id) ON DELETE SET NULL,     -- Ajout de la cuve pour les carburants
    quantite NUMERIC(18,3) NOT NULL CHECK (quantite >= 0),
    prix_unitaire NUMERIC(18,4) NOT NULL CHECK (prix_unitaire >= 0),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    montant NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED
);
```

#### 3.2.21 Table `dette_fournisseurs`
```sql
CREATE TABLE dettes_fournisseurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID NOT NULL REFERENCES fournisseurs(id),
    achat_id UUID NOT NULL REFERENCES achats(id),
    montant_achat NUMERIC(18,2) NOT NULL, -- Montant total (peut être négatif pour une créance)
    montant_paye NUMERIC(18,2) NOT NULL DEFAULT 0 CHECK (montant_paye >= 0), -- Montant déjà payé
    solde NUMERIC(18,2) NOT NULL, -- Solde restant (peut être négatif pour une créance)
    date_creation DATE NOT NULL DEFAULT CURRENT_DATE,
    reference_facture VARCHAR(100) NOT NULL,
    compagnie_id UUID NOT NULL REFERENCES compagnies(id),
    nb_jrs_creance INTEGER DEFAULT 0,
    date_prevu_paiement DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Paye', 'EnRetard', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### 3.2.22 Table `achats_tresorerie`
```sql
CREATE TABLE achats_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    tresorerie_id UUID REFERENCES tresoreries(id) ON DELETE SET NULL,
    montant NUMERIC(18,2) NOT NULL CHECK (montant >= 0),
    note_paiement JSONB DEFAULT '{}',
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.23 Table `mesures_livraison`
```sql
CREATE TABLE mesures_livraison (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    mesure_avant_livraison NUMERIC(18,3) NOT NULL,
    mesure_apres_livraison NUMERIC(18,3) NOT NULL,
    ecart_livraison NUMERIC(18,3) GENERATED ALWAYS AS (mesure_apres_livraison - mesure_avant_livraison) STORED,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.24 Table `tentatives_connexion`
```sql
CREATE TABLE tentatives_connexion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) NOT NULL,
    ip_connexion VARCHAR(45),
    resultat_connexion VARCHAR(10) CHECK (resultat_connexion IN ('Reussie', 'Echouee')),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.25 Table `evenements_securite`
```sql
CREATE TABLE evenements_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_evenement VARCHAR(50) NOT NULL, -- 'connexion_anormale', 'tentative_acces_non_autorise', etc.
    description TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    session_id VARCHAR(100),
    donnees_supplementaires JSONB,
    statut VARCHAR(20) DEFAULT 'NonTraite' CHECK (statut IN ('NonTraite', 'EnCours', 'Traite', 'Ferme')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.26 Table `modifications_sensibles`
```sql
CREATE TABLE modifications_sensibles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    type_operation VARCHAR(50) NOT NULL, -- 'modification_vente', 'annulation_vente', 'modification_stock', etc.
    objet_modifie VARCHAR(50), -- 'vente', 'stock', 'achat', etc.
    objet_id UUID,
    ancienne_valeur JSONB,
    nouvelle_valeur JSONB,
    seuil_alerte BOOLEAN DEFAULT FALSE, -- TRUE si dépasse un seuil défini
    commentaire TEXT,
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    statut VARCHAR(20) DEFAULT 'Enregistre' CHECK (statut IN ('Enregistre', 'Enquete', 'Traite', 'Ferme')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.3 Tables avancées

#### 3.3.1 Table `stocks`
```sql
CREATE TABLE stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE, -- Pour les carburants
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    stock_theorique NUMERIC(18,3) DEFAULT 0 CHECK (stock_theorique >= 0),
    stock_reel NUMERIC(18,3) DEFAULT 0 CHECK (stock_reel >= 0),
    ecart_stock NUMERIC(18,3) GENERATED ALWAYS AS (stock_reel - stock_theorique) STORED,
    compagnie_id UUID REFERENCES compagnies(id),
    est_initial BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.2 Table `stocks_mouvements`
```sql
CREATE TABLE stocks_mouvements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('Entree', 'Sortie', 'Ajustement', 'Inventaire', 'Initial')),
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire NUMERIC(18,4) DEFAULT 0, -- Pour calcul CUMP
    cout_total NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED,
    date_mouvement DATE NOT NULL,
    reference_operation VARCHAR(100), -- Référence à l'opération d'origine
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    valeur_stock_avant NUMERIC(18,2) DEFAULT 0,  -- Valeur du stock avant le mouvement
    valeur_stock_apres NUMERIC(18,2) DEFAULT 0,  -- Valeur du stock après le mouvement
    cout_unitaire_moyen_apres NUMERIC(18,4) DEFAULT 0, -- CUMP après le mouvement
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.3 Table `mouvements_tresorerie`
```sql
CREATE TABLE mouvements_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tresorerie_id UUID REFERENCES tresoreries(id),
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('Entree', 'Sortie', 'Annulation', 'Correction')),
    sous_type_mouvement VARCHAR(30) NOT NULL, -- 'Vente_carburant', 'Vente_boutique', 'Achat', 'Depense', etc.
    montant NUMERIC(18,2) NOT NULL,
    reference_operation VARCHAR(100), -- ID de l'opération source
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    date_mouvement DATE NOT NULL,
    date_enregistrement TIMESTAMPTZ NOT NULL DEFAULT now(),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Annule', 'Corrige', 'EnAttente')),
    mouvement_origine_id UUID REFERENCES mouvements_tresorerie(id), -- Pour les annulations
    compagnie_id UUID REFERENCES compagnies(id),
    CHECK ((type_mouvement = 'Annulation' AND mouvement_origine_id IS NOT NULL) OR (type_mouvement != 'Annulation'))
);
```

#### 3.3.4 Table `ventes`
```sql
CREATE TABLE ventes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    date_vente DATE NOT NULL,
    total_ht NUMERIC(18,2) NOT NULL CHECK (total_ht >= 0),
    total_ttc NUMERIC(18,2) NOT NULL CHECK (total_ttc >= 0),
    total_tva NUMERIC(18,2) NOT NULL CHECK (total_tva >= 0),
    reference_facture VARCHAR(100),
    observation TEXT,
    type_vente VARCHAR(20) DEFAULT 'Boutique' CHECK (type_vente IN ('Carburant', 'Boutique', 'Service')) NOT NULL,
    type_transaction VARCHAR(20) DEFAULT 'General' CHECK (type_transaction IN ('General', 'Boutique', 'Station', 'Carburant')),
    compagnie_id UUID REFERENCES compagnies(id),
    pays_id UUID REFERENCES pays(id),
    devise_code VARCHAR(3) DEFAULT 'MGA',
    taux_change NUMERIC(15,6) DEFAULT 1.000000,
    journal_entry_id UUID,
    statut VARCHAR(20) DEFAULT 'Valide' CHECK (statut IN ('Valide', 'Retour', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.5 Table `ventes_details`
```sql
CREATE TABLE ventes_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE SET NULL,
    pistolet_id UUID REFERENCES pistolets(id) ON DELETE SET NULL, -- Pour les ventes de carburant
    index_debut NUMERIC(18,3), -- Index de début pour le carburant
    index_fin NUMERIC(18,3),   -- Index de fin pour le carburant
    quantite NUMERIC(18,3) NOT NULL CHECK (quantite >= 0),
    prix_unitaire_ht NUMERIC(18,4) NOT NULL CHECK (prix_unitaire_ht >= 0),
    prix_unitaire_ttc NUMERIC(18,4) NOT NULL CHECK (prix_unitaire_ttc >= 0),
    taux_tva NUMERIC(5,2) DEFAULT 0,
    montant_ht NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire_ht) STORED,
    montant_tva NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht * (taux_tva / 100)) STORED,
    montant_ttc NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht + montant_tva) STORED,
    taxes_detaillees JSONB DEFAULT '{}', -- Détail des taxes par ligne
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.6 Table `ventes_tresorerie`
```sql
CREATE TABLE ventes_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id) ON DELETE CASCADE,
    tresorerie_id UUID REFERENCES tresoreries(id) ON DELETE SET NULL,
    montant NUMERIC(18,2) NOT NULL CHECK (montant >= 0),
    note_paiement JSONB DEFAULT '{}',
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.7 Table `permissions_tresorerie`
```sql
CREATE TABLE permissions_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    droits VARCHAR(20) CHECK (droits IN ('lecture', 'ecriture', 'validation', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 4. Contraintes et validations

### 4.1 Contraintes d'intégrité
- Toutes les tables utilisent des clés primaires UUID
- Les relations entre tables sont gérées par des clés étrangères avec contraintes
- Les contraintes de validation sont définies au niveau de la base de données (CHECK, NOT NULL, UNIQUE)
- Les champs obligatoires sont marqués NOT NULL

### 4.2 Contraintes de sécurité
- Les identifiants sont générés de manière aléatoire (gen_random_uuid())
- Les mots de passe sont stockés de manière chiffrée dans la base
- Les dates et heures sont stockées avec fuseau horaire (TIMESTAMPTZ)
- Les validations sont effectuées au niveau de la base de données
- Les données sensibles sont protégées par des contraintes d'accès

### 4.3 Contraintes spécifiques
- Les montants sont stockés avec une précision de 18 chiffres avec 2 décimales (NUMERIC(18,2))
- Les quantités sont stockées avec une précision de 18 chiffres avec 3 décimales (NUMERIC(18,3))
- Les prix sont stockés avec une précision de 18 chiffres avec 4 décimales (NUMERIC(18,4))
- Les taux sont stockés avec une précision de 5 chiffres avec 2 décimales (NUMERIC(5,2))

---

## 5. Vues et fonctions

### 5.1 Vues

#### 5.1.1 Vue `vue_permissions_utilisateur`
Affiche les permissions d'un utilisateur avec les détails de ses profils, modules et permissions.

#### 5.1.2 Vue `vue_grand_livre`
Affiche les écritures comptables avec les détails des comptes et des opérations.

#### 5.1.3 Vue `vue_balance_verif`
Affiche la balance de vérification des comptes avec les totaux débit et crédit.

#### 5.1.4 Vue `vue_soldes_comptes`
Affiche les soldes nets des comptes.

#### 5.1.5 Vue `vue_rendement_pompistes`
Affiche les indicateurs de rendement des pompistes par station et pays.

### 5.2 Fonctions

#### 5.2.1 Fonction `solde_client_disponible(client_id UUID)`
Calcule le solde disponible d'un client en prenant en compte les dépôts de garantie.

#### 5.2.2 Fonction `rapprochement_mensuel_tiers()`
Effectue le rapprochement mensuel des soldes de tiers (clients et fournisseurs).

#### 5.2.3 Fonction `update_fournisseur_solde()`
Met à jour le solde d'un fournisseur après une modification de dette.

#### 5.2.4 Fonction `calculer_solde_tresorerie(tresorerie_uuid UUID)`
Calcule le solde actuel d'une trésorerie.

#### 5.2.5 Fonction `modifier_mouvement_tresorerie()`
Modifie un mouvement de trésorerie avec processus de correction.

#### 5.2.6 Fonction `annuler_operation_trésorerie()`
Annule une opération de trésorerie avec processus de validation.

---

## 6. Triggers

### 6.1 Trigger `trigger_update_fournisseur_solde`
Mis à jour automatiquement le solde d'un fournisseur après une modification de dette.

### 6.2 Trigger `trigger_update_solde_tresorerie`
Met à jour le solde d'une trésorerie après un mouvement de trésorerie.

### 6.3 Trigger `trigger_verifier_pays_station`
Vérifie que les spécifications pays sont respectées lors de la création ou modification d'une station.

---

## 7. Index et optimisation

### 7.1 Index principaux
- `idx_journal_entries_date_compagnie` : Sur date_ecriture et compagnie_id
- `idx_journal_entries_type_compagnie` : Sur type_operation et compagnie_id
- `idx_journal_lines_compte_date` : Sur compte_num et entry_id
- `idx_journal_entries_dates` : Sur date_ecriture
- `idx_stocks_article_station` : Sur article_id et station_id
- `idx_ventes_date_client` : Sur date_vente et client_id
- `idx_achats_date_fournisseur` : Sur date_achat et fournisseur_id

### 7.2 Optimisation
- Les requêtes critiques sont optimisées avec des index appropriés
- Les vues sont indexées là où c'est pertinent
- Les colonnes de recherche fréquente sont indexées
- Les colonnes de tri fréquent sont indexées

---

## 8. Sécurité

### 8.1 Authentification
- Jetons d'authentification chiffrés
- Durée de vie limitée des jetons
- Historique des connexions

### 8.2 Autorisation
- Système de permissions basé sur les rôles (RBAC)
- Contrôles d'accès basés sur les stations
- Validations hiérarchiques pour les opérations sensibles

### 8.3 Journalisation
- Journalisation complète des actions des utilisateurs
- Journalisation des événements de sécurité
- Journalisation des modifications critiques
- Suivi des tentatives de connexion

---

## 9. Internationalisation

### 9.1 Gestion multi-pays
- Structure de base de données conçue pour le multilocale
- Support des spécifications locales par pays
- Tables dédiées pour les spécificités pays (pays, specifications_locales, configurations_pays)

### 9.2 Gestion des devises
- Support des taux de change
- Conversion automatique des montants
- Historique des taux de change

### 9.3 Gestion des taxes
- Système de taxation modulaire
- Configuration variable selon les pays
- Calcul dynamique selon les spécifications locales

### 9.4 Unités de mesure
- Gestion des différentes unités de mesure selon les pays
- Système de conversion entre unités
- Support des unités locales

---

## 10. Aspects techniques avancés

### 10.1 Génération automatique de champs
- Utilisation de GENERATED ALWAYS AS pour les calculs automatiques (ex: montants, écarts)
- Calculs de champs basés sur d'autres champs de la même table
- Calculs persistés (STORED) pour les champs fréquemment consultés

### 10.2 Données semi-structurées
- Utilisation de JSONB pour les données flexibles (ex: stations_user, mode_paiement)
- Indexation des données JSONB pour les performances
- Validation des structures JSONB

### 10.3 Gestion des contraintes complexes
- Utilisation de CHECK pour valider les valeurs
- Contraintes de domaine personnalisées
- Validations croisées entre champs