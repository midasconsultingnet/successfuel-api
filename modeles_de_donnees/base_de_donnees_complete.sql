-- Base de données complète pour le système de gestion des stations-service

-- Extension pour les UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des pays (table de référence sans dépendances)
CREATE TABLE IF NOT EXISTS pays (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(100) NOT NULL,
    code VARCHAR(3) UNIQUE
);

-- Table des administrateurs (user_admin)
CREATE TABLE IF NOT EXISTS user_admin (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    userlogin VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    type_utilisateur VARCHAR(50) NOT NULL DEFAULT 'administrateur',
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Table Compagnie
CREATE TABLE compagnie (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    pays_id UUID NOT NULL REFERENCES pays(id),
    adresse TEXT,
    telephone VARCHAR(20),
    email VARCHAR(255),
    devise VARCHAR(10) DEFAULT 'XOF',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Utilisateur
CREATE TABLE utilisateur (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    login VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('gerant_compagnie', 'utilisateur_compagnie')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_derniere_connexion TIMESTAMP,
    actif BOOLEAN DEFAULT TRUE,
    compagnie_id UUID
);

-- Table Station
CREATE TABLE station (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    compagnie_id UUID NOT NULL REFERENCES compagnie(id),
    nom VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL,
    adresse TEXT,
    coordonnees_gps JSONB,
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'inactif', 'supprimer')),
    config JSONB DEFAULT '{"completion": {"station": false, "carburants": false, "cuves": false, "pistolets": false, "jauge": false, "fournisseurs": false, "clients": false, "employes": false, "tresorerie": false, "immobilisations": false, "soldes": false}}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(compagnie_id, code)
);

-- Table Affectation_Utilisateur_Station
CREATE TABLE affectation_utilisateur_station (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    station_id UUID NOT NULL REFERENCES station(id),
    date_affectation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(utilisateur_id, station_id)
);

-- Table Token_Session
CREATE TABLE token_session (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    token VARCHAR(500) NOT NULL,
    token_refresh VARCHAR(500) NOT NULL,
    date_expiration TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actif BOOLEAN DEFAULT TRUE
);

-- Table Carburant
CREATE TABLE carburant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    libelle VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL UNIQUE
);

-- Table Prix_Carburant
CREATE TABLE prix_carburant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    carburant_id UUID NOT NULL REFERENCES carburant(id),
    station_id UUID NOT NULL REFERENCES station(id),
    prix_achat DECIMAL(15,2),
    prix_vente DECIMAL(15,2),
    UNIQUE(carburant_id, station_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Famille_Produit
CREATE TABLE famille_produit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    code VARCHAR(100),
    famille_parente_id UUID REFERENCES famille_produit(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Produit
CREATE TABLE produit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL,
    description TEXT,
    unite_mesure VARCHAR(20) NOT NULL,
    famille_id UUID REFERENCES famille_produit(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('boutique', 'lubrifiant', 'gaz', 'service')),
    prix_vente DECIMAL(15,2) NOT NULL,
    seuil_stock_minimum DECIMAL(10,2),
    est_avec_stock BOOLEAN DEFAULT TRUE,
    station_id UUID NOT NULL REFERENCES station(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Cuve
CREATE TABLE cuve (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    nom VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL,
    capacite_maximale DECIMAL(12,2) NOT NULL,
    niveau_actuel DECIMAL(12,2) DEFAULT 0,
    carburant_id UUID NOT NULL REFERENCES carburant(id),
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'inactif', 'maintenance')),
    barremage JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Pistolet
CREATE TABLE pistolet (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cuve_id UUID NOT NULL REFERENCES cuve(id),
    numero VARCHAR(50) NOT NULL,
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'inactif', 'maintenance')),
    index_initial DECIMAL(12,2) DEFAULT 0,
    index_final DECIMAL(12,2),
    date_derniere_utilisation TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Etat_Initial_Cuve
CREATE TABLE etat_initial_cuve (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cuve_id UUID NOT NULL REFERENCES cuve(id),
    hauteur_jauge_initiale DECIMAL(12,2) NOT NULL,
    volume_initial_calcule DECIMAL(12,2) NOT NULL,
    date_initialisation TIMESTAMP NOT NULL,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    verrouille BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Journal_Action_Utilisateur
CREATE TABLE journal_action_utilisateur (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    date_action TIMESTAMP NOT NULL,
    type_action VARCHAR(100) NOT NULL,
    module_concerne VARCHAR(100) NOT NULL,
    donnees_avant JSONB,
    donnees_apres JSONB,
    ip_utilisateur VARCHAR(45),
    user_agent TEXT
);

-- Table Trésorerie
CREATE TABLE tresorerie (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('caisse', 'banque', 'mobile_money', 'note_credit', 'coffre', 'fonds_divers')),
    solde_initial DECIMAL(15,2) NOT NULL,
    devise VARCHAR(10) DEFAULT 'XOF',
    informations_bancaires JSONB,
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'inactif')),
    compagnie_id UUID NOT NULL REFERENCES compagnie(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Trésorerie_Station
CREATE TABLE tresorerie_station (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trésorerie_id UUID NOT NULL REFERENCES tresorerie(id),
    station_id UUID NOT NULL REFERENCES station(id),
    solde_initial DECIMAL(15,2) NOT NULL,
    solde_actuel DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table État Initial Trésorerie
CREATE TABLE etat_initial_tresorerie (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tresorerie_station_id UUID NOT NULL REFERENCES tresorerie_station(id),
    date_enregistrement DATE NOT NULL,
    montant DECIMAL(15,2) NOT NULL,
    commentaire TEXT,
    enregistre_par UUID NOT NULL REFERENCES utilisateur(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Contrainte pour s'assurer qu'il n'y ait qu'un seul solde initial par trésorerie station
    CONSTRAINT unique_solde_initial_par_station UNIQUE (tresorerie_station_id)
);

-- Table Tiers
CREATE TABLE tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(20) NOT NULL CHECK (type IN ('client', 'fournisseur', 'employé')),
    nom VARCHAR(255) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(20),
    email VARCHAR(255),
    seuil_credit DECIMAL(15,2) NOT NULL,
    compagnie_id UUID NOT NULL REFERENCES compagnie(id),
    conditions_paiement VARCHAR(100),
    categorie_client VARCHAR(50),
    conditions_livraison VARCHAR(100),
    delai_paiement INTEGER,
    poste VARCHAR(100),
    date_embauche DATE,
    statut VARCHAR(20) DEFAULT 'actif',
    solde DECIMAL(15,2) DEFAULT,
    identifiant_fiscal VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Solde_Tiers
CREATE TABLE solde_tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tiers_id UUID NOT NULL UNIQUE REFERENCES tiers(id),
    montant_initial DECIMAL(15,2) NOT NULL,
    montant_actuel DECIMAL(15,2) DEFAULT 0,
    devise VARCHAR(10) DEFAULT 'XOF',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Journal_Modification_Tiers
CREATE TABLE journal_modification_tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    updated_at TIMESTAMP NOT NULL,
    type_modification VARCHAR(100) NOT NULL,
    donnees_avant JSONB,
    donnees_apres JSONB,
    champs_modifies JSONB
);

-- Table Mouvement_Tiers
CREATE TABLE mouvement_tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    type_mouvement VARCHAR(10) NOT NULL CHECK (type_mouvement IN ('débit', 'crédit')),
    montant DECIMAL(15,2) NOT NULL,
    date_mouvement TIMESTAMP NOT NULL,
    description TEXT,
    module_origine VARCHAR(100) NOT NULL,
    reference_origine VARCHAR(100) NOT NULL,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    numero_piece_comptable VARCHAR(50),
    statut VARCHAR(20) DEFAULT 'validé' CHECK (statut IN ('validé', 'annulé'))
);

-- Table Immobilisation
CREATE TABLE immobilisation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    code VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    date_acquisition DATE NOT NULL,
    valeur_origine DECIMAL(15,2) NOT NULL,
    valeur_nette DECIMAL(15,2),
    taux_amortissement DECIMAL(5,2),
    duree_vie INTEGER,
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'inactif', 'cessionné', 'hors_service')),
    station_id UUID NOT NULL REFERENCES station(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Mouvement_Immobilisation
CREATE TABLE mouvement_immobilisation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    immobilisation_id UUID NOT NULL REFERENCES immobilisation(id),
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('acquisition', 'amélioration', 'cession', 'sortie', 'amortissement')),
    date_mouvement TIMESTAMP NOT NULL,
    description TEXT,
    valeur_variation DECIMAL(15,2),
    valeur_apres_mouvement DECIMAL(15,2),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    reference_document VARCHAR(100),
    statut VARCHAR(20) DEFAULT 'validé' CHECK (statut IN ('validé', 'annulé'))
);

