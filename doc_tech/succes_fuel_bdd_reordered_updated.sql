-- succes_fuel_bdd_reordered.sql
-- Fichier de la base de données pour l'ERP SuccessFuel
-- Tables réorganisées dans l'ordre correct des dépendances

-- Activer l'extension UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1) Tables de base sans dépendances
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

CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);

-- 2) Tables dépendant uniquement de pays
CREATE TABLE unites_mesure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_unite VARCHAR(10) UNIQUE NOT NULL, -- 'L', 'GAL', 'KG', 'TON', etc.
    libelle_unite VARCHAR(50) NOT NULL,
    pays_id UUID REFERENCES pays(id), -- Unités spécifiques à un pays
    est_standard BOOLEAN DEFAULT FALSE, -- Unité standard internationale
    est_utilisee BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

-- 3) Tables dépendant de compagnies
CREATE TABLE type_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    num_compte VARCHAR(10),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE methode_paiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_tresorerie VARCHAR(100) NOT NULL,
    mode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) NOT NULL DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4) Tables dépendant de plusieurs tables ci-dessus
CREATE TABLE specifications_locales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES pays(id),
    type_specification VARCHAR(50) NOT NULL, -- 'taxe', 'reglementation', 'comptabilite', etc.
    code_specification VARCHAR(50) NOT NULL, -- 'tva', 'timbre', 'cnaps', etc.
    libelle_specification VARCHAR(200) NOT NULL,
    valeur_specification VARCHAR(200), -- Valeur textuelle (ex: 18% ou "Obligatoire")
    taux_specification NUMERIC(10,4), -- Pour les taux (ex: 18.0000%)
    est_actif BOOLEAN DEFAULT TRUE,
    date_debut_validite DATE,
    date_fin_validite DATE,
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE configurations_pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES pays(id),
    cle_configuration VARCHAR(100) NOT NULL, -- 'format_date', 'format_numero_facture', etc.
    valeur_configuration TEXT NOT NULL, -- Valeur de la configuration
    description TEXT,
    est_systeme BOOLEAN DEFAULT FALSE, -- TRUE si c'est une configuration système
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

-- 5) Tables dépendant de tables précédentes
CREATE TABLE types_taxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_taxe VARCHAR(20) UNIQUE NOT NULL,
    libelle_taxe VARCHAR(100) NOT NULL,
    description TEXT,
    pays_id UUID REFERENCES pays(id),
    taux_par_defaut NUMERIC(5,2) DEFAULT 0,
    type_calcul VARCHAR(20) NOT NULL CHECK (type_calcul IN ('fixe', 'pourcentage', 'tranche')), -- Calcul de la taxe
    compte_comptable VARCHAR(20) REFERENCES plan_comptable(numero), -- Compte de taxe
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,        -- Ex: 'lire_ventes', 'creer_vente', 'modifier_vente', 'supprimer_vente'
    description TEXT,
    module_id UUID REFERENCES modules(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE pompes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL UNIQUE,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la pompe appartient (via la cuve/station)
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE tranches_taxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_taxe_id UUID REFERENCES types_taxes(id),
    borne_inferieure NUMERIC(18,2) DEFAULT 0,
    borne_superieure NUMERIC(18,2),
    taux NUMERIC(5,2) NOT NULL,
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6) Table utilisateurs qui dépend de profils et compagnies
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
    type_utilisateur VARCHAR(30) DEFAULT 'utilisateur_compagnie' CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7) Tables dépendant de utilisateurs ou fournisseurs
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

-- Maintenant que toutes les tables de dépendance sont créées, nous pouvons créer les tables restantes
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

CREATE TABLE conversions_unite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unite_origine_id UUID REFERENCES unites_mesure(id),
    unite_destination_id UUID REFERENCES unites_mesure(id),
    facteur_conversion NUMERIC(15,6) NOT NULL, -- Facteur pour convertir d'une unité à l'autre
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tables dépendant de 'utilisateurs'
CREATE TABLE auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
);