-- Table Historique_Affectation_Immobilisation
CREATE TABLE historique_affectation_immobilisation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    immobilisation_id UUID NOT NULL REFERENCES immobilisation(id),
    station_origine_id UUID NOT NULL REFERENCES station(id),
    station_destination_id UUID NOT NULL REFERENCES station(id),
    date_affectation TIMESTAMP NOT NULL,
    motif_affectation TEXT,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id)
);

-- Table Achat_Carburant
CREATE TABLE achat_carburant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fournisseur_id UUID NOT NULL REFERENCES tiers(id),
    date_achat TIMESTAMP NOT NULL,
    numero_bl VARCHAR(100) NOT NULL,
    numero_facture VARCHAR(100) NOT NULL,
    montant_total DECIMAL(15,2) NOT NULL,
    statut VARCHAR(20) DEFAULT 'brouillon' CHECK (statut IN ('brouillon', 'validé', 'facturé', 'annulé')),
    station_id UUID NOT NULL REFERENCES station(id),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Ligne_Achat_Carburant
CREATE TABLE ligne_achat_carburant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    achat_carburant_id UUID NOT NULL REFERENCES achat_carburant(id),
    carburant_id UUID NOT NULL REFERENCES carburant(id),
    quantite DECIMAL(12,2) NOT NULL,
    prix_unitaire DECIMAL(15,2) NOT NULL,
    montant DECIMAL(15,2),
    cuve_id UUID NOT NULL REFERENCES cuve(id)
);

-- Table Compensation_Financiere
CREATE TABLE compensation_financiere (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    achat_carburant_id UUID NOT NULL REFERENCES achat_carburant(id),
    type_compensation VARCHAR(20) NOT NULL CHECK (type_compensation IN ('avoir_reçu', 'avoir_dû')),
    quantite_theorique DECIMAL(12,2) NOT NULL,
    quantite_reelle DECIMAL(12,2) NOT NULL,
    difference DECIMAL(12,2),
    montant_compensation DECIMAL(15,2) NOT NULL,
    motif TEXT,
    statut VARCHAR(20) DEFAULT 'émis' CHECK (statut IN ('émis', 'utilisé', 'partiellement_utilisé', 'expiré')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_expiration TIMESTAMP
);

-- Table Avoir_Compensation
CREATE TABLE avoir_compensation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    compensation_financiere_id UUID NOT NULL REFERENCES compensation_financiere(id),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    montant DECIMAL(15,2) NOT NULL,
    date_emission TIMESTAMP NOT NULL,
    date_utilisation TIMESTAMP,
    statut VARCHAR(20) DEFAULT 'émis' CHECK (statut IN ('émis', 'utilisé', 'partiellement_utilisé', 'expiré')),
    utilisateur_emission_id UUID NOT NULL REFERENCES utilisateur(id),
    utilisateur_utilisation_id UUID REFERENCES utilisateur(id)
);

-- Table Demande_Achat
CREATE TABLE demande_achat (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    utilisateur_demandeur_id UUID NOT NULL REFERENCES utilisateur(id),
    date_demande TIMESTAMP NOT NULL,
    date_besoin DATE NOT NULL,
    urgence BOOLEAN DEFAULT FALSE,
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'approuvée', 'rejetée')),
    indicateur_traitee BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Ligne_Demande_Achat
CREATE TABLE ligne_demande_achat (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    demande_achat_id UUID NOT NULL REFERENCES demande_achat(id),
    produit_id UUID NOT NULL REFERENCES produit(id),
    quantite_demandee DECIMAL(12,2) NOT NULL,
    unite VARCHAR(20)
);

-- Table Historique_Prix_Achat
CREATE TABLE historique_prix_achat (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produit_id UUID NOT NULL REFERENCES produit(id),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    prix_unitaire DECIMAL(15,2) NOT NULL,
    date_enregistrement TIMESTAMP NOT NULL
);

-- Table Commande_Achat
CREATE TABLE commande_achat (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    demande_achat_id UUID REFERENCES demande_achat(id),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    station_id UUID NOT NULL REFERENCES station(id),
    date_commande TIMESTAMP NOT NULL,
    date_livraison_prevue DATE NOT NULL,
    statut VARCHAR(20) DEFAULT 'brouillon' CHECK (statut IN ('brouillon', 'confirmée', 'en_cours', 'reçue', 'terminée', 'annulée')),
    type_paiement VARCHAR(20) NOT NULL CHECK (type_paiement IN ('prépayé', 'COD', 'différé', 'consignation', 'mixte', 'partiel')),
    delai_paiement INTEGER,
    pourcentage_acompte DECIMAL(5,2),
    limite_credit DECIMAL(15,2),
    mode_reglement VARCHAR(50),
    documents_requis JSONB,
    config_produit JSONB,
    regles_stock JSONB,
    frequence_appro VARCHAR(50),
    limites_budget_stock JSONB,
    niveaux_validation JSONB,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    numero_piece_comptable VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Ligne_Commande_Achat
CREATE TABLE ligne_commande_achat (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    commande_achat_id UUID NOT NULL REFERENCES commande_achat(id),
    produit_id UUID NOT NULL REFERENCES produit(id),
    quantite_demandee DECIMAL(12,2) NOT NULL,
    quantite_recue DECIMAL(12,2) DEFAULT 0,
    quantite_facturee DECIMAL(12,2) DEFAULT 0,
    prix_unitaire_demande DECIMAL(15,2) NOT NULL,
    prix_unitaire_facture DECIMAL(15,2),
    montant DECIMAL(15,2),
    ecart_prix DECIMAL(15,2)
);

-- Table Livraison_Carburant
CREATE TABLE livraison_carburant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    cuve_id UUID NOT NULL REFERENCES cuve(id),
    carburant_id UUID NOT NULL REFERENCES carburant(id),
    quantite_livree DECIMAL(12,2) NOT NULL,
    date_livraison TIMESTAMP NOT NULL,
    fournisseur_id UUID REFERENCES tiers(id),
    numero_bl VARCHAR(100),
    numero_facture VARCHAR(100),
    jauge_avant_livraison DECIMAL(12,2),
    jauge_apres_livraison DECIMAL(12,2),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    statut VARCHAR(20) DEFAULT 'enregistrée' CHECK (statut IN ('enregistrée', 'validée', 'annulée')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Inventaire_Carburant
CREATE TABLE inventaire_carburant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    cuve_id UUID NOT NULL REFERENCES cuve(id),
    carburant_id UUID NOT NULL REFERENCES carburant(id),
    quantite_reelle DECIMAL(12,2) NOT NULL,
    date_inventaire TIMESTAMP NOT NULL,
    statut VARCHAR(20) DEFAULT 'brouillon' CHECK (statut IN ('brouillon', 'en_cours', 'terminé', 'validé', 'rapproché', 'clôturé')),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    commentaire TEXT,
    methode_mesure VARCHAR(50) NOT NULL CHECK (methode_mesure IN ('manuel', 'jauge_digitale', 'sonde_automatique')),
    seuil_tolerance DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Inventaire_Boutique
CREATE TABLE inventaire_boutique (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    produit_id UUID NOT NULL REFERENCES produit(id),
    quantite_reelle DECIMAL(12,2) NOT NULL,
    date_inventaire TIMESTAMP NOT NULL,
    statut VARCHAR(20) DEFAULT 'brouillon' CHECK (statut IN ('brouillon', 'en_cours', 'terminé', 'validé', 'rapproché', 'clôturé')),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    commentaire TEXT,
    seuil_tolerance DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Ecart_Inventaire
CREATE TABLE ecart_inventaire (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventaire_carburant_id UUID NOT NULL REFERENCES inventaire_carburant(id),
    inventaire_boutique_id UUID NOT NULL REFERENCES inventaire_boutique(id),
    quantite_theorique DECIMAL(12,2),
    quantite_reelle DECIMAL(12,2),
    ecart DECIMAL(12,2),
    type_ecart VARCHAR(20) NOT NULL CHECK (type_ecart IN ('perte', 'évaporation', 'anomalie', 'erreur', 'surplus')),
    seuil_tolerance DECIMAL(5,2),
    est_significatif BOOLEAN,
    commentaire TEXT
);

-- Table Parametre_Inventaire
CREATE TABLE parametre_inventaire (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_carburant VARCHAR(50) NOT NULL,
    seuil_tolerance DECIMAL(5,2) NOT NULL,
    categorie_produit VARCHAR(100),
    saison VARCHAR(20),
    capacite_cuve DECIMAL(12,2),
    produit_id UUID REFERENCES produit(id),
    station_id UUID REFERENCES station(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Mouvement_Stock
CREATE TABLE mouvement_stock (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produit_id UUID NOT NULL REFERENCES produit(id),
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('entrée', 'sortie', 'ajustement', 'inventaire')),
    quantite DECIMAL(12,2) NOT NULL,
    date_mouvement TIMESTAMP NOT NULL,
    description TEXT,
    module_origine VARCHAR(100) NOT NULL,
    reference_origine VARCHAR(100) NOT NULL,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    cout_unitaire DECIMAL(15,2),
    statut VARCHAR(20) DEFAULT 'validé' CHECK (statut IN ('validé', 'annulé'))
);

-- Table Stock_Produit
CREATE TABLE stock_produit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produit_id UUID NOT NULL UNIQUE REFERENCES produit(id),
    quantite_theorique DECIMAL(12,2) DEFAULT 0,
    quantite_reelle DECIMAL(12,2) DEFAULT 0,
    date_dernier_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cout_moyen_pondere DECIMAL(15,2) DEFAULT 0
);

-- Table Lot_Produit
CREATE TABLE lot_produit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produit_id UUID NOT NULL REFERENCES produit(id),
    numero_lot VARCHAR(100) NOT NULL,
    quantite DECIMAL(12,2) NOT NULL,
    date_production DATE,
    date_peremption DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Vente_Carburant
CREATE TABLE vente_carburant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    carburant_id UUID NOT NULL REFERENCES carburant(id),
    cuve_id UUID NOT NULL REFERENCES cuve(id),
    pistolet_id UUID NOT NULL REFERENCES pistolet(id),
    quantite_vendue DECIMAL(12,2) NOT NULL,
    prix_unitaire DECIMAL(15,2) NOT NULL,
    montant_total DECIMAL(15,2),
    date_vente TIMESTAMP NOT NULL,
    index_initial DECIMAL(12,2) NOT NULL,
    index_final DECIMAL(12,2) NOT NULL,
    pompiste VARCHAR(255) NOT NULL,
    qualite_marshalle_id UUID REFERENCES utilisateur(id),
    montant_paye DECIMAL(15,2),
    mode_paiement VARCHAR(50),
    statut VARCHAR(20) DEFAULT 'enregistrée' CHECK (statut IN ('enregistrée', 'validée', 'annulée')),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    numero_piece_comptable VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Mouvement_Stock_Cuve
CREATE TABLE mouvement_stock_cuve (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    livraison_carburant_id UUID REFERENCES livraison_carburant(id),
    vente_carburant_id UUID REFERENCES vente_carburant(id),
    inventaire_carburant_id UUID REFERENCES inventaire_carburant(id),
    cuve_id UUID NOT NULL REFERENCES cuve(id),
    type_mouvement VARCHAR(10) NOT NULL CHECK (type_mouvement IN ('entrée', 'sortie', 'ajustement')),
    quantite DECIMAL(12,2) NOT NULL,
    date_mouvement TIMESTAMP NOT NULL,
    stock_avant DECIMAL(12,2),
    stock_apres DECIMAL(12,2),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    reference_origine VARCHAR(100) NOT NULL,
    module_origine VARCHAR(100) NOT NULL,
    statut VARCHAR(20) DEFAULT 'validé' CHECK (statut IN ('validé', 'annulé'))
);

-- Table Historique_Livraison
CREATE TABLE historique_livraison (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    livraison_carburant_id UUID NOT NULL REFERENCES livraison_carburant(id),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    type_historique VARCHAR(20) NOT NULL CHECK (type_historique IN ('création', 'modification', 'validation', 'annulation')),
    donnees_avant JSONB,
    donnees_apres JSONB,
    date_historique TIMESTAMP NOT NULL,
    description TEXT
);

-- Table Creance_Employe
CREATE TABLE creance_employe (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vente_carburant_id UUID REFERENCES vente_carburant(id),
    pompiste VARCHAR(255) NOT NULL,
    montant_du DECIMAL(15,2) NOT NULL,
    montant_paye DECIMAL(15,2) NOT NULL,
    solde_creance DECIMAL(15,2),
    created_at DATE NOT NULL,
    date_echeance DATE,
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK (statut IN ('en_cours', 'payé', 'partiellement_payé')),
    utilisateur_gestion_id UUID NOT NULL REFERENCES utilisateur(id)
);

-- Table Historique_Vente
CREATE TABLE historique_vente (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vente_carburant_id UUID NOT NULL REFERENCES vente_carburant(id),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    type_historique VARCHAR(20) NOT NULL CHECK (type_historique IN ('création', 'modification', 'validation', 'annulation')),
    donnees_avant JSONB,
    donnees_apres JSONB,
    date_historique TIMESTAMP NOT NULL,
    motif_annulation TEXT
);

-- Table Vente_Boutique
CREATE TABLE vente_boutique (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    client_id UUID REFERENCES tiers(id),
    date_vente TIMESTAMP NOT NULL,
    montant_total DECIMAL(15,2),
    type_vente VARCHAR(20) NOT NULL CHECK (type_vente IN ('produit', 'service', 'hybride')),
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK (statut IN ('en_cours', 'terminée', 'annulée')),
    trésorerie_id UUID NOT NULL REFERENCES tresorerie_station(id),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    remise_globale DECIMAL(5,2) DEFAULT 0,
    numero_piece_comptable VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Ligne_Vente
CREATE TABLE ligne_vente (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vente_boutique_id UUID NOT NULL REFERENCES vente_boutique(id),
    produit_id UUID NOT NULL REFERENCES produit(id),
    quantite DECIMAL(12,2) NOT NULL,
    prix_unitaire DECIMAL(15,2) NOT NULL,
    montant DECIMAL(15,2),
    remise_ligne DECIMAL(5,2) DEFAULT 0
);

-- Table Promotion
CREATE TABLE promotion (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    type_promotion VARCHAR(50) NOT NULL,
    valeur_promotion DECIMAL(10,2) NOT NULL,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP NOT NULL,
    statut VARCHAR(20) DEFAULT 'inactive' CHECK (statut IN ('active', 'inactive', 'expirée')),
    conditions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Application_Promotion
CREATE TABLE application_promotion (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    promotion_id UUID NOT NULL REFERENCES promotion(id),
    vente_boutique_id UUID REFERENCES vente_boutique(id),
    ligne_vente_id UUID REFERENCES ligne_vente(id),
    montant_applique DECIMAL(15,2) NOT NULL,
    date_application TIMESTAMP NOT NULL
);

-- Table Categorie_Charge
CREATE TABLE categorie_charge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL CHECK (type IN ('fixe', 'variable')),
    seuil_alerte DECIMAL(15,2),
    compte_comptable_associe VARCHAR(50),
    hierarchie_parente_id UUID REFERENCES categorie_charge(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Methode_Paiement
CREATE TABLE methode_paiement (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    type_paiement VARCHAR(100) NOT NULL, -- 'cash', 'cheque', 'virement', 'mobile_money', etc.
    actif BOOLEAN DEFAULT TRUE,
    trésorerie_id UUID REFERENCES tresorerie(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table de liaison entre trésorerie et méthode de paiement
CREATE TABLE tresorerie_methode_paiement (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trésorerie_id UUID NOT NULL REFERENCES tresorerie(id),
    methode_paiement_id UUID NOT NULL REFERENCES methode_paiement(id),
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table Mouvement_Tresorerie
CREATE TABLE mouvement_tresorerie (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trésorerie_station_id UUID NOT NULL REFERENCES tresorerie_station(id),
    type_mouvement VARCHAR(10) NOT NULL CHECK (type_mouvement IN ('entrée', 'sortie')),
    montant DECIMAL(15,2) NOT NULL,
    date_mouvement TIMESTAMP NOT NULL,
    description TEXT,
    module_origine VARCHAR(100) NOT NULL,
    reference_origine VARCHAR(100) NOT NULL,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    numero_piece_comptable VARCHAR(50),
    statut VARCHAR(20) DEFAULT 'validé' CHECK (statut IN ('validé', 'annulé')),
    methode_paiement_id UUID REFERENCES methode_paiement(id) -- Ajout de la méthode de paiement
);

-- Table Transfert_Tresorerie
CREATE TABLE transfert_tresorerie (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trésorerie_source_id UUID NOT NULL REFERENCES tresorerie_station(id),
    trésorerie_destination_id UUID NOT NULL REFERENCES tresorerie_station(id),
    montant DECIMAL(15,2) NOT NULL,
    date_transfert TIMESTAMP NOT NULL,
    description TEXT,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    statut VARCHAR(20) DEFAULT 'validé' CHECK (statut IN ('validé', 'annulé')),
    CHECK (trésorerie_source_id != trésorerie_destination_id)
);

-- Table Charge_Fonctionnement
CREATE TABLE charge_fonctionnement (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES station(id),
    categorie_id UUID NOT NULL REFERENCES categorie_charge(id),
    fournisseur_id UUID REFERENCES tiers(id),
    date_charge TIMESTAMP NOT NULL,
    montant DECIMAL(15,2) NOT NULL,
    description TEXT,
    date_echeance DATE NOT NULL,
    statut VARCHAR(20) DEFAULT 'prévu' CHECK (statut IN ('prévu', 'échu', 'en_cours_paiement', 'payé')),
    methode_paiement VARCHAR(50),
    numero_piece_comptable VARCHAR(50),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Paiement_Charge
CREATE TABLE paiement_charge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    charge_fonctionnement_id UUID NOT NULL REFERENCES charge_fonctionnement(id),
    trésorerie_station_id UUID NOT NULL REFERENCES tresorerie_station(id),
    montant_paye DECIMAL(15,2) NOT NULL,
    date_paiement TIMESTAMP NOT NULL,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    description TEXT,
    numero_piece_comptable VARCHAR(50)
);

-- Table Historique_Charge
CREATE TABLE historique_charge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    charge_fonctionnement_id UUID NOT NULL REFERENCES charge_fonctionnement(id),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    type_historique VARCHAR(20) NOT NULL CHECK (type_historique IN ('création', 'modification', 'paiement', 'annulation')),
    donnees_avant JSONB,
    donnees_apres JSONB,
    date_historique TIMESTAMP NOT NULL
);

-- Table Paie_Employe
CREATE TABLE paie_employe (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employe_id UUID NOT NULL REFERENCES tiers(id),
    periode VARCHAR(10) NOT NULL,
    date_echeance DATE NOT NULL,
    date_paiement DATE,
    salaire_base DECIMAL(15,2) NOT NULL,
    montant_total DECIMAL(15,2),
    statut VARCHAR(20) DEFAULT 'prévu' CHECK (statut IN ('prévu', 'échu', 'payé', 'dû', 'en_retard')),
    methode_paiement VARCHAR(50),
    utilisateur_gestion_id UUID REFERENCES utilisateur(id),
    commentaire TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Element_Paie
CREATE TABLE element_paie (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paie_employe_id UUID NOT NULL REFERENCES paie_employe(id),
    type_element VARCHAR(20) NOT NULL CHECK (type_element IN ('prime', 'avance', 'retenue', 'cotisation', 'impot')),
    libelle VARCHAR(255) NOT NULL,
    montant DECIMAL(15,2) NOT NULL,
    est_calcul_automatique BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Parametre_Salaire
CREATE TABLE parametre_salaire (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employe_id UUID NOT NULL REFERENCES tiers(id),
    taux_cotisations_sociales DECIMAL(5,2),
    taux_impots DECIMAL(5,2),
    periodicite_paiement VARCHAR(20) DEFAULT 'mensuel',
    date_derniere_mise_a_jour TIMESTAMP
);

-- Table Paiement_Creance
CREATE TABLE paiement_creance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creance_employe_id UUID NOT NULL REFERENCES creance_employe(id),
    trésorerie_station_id UUID NOT NULL REFERENCES tresorerie_station(id),
    montant_paye DECIMAL(15,2) NOT NULL,
    date_paiement TIMESTAMP NOT NULL,
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    commentaire TEXT
);

-- Table Historique_Paie
CREATE TABLE historique_paie (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paie_employe_id UUID NOT NULL REFERENCES paie_employe(id),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    type_historique VARCHAR(20) NOT NULL CHECK (type_historique IN ('création', 'modification', 'paiement', 'relance', 'mise_en_demeure')),
    donnees_avant JSONB,
    donnees_apres JSONB,
    date_historique TIMESTAMP NOT NULL
);

-- Table Mouvement_Financier
CREATE TABLE mouvement_financier (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    type_mouvement VARCHAR(50) NOT NULL CHECK (type_mouvement IN ('reglement_dette', 'recouvrement_creance', 'avoir', 'penalite', 'divers')),
    montant DECIMAL(15,2) NOT NULL,
    date_mouvement TIMESTAMP NOT NULL,
    date_echeance DATE,
    methode_paiement VARCHAR(50),
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'payé', 'partiellement_payé', 'annulé', 'en_retard')),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id),
    numero_piece_comptable VARCHAR(50),
    penalites DECIMAL(15,2) DEFAULT 0,
    motif TEXT,
    reference_origine VARCHAR(100),
    module_origine VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Avoir
CREATE TABLE avoir (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    montant_initial DECIMAL(15,2) NOT NULL,
    montant_utilise DECIMAL(15,2) DEFAULT 0,
    montant_restant DECIMAL(15,2),
    date_emission TIMESTAMP NOT NULL,
    date_utilisation TIMESTAMP,
    date_expiration TIMESTAMP,
    motif TEXT NOT NULL,
    statut VARCHAR(20) DEFAULT 'émis' CHECK (statut IN ('émis', 'utilisé', 'partiellement_utilisé', 'expiré')),
    utilisateur_emission_id UUID NOT NULL REFERENCES utilisateur(id),
    utilisateur_utilisation_id UUID REFERENCES utilisateur(id),
    reference_origine VARCHAR(100) NOT NULL,
    module_origine VARCHAR(50) NOT NULL CHECK (module_origine IN ('ventes', 'achats', 'compensations'))
);


-- Table Etat_Financier
CREATE TABLE etat_financier (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_etat VARCHAR(50) NOT NULL CHECK (type_etat IN ('tresorerie', 'tiers', 'stocks', 'bilan_operations', 'journal_operations', 'journal_comptable', 'bilan_initial', 'etat_resultat')),
    nom_etat VARCHAR(255) NOT NULL,
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    station_id UUID REFERENCES station(id),
    utilisateur_generation_id UUID NOT NULL REFERENCES utilisateur(id),
    date_generation TIMESTAMP NOT NULL,
    parametres_filtrage JSONB,
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK (statut IN ('en_cours', 'genere', 'valide')),
    fichier_export VARCHAR(500)
);

-- Table Bilan_Initial_Depart
CREATE TABLE bilan_initial_depart (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    compagnie_id UUID NOT NULL REFERENCES compagnie(id),
    station_id UUID REFERENCES station(id),
    date_bilan DATE NOT NULL,
    actif_immobilise DECIMAL(15,2) NOT NULL,
    actif_circulant DECIMAL(15,2) NOT NULL,
    total_actif DECIMAL(15,2),
    capitaux_propres DECIMAL(15,2) NOT NULL,
    dettes DECIMAL(15,2) NOT NULL,
    provisions DECIMAL(15,2) NOT NULL,
    total_passif DECIMAL(15,2),
    utilisateur_generation_id UUID NOT NULL REFERENCES utilisateur(id),
    date_generation TIMESTAMP NOT NULL,
    est_valide BOOLEAN DEFAULT FALSE
);

-- Table Journal_Operations
CREATE TABLE journal_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID REFERENCES station(id),
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    nombre_operations INTEGER,
    total_debit DECIMAL(15,2),
    total_credit DECIMAL(15,2),
    utilisateur_generation_id UUID NOT NULL REFERENCES utilisateur(id),
    date_generation TIMESTAMP NOT NULL
);

-- Table Operation_Journal
CREATE TABLE operation_journal (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_operations_id UUID NOT NULL REFERENCES journal_operations(id),
    date_operation DATE NOT NULL,
    libelle_operation TEXT NOT NULL,
    compte_debit VARCHAR(50) NOT NULL,
    compte_credit VARCHAR(50) NOT NULL,
    montant DECIMAL(15,2) NOT NULL,
    devise VARCHAR(10) DEFAULT 'XOF',
    reference_operation VARCHAR(100) NOT NULL,
    module_origine VARCHAR(100) NOT NULL,
    utilisateur_enregistrement_id UUID NOT NULL REFERENCES utilisateur(id)
);

-- Table Bilan_Operations
CREATE TABLE bilan_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID REFERENCES station(id),
    date_bilan DATE NOT NULL,
    situation_tresoreries DECIMAL(15,2),
    immobilisations DECIMAL(15,2),
    stocks_carburant DECIMAL(15,2),
    stocks_boutique DECIMAL(15,2),
    creances DECIMAL(15,2),
    dettes DECIMAL(15,2),
    resultat_operations DECIMAL(15,2),
    utilisateur_generation_id UUID NOT NULL REFERENCES utilisateur(id),
    date_generation TIMESTAMP NOT NULL
);

-- Table Export_Etat
CREATE TABLE export_etat (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    etat_financier_id UUID NOT NULL REFERENCES etat_financier(id),
    type_export VARCHAR(10) NOT NULL CHECK (type_export IN ('CSV', 'Excel', 'PDF', 'XML')),
    utilisateur_export_id UUID NOT NULL REFERENCES utilisateur(id),
    date_export TIMESTAMP NOT NULL,
    chemin_fichier VARCHAR(500) NOT NULL,
    nom_fichier VARCHAR(255) NOT NULL
);

-- Indexes pour améliorer les performances
CREATE INDEX idx_utilisateur_compagnie ON utilisateur(compagnie_id);
CREATE INDEX idx_station_compagnie ON station(compagnie_id);
CREATE INDEX idx_produit_station ON produit(station_id);
CREATE INDEX idx_tiers_compagnie ON tiers(compagnie_id);
CREATE INDEX idx_achat_carburant_fournisseur ON achat_carburant(fournisseur_id);
CREATE INDEX idx_achat_carburant_station ON achat_carburant(station_id);
CREATE INDEX idx_commande_achat_tiers ON commande_achat(tiers_id);
CREATE INDEX idx_vente_carburant_station ON vente_carburant(station_id);
CREATE INDEX idx_vente_boutique_station ON vente_boutique(station_id);
CREATE INDEX idx_charge_fonctionnement_station ON charge_fonctionnement(station_id);
CREATE INDEX idx_mouvement_financier_tiers ON mouvement_financier(tiers_id);

-- Contraintes supplémentaires
ALTER TABLE utilisateur ADD CONSTRAINT fk_utilisateur_compagnie FOREIGN KEY (compagnie_id) REFERENCES compagnie(id);
ALTER TABLE mouvement_stock_cuve ADD CONSTRAINT check_reference_origine CHECK (
    (livraison_carburant_id IS NOT NULL AND vente_carburant_id IS NULL AND inventaire_carburant_id IS NULL) OR
    (livraison_carburant_id IS NULL AND vente_carburant_id IS NOT NULL AND inventaire_carburant_id IS NULL) OR
    (livraison_carburant_id IS NULL AND vente_carburant_id IS NULL AND inventaire_carburant_id IS NOT NULL)
);
ALTER TABLE ecart_inventaire ADD CONSTRAINT check_inventaire_reference CHECK (
    (inventaire_carburant_id IS NOT NULL AND inventaire_boutique_id IS NULL) OR
    (inventaire_carburant_id IS NULL AND inventaire_boutique_id IS NOT NULL)
);

-- Fonction pour mettre à jour le champ updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Déclencheurs pour la mise à jour automatique de updated_at
CREATE TRIGGER update_utilisateur_updated_at
    BEFORE UPDATE ON utilisateur
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_compagnie_updated_at
    BEFORE UPDATE ON compagnie
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_station_updated_at
    BEFORE UPDATE ON station
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_achat_carburant_updated_at
    BEFORE UPDATE ON achat_carburant
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_commande_achat_updated_at
    BEFORE UPDATE ON commande_achat
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Autres déclencheurs pourraient être ajoutés de la même manière pour d'autres tables

-- Vues pour les rapports et les analyses

-- Vue pour les ventes de carburant avec détails
CREATE VIEW vue_ventes_carburant AS
SELECT
    vc.id,
    vc.station_id,
    s.nom AS station_nom,
    vc.carburant_id,
    c.libelle AS carburant_libelle,
    vc.cuve_id,
    cu.nom AS cuve_nom,
    vc.pistolet_id,
    vc.quantite_vendue,
    vc.prix_unitaire,
    vc.montant_total,
    vc.date_vente,
    vc.index_initial,
    vc.index_final,
    vc.pompiste,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom,
    vc.mode_paiement,
    vc.statut
FROM vente_carburant vc
JOIN station s ON vc.station_id = s.id
JOIN carburant c ON vc.carburant_id = c.id
JOIN cuve cu ON vc.cuve_id = cu.id
JOIN utilisateur u ON vc.utilisateur_id = u.id;

-- Vue pour les ventes boutique avec détails
CREATE VIEW vue_ventes_boutique AS
SELECT
    vb.id,
    vb.station_id,
    s.nom AS station_nom,
    vb.client_id,
    t.nom AS client_nom,
    vb.date_vente,
    vb.montant_total,
    vb.type_vente,
    vb.statut,
    vb.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom,
    vb.trésorerie_id,
    trs.nom AS trésorerie_nom
FROM vente_boutique vb
JOIN station s ON vb.station_id = s.id
LEFT JOIN tiers t ON vb.client_id = t.id
JOIN utilisateur u ON vb.utilisateur_id = u.id
JOIN tresorerie_station ts ON vb.trésorerie_id = ts.id
JOIN tresorerie trs ON ts.trésorerie_id = trs.id;

-- Vue pour les achats carburant avec détails
CREATE VIEW vue_achats_carburant AS
SELECT
    ac.id,
    ac.fournisseur_id,
    t.nom AS fournisseur_nom,
    lac.carburant_id,
    c.libelle AS carburant_libelle,
    ac.date_achat,
    ac.numero_bl,
    ac.numero_facture,
    ac.montant_total,
    ac.statut,
    ac.station_id,
    s.nom AS station_nom,
    ac.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom
FROM achat_carburant ac
JOIN tiers t ON ac.fournisseur_id = t.id
JOIN station s ON ac.station_id = s.id
JOIN utilisateur u ON ac.utilisateur_id = u.id
JOIN ligne_achat_carburant lac ON ac.id = lac.achat_carburant_id
JOIN carburant c ON lac.carburant_id = c.id;

-- Vue pour les achats boutique avec détails
CREATE VIEW vue_achats_boutique AS
SELECT
    ca.id,
    ca.tiers_id,
    t.nom AS tiers_nom,
    ca.date_commande,
    ca.date_livraison_prevue,
    ca.statut,
    ca.station_id,
    s.nom AS station_nom,
    ca.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom
FROM commande_achat ca
JOIN tiers t ON ca.tiers_id = t.id
JOIN station s ON ca.station_id = s.id
JOIN utilisateur u ON ca.utilisateur_id = u.id;

-- Vue pour le suivi des stocks produits
CREATE VIEW vue_stocks_produits AS
SELECT
    p.id,
    p.nom AS produit_nom,
    p.code AS produit_code,
    p.station_id,
    s.nom AS station_nom,
    sp.quantite_theorique,
    sp.quantite_reelle,
    sp.cout_moyen_pondere,
    p.seuil_stock_minimum
FROM produit p
JOIN station s ON p.station_id = s.id
JOIN stock_produit sp ON p.id = sp.produit_id;

-- Vue pour les mouvements de trésorerie consolidés
CREATE VIEW vue_mouvements_tresorerie AS
SELECT
    mt.id,
    mt.trésorerie_station_id,
    ts.station_id,
    st.nom AS station_nom,
    trs.nom AS trésorerie_nom,
    mt.type_mouvement,
    mt.montant,
    mt.date_mouvement,
    mt.description,
    mt.module_origine,
    mt.reference_origine,
    mt.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom,
    mt.numero_piece_comptable,
    mt.statut
FROM mouvement_tresorerie mt
JOIN tresorerie_station ts ON mt.trésorerie_station_id = ts.id
JOIN station st ON ts.station_id = st.id
JOIN tresorerie trs ON ts.trésorerie_id = trs.id
JOIN utilisateur u ON mt.utilisateur_id = u.id;

-- Vue pour les soldes des tiers
CREATE VIEW vue_soldes_tiers AS
SELECT
    t.id,
    t.type,
    t.nom,
    t.email,
    st.montant_actuel AS solde_actuel,
    st.devise,
    t.created_at
FROM tiers t
JOIN solde_tiers st ON t.id = st.tiers_id;

-- Vue pour les immobilisations par station
CREATE VIEW vue_immobilisations AS
SELECT
    i.id,
    i.nom,
    i.description,
    i.code,
    i.type,
    i.date_acquisition,
    i.valeur_origine,
    i.valeur_nette,
    i.statut,
    i.station_id,
    s.nom AS station_nom
FROM immobilisation i
JOIN station s ON i.station_id = s.id;

-- Vue pour les charges de fonctionnement par catégorie et station
CREATE VIEW vue_charges_fonctionnement AS
SELECT
    cf.id,
    cf.station_id,
    s.nom AS station_nom,
    cf.categorie_id,
    cc.nom AS categorie_nom,
    cf.fournisseur_id,
    tf.nom AS fournisseur_nom,
    cf.date_charge,
    cf.montant,
    cf.date_echeance,
    cf.statut,
    cf.methode_paiement,
    cf.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom
FROM charge_fonctionnement cf
JOIN station s ON cf.station_id = s.id
JOIN categorie_charge cc ON cf.categorie_id = cc.id
LEFT JOIN tiers tf ON cf.fournisseur_id = tf.id
JOIN utilisateur u ON cf.utilisateur_id = u.id;

-- Vue pour les salaires et paies
CREATE VIEW vue_paies_employes AS
SELECT
    pe.id,
    pe.employe_id,
    t.nom AS employe_nom,
    pe.periode,
    pe.date_echeance,
    pe.date_paiement,
    pe.salaire_base,
    pe.montant_total,
    pe.statut,
    pe.utilisateur_gestion_id,
    u.nom AS gestionnaire_nom,
    u.prenom AS gestionnaire_prenom
FROM paie_employe pe
JOIN tiers t ON pe.employe_id = t.id
LEFT JOIN utilisateur u ON pe.utilisateur_gestion_id = u.id;

-- Vue pour les mouvements financiers
CREATE VIEW vue_mouvements_financiers AS
SELECT
    mf.id,
    mf.tiers_id,
    t.nom AS tiers_nom,
    t.type AS tiers_type,
    mf.type_mouvement,
    mf.montant,
    mf.date_mouvement,
    mf.date_echeance,
    mf.methode_paiement,
    mf.statut,
    mf.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom,
    mf.numero_piece_comptable,
    mf.penalites,
    mf.motif
FROM mouvement_financier mf
JOIN tiers t ON mf.tiers_id = t.id
JOIN utilisateur u ON mf.utilisateur_id = u.id;

-- Vue pour les inventaires carburant avec écarts
CREATE VIEW vue_inventaires_carburant AS
SELECT
    ic.id,
    ic.station_id,
    s.nom AS station_nom,
    ic.cuve_id,
    cu.nom AS cuve_nom,
    ic.carburant_id,
    c.libelle AS carburant_libelle,
    ic.quantite_reelle,
    ic.date_inventaire,
    ic.statut,
    ic.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom,
    ei.ecart,
    ei.type_ecart
FROM inventaire_carburant ic
JOIN station s ON ic.station_id = s.id
JOIN cuve cu ON ic.cuve_id = cu.id
JOIN carburant c ON ic.carburant_id = c.id
JOIN utilisateur u ON ic.utilisateur_id = u.id
LEFT JOIN ecart_inventaire ei ON ic.id = ei.inventaire_carburant_id;

-- Vue pour les inventaires boutique avec écarts
CREATE VIEW vue_inventaires_boutique AS
SELECT
    ib.id,
    ib.station_id,
    s.nom AS station_nom,
    ib.produit_id,
    p.nom AS produit_nom,
    p.code AS produit_code,
    ib.quantite_reelle,
    ib.date_inventaire,
    ib.statut,
    ib.utilisateur_id,
    u.nom AS utilisateur_nom,
    u.prenom AS utilisateur_prenom,
    ei.ecart,
    ei.type_ecart
FROM inventaire_boutique ib
JOIN station s ON ib.station_id = s.id
JOIN produit p ON ib.produit_id = p.id
JOIN utilisateur u ON ib.utilisateur_id = u.id
LEFT JOIN ecart_inventaire ei ON ib.id = ei.inventaire_boutique_id;

-- Vue pour les stocks de cuves
CREATE VIEW vue_stock_cuve AS
SELECT
    c.id AS cuve_id,
    c.station_id,
    c.carburant_id,
    c.nom AS cuve_nom,
    c.code AS cuve_code,
    c.capacite_maximale,
    c.statut AS cuve_statut,
    -- Stock initial (ou 0 si non défini)
    COALESCE(eic.volume_initial_calcule, 0) AS stock_initial,
    -- Calcul du stock final basé sur les mouvements
    COALESCE(eic.volume_initial_calcule, 0) +
    COALESCE(SUM(
        CASE
            WHEN msc.type_mouvement = 'entrée' THEN msc.quantite
            WHEN msc.type_mouvement = 'sortie' THEN -msc.quantite
            WHEN msc.type_mouvement = 'ajustement' THEN msc.quantite
            ELSE 0
        END
    ), 0) AS stock_actuel,
    -- Dernière date de mouvement
    GREATEST(COALESCE(eic.date_initialisation, '1900-01-01'::date),
             COALESCE(MAX(msc.date_mouvement), '1900-01-01'::date)) AS derniere_date_mouvement,
    -- Dernier mouvement
    MAX(msc.date_mouvement) AS date_dernier_mouvement,
    -- Informations du carburant
    car.libelle AS carburant_libelle,
    car.code AS carburant_code,
    -- Informations de la station
    st.nom AS station_nom,
    st.code AS station_code,
    comp.nom AS compagnie_nom
FROM cuve c
LEFT JOIN etat_initial_cuve eic ON c.id = eic.cuve_id
LEFT JOIN mouvement_stock_cuve msc ON c.id = msc.cuve_id
LEFT JOIN carburant car ON c.carburant_id = car.id
LEFT JOIN station st ON c.station_id = st.id
LEFT JOIN compagnie comp ON st.compagnie_id = comp.id
GROUP BY c.id, c.station_id, c.carburant_id, c.nom, c.code,
         c.capacite_maximale, c.statut, eic.volume_initial_calcule,
         eic.date_initialisation, car.libelle, car.code,
         st.nom, st.code, comp.nom;

-- Index pour améliorer les performances sur les consultations fréquentes
CREATE INDEX idx_mouvement_tresorerie_station_statut
ON mouvement_tresorerie(trésorerie_station_id, statut, date_mouvement);

CREATE INDEX idx_transfert_tresorerie_dates
ON transfert_tresorerie(date_transfert, statut);

-- Vue matérialisée pour les soldes de trésorerie
CREATE MATERIALIZED VIEW vue_materia_sldes_tresorerie AS
SELECT
    ts.id AS trésorerie_station_id,
    trs.id AS trésorerie_id,
    trs.nom AS nom_trésorerie,
    trs.type AS type_trésorerie,
    s.id AS station_id,
    s.nom AS station_nom,
    ts.solde_initial,
    ts.solde_actuel,
    -- Calcul en temps réel pour vérification
    (ts.solde_initial +
     COALESCE(credits.montant_total_credits, 0) -
     COALESCE(debits.montant_total_debits, 0) +
     COALESCE(recus.montant_total_recus, 0) -
     COALESCE(envoyes.montant_total_envoyes, 0)) AS solde_calculé
FROM tresorerie_station ts
JOIN tresorerie trs ON ts.trésorerie_id = trs.id
JOIN station s ON ts.station_id = s.id
LEFT JOIN (
    SELECT trésorerie_station_id, SUM(montant) AS montant_total_credits
    FROM mouvement_tresorerie
    WHERE type_mouvement = 'entrée' AND statut = 'validé'
    GROUP BY trésorerie_station_id
) credits ON ts.id = credits.trésorerie_station_id
LEFT JOIN (
    SELECT trésorerie_station_id, SUM(montant) AS montant_total_debits
    FROM mouvement_tresorerie
    WHERE type_mouvement = 'sortie' AND statut = 'validé'
    GROUP BY trésorerie_station_id
) debits ON ts.id = debits.trésorerie_station_id
LEFT JOIN (
    SELECT trésorerie_destination_id AS trésorerie_station_id,
           SUM(montant) AS montant_total_recus
    FROM transfert_tresorerie
    WHERE statut = 'validé'
    GROUP BY trésorerie_destination_id
) recus ON ts.id = recus.trésorerie_station_id
LEFT JOIN (
    SELECT trésorerie_source_id AS trésorerie_station_id,
           SUM(montant) AS montant_total_envoyes
    FROM transfert_tresorerie
    WHERE statut = 'validé'
    GROUP BY trésorerie_source_id
) envoyes ON ts.id = envoyes.trésorerie_station_id;

-- Fonction pour enregistrer un mouvement de trésorerie
CREATE OR REPLACE FUNCTION enregistrer_mouvement_trésorerie(
    p_trésorerie_station_id UUID,
    p_type_mouvement VARCHAR(10),
    p_montant DECIMAL,
    p_date_mouvement TIMESTAMP,
    p_description TEXT,
    p_module_origine VARCHAR(100),
    p_reference_origine VARCHAR(100),
    p_utilisateur_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_nouveau_solde DECIMAL;
    v_id UUID;
BEGIN
    -- Validation du solde pour les sorties
    IF p_type_mouvement = 'sortie' THEN
        SELECT solde_actuel INTO v_nouveau_solde
        FROM tresorerie_station
        WHERE id = p_trésorerie_station_id;

        IF v_nouveau_solde < p_montant THEN
            RAISE EXCEPTION 'Solde insuffisant pour effectuer cette opération';
        END IF;
    END IF;

    -- Insérer le mouvement
    INSERT INTO mouvement_tresorerie (
        trésorerie_station_id, type_mouvement, montant, date_mouvement,
        description, module_origine, reference_origine, utilisateur_id
    ) VALUES (
        p_trésorerie_station_id, p_type_mouvement, p_montant, p_date_mouvement,
        p_description, p_module_origine, p_reference_origine, p_utilisateur_id
    ) RETURNING id INTO v_id;

    -- Mettre à jour le solde actuel
    UPDATE tresorerie_station
    SET solde_actuel = (
        CASE
            WHEN p_type_mouvement = 'entrée' THEN solde_actuel + p_montant
            WHEN p_type_mouvement = 'sortie' THEN solde_actuel - p_montant
        END
    )
    WHERE id = p_trésorerie_station_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Fonction de vérification des écarts
CREATE OR REPLACE FUNCTION verifier_soldes_tresorerie()
RETURNS TABLE(
    trésorerie_station_id UUID,
    nom_trésorerie VARCHAR,
    station_nom VARCHAR,
    solde_enregistré DECIMAL,
    solde_calculé DECIMAL,
    écart DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ts.id,
        trs.nom,
        s.nom,
        ts.solde_actuel,
        (ts.solde_initial +
         COALESCE(credits.montant_total_credits, 0) -
         COALESCE(debits.montant_total_debits, 0) +
         COALESCE(recus.montant_total_recus, 0) -
         COALESCE(envoyes.montant_total_envoyes, 0)) AS solde_calculé,
        (ts.solde_actuel - (
            ts.solde_initial +
            COALESCE(credits.montant_total_credits, 0) -
            COALESCE(debits.montant_total_debits, 0) +
            COALESCE(recus.montant_total_recus, 0) -
            COALESCE(envoyes.montant_total_envoyes, 0)
        )) AS écart
    FROM tresorerie_station ts
    JOIN tresorerie trs ON ts.trésorerie_id = trs.id
    JOIN station s ON ts.station_id = s.id
    LEFT JOIN (
        SELECT trésorerie_station_id, SUM(montant) AS montant_total_credits
        FROM mouvement_tresorerie
        WHERE type_mouvement = 'entrée' AND statut = 'validé'
        GROUP BY trésorerie_station_id
    ) credits ON ts.id = credits.trésorerie_station_id
    LEFT JOIN (
        SELECT trésorerie_station_id, SUM(montant) AS montant_total_debits
        FROM mouvement_tresorerie
        WHERE type_mouvement = 'sortie' AND statut = 'validé'
        GROUP BY trésorerie_station_id
    ) debits ON ts.id = debits.trésorerie_station_id
    LEFT JOIN (
        SELECT trésorerie_destination_id AS trésorerie_station_id,
               SUM(montant) AS montant_total_recus
        FROM transfert_tresorerie
        WHERE statut = 'validé'
        GROUP BY trésorerie_destination_id
    ) recus ON ts.id = recus.trésorerie_station_id
    LEFT JOIN (
        SELECT trésorerie_source_id AS trésorerie_station_id,
               SUM(montant) AS montant_total_envoyes
        FROM transfert_tresorerie
        WHERE statut = 'validé'
        GROUP BY trésorerie_source_id
    ) envoyes ON ts.id = envoyes.trésorerie_station_id
    WHERE ABS(ts.solde_actuel - (
        ts.solde_initial +
        COALESCE(credits.montant_total_credits, 0) -
        COALESCE(debits.montant_total_debits, 0) +
        COALESCE(recus.montant_total_recus, 0) -
        COALESCE(envoyes.montant_total_envoyes, 0)
    )) > 0.01; -- Tolérance de 0.01 pour les arrondis
END;
$$ LANGUAGE plpgsql;

-- Table pour les tiers (clients, fournisseurs, employés)
CREATE TABLE IF NOT EXISTS tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID NOT NULL REFERENCES compagnie(id),
    type VARCHAR(50) CHECK (type IN ('client', 'fournisseur', 'employé')) NOT NULL,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telephone VARCHAR(50),
    adresse TEXT,
    statut VARCHAR(20) DEFAULT 'actif',
    donnees_personnelles JSONB,  -- Informations spécifiques selon le type
    station_ids JSONB DEFAULT '[]',  -- IDs des stations associées
    metadonnees JSONB,  -- Pour stocker des infos additionnelles
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table pour les soldes des tiers par station
CREATE TABLE IF NOT EXISTS solde_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    station_id UUID NOT NULL REFERENCES station(id),  -- Lier le solde à une station
    solde_actuel DECIMAL(15,2) DEFAULT 0.0,
    devise VARCHAR(10) DEFAULT 'XOF',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table pour les mouvements des tiers par station
CREATE TABLE IF NOT EXISTS mouvement_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tiers_id UUID NOT NULL REFERENCES tiers(id),
    station_id UUID NOT NULL REFERENCES station(id),  -- Lier le mouvement à une station
    type_mouvement VARCHAR(20) CHECK (type_mouvement IN ('entree', 'sortie')) NOT NULL,
    montant DECIMAL(15,2) NOT NULL,
    description VARCHAR(255),
    reference VARCHAR(100),  -- Référence de la transaction
    statut VARCHAR(20) DEFAULT 'en_attente',  -- en_attente, valide, annule
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);