CREATE TABLE tentatives_connexion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) NOT NULL,
    ip_connexion VARCHAR(45),
    resultat_connexion VARCHAR(10) CHECK (resultat_connexion IN ('Reussie', 'Echouee')),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE politiques_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom_politique VARCHAR(100) NOT NULL,
    description TEXT,
    type_politique VARCHAR(50) NOT NULL, -- 'mot_de_passe', 'connexion', 'acces_donnees', etc.
    valeur_parametre VARCHAR(200),
    seuil_valeur INTEGER,
    est_actif BOOLEAN DEFAULT TRUE,
    commentaire TEXT,
    utilisateur_config_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a configuré la politique
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE historique_prix_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE historique_prix_carburants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID NOT NULL REFERENCES carburants(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

-- Table pour les stocks (ajoutée pour l'initialisation)
CREATE TABLE stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    cuve_id UUID REFERENCES cuves(id),
    station_id UUID REFERENCES stations(id),
    stock_theorique NUMERIC(18,3) DEFAULT 0, -- Stock théorique (calculé)
    stock_reel NUMERIC(18,3) DEFAULT 0,      -- Stock réel (compté physiquement)
    stock_minimal NUMERIC(18,3) DEFAULT 0,   -- Stock minimal avant alerte
    stock_maximal NUMERIC(18,3) DEFAULT 0,   -- Stock maximal possible
    prix_unitaire NUMERIC(18,4) DEFAULT 0,   -- Prix unitaire utilisé pour la valorisation
    est_initial BOOLEAN DEFAULT FALSE,       -- Indique si ce stock est initial
    date_initialisation DATE,                -- Date d'initialisation
    utilisateur_initialisation UUID REFERENCES utilisateurs(id), -- Utilisateur qui a effectué l'initialisation
    observation_initialisation TEXT,         -- Observations sur l'initialisation
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le stock appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les mouvements de stock
CREATE TABLE stocks_mouvements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id),
    cuve_id UUID REFERENCES cuves(id),
    station_id UUID REFERENCES stations(id),
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('entree', 'sortie', 'ajustement', 'initial')), -- Type de mouvement
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire NUMERIC(18,4) DEFAULT 0,
    date_mouvement DATE NOT NULL,
    reference_operation VARCHAR(100), -- Référence de l'opération (ex: numéro de facture)
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le mouvement appartient
    est_initial BOOLEAN DEFAULT FALSE, -- Indique si c'est un mouvement d'initialisation
    operation_initialisation_id UUID, -- Référence à l'opération d'initialisation
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'analyse de la qualité du carburant initial
CREATE TABLE qualite_carburant_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_id UUID REFERENCES cuves(id),
    carburant_id UUID REFERENCES carburants(id),
    date_analyse DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    densite NUMERIC(8,4), -- Ex: 0.8350 kg/L
    indice_octane INTEGER, -- Ex: 95 pour SP95
    soufre_ppm NUMERIC(10,2), -- Partie par million
    type_additif VARCHAR(100), -- Type d'additif utilisé
    commentaire_qualite TEXT,
    resultat_qualite VARCHAR(20) CHECK (resultat_qualite IN ('Conforme', 'Non conforme', 'En attente')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'analyse des coûts logistiques initiaux
CREATE TABLE couts_logistique_stocks_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_cout VARCHAR(50) NOT NULL, -- 'transport', 'stockage', 'manutention', 'assurance', 'autres'
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_cout DATE NOT NULL,
    article_id UUID REFERENCES articles(id),
    cuve_id UUID REFERENCES cuves(id),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    utilisateur_saisie_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le bilan initial global (mise à jour pour correspondre au document technique)
ALTER TABLE bilan_initial ADD COLUMN IF NOT EXISTS valeur_totale_stocks NUMERIC(18,2) DEFAULT 0;
ALTER TABLE bilan_initial ADD COLUMN IF NOT EXISTS nombre_elements INTEGER DEFAULT 0;
ALTER TABLE bilan_initial ADD COLUMN IF NOT EXISTS statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'En cours', 'Termine', 'Validé'));
ALTER TABLE bilan_initial ADD COLUMN IF NOT EXISTS utilisateur_validation_id UUID REFERENCES utilisateurs(id);
ALTER TABLE bilan_initial ADD COLUMN IF NOT EXISTS date_validation DATE;
ALTER TABLE bilan_initial ADD COLUMN IF NOT EXISTS date_bilan DATE;

-- Mise à jour de la date_bilan existante si elle n'est pas encore renseignée
UPDATE bilan_initial SET date_bilan = date_bilan_initial WHERE date_bilan IS NULL;

-- Table pour les lignes du bilan initial
CREATE TABLE bilan_initial_lignes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    type_element VARCHAR(20) NOT NULL CHECK (type_element IN ('carburant', 'article_boutique', 'autre')),
    element_id UUID NOT NULL,  -- ID de la cuve ou de l'article
    description_element TEXT,
    quantite NUMERIC(18,3) NOT NULL,
    unite_mesure VARCHAR(10),
    prix_unitaire NUMERIC(18,4) NOT NULL,
    valeur_totale NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED,
    taux_tva NUMERIC(5,2) DEFAULT 0,
    montant_tva NUMERIC(18,2),
    montant_ht NUMERIC(18,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les stocks initiaux
CREATE INDEX IF NOT EXISTS idx_stocks_est_initial ON stocks(est_initial);
CREATE INDEX IF NOT EXISTS idx_stocks_date_initialisation ON stocks(date_initialisation);

-- Index pour les mouvements de stock initiaux
CREATE INDEX IF NOT EXISTS idx_stocks_mouvements_est_initial ON stocks_mouvements(est_initial);
CREATE INDEX IF NOT EXISTS idx_stocks_mouvements_operation ON stocks_mouvements(operation_initialisation_id);

-- Index pour la qualité du carburant initial
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_initial_cuve ON qualite_carburant_initial(cuve_id);
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_initial_date ON qualite_carburant_initial(date_analyse);

-- Index pour les coûts logistiques initiaux
CREATE INDEX IF NOT EXISTS idx_couts_logistique_initial_article ON couts_logistique_stocks_initial(article_id);
CREATE INDEX IF NOT EXISTS idx_couts_logistique_initial_date ON couts_logistique_stocks_initial(date_cout);

-- Index pour le bilan initial
CREATE INDEX IF NOT EXISTS idx_bilan_initial_compagnie ON bilan_initial(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_bilan_initial_date ON bilan_initial(date_bilan);
CREATE INDEX IF NOT EXISTS idx_bilan_initial_statut ON bilan_initial(statut);

-- Trigger pour empêcher la modification d'un stock initialisé
CREATE OR REPLACE FUNCTION prevent_initial_stock_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'un stock marqué comme initial
    IF OLD.est_initial = TRUE THEN
        RAISE EXCEPTION 'Impossible de modifier un stock initialisé';
    END IF;

    -- Si le stock devient initial, effectuer des validations
    IF NEW.est_initial = TRUE AND OLD.est_initial IS DISTINCT FROM TRUE THEN
        -- Validation de la quantité par rapport à la capacité
        IF NEW.cuve_id IS NOT NULL THEN
            DECLARE
                capacite_cuve NUMERIC(18,3);
            BEGIN
                SELECT capacite INTO capacite_cuve
                FROM cuves
                WHERE id = NEW.cuve_id;

                IF NEW.stock_theorique > capacite_cuve THEN
                    RAISE EXCEPTION 'La quantité initiale dépasse la capacité de la cuve (% litres)', capacite_cuve;
                END IF;
            END;
        END IF;

        -- Historisation automatique du mouvement initial
        INSERT INTO stocks_mouvements (
            stock_id, article_id, cuve_id, station_id, type_mouvement,
            quantite, prix_unitaire, date_mouvement, reference_operation,
            utilisateur_id, commentaire, compagnie_id, est_initial
        )
        VALUES (
            NEW.id, NEW.article_id, NEW.cuve_id, NEW.station_id, 'Initial',
            NEW.stock_theorique, NEW.prix_unitaire, NEW.date_initialisation, 'INIT-' || NEW.id,
            NEW.utilisateur_initialisation, 'Initialisation du stock', NEW.compagnie_id, TRUE
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_initial_stock_modification
    BEFORE UPDATE ON stocks
    FOR EACH ROW EXECUTE FUNCTION prevent_initial_stock_modification();

-- Trigger pour calculer automatiquement les totaux du bilan initial
CREATE OR REPLACE FUNCTION update_bilan_initial_totals()
RETURNS TRIGGER AS $$
DECLARE
    total_valeur NUMERIC(18,2);
    count_elements INTEGER;
BEGIN
    CASE TG_OP
        WHEN 'INSERT', 'UPDATE' THEN
            -- Calculer le total et le nombre d'éléments
            SELECT
                COALESCE(SUM(valeur_totale), 0),
                COUNT(*)
            INTO total_valeur, count_elements
            FROM bilan_initial_lignes
            WHERE bilan_initial_id = NEW.bilan_initial_id;

        WHEN 'DELETE' THEN
            -- Récalculer après suppression
            SELECT
                COALESCE(SUM(valeur_totale), 0),
                COUNT(*)
            INTO total_valeur, count_elements
            FROM bilan_initial_lignes
            WHERE bilan_initial_id = OLD.bilan_initial_id;
    END CASE;

    -- Mettre à jour le bilan principal
    UPDATE bilan_initial
    SET
        valeur_totale_stocks = total_valeur,
        nombre_elements = count_elements
    WHERE id = (
        CASE WHEN TG_OP = 'DELETE' THEN OLD.bilan_initial_id ELSE NEW.bilan_initial_id END
    );

    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_bilan_initial_totals
    AFTER INSERT OR UPDATE OR DELETE ON bilan_initial_lignes
    FOR EACH ROW EXECUTE FUNCTION update_bilan_initial_totals();