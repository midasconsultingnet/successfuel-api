--
-- PostgreSQL database dump
--

-- Dumped from database version 17.6 (Debian 17.6-2.pgdg12+1)
-- Dumped by pg_dump version 17.5

-- Started on 2025-11-28 18:55:42

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4946 (class 1262 OID 28090)
-- Name: successfuel; Type: DATABASE; Schema: -; Owner: energixdb_k3c4_user
--

CREATE DATABASE successfuel WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF8';


ALTER DATABASE successfuel OWNER TO energixdb_k3c4_user;

\connect successfuel

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 258 (class 1259 OID 34366)
-- Name: achats; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.achats (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    fournisseur_id uuid,
    date_achat date NOT NULL,
    total numeric(18,2) NOT NULL,
    reference_facture character varying(100),
    observation text,
    type_achat character varying(20) DEFAULT 'Produits'::character varying NOT NULL,
    compagnie_id uuid,
    pays_id uuid,
    devise_code character varying(3) DEFAULT 'MGA'::character varying,
    taux_change numeric(15,6) DEFAULT 1.000000,
    journal_entry_id uuid,
    statut character varying(40) DEFAULT 'En attente de livraison'::character varying NOT NULL,
    date_livraison date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT achats_statut_check CHECK (((statut)::text = ANY ((ARRAY['En attente de livraison'::character varying, 'Livré'::character varying, 'Annulé'::character varying])::text[]))),
    CONSTRAINT achats_total_check CHECK ((total >= (0)::numeric)),
    CONSTRAINT achats_type_achat_check CHECK (((type_achat)::text = ANY ((ARRAY['Produits'::character varying, 'Carburants'::character varying])::text[])))
);


ALTER TABLE public.achats OWNER TO energixdb_k3c4_user;

--
-- TOC entry 260 (class 1259 OID 34417)
-- Name: achats_details; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.achats_details (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    achat_id uuid,
    article_id uuid NOT NULL,
    station_id uuid,
    cuve_id uuid,
    quantite numeric(18,3) NOT NULL,
    prix_unitaire numeric(18,4) NOT NULL,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    montant numeric(18,2) GENERATED ALWAYS AS ((quantite * prix_unitaire)) STORED,
    CONSTRAINT achats_details_prix_unitaire_check CHECK ((prix_unitaire >= (0)::numeric)),
    CONSTRAINT achats_details_quantite_check CHECK ((quantite >= (0)::numeric)),
    CONSTRAINT achats_details_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.achats_details OWNER TO energixdb_k3c4_user;

--
-- TOC entry 259 (class 1259 OID 34398)
-- Name: achats_stations; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.achats_stations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    achat_id uuid,
    station_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.achats_stations OWNER TO energixdb_k3c4_user;

--
-- TOC entry 262 (class 1259 OID 34472)
-- Name: achats_tresorerie; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.achats_tresorerie (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    achat_id uuid,
    tresorerie_id uuid,
    montant numeric(18,2) NOT NULL,
    note_paiement jsonb DEFAULT '{}'::jsonb,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT achats_tresorerie_montant_check CHECK ((montant >= (0)::numeric)),
    CONSTRAINT achats_tresorerie_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.achats_tresorerie OWNER TO energixdb_k3c4_user;

--
-- TOC entry 284 (class 1259 OID 35134)
-- Name: ajustements_stock; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.ajustements_stock (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    article_id uuid,
    cuve_id uuid,
    station_id uuid,
    type_ajustement character varying(20) NOT NULL,
    quantite numeric(18,3) NOT NULL,
    motif text NOT NULL,
    utilisateur_id uuid,
    date_ajustement date NOT NULL,
    commentaire text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ajustements_stock_type_ajustement_check CHECK (((type_ajustement)::text = ANY ((ARRAY['Entree'::character varying, 'Sortie'::character varying, 'Perte'::character varying, 'Casse'::character varying, 'Peremption'::character varying])::text[])))
);


ALTER TABLE public.ajustements_stock OWNER TO energixdb_k3c4_user;

--
-- TOC entry 325 (class 1259 OID 36823)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO energixdb_k3c4_user;

--
-- TOC entry 297 (class 1259 OID 35433)
-- Name: analyse_commerciale; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.analyse_commerciale (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    type_analyse character varying(50) NOT NULL,
    periode_debut date NOT NULL,
    periode_fin date NOT NULL,
    resultat jsonb,
    commentaire text,
    utilisateur_analyse_id uuid,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.analyse_commerciale OWNER TO energixdb_k3c4_user;

--
-- TOC entry 275 (class 1259 OID 34875)
-- Name: arrets_compte_caissier; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.arrets_compte_caissier (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ticket_caisse_id uuid,
    utilisateur_id uuid,
    date_arret date NOT NULL,
    heure_arret time without time zone NOT NULL,
    total_vente_especes numeric(18,2) DEFAULT 0,
    total_vente_cb numeric(18,2) DEFAULT 0,
    total_vente_chq numeric(18,2) DEFAULT 0,
    total_vente_autre numeric(18,2) DEFAULT 0,
    total_vente_credit numeric(18,2) DEFAULT 0,
    total_vente_total numeric(18,2) GENERATED ALWAYS AS (((((total_vente_especes + total_vente_cb) + total_vente_chq) + total_vente_autre) + total_vente_credit)) STORED,
    commentaire text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.arrets_compte_caissier OWNER TO energixdb_k3c4_user;

--
-- TOC entry 236 (class 1259 OID 33871)
-- Name: articles; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.articles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(40) NOT NULL,
    libelle character varying(150) NOT NULL,
    codebarre character varying(100),
    famille_id uuid,
    unite character varying(20) DEFAULT 'Litre'::character varying,
    unite_principale character varying(10),
    unite_stock character varying(10),
    compagnie_id uuid,
    type_article character varying(20) DEFAULT 'produit'::character varying,
    prix_achat numeric(18,4) DEFAULT 0,
    prix_vente numeric(18,4) DEFAULT 0,
    tva numeric(5,2) DEFAULT 0,
    taxes_applicables jsonb DEFAULT '[]'::jsonb,
    stock_minimal numeric(18,3) DEFAULT 0,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT articles_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[]))),
    CONSTRAINT articles_type_article_check CHECK (((type_article)::text = ANY ((ARRAY['produit'::character varying, 'service'::character varying])::text[])))
);


ALTER TABLE public.articles OWNER TO energixdb_k3c4_user;

--
-- TOC entry 296 (class 1259 OID 35411)
-- Name: assurances; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.assurances (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    type_assurance character varying(50) NOT NULL,
    compagnie_assurance character varying(100) NOT NULL,
    numero_police character varying(50) NOT NULL,
    date_debut date NOT NULL,
    date_fin date NOT NULL,
    montant_couverture numeric(18,2) NOT NULL,
    prime_annuelle numeric(18,2) NOT NULL,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    fichier_joint text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT assurances_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Expiré'::character varying, 'Annulé'::character varying])::text[])))
);


ALTER TABLE public.assurances OWNER TO energixdb_k3c4_user;

--
-- TOC entry 245 (class 1259 OID 34115)
-- Name: auth_tokens; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.auth_tokens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    token_hash character varying(255) NOT NULL,
    user_id uuid NOT NULL,
    expires_at timestamp with time zone,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    type_endpoint character varying(20) DEFAULT 'utilisateur'::character varying,
    CONSTRAINT auth_tokens_type_endpoint_check CHECK (((type_endpoint)::text = ANY ((ARRAY['administrateur'::character varying, 'utilisateur'::character varying])::text[])))
);


ALTER TABLE public.auth_tokens OWNER TO energixdb_k3c4_user;

--
-- TOC entry 242 (class 1259 OID 34045)
-- Name: barremage_cuves; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.barremage_cuves (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cuve_id uuid,
    station_id uuid,
    hauteur numeric(18,3) NOT NULL,
    volume numeric(18,3) NOT NULL,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    compagnie_id uuid,
    CONSTRAINT barremage_cuves_hauteur_check CHECK ((hauteur >= (0)::numeric)),
    CONSTRAINT barremage_cuves_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[]))),
    CONSTRAINT barremage_cuves_volume_check CHECK ((volume >= (0)::numeric))
);


ALTER TABLE public.barremage_cuves OWNER TO energixdb_k3c4_user;

--
-- TOC entry 254 (class 1259 OID 34291)
-- Name: bilan_initial; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.bilan_initial (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    compagnie_id uuid,
    date_bilan_initial date NOT NULL,
    est_valide boolean DEFAULT false,
    est_verifie boolean DEFAULT false,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    valeur_totale_stocks numeric(18,2) DEFAULT 0,
    nombre_elements integer DEFAULT 0,
    statut character varying(20) DEFAULT 'Brouillon'::character varying,
    utilisateur_validation_id uuid,
    date_validation date,
    date_bilan date,
    CONSTRAINT bilan_initial_statut_check CHECK (((statut)::text = ANY ((ARRAY['Brouillon'::character varying, 'En cours'::character varying, 'Termine'::character varying, 'Validé'::character varying])::text[])))
);


ALTER TABLE public.bilan_initial OWNER TO energixdb_k3c4_user;

--
-- TOC entry 287 (class 1259 OID 35221)
-- Name: bilan_initial_lignes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.bilan_initial_lignes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    bilan_initial_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    type_element character varying(20),
    element_id uuid,
    description_element text,
    quantite numeric(18,3) DEFAULT 0,
    unite_mesure character varying(10),
    prix_unitaire numeric(18,4) DEFAULT 0,
    valeur_totale numeric(18,2) DEFAULT 0,
    taux_tva numeric(5,2) DEFAULT 0,
    montant_tva numeric(18,2) DEFAULT 0,
    montant_ht numeric(18,2) DEFAULT 0,
    CONSTRAINT bilan_initial_lignes_type_element_check CHECK (((type_element)::text = ANY ((ARRAY['carburant'::character varying, 'article_boutique'::character varying, 'autre'::character varying])::text[])))
);


ALTER TABLE public.bilan_initial_lignes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 273 (class 1259 OID 34815)
-- Name: bons_commande; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.bons_commande (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    numero_bon character varying(50) NOT NULL,
    fournisseur_id uuid,
    date_bon date NOT NULL,
    total numeric(18,2) NOT NULL,
    observation text,
    type_bon character varying(20) DEFAULT 'Produits'::character varying NOT NULL,
    compagnie_id uuid,
    statut character varying(40) DEFAULT 'En cours'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT bons_commande_statut_check CHECK (((statut)::text = ANY ((ARRAY['En cours'::character varying, 'Livre'::character varying, 'Facture'::character varying, 'Annule'::character varying])::text[]))),
    CONSTRAINT bons_commande_total_check CHECK ((total >= (0)::numeric)),
    CONSTRAINT bons_commande_type_bon_check CHECK (((type_bon)::text = ANY ((ARRAY['Produits'::character varying, 'Carburants'::character varying])::text[])))
);


ALTER TABLE public.bons_commande OWNER TO energixdb_k3c4_user;

--
-- TOC entry 229 (class 1259 OID 33714)
-- Name: carburants; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.carburants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(40) NOT NULL,
    libelle character varying(150) NOT NULL,
    type character varying(50) NOT NULL,
    compagnie_id uuid,
    prix_achat numeric(18,4) DEFAULT 0,
    prix_vente numeric(18,4) DEFAULT 0,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT carburants_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.carburants OWNER TO energixdb_k3c4_user;

--
-- TOC entry 303 (class 1259 OID 35578)
-- Name: cartes_carburant; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.cartes_carburant (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    numero_carte character varying(50) NOT NULL,
    date_activation date NOT NULL,
    date_expiration date,
    solde_carte numeric(18,2) DEFAULT 0,
    plafond_mensuel numeric(18,2),
    statut character varying(20) DEFAULT 'Active'::character varying,
    utilisateur_creation_id uuid,
    utilisateur_blocage_id uuid,
    motif_blocage text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT cartes_carburant_statut_check CHECK (((statut)::text = ANY ((ARRAY['Active'::character varying, 'Inactive'::character varying, 'Bloquee'::character varying, 'Perdue'::character varying, 'Remplacee'::character varying])::text[])))
);


ALTER TABLE public.cartes_carburant OWNER TO energixdb_k3c4_user;

--
-- TOC entry 231 (class 1259 OID 33761)
-- Name: clients; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.clients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20) NOT NULL,
    nom character varying(150) NOT NULL,
    adresse text,
    telephone character varying(30),
    nif character varying(50),
    email character varying(150),
    compagnie_id uuid,
    station_ids jsonb DEFAULT '[]'::jsonb,
    type_tiers_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    nb_jrs_creance integer DEFAULT 0,
    solde_comptable numeric(18,2) DEFAULT 0,
    solde_confirme numeric(18,2) DEFAULT 0,
    date_dernier_rapprochement timestamp with time zone,
    devise_facturation character varying(3) DEFAULT 'MGA'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT clients_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.clients OWNER TO energixdb_k3c4_user;

--
-- TOC entry 221 (class 1259 OID 33560)
-- Name: compagnies; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.compagnies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20) NOT NULL,
    nom character varying(150) NOT NULL,
    adresse text,
    telephone character varying(30),
    email character varying(150),
    nif character varying(50),
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    pays_id uuid,
    devise_principale character varying(3) DEFAULT 'MGA'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT compagnies_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.compagnies OWNER TO energixdb_k3c4_user;

--
-- TOC entry 226 (class 1259 OID 33645)
-- Name: configurations_pays; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.configurations_pays (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pays_id uuid,
    cle_configuration character varying(100) NOT NULL,
    valeur_configuration text NOT NULL,
    description text,
    est_systeme boolean DEFAULT false,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT configurations_pays_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying])::text[])))
);


ALTER TABLE public.configurations_pays OWNER TO energixdb_k3c4_user;

--
-- TOC entry 304 (class 1259 OID 35613)
-- Name: contrats_clients; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.contrats_clients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    type_contrat character varying(50) NOT NULL,
    libelle character varying(100) NOT NULL,
    description text,
    date_debut date NOT NULL,
    date_fin date,
    volume_garanti numeric(18,3),
    prix_contractuel numeric(18,4),
    frequence_livraison integer,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT contrats_clients_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Expiré'::character varying, 'Annulé'::character varying, 'Suspendu'::character varying])::text[])))
);


ALTER TABLE public.contrats_clients OWNER TO energixdb_k3c4_user;

--
-- TOC entry 300 (class 1259 OID 35510)
-- Name: contrats_maintenance; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.contrats_maintenance (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    fournisseur_id uuid,
    type_contrat character varying(50) NOT NULL,
    libelle character varying(100) NOT NULL,
    description text,
    date_debut date NOT NULL,
    date_fin date,
    cout_mensuel numeric(18,2) NOT NULL,
    frequence integer,
    prochaine_intervention date,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT contrats_maintenance_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Expiré'::character varying, 'Annulé'::character varying])::text[])))
);


ALTER TABLE public.contrats_maintenance OWNER TO energixdb_k3c4_user;

--
-- TOC entry 301 (class 1259 OID 35537)
-- Name: controle_interne; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.controle_interne (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_controle character varying(50) NOT NULL,
    element_controle character varying(100),
    date_controle date NOT NULL,
    utilisateur_controle_id uuid,
    resultat character varying(20),
    montant_ecart numeric(18,2) DEFAULT 0,
    commentaire text,
    statut character varying(20) DEFAULT 'Terminé'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT controle_interne_resultat_check CHECK (((resultat)::text = ANY ((ARRAY['Conforme'::character varying, 'Anomalie'::character varying, 'Non applicable'::character varying])::text[]))),
    CONSTRAINT controle_interne_statut_check CHECK (((statut)::text = ANY ((ARRAY['Planifié'::character varying, 'En cours'::character varying, 'Terminé'::character varying, 'En attente'::character varying])::text[])))
);


ALTER TABLE public.controle_interne OWNER TO energixdb_k3c4_user;

--
-- TOC entry 244 (class 1259 OID 34097)
-- Name: conversions_unite; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.conversions_unite (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    unite_origine_id uuid,
    unite_destination_id uuid,
    facteur_conversion numeric(15,6) NOT NULL,
    est_actif boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.conversions_unite OWNER TO energixdb_k3c4_user;

--
-- TOC entry 306 (class 1259 OID 35665)
-- Name: couts_logistique; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.couts_logistique (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_cout character varying(50) NOT NULL,
    description text,
    montant numeric(18,2) NOT NULL,
    date_cout date NOT NULL,
    carburant_id uuid,
    station_id uuid,
    fournisseur_id uuid,
    utilisateur_saisie_id uuid,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.couts_logistique OWNER TO energixdb_k3c4_user;

--
-- TOC entry 327 (class 1259 OID 36873)
-- Name: couts_logistique_stocks_initial; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.couts_logistique_stocks_initial (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_cout character varying(50) NOT NULL,
    description text,
    montant numeric(18,2) NOT NULL,
    date_cout date NOT NULL,
    article_id uuid,
    cuve_id uuid,
    station_id uuid,
    fournisseur_id uuid,
    utilisateur_saisie_id uuid,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.couts_logistique_stocks_initial OWNER TO energixdb_k3c4_user;

--
-- TOC entry 310 (class 1259 OID 35752)
-- Name: cuve_stocks; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.cuve_stocks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cuve_id uuid,
    station_id uuid,
    stock_theorique numeric(18,3) DEFAULT 0,
    stock_reel numeric(18,3) DEFAULT 0,
    ecart_stock numeric(18,3) GENERATED ALWAYS AS ((stock_reel - stock_theorique)) STORED,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT cuve_stocks_stock_reel_check CHECK ((stock_reel >= (0)::numeric)),
    CONSTRAINT cuve_stocks_stock_theorique_check CHECK ((stock_theorique >= (0)::numeric))
);


ALTER TABLE public.cuve_stocks OWNER TO energixdb_k3c4_user;

--
-- TOC entry 311 (class 1259 OID 35780)
-- Name: cuve_stocks_mouvements; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.cuve_stocks_mouvements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cuve_stock_id uuid,
    cuve_id uuid,
    station_id uuid,
    type_mouvement character varying(20) NOT NULL,
    quantite numeric(18,3) NOT NULL,
    prix_unitaire numeric(18,4) DEFAULT 0,
    cout_total numeric(18,2) GENERATED ALWAYS AS ((quantite * prix_unitaire)) STORED,
    date_mouvement date NOT NULL,
    reference_operation character varying(100),
    utilisateur_id uuid,
    commentaire text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT cuve_stocks_mouvements_type_mouvement_check CHECK (((type_mouvement)::text = ANY ((ARRAY['Entree'::character varying, 'Sortie'::character varying, 'Ajustement'::character varying, 'Initial'::character varying])::text[])))
);


ALTER TABLE public.cuve_stocks_mouvements OWNER TO energixdb_k3c4_user;

--
-- TOC entry 238 (class 1259 OID 33936)
-- Name: cuves; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.cuves (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    code character varying(40) NOT NULL,
    capacite numeric(18,3) NOT NULL,
    carburant_id uuid,
    compagnie_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    temperature numeric(5,2) DEFAULT '0'::numeric NOT NULL,
    CONSTRAINT cuves_capacite_check CHECK ((capacite >= (0)::numeric)),
    CONSTRAINT cuves_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.cuves OWNER TO energixdb_k3c4_user;

--
-- TOC entry 293 (class 1259 OID 35336)
-- Name: declarations_fiscales; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.declarations_fiscales (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_declaration character varying(50) NOT NULL,
    periode_debut date NOT NULL,
    periode_fin date NOT NULL,
    montant_total numeric(18,2) NOT NULL,
    montant_declare numeric(18,2) NOT NULL,
    ecart numeric(18,2) GENERATED ALWAYS AS ((montant_declare - montant_total)) STORED,
    date_depot date,
    statut character varying(20) DEFAULT 'En attente'::character varying,
    fichier_joint text,
    utilisateur_depose_id uuid,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT declarations_fiscales_statut_check CHECK (((statut)::text = ANY ((ARRAY['En attente'::character varying, 'Soumis'::character varying, 'Traite'::character varying, 'Retour'::character varying])::text[])))
);


ALTER TABLE public.declarations_fiscales OWNER TO energixdb_k3c4_user;

--
-- TOC entry 280 (class 1259 OID 35003)
-- Name: depenses; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.depenses (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    categorie character varying(100) NOT NULL,
    libelle text NOT NULL,
    montant numeric(18,2) NOT NULL,
    date_depense date NOT NULL,
    mode_paiement character varying(50),
    tresorerie_id uuid,
    fournisseur_id uuid,
    utilisateur_id uuid,
    projet text,
    statut character varying(20) DEFAULT 'Active'::character varying NOT NULL,
    reference_piece character varying(100),
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT depenses_montant_check CHECK ((montant >= (0)::numeric)),
    CONSTRAINT depenses_statut_check CHECK (((statut)::text = ANY ((ARRAY['Active'::character varying, 'Payee'::character varying, 'Annulee'::character varying])::text[])))
);


ALTER TABLE public.depenses OWNER TO energixdb_k3c4_user;

--
-- TOC entry 285 (class 1259 OID 35169)
-- Name: depot_garantie; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.depot_garantie (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    montant numeric(18,2) NOT NULL,
    date_enregistrement date NOT NULL,
    mode_paiement character varying(50),
    reference_paiement character varying(100),
    utilisateur_enregistre_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    commentaire text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT depot_garantie_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Utilise'::character varying, 'Rembourse'::character varying, 'Transfere'::character varying])::text[])))
);


ALTER TABLE public.depot_garantie OWNER TO energixdb_k3c4_user;

--
-- TOC entry 261 (class 1259 OID 34443)
-- Name: dettes_fournisseurs; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.dettes_fournisseurs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    fournisseur_id uuid NOT NULL,
    achat_id uuid NOT NULL,
    montant_achat numeric(18,2) NOT NULL,
    montant_paye numeric(18,2) DEFAULT 0 NOT NULL,
    solde numeric(18,2) NOT NULL,
    date_creation date DEFAULT CURRENT_DATE NOT NULL,
    reference_facture character varying(100) NOT NULL,
    compagnie_id uuid NOT NULL,
    nb_jrs_creance integer DEFAULT 0,
    date_prevu_paiement date,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT dettes_fournisseurs_montant_paye_check CHECK ((montant_paye >= (0)::numeric)),
    CONSTRAINT dettes_fournisseurs_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Paye'::character varying, 'EnRetard'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.dettes_fournisseurs OWNER TO energixdb_k3c4_user;

--
-- TOC entry 255 (class 1259 OID 34308)
-- Name: ecarts_soldes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.ecarts_soldes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tiers_type character varying(20),
    tiers_id uuid,
    solde_fiche numeric(18,2),
    solde_reel numeric(18,2),
    ecart numeric(18,2) GENERATED ALWAYS AS ((solde_fiche - solde_reel)) STORED,
    statut character varying(20) DEFAULT 'Identifie'::character varying,
    utilisateur_detecte_id uuid,
    utilisateur_traite_id uuid,
    date_detection timestamp with time zone DEFAULT now(),
    date_traitement timestamp with time zone,
    motif text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ecarts_soldes_statut_check CHECK (((statut)::text = ANY ((ARRAY['Identifie'::character varying, 'Enquete'::character varying, 'Corrige'::character varying, 'Rejete'::character varying])::text[]))),
    CONSTRAINT ecarts_soldes_tiers_type_check CHECK (((tiers_type)::text = ANY ((ARRAY['Client'::character varying, 'Fournisseur'::character varying])::text[])))
);


ALTER TABLE public.ecarts_soldes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 232 (class 1259 OID 33790)
-- Name: employes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.employes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20) NOT NULL,
    nom character varying(150) NOT NULL,
    prenom character varying(150),
    adresse text,
    telephone character varying(30),
    poste character varying(100),
    salaire_base numeric(18,2) DEFAULT 0,
    station_ids jsonb DEFAULT '[]'::jsonb,
    compagnie_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    avances numeric(18,2) DEFAULT 0,
    creances numeric(18,2) DEFAULT 0,
    CONSTRAINT employes_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.employes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 319 (class 1259 OID 36010)
-- Name: etat_caisse; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.etat_caisse (
    id uuid NOT NULL,
    date_etat date NOT NULL,
    tresorerie_id uuid NOT NULL,
    solde_initial numeric(18,2),
    encaissements numeric(18,2),
    decaissements numeric(18,2),
    solde_final numeric(18,2),
    ecart numeric(18,2),
    observation text,
    statut character varying(20),
    compagnie_id uuid,
    created_at timestamp with time zone
);


ALTER TABLE public.etat_caisse OWNER TO energixdb_k3c4_user;

--
-- TOC entry 320 (class 1259 OID 36027)
-- Name: etat_comptable; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.etat_comptable (
    id uuid NOT NULL,
    date_etat date NOT NULL,
    compte_id uuid NOT NULL,
    solde_initial numeric(18,2),
    debit_periode numeric(18,2),
    credit_periode numeric(18,2),
    solde_final numeric(18,2),
    observation text,
    statut character varying(20),
    compagnie_id uuid,
    created_at timestamp with time zone
);


ALTER TABLE public.etat_comptable OWNER TO energixdb_k3c4_user;

--
-- TOC entry 318 (class 1259 OID 35993)
-- Name: etat_stock; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.etat_stock (
    id uuid NOT NULL,
    date_etat date NOT NULL,
    article_id uuid NOT NULL,
    station_id uuid NOT NULL,
    stock_initial numeric(18,3),
    entrees numeric(18,3),
    sorties numeric(18,3),
    stock_final numeric(18,3),
    valeur_stock numeric(18,2),
    observation text,
    statut character varying(20),
    compagnie_id uuid,
    created_at timestamp with time zone
);


ALTER TABLE public.etat_stock OWNER TO energixdb_k3c4_user;

--
-- TOC entry 247 (class 1259 OID 34141)
-- Name: evenements_securite; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.evenements_securite (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_evenement character varying(50) NOT NULL,
    description text,
    utilisateur_id uuid,
    ip_utilisateur character varying(45),
    poste_utilisateur character varying(100),
    session_id character varying(100),
    donnees_supplementaires jsonb,
    statut character varying(20) DEFAULT 'NonTraite'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT evenements_securite_statut_check CHECK (((statut)::text = ANY ((ARRAY['NonTraite'::character varying, 'EnCours'::character varying, 'Traite'::character varying, 'Ferme'::character varying])::text[])))
);


ALTER TABLE public.evenements_securite OWNER TO energixdb_k3c4_user;

--
-- TOC entry 227 (class 1259 OID 33663)
-- Name: familles_articles; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.familles_articles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(10) NOT NULL,
    libelle character varying(100) NOT NULL,
    compagnie_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    parent_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT familles_articles_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.familles_articles OWNER TO energixdb_k3c4_user;

--
-- TOC entry 281 (class 1259 OID 35036)
-- Name: fiches_paie; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.fiches_paie (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    employe_id uuid,
    mois_paie integer NOT NULL,
    annee_paie integer NOT NULL,
    date_paie date NOT NULL,
    salaire_base numeric(18,2) NOT NULL,
    avances numeric(18,2) DEFAULT 0,
    autres_deductions numeric(18,2) DEFAULT 0,
    cotisations_sociales numeric(18,2) DEFAULT 0,
    autres_retenues numeric(18,2) DEFAULT 0,
    salaire_net numeric(18,2) GENERATED ALWAYS AS (((((salaire_base - avances) - autres_deductions) - cotisations_sociales) - autres_retenues)) STORED,
    commentaire text,
    utilisateur_calcul_id uuid,
    utilisateur_paye_id uuid,
    statut character varying(20) DEFAULT 'Calculee'::character varying NOT NULL,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT fiches_paie_statut_check CHECK (((statut)::text = ANY ((ARRAY['Calculee'::character varying, 'Payee'::character varying, 'Annulee'::character varying])::text[])))
);


ALTER TABLE public.fiches_paie OWNER TO energixdb_k3c4_user;

--
-- TOC entry 230 (class 1259 OID 33733)
-- Name: fournisseurs; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.fournisseurs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20) NOT NULL,
    nom character varying(150) NOT NULL,
    adresse text,
    telephone character varying(30),
    nif character varying(50),
    email character varying(150),
    compagnie_id uuid,
    station_ids jsonb DEFAULT '[]'::jsonb,
    type_tiers_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    nb_jrs_creance integer DEFAULT 0,
    solde_comptable numeric(18,2) DEFAULT 0,
    solde_confirme numeric(18,2) DEFAULT 0,
    date_dernier_rapprochement timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT fournisseurs_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.fournisseurs OWNER TO energixdb_k3c4_user;

--
-- TOC entry 308 (class 1259 OID 35713)
-- Name: historique_actions_utilisateurs; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.historique_actions_utilisateurs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    utilisateur_id uuid,
    action character varying(100) NOT NULL,
    module character varying(50) NOT NULL,
    sous_module character varying(50),
    objet_id uuid,
    donnees_avant jsonb,
    donnees_apres jsonb,
    ip_utilisateur character varying(45),
    poste_utilisateur character varying(100),
    session_id character varying(100),
    statut_action character varying(20) DEFAULT 'Reussie'::character varying,
    commentaire text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT historique_actions_utilisateurs_statut_action_check CHECK (((statut_action)::text = ANY ((ARRAY['Reussie'::character varying, 'Echouee'::character varying, 'Bloquee'::character varying])::text[])))
);


ALTER TABLE public.historique_actions_utilisateurs OWNER TO energixdb_k3c4_user;

--
-- TOC entry 252 (class 1259 OID 34243)
-- Name: historique_index_pistolets; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.historique_index_pistolets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pistolet_id uuid,
    index_releve numeric(18,3) NOT NULL,
    date_releve date NOT NULL,
    utilisateur_id uuid,
    observation text,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT historique_index_pistolets_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.historique_index_pistolets OWNER TO energixdb_k3c4_user;

--
-- TOC entry 276 (class 1259 OID 34905)
-- Name: historique_paiements_clients; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.historique_paiements_clients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    montant_paye numeric(18,2) NOT NULL,
    date_paiement date NOT NULL,
    mode_paiement character varying(50),
    reference_paiement character varying(100),
    utilisateur_id uuid,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.historique_paiements_clients OWNER TO energixdb_k3c4_user;

--
-- TOC entry 250 (class 1259 OID 34205)
-- Name: historique_prix_articles; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.historique_prix_articles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    article_id uuid NOT NULL,
    prix_achat numeric(18,4) DEFAULT 0,
    prix_vente numeric(18,4) DEFAULT 0,
    date_application date NOT NULL,
    utilisateur_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.historique_prix_articles OWNER TO energixdb_k3c4_user;

--
-- TOC entry 251 (class 1259 OID 34224)
-- Name: historique_prix_carburants; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.historique_prix_carburants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    carburant_id uuid NOT NULL,
    prix_achat numeric(18,4) DEFAULT 0,
    prix_vente numeric(18,4) DEFAULT 0,
    date_application date NOT NULL,
    utilisateur_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.historique_prix_carburants OWNER TO energixdb_k3c4_user;

--
-- TOC entry 282 (class 1259 OID 35073)
-- Name: immobilisations; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.immobilisations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(50) NOT NULL,
    libelle text NOT NULL,
    categorie character varying(100) NOT NULL,
    date_achat date NOT NULL,
    valeur_acquisition numeric(18,2) NOT NULL,
    valeur_nette_comptable numeric(18,2) NOT NULL,
    amortissement_annuel numeric(18,2) DEFAULT 0,
    duree_amortissement integer DEFAULT 0,
    date_fin_amortissement date,
    fournisseur_id uuid,
    tresorerie_id uuid,
    utilisateur_achat_id uuid,
    observation text,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT immobilisations_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Cede'::character varying, 'Hors service'::character varying, 'Vendu'::character varying])::text[])))
);


ALTER TABLE public.immobilisations OWNER TO energixdb_k3c4_user;

--
-- TOC entry 295 (class 1259 OID 35378)
-- Name: incidents_securite; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.incidents_securite (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    type_incident character varying(50) NOT NULL,
    date_incident timestamp with time zone NOT NULL,
    description text NOT NULL,
    gravite integer,
    statut character varying(20) DEFAULT 'Ouvert'::character varying,
    utilisateur_declare_id uuid,
    utilisateur_traite_id uuid,
    action_corrective text,
    date_resolution timestamp with time zone,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT incidents_securite_gravite_check CHECK (((gravite >= 1) AND (gravite <= 5))),
    CONSTRAINT incidents_securite_statut_check CHECK (((statut)::text = ANY ((ARRAY['Ouvert'::character varying, 'En cours'::character varying, 'Résolu'::character varying, 'Fermé'::character varying])::text[]))),
    CONSTRAINT incidents_securite_type_incident_check CHECK (((type_incident)::text = ANY ((ARRAY['Fuite'::character varying, 'Accident'::character varying, 'Vol'::character varying, 'Intrusion'::character varying, 'Autre'::character varying])::text[])))
);


ALTER TABLE public.incidents_securite OWNER TO energixdb_k3c4_user;

--
-- TOC entry 314 (class 1259 OID 35911)
-- Name: inventaire; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.inventaire (
    id uuid NOT NULL,
    numero character varying(50) NOT NULL,
    date_inventaire date NOT NULL,
    heure_debut time without time zone NOT NULL,
    heure_fin time without time zone,
    utilisateur_id uuid,
    station_id uuid NOT NULL,
    type_inventaire character varying(20),
    observation text,
    statut character varying(20),
    compagnie_id uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.inventaire OWNER TO energixdb_k3c4_user;

--
-- TOC entry 322 (class 1259 OID 36059)
-- Name: inventaire_details; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.inventaire_details (
    id uuid NOT NULL,
    inventaire_id uuid NOT NULL,
    article_id uuid NOT NULL,
    cuve_id uuid,
    stock_theorique numeric(18,3),
    stock_reel numeric(18,3),
    ecart numeric(18,3),
    observation text,
    statut character varying(20),
    created_at timestamp with time zone
);


ALTER TABLE public.inventaire_details OWNER TO energixdb_k3c4_user;

--
-- TOC entry 277 (class 1259 OID 34924)
-- Name: inventaires; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.inventaires (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    type_inventaire character varying(20) DEFAULT 'Complet'::character varying NOT NULL,
    date_inventaire date NOT NULL,
    utilisateur_id uuid,
    statut character varying(20) DEFAULT 'En cours'::character varying NOT NULL,
    commentaire text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT inventaires_statut_check CHECK (((statut)::text = ANY ((ARRAY['En cours'::character varying, 'Termine'::character varying, 'Cloture'::character varying])::text[]))),
    CONSTRAINT inventaires_type_inventaire_check CHECK (((type_inventaire)::text = ANY ((ARRAY['Carburant'::character varying, 'Boutique'::character varying, 'Complet'::character varying])::text[])))
);


ALTER TABLE public.inventaires OWNER TO energixdb_k3c4_user;

--
-- TOC entry 271 (class 1259 OID 34753)
-- Name: journal_entries; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.journal_entries (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    date_ecriture date NOT NULL,
    libelle text NOT NULL,
    type_operation character varying(30) DEFAULT 'Autre'::character varying,
    reference_operation character varying(100),
    compagnie_id uuid,
    pays_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_by uuid,
    est_valide boolean DEFAULT false,
    valide_par uuid,
    date_validation timestamp with time zone,
    type_document_origine character varying(50),
    document_origine_id uuid,
    est_ouverture boolean DEFAULT false,
    bilan_initial_id uuid,
    CONSTRAINT journal_entries_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[]))),
    CONSTRAINT journal_entries_type_operation_check CHECK (((type_operation)::text = ANY ((ARRAY['Achat'::character varying, 'Vente'::character varying, 'Tresorerie'::character varying, 'Stock'::character varying, 'Autre'::character varying, 'Ouverture'::character varying, 'Regul'::character varying])::text[])))
);


ALTER TABLE public.journal_entries OWNER TO energixdb_k3c4_user;

--
-- TOC entry 272 (class 1259 OID 34793)
-- Name: journal_lines; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.journal_lines (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entry_id uuid,
    compte_num character varying(20),
    compte_id uuid,
    debit numeric(18,2) DEFAULT 0,
    credit numeric(18,2) DEFAULT 0,
    sens character(1) GENERATED ALWAYS AS (
CASE
    WHEN (debit > credit) THEN 'D'::text
    WHEN (credit > debit) THEN 'C'::text
    ELSE 'D'::text
END) STORED,
    CONSTRAINT journal_lines_credit_check CHECK ((credit >= (0)::numeric)),
    CONSTRAINT journal_lines_debit_check CHECK ((debit >= (0)::numeric)),
    CONSTRAINT journal_lines_sens_check CHECK ((sens = ANY (ARRAY['D'::bpchar, 'C'::bpchar])))
);


ALTER TABLE public.journal_lines OWNER TO energixdb_k3c4_user;

--
-- TOC entry 317 (class 1259 OID 35979)
-- Name: journaux; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.journaux (
    id uuid NOT NULL,
    code character varying(20) NOT NULL,
    libelle character varying(100) NOT NULL,
    type_journal character varying(30) NOT NULL,
    observation text,
    statut character varying(20),
    compagnie_id uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.journaux OWNER TO energixdb_k3c4_user;

--
-- TOC entry 292 (class 1259 OID 35304)
-- Name: kpi_operations; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.kpi_operations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    periode date NOT NULL,
    type_carburant uuid,
    litres_vendus numeric(18,3) DEFAULT 0,
    marge_brute numeric(18,2) DEFAULT 0,
    nombre_clients_servis integer DEFAULT 0,
    volume_moyen_transaction numeric(18,3) DEFAULT 0,
    rendement_pompiste uuid,
    productivite_horaires numeric(18,3) DEFAULT 0,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.kpi_operations OWNER TO energixdb_k3c4_user;

--
-- TOC entry 279 (class 1259 OID 34978)
-- Name: mesures_inventaire_articles; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mesures_inventaire_articles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    inventaire_id uuid,
    article_id uuid,
    stock_reel numeric(18,3) NOT NULL,
    stock_theorique numeric(18,3) NOT NULL,
    ecart numeric(18,3) GENERATED ALWAYS AS ((stock_reel - stock_theorique)) STORED,
    utilisateur_id uuid,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mesures_inventaire_articles OWNER TO energixdb_k3c4_user;

--
-- TOC entry 278 (class 1259 OID 34953)
-- Name: mesures_inventaire_cuves; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mesures_inventaire_cuves (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    inventaire_id uuid,
    cuve_id uuid,
    hauteur_reelle numeric(18,3) NOT NULL,
    volume_reel numeric(18,3) NOT NULL,
    stock_reel numeric(18,3) NOT NULL,
    stock_theorique numeric(18,3) NOT NULL,
    ecart numeric(18,3) GENERATED ALWAYS AS ((stock_reel - stock_theorique)) STORED,
    utilisateur_id uuid,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mesures_inventaire_cuves OWNER TO energixdb_k3c4_user;

--
-- TOC entry 263 (class 1259 OID 34496)
-- Name: mesures_livraison; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mesures_livraison (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    achat_id uuid,
    cuve_id uuid,
    mesure_avant_livraison numeric(18,3) NOT NULL,
    mesure_apres_livraison numeric(18,3) NOT NULL,
    ecart_livraison numeric(18,3) GENERATED ALWAYS AS ((mesure_apres_livraison - mesure_avant_livraison)) STORED,
    utilisateur_id uuid,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mesures_livraison OWNER TO energixdb_k3c4_user;

--
-- TOC entry 224 (class 1259 OID 33616)
-- Name: methode_paiment; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.methode_paiment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_tresorerie character varying(100) NOT NULL,
    mode_paiement jsonb DEFAULT '[]'::jsonb,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT methode_paiment_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.methode_paiment OWNER TO energixdb_k3c4_user;

--
-- TOC entry 291 (class 1259 OID 35287)
-- Name: modeles_rapports; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.modeles_rapports (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code_modele character varying(50) NOT NULL,
    libelle_modele character varying(200) NOT NULL,
    pays_id uuid,
    type_rapport character varying(50) NOT NULL,
    format_sortie character varying(20) DEFAULT 'PDF'::character varying,
    contenu_modele text,
    est_actif boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.modeles_rapports OWNER TO energixdb_k3c4_user;

--
-- TOC entry 248 (class 1259 OID 34162)
-- Name: modifications_sensibles; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.modifications_sensibles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    utilisateur_id uuid,
    type_operation character varying(50) NOT NULL,
    objet_modifie character varying(50),
    objet_id uuid,
    ancienne_valeur jsonb,
    nouvelle_valeur jsonb,
    seuil_alerte boolean DEFAULT false,
    commentaire text,
    ip_utilisateur character varying(45),
    poste_utilisateur character varying(100),
    statut character varying(20) DEFAULT 'Enregistre'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT modifications_sensibles_statut_check CHECK (((statut)::text = ANY ((ARRAY['Enregistre'::character varying, 'Enquete'::character varying, 'Traite'::character varying, 'Ferme'::character varying])::text[])))
);


ALTER TABLE public.modifications_sensibles OWNER TO energixdb_k3c4_user;

--
-- TOC entry 219 (class 1259 OID 33534)
-- Name: modules; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.modules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    libelle character varying(100) NOT NULL,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    CONSTRAINT modules_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying])::text[])))
);


ALTER TABLE public.modules OWNER TO energixdb_k3c4_user;

--
-- TOC entry 283 (class 1259 OID 35109)
-- Name: mouvements_immobilisations; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mouvements_immobilisations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    immobilisation_id uuid,
    type_mouvement character varying(20) NOT NULL,
    date_mouvement date NOT NULL,
    valeur_mouvement numeric(18,2) NOT NULL,
    commentaire text,
    utilisateur_id uuid,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT mouvements_immobilisations_type_mouvement_check CHECK (((type_mouvement)::text = ANY ((ARRAY['Achat'::character varying, 'Amortissement'::character varying, 'Cession'::character varying, 'Hors service'::character varying, 'Vente'::character varying])::text[])))
);


ALTER TABLE public.mouvements_immobilisations OWNER TO energixdb_k3c4_user;

--
-- TOC entry 313 (class 1259 OID 35872)
-- Name: mouvements_stock; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mouvements_stock (
    id uuid NOT NULL,
    numero character varying(50) NOT NULL,
    type_mouvement character varying(20) NOT NULL,
    article_id uuid NOT NULL,
    station_id uuid NOT NULL,
    fournisseur_id uuid,
    client_id uuid,
    utilisateur_id uuid,
    date_mouvement date NOT NULL,
    quantite numeric(18,3) NOT NULL,
    prix_unitaire numeric(18,4),
    valeur_totale numeric(18,2),
    observation text,
    reference_externe character varying(100),
    compagnie_id uuid,
    pays_id uuid,
    statut character varying(20),
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.mouvements_stock OWNER TO energixdb_k3c4_user;

--
-- TOC entry 321 (class 1259 OID 36044)
-- Name: mouvements_stock_details; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mouvements_stock_details (
    id uuid NOT NULL,
    mouvement_id uuid NOT NULL,
    article_id uuid NOT NULL,
    cuve_id uuid,
    quantite numeric(18,3) NOT NULL,
    prix_unitaire numeric(18,4),
    valeur_totale numeric(18,2),
    statut character varying(20),
    created_at timestamp with time zone
);


ALTER TABLE public.mouvements_stock_details OWNER TO energixdb_k3c4_user;

--
-- TOC entry 266 (class 1259 OID 34600)
-- Name: mouvements_tresorerie; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mouvements_tresorerie (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tresorerie_id uuid,
    type_mouvement character varying(20) NOT NULL,
    sous_type_mouvement character varying(30) NOT NULL,
    montant numeric(18,2) NOT NULL,
    reference_operation character varying(100),
    utilisateur_id uuid,
    commentaire text,
    date_mouvement date NOT NULL,
    date_enregistrement timestamp with time zone DEFAULT now() NOT NULL,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    mouvement_origine_id uuid,
    compagnie_id uuid,
    CONSTRAINT mouvements_tresorerie_check CHECK (((((type_mouvement)::text = 'Annulation'::text) AND (mouvement_origine_id IS NOT NULL)) OR ((type_mouvement)::text <> 'Annulation'::text))),
    CONSTRAINT mouvements_tresorerie_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Annule'::character varying, 'Corrige'::character varying, 'EnAttente'::character varying])::text[]))),
    CONSTRAINT mouvements_tresorerie_type_mouvement_check CHECK (((type_mouvement)::text = ANY ((ARRAY['Entree'::character varying, 'Sortie'::character varying, 'Annulation'::character varying, 'Correction'::character varying])::text[])))
);


ALTER TABLE public.mouvements_tresorerie OWNER TO energixdb_k3c4_user;

--
-- TOC entry 316 (class 1259 OID 35964)
-- Name: mouvements_tresorerie_details; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.mouvements_tresorerie_details (
    id uuid NOT NULL,
    mouvement_id uuid NOT NULL,
    compte_comptable_id uuid,
    type_operation character varying(20),
    montant numeric(18,2) NOT NULL,
    statut character varying(20),
    created_at timestamp with time zone
);


ALTER TABLE public.mouvements_tresorerie_details OWNER TO energixdb_k3c4_user;

--
-- TOC entry 218 (class 1259 OID 33520)
-- Name: pays; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.pays (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code_pays character(3) NOT NULL,
    nom_pays character varying(100) NOT NULL,
    devise_principale character varying(3) NOT NULL,
    taux_tva_par_defaut numeric(5,2) DEFAULT 0,
    systeme_comptable character varying(50) DEFAULT 'OHADA'::character varying,
    date_application_tva date,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT pays_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying])::text[])))
);


ALTER TABLE public.pays OWNER TO energixdb_k3c4_user;

--
-- TOC entry 288 (class 1259 OID 35239)
-- Name: periodes_comptables; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.periodes_comptables (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    annee integer NOT NULL,
    mois integer NOT NULL,
    date_debut date NOT NULL,
    date_fin date NOT NULL,
    est_cloture boolean DEFAULT false,
    est_exercice boolean DEFAULT false,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT periodes_comptables_mois_check CHECK (((mois >= 1) AND (mois <= 12)))
);


ALTER TABLE public.periodes_comptables OWNER TO energixdb_k3c4_user;

--
-- TOC entry 235 (class 1259 OID 33855)
-- Name: permissions; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.permissions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    libelle character varying(100) NOT NULL,
    description text,
    module_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT permissions_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying])::text[])))
);


ALTER TABLE public.permissions OWNER TO energixdb_k3c4_user;

--
-- TOC entry 270 (class 1259 OID 34735)
-- Name: permissions_tresorerie; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.permissions_tresorerie (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    utilisateur_id uuid,
    tresorerie_id uuid,
    droits character varying(20),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT permissions_tresorerie_droits_check CHECK (((droits)::text = ANY ((ARRAY['lecture'::character varying, 'ecriture'::character varying, 'validation'::character varying, 'admin'::character varying])::text[])))
);


ALTER TABLE public.permissions_tresorerie OWNER TO energixdb_k3c4_user;

--
-- TOC entry 243 (class 1259 OID 34072)
-- Name: pistolets; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.pistolets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(40) NOT NULL,
    pompe_id uuid,
    cuve_id uuid,
    index_initiale numeric(18,3) DEFAULT 0,
    compagnie_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT pistolets_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.pistolets OWNER TO energixdb_k3c4_user;

--
-- TOC entry 228 (class 1259 OID 33685)
-- Name: plan_comptable; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.plan_comptable (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    numero character varying(20) NOT NULL,
    intitule character varying(255) NOT NULL,
    classe character varying(5) NOT NULL,
    type_compte character varying(100) NOT NULL,
    sens_solde character varying(10),
    compte_parent_id uuid,
    description text,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    est_compte_racine boolean DEFAULT false,
    est_compte_de_resultat boolean DEFAULT false,
    est_compte_actif boolean DEFAULT true,
    pays_id uuid,
    compagnie_id UUID REFERENCES compagnies(id),
    est_specifique_pays boolean DEFAULT false,
    code_pays character varying(3),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT plan_comptable_sens_solde_check CHECK (((sens_solde)::text = ANY ((ARRAY['D'::character varying, 'C'::character varying])::text[]))),
    CONSTRAINT plan_comptable_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.plan_comptable OWNER TO energixdb_k3c4_user;

--
-- TOC entry 309 (class 1259 OID 35734)
-- Name: plan_comptable_pays; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.plan_comptable_pays (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    plan_comptable_id uuid,
    pays_id uuid,
    numero_compte_local character varying(20),
    intitule_local character varying(255),
    est_compte_obligatoire boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.plan_comptable_pays OWNER TO energixdb_k3c4_user;

--
-- TOC entry 249 (class 1259 OID 34184)
-- Name: politiques_securite; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.politiques_securite (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nom_politique character varying(100) NOT NULL,
    description text,
    type_politique character varying(50) NOT NULL,
    valeur_parametre character varying(200),
    seuil_valeur integer,
    est_actif boolean DEFAULT true,
    commentaire text,
    utilisateur_config_id uuid,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.politiques_securite OWNER TO energixdb_k3c4_user;

--
-- TOC entry 237 (class 1259 OID 33915)
-- Name: pompes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.pompes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    code character varying(40) NOT NULL,
    compagnie_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT pompes_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.pompes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 298 (class 1259 OID 35457)
-- Name: prevision_demande; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.prevision_demande (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    carburant_id uuid,
    station_id uuid,
    date_prevision date NOT NULL,
    quantite_prevue numeric(18,3) NOT NULL,
    methode_prevision character varying(50) NOT NULL,
    confiance_prevision numeric(5,2),
    commentaire text,
    utilisateur_prevision_id uuid,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT prevision_demande_confiance_prevision_check CHECK (((confiance_prevision >= (0)::numeric) AND (confiance_prevision <= (100)::numeric)))
);


ALTER TABLE public.prevision_demande OWNER TO energixdb_k3c4_user;

--
-- TOC entry 256 (class 1259 OID 34332)
-- Name: profil_permissions; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.profil_permissions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    profil_id uuid,
    permission_id uuid
);


ALTER TABLE public.profil_permissions OWNER TO energixdb_k3c4_user;

--
-- TOC entry 234 (class 1259 OID 33836)
-- Name: profils; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.profils (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20) NOT NULL,
    libelle character varying(100) NOT NULL,
    compagnie_id uuid,
    description text,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    type_profil character varying(50) DEFAULT 'utilisateur_compagnie'::character varying,
    CONSTRAINT profils_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[]))),
    CONSTRAINT type_profil_check CHECK (((type_profil)::text = ANY ((ARRAY['administrateur'::character varying, 'gerant_compagnie'::character varying, 'utilisateur_compagnie'::character varying])::text[])))
);


ALTER TABLE public.profils OWNER TO energixdb_k3c4_user;

--
-- TOC entry 302 (class 1259 OID 35560)
-- Name: programme_fidelite; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.programme_fidelite (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    libelle character varying(100) NOT NULL,
    description text,
    type_programme character varying(50) NOT NULL,
    seuil_activation numeric(18,2) DEFAULT 0,
    benefice text,
    date_debut date NOT NULL,
    date_fin date,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT programme_fidelite_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Expiré'::character varying])::text[])))
);


ALTER TABLE public.programme_fidelite OWNER TO energixdb_k3c4_user;

--
-- TOC entry 305 (class 1259 OID 35635)
-- Name: qualite_carburant; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.qualite_carburant (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    carburant_id uuid,
    cuve_id uuid,
    date_controle date NOT NULL,
    utilisateur_controle_id uuid,
    type_controle character varying(50) NOT NULL,
    valeur_relevee character varying(50),
    valeur_standard character varying(50),
    resultat character varying(20),
    observation text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT qualite_carburant_resultat_check CHECK (((resultat)::text = ANY ((ARRAY['Conforme'::character varying, 'Non conforme'::character varying])::text[])))
);


ALTER TABLE public.qualite_carburant OWNER TO energixdb_k3c4_user;

--
-- TOC entry 326 (class 1259 OID 36843)
-- Name: qualite_carburant_initial; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.qualite_carburant_initial (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cuve_id uuid,
    carburant_id uuid,
    date_analyse date NOT NULL,
    utilisateur_id uuid,
    densite numeric(8,4),
    indice_octane integer,
    soufre_ppm numeric(10,2),
    type_additif character varying(100),
    commentaire_qualite text,
    resultat_qualite character varying(20),
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT qualite_carburant_initial_resultat_qualite_check CHECK (((resultat_qualite)::text = ANY ((ARRAY['Conforme'::character varying, 'Non conforme'::character varying, 'En attente'::character varying])::text[])))
);


ALTER TABLE public.qualite_carburant_initial OWNER TO energixdb_k3c4_user;

--
-- TOC entry 290 (class 1259 OID 35273)
-- Name: rapports_financiers; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.rapports_financiers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_rapport character varying(50) NOT NULL,
    periode_debut date NOT NULL,
    periode_fin date NOT NULL,
    contenu jsonb,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.rapports_financiers OWNER TO energixdb_k3c4_user;

--
-- TOC entry 312 (class 1259 OID 35838)
-- Name: reglements; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.reglements (
    id uuid NOT NULL,
    numero character varying(50) NOT NULL,
    client_id uuid,
    utilisateur_id uuid,
    station_id uuid NOT NULL,
    date_reglement date NOT NULL,
    montant numeric(18,2) NOT NULL,
    type_paiement character varying(50) NOT NULL,
    reference_paiement character varying(100),
    observation text,
    compagnie_id uuid,
    pays_id uuid,
    statut character varying(20),
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.reglements OWNER TO energixdb_k3c4_user;

--
-- TOC entry 253 (class 1259 OID 34264)
-- Name: reinitialisation_index_pistolets; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.reinitialisation_index_pistolets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pistolet_id uuid,
    ancien_index numeric(18,3) NOT NULL,
    nouvel_index numeric(18,3) NOT NULL,
    utilisateur_demande_id uuid,
    utilisateur_autorise_id uuid,
    motif text NOT NULL,
    date_demande timestamp with time zone DEFAULT now() NOT NULL,
    date_autorisation timestamp with time zone,
    statut character varying(20) DEFAULT 'En attente'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT reinitialisation_index_pistolets_statut_check CHECK (((statut)::text = ANY ((ARRAY['En attente'::character varying, 'Approuve'::character varying, 'Rejete'::character varying, 'Annule'::character varying])::text[])))
);


ALTER TABLE public.reinitialisation_index_pistolets OWNER TO energixdb_k3c4_user;

--
-- TOC entry 299 (class 1259 OID 35487)
-- Name: services_annexes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.services_annexes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    type_service character varying(50) NOT NULL,
    libelle character varying(100) NOT NULL,
    description text,
    prix_unitaire numeric(18,2) NOT NULL,
    unite_mesure character varying(20) DEFAULT 'Unité'::character varying,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT services_annexes_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprimé'::character varying])::text[])))
);


ALTER TABLE public.services_annexes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 289 (class 1259 OID 35254)
-- Name: soldes_comptables; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.soldes_comptables (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    compte_numero character varying(20) NOT NULL,
    date_solde date NOT NULL,
    solde_debit numeric(18,2) DEFAULT 0,
    solde_credit numeric(18,2) DEFAULT 0,
    compagnie_id uuid,
    periode_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.soldes_comptables OWNER TO energixdb_k3c4_user;

--
-- TOC entry 225 (class 1259 OID 33629)
-- Name: specifications_locales; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.specifications_locales (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pays_id uuid,
    type_specification character varying(50) NOT NULL,
    code_specification character varying(50) NOT NULL,
    libelle_specification character varying(200) NOT NULL,
    valeur_specification character varying(200),
    taux_specification numeric(10,4),
    est_actif boolean DEFAULT true,
    date_debut_validite date,
    date_fin_validite date,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.specifications_locales OWNER TO energixdb_k3c4_user;

--
-- TOC entry 223 (class 1259 OID 33593)
-- Name: stations; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.stations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    compagnie_id uuid,
    code character varying(20) NOT NULL,
    nom character varying(100) NOT NULL,
    telephone character varying(30),
    email character varying(150),
    adresse text,
    pays_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT stations_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.stations OWNER TO energixdb_k3c4_user;

--
-- TOC entry 264 (class 1259 OID 34521)
-- Name: stocks; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.stocks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    article_id uuid,
    cuve_id uuid,
    station_id uuid,
    stock_theorique numeric(18,3) DEFAULT 0,
    stock_reel numeric(18,3) DEFAULT 0,
    ecart_stock numeric(18,3) GENERATED ALWAYS AS ((stock_reel - stock_theorique)) STORED,
    compagnie_id uuid,
    est_initial boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    date_initialisation date,
    utilisateur_initialisation uuid,
    observation_initialisation text,
    stock_minimal numeric(18,3) DEFAULT 0,
    stock_maximal numeric(18,3) DEFAULT 0,
    prix_unitaire numeric(18,4) DEFAULT 0,
    CONSTRAINT stocks_stock_reel_check CHECK ((stock_reel >= (0)::numeric)),
    CONSTRAINT stocks_stock_theorique_check CHECK ((stock_theorique >= (0)::numeric))
);


ALTER TABLE public.stocks OWNER TO energixdb_k3c4_user;

--
-- TOC entry 265 (class 1259 OID 34555)
-- Name: stocks_mouvements; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.stocks_mouvements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    stock_id uuid,
    article_id uuid,
    cuve_id uuid,
    station_id uuid,
    type_mouvement character varying(20) NOT NULL,
    quantite numeric(18,3) NOT NULL,
    prix_unitaire numeric(18,4) DEFAULT 0,
    cout_total numeric(18,2) GENERATED ALWAYS AS ((quantite * prix_unitaire)) STORED,
    date_mouvement date NOT NULL,
    reference_operation character varying(100),
    utilisateur_id uuid,
    commentaire text,
    compagnie_id uuid,
    valeur_stock_avant numeric(18,2) DEFAULT 0,
    valeur_stock_apres numeric(18,2) DEFAULT 0,
    cout_unitaire_moyen_apres numeric(18,4) DEFAULT 0,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    est_initial boolean DEFAULT false,
    operation_initialisation_id uuid,
    CONSTRAINT stocks_mouvements_type_mouvement_check CHECK (((type_mouvement)::text = ANY ((ARRAY['Entree'::character varying, 'Sortie'::character varying, 'Ajustement'::character varying, 'Inventaire'::character varying, 'Initial'::character varying])::text[])))
);


ALTER TABLE public.stocks_mouvements OWNER TO energixdb_k3c4_user;

--
-- TOC entry 294 (class 1259 OID 35358)
-- Name: suivi_conformite; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.suivi_conformite (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_norme character varying(50) NOT NULL,
    libelle character varying(100) NOT NULL,
    description text,
    date_prevue date NOT NULL,
    date_realisee date,
    resultat character varying(20),
    responsable_id uuid,
    observation text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT suivi_conformite_resultat_check CHECK (((resultat)::text = ANY ((ARRAY['Conforme'::character varying, 'Non conforme'::character varying, 'En attente'::character varying, 'Non applicable'::character varying])::text[])))
);


ALTER TABLE public.suivi_conformite OWNER TO energixdb_k3c4_user;

--
-- TOC entry 257 (class 1259 OID 34350)
-- Name: taux_changes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.taux_changes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    devise_source character varying(3) NOT NULL,
    devise_cible character varying(3) NOT NULL,
    taux numeric(15,6) NOT NULL,
    date_application date NOT NULL,
    heure_application time without time zone DEFAULT CURRENT_TIME,
    est_actuel boolean DEFAULT false,
    utilisateur_id uuid,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.taux_changes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 324 (class 1259 OID 36165)
-- Name: tentatives_acces_non_autorise; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.tentatives_acces_non_autorise (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    utilisateur_id uuid,
    endpoint_accesse character varying(20) NOT NULL,
    endpoint_autorise character varying(20),
    ip_connexion character varying(45),
    statut character varying(20) DEFAULT 'Traite'::character varying,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT tentatives_acces_non_autorise_statut_check CHECK (((statut)::text = ANY ((ARRAY['EnAttente'::character varying, 'Traite'::character varying, 'Enquete'::character varying])::text[])))
);


ALTER TABLE public.tentatives_acces_non_autorise OWNER TO energixdb_k3c4_user;

--
-- TOC entry 246 (class 1259 OID 34128)
-- Name: tentatives_connexion; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.tentatives_connexion (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    login character varying(50) NOT NULL,
    ip_connexion character varying(45),
    resultat_connexion character varying(10),
    utilisateur_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    type_endpoint character varying(20) DEFAULT 'utilisateur'::character varying,
    type_utilisateur character varying(30) DEFAULT 'utilisateur_compagnie'::character varying,
    CONSTRAINT tentatives_connexion_resultat_connexion_check CHECK (((resultat_connexion)::text = ANY ((ARRAY['Reussie'::character varying, 'Echouee'::character varying])::text[]))),
    CONSTRAINT tentatives_connexion_type_endpoint_check CHECK (((type_endpoint)::text = ANY ((ARRAY['administrateur'::character varying, 'utilisateur'::character varying])::text[]))),
    CONSTRAINT tentatives_connexion_type_utilisateur_check CHECK (((type_utilisateur)::text = ANY ((ARRAY['super_administrateur'::character varying, 'administrateur'::character varying, 'gerant_compagnie'::character varying, 'utilisateur_compagnie'::character varying])::text[])))
);


ALTER TABLE public.tentatives_connexion OWNER TO energixdb_k3c4_user;

--
-- TOC entry 274 (class 1259 OID 34842)
-- Name: tickets_caisse; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.tickets_caisse (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    numero_ticket character varying(50) NOT NULL,
    station_id uuid,
    caissier_id uuid,
    date_ticket date NOT NULL,
    heure_debut time without time zone NOT NULL,
    heure_fin time without time zone,
    montant_initial numeric(18,2) DEFAULT 0,
    montant_final_theorique numeric(18,2) DEFAULT 0,
    montant_final_reel numeric(18,2) DEFAULT 0,
    ecart numeric(18,2) DEFAULT 0,
    commentaire text,
    compagnie_id uuid,
    statut character varying(20) DEFAULT 'Ouvert'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT tickets_caisse_statut_check CHECK (((statut)::text = ANY ((ARRAY['Ouvert'::character varying, 'Ferme'::character varying, 'Reconcilie'::character varying])::text[])))
);


ALTER TABLE public.tickets_caisse OWNER TO energixdb_k3c4_user;

--
-- TOC entry 239 (class 1259 OID 33964)
-- Name: tranches_taxes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.tranches_taxes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_taxe_id uuid,
    borne_inferieure numeric(18,2) DEFAULT 0,
    borne_superieure numeric(18,2),
    taux numeric(5,2) NOT NULL,
    est_actif boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tranches_taxes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 315 (class 1259 OID 35935)
-- Name: transfert_stock; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.transfert_stock (
    id uuid NOT NULL,
    numero character varying(50) NOT NULL,
    date_transfert date NOT NULL,
    heure_transfert time without time zone NOT NULL,
    utilisateur_id uuid,
    station_origine_id uuid NOT NULL,
    station_destination_id uuid NOT NULL,
    observation text,
    statut character varying(20),
    compagnie_id uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.transfert_stock OWNER TO energixdb_k3c4_user;

--
-- TOC entry 323 (class 1259 OID 36076)
-- Name: transfert_stock_details; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.transfert_stock_details (
    id uuid NOT NULL,
    transfert_id uuid NOT NULL,
    article_id uuid NOT NULL,
    cuve_origine_id uuid,
    cuve_destination_id uuid,
    quantite numeric(18,3) NOT NULL,
    prix_unitaire numeric(18,4),
    valeur_totale numeric(18,2),
    statut character varying(20),
    created_at timestamp with time zone
);


ALTER TABLE public.transfert_stock_details OWNER TO energixdb_k3c4_user;

--
-- TOC entry 241 (class 1259 OID 34003)
-- Name: tresoreries; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.tresoreries (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20) NOT NULL,
    libelle character varying(100) NOT NULL,
    compagnie_id uuid,
    station_ids jsonb DEFAULT '[]'::jsonb,
    solde numeric(18,2) DEFAULT 0,
    devise_code character varying(3) DEFAULT 'MGA'::character varying,
    taux_change numeric(15,6) DEFAULT 1.000000,
    fournisseur_id uuid,
    type_tresorerie uuid,
    methode_paiement jsonb DEFAULT '[]'::jsonb,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    solde_theorique numeric(18,2) DEFAULT 0,
    solde_reel numeric(18,2) DEFAULT 0,
    date_dernier_rapprochement timestamp with time zone,
    utilisateur_dernier_rapprochement uuid,
    type_tresorerie_libelle character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT tresoreries_solde_check CHECK ((solde >= ('-1000000000'::integer)::numeric)),
    CONSTRAINT tresoreries_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.tresoreries OWNER TO energixdb_k3c4_user;

--
-- TOC entry 222 (class 1259 OID 33580)
-- Name: type_tiers; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.type_tiers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type character varying(50) NOT NULL,
    libelle character varying(100) NOT NULL,
    num_compte character varying(10),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.type_tiers OWNER TO energixdb_k3c4_user;

--
-- TOC entry 233 (class 1259 OID 33811)
-- Name: types_taxes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.types_taxes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code_taxe character varying(20) NOT NULL,
    libelle_taxe character varying(100) NOT NULL,
    description text,
    pays_id uuid,
    taux_par_defaut numeric(5,2) DEFAULT 0,
    type_calcul character varying(20) NOT NULL,
    compte_comptable character varying(20),
    est_actif boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT types_taxes_type_calcul_check CHECK (((type_calcul)::text = ANY ((ARRAY['fixe'::character varying, 'pourcentage'::character varying, 'tranche'::character varying])::text[])))
);


ALTER TABLE public.types_taxes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 220 (class 1259 OID 33544)
-- Name: unites_mesure; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.unites_mesure (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code_unite character varying(10) NOT NULL,
    libelle_unite character varying(50) NOT NULL,
    pays_id uuid,
    est_standard boolean DEFAULT false,
    est_utilisee boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.unites_mesure OWNER TO energixdb_k3c4_user;

--
-- TOC entry 240 (class 1259 OID 33978)
-- Name: utilisateurs; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.utilisateurs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    login character varying(50) NOT NULL,
    mot_de_passe text NOT NULL,
    nom character varying(150) NOT NULL,
    profil_id uuid,
    email character varying(150),
    telephone character varying(30),
    stations_user jsonb DEFAULT '[]'::jsonb,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    last_login timestamp with time zone,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    type_utilisateur character varying(30) DEFAULT 'utilisateur_compagnie'::character varying,
    CONSTRAINT utilisateurs_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[]))),
    CONSTRAINT utilisateurs_type_utilisateur_check CHECK (((type_utilisateur)::text = ANY ((ARRAY['super_administrateur'::character varying, 'administrateur'::character varying, 'gerant_compagnie'::character varying, 'utilisateur_compagnie'::character varying])::text[])))
);


ALTER TABLE public.utilisateurs OWNER TO energixdb_k3c4_user;

--
-- TOC entry 286 (class 1259 OID 35196)
-- Name: utilisation_depot_garantie; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.utilisation_depot_garantie (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    depot_garantie_id uuid,
    type_utilisation character varying(20) NOT NULL,
    montant_utilise numeric(18,2) NOT NULL,
    reference_operation character varying(100),
    utilisateur_utilise_id uuid,
    date_utilisation date NOT NULL,
    commentaire text,
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT utilisation_depot_garantie_type_utilisation_check CHECK (((type_utilisation)::text = ANY ((ARRAY['Dette'::character varying, 'Vente'::character varying, 'Ecart'::character varying, 'Autre'::character varying])::text[])))
);


ALTER TABLE public.utilisation_depot_garantie OWNER TO energixdb_k3c4_user;

--
-- TOC entry 307 (class 1259 OID 35699)
-- Name: validations_hierarchiques; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.validations_hierarchiques (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    operation_type character varying(50) NOT NULL,
    seuil_montant numeric(18,2),
    niveau_validation integer DEFAULT 1,
    profil_autorise_id uuid,
    statut character varying(20) DEFAULT 'Actif'::character varying,
    CONSTRAINT validations_hierarchiques_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying])::text[])))
);


ALTER TABLE public.validations_hierarchiques OWNER TO energixdb_k3c4_user;

--
-- TOC entry 267 (class 1259 OID 34633)
-- Name: ventes; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.ventes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    date_vente date NOT NULL,
    total_ht numeric(18,2) NOT NULL,
    total_ttc numeric(18,2) NOT NULL,
    total_tva numeric(18,2) NOT NULL,
    reference_facture character varying(100),
    observation text,
    type_vente character varying(20) DEFAULT 'Boutique'::character varying NOT NULL,
    type_transaction character varying(20) DEFAULT 'General'::character varying,
    compagnie_id uuid,
    pays_id uuid,
    devise_code character varying(3) DEFAULT 'MGA'::character varying,
    taux_change numeric(15,6) DEFAULT 1.000000,
    journal_entry_id uuid,
    statut character varying(20) DEFAULT 'Valide'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ventes_statut_check CHECK (((statut)::text = ANY ((ARRAY['Valide'::character varying, 'Retour'::character varying, 'Annule'::character varying])::text[]))),
    CONSTRAINT ventes_total_ht_check CHECK ((total_ht >= (0)::numeric)),
    CONSTRAINT ventes_total_ttc_check CHECK ((total_ttc >= (0)::numeric)),
    CONSTRAINT ventes_total_tva_check CHECK ((total_tva >= (0)::numeric)),
    CONSTRAINT ventes_type_transaction_check CHECK (((type_transaction)::text = ANY ((ARRAY['General'::character varying, 'Boutique'::character varying, 'Station'::character varying, 'Carburant'::character varying])::text[]))),
    CONSTRAINT ventes_type_vente_check CHECK (((type_vente)::text = ANY ((ARRAY['Carburant'::character varying, 'Boutique'::character varying, 'Service'::character varying])::text[])))
);


ALTER TABLE public.ventes OWNER TO energixdb_k3c4_user;

--
-- TOC entry 268 (class 1259 OID 34669)
-- Name: ventes_details; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.ventes_details (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vente_id uuid,
    article_id uuid,
    pistolet_id uuid,
    index_debut numeric(18,3),
    index_fin numeric(18,3),
    quantite numeric(18,3) NOT NULL,
    prix_unitaire_ht numeric(18,4) NOT NULL,
    prix_unitaire_ttc numeric(18,4) NOT NULL,
    taux_tva numeric(5,2) DEFAULT 0,
    montant_ht numeric(18,2) GENERATED ALWAYS AS ((quantite * prix_unitaire_ht)) STORED,
    montant_tva numeric(18,2) GENERATED ALWAYS AS (((quantite * prix_unitaire_ht) * (taux_tva / (100)::numeric))) STORED,
    montant_ttc numeric(18,2) GENERATED ALWAYS AS (((quantite * prix_unitaire_ht) * ((1)::numeric + (taux_tva / (100)::numeric)))) STORED,
    taxes_detaillees jsonb DEFAULT '{}'::jsonb,
    station_id uuid,
    utilisateur_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ventes_details_prix_unitaire_ht_check CHECK ((prix_unitaire_ht >= (0)::numeric)),
    CONSTRAINT ventes_details_prix_unitaire_ttc_check CHECK ((prix_unitaire_ttc >= (0)::numeric)),
    CONSTRAINT ventes_details_quantite_check CHECK ((quantite >= (0)::numeric))
);


ALTER TABLE public.ventes_details OWNER TO energixdb_k3c4_user;

--
-- TOC entry 269 (class 1259 OID 34711)
-- Name: ventes_tresorerie; Type: TABLE; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TABLE public.ventes_tresorerie (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vente_id uuid,
    tresorerie_id uuid,
    montant numeric(18,2) NOT NULL,
    note_paiement jsonb DEFAULT '{}'::jsonb,
    statut character varying(20) DEFAULT 'Actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ventes_tresorerie_montant_check CHECK ((montant >= (0)::numeric)),
    CONSTRAINT ventes_tresorerie_statut_check CHECK (((statut)::text = ANY ((ARRAY['Actif'::character varying, 'Inactif'::character varying, 'Supprime'::character varying])::text[])))
);


ALTER TABLE public.ventes_tresorerie OWNER TO energixdb_k3c4_user;

--
-- TOC entry 4871 (class 0 OID 34366)
-- Dependencies: 258
-- Data for Name: achats; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.achats (id, fournisseur_id, date_achat, total, reference_facture, observation, type_achat, compagnie_id, pays_id, devise_code, taux_change, journal_entry_id, statut, date_livraison, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4873 (class 0 OID 34417)
-- Dependencies: 260
-- Data for Name: achats_details; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.achats_details (id, achat_id, article_id, station_id, cuve_id, quantite, prix_unitaire, statut) FROM stdin;
\.


--
-- TOC entry 4872 (class 0 OID 34398)
-- Dependencies: 259
-- Data for Name: achats_stations; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.achats_stations (id, achat_id, station_id, created_at) FROM stdin;
\.


--
-- TOC entry 4875 (class 0 OID 34472)
-- Dependencies: 262
-- Data for Name: achats_tresorerie; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.achats_tresorerie (id, achat_id, tresorerie_id, montant, note_paiement, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4897 (class 0 OID 35134)
-- Dependencies: 284
-- Data for Name: ajustements_stock; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.ajustements_stock (id, article_id, cuve_id, station_id, type_ajustement, quantite, motif, utilisateur_id, date_ajustement, commentaire, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4938 (class 0 OID 36823)
-- Dependencies: 325
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.alembic_version (version_num) FROM stdin;
001_add_temperature_to_cuves
\.


--
-- TOC entry 4910 (class 0 OID 35433)
-- Dependencies: 297
-- Data for Name: analyse_commerciale; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.analyse_commerciale (id, station_id, type_analyse, periode_debut, periode_fin, resultat, commentaire, utilisateur_analyse_id, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4888 (class 0 OID 34875)
-- Dependencies: 275
-- Data for Name: arrets_compte_caissier; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.arrets_compte_caissier (id, ticket_caisse_id, utilisateur_id, date_arret, heure_arret, total_vente_especes, total_vente_cb, total_vente_chq, total_vente_autre, total_vente_credit, commentaire, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4849 (class 0 OID 33871)
-- Dependencies: 236
-- Data for Name: articles; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.articles (id, code, libelle, codebarre, famille_id, unite, unite_principale, unite_stock, compagnie_id, type_article, prix_achat, prix_vente, tva, taxes_applicables, stock_minimal, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4909 (class 0 OID 35411)
-- Dependencies: 296
-- Data for Name: assurances; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.assurances (id, station_id, type_assurance, compagnie_assurance, numero_police, date_debut, date_fin, montant_couverture, prime_annuelle, statut, fichier_joint, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4858 (class 0 OID 34115)
-- Dependencies: 245
-- Data for Name: auth_tokens; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.auth_tokens (id, token_hash, user_id, expires_at, is_active, created_at, type_endpoint) FROM stdin;
\.


--
-- TOC entry 4855 (class 0 OID 34045)
-- Dependencies: 242
-- Data for Name: barremage_cuves; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.barremage_cuves (id, cuve_id, station_id, hauteur, volume, statut, created_at, updated_at, compagnie_id) FROM stdin;
3a533d4e-35fc-409a-943f-38d79d3d4eea	1f20591c-b0f6-49f6-a10e-0157be2954dc	ed498670-c5a3-464f-abd0-400e4d2fafa4	5.000	200.000	Actif	2025-11-28 09:28:22.249+00	2025-11-28 09:28:22.249064+00	e3c24054-8402-4e93-a330-27c4b3a83bf4
52d064fd-023e-4b68-abcf-0fc74750b18b	1f20591c-b0f6-49f6-a10e-0157be2954dc	ed498670-c5a3-464f-abd0-400e4d2fafa4	10.000	400.000	Actif	2025-11-28 09:28:22.249112+00	2025-11-28 09:28:22.249122+00	e3c24054-8402-4e93-a330-27c4b3a83bf4
3f7bf9cc-2eb7-4b0d-94c6-a3dd32dc65c3	1f20591c-b0f6-49f6-a10e-0157be2954dc	ed498670-c5a3-464f-abd0-400e4d2fafa4	15.000	600.000	Actif	2025-11-28 09:28:22.249149+00	2025-11-28 09:28:22.249197+00	e3c24054-8402-4e93-a330-27c4b3a83bf4
f7d881f0-d44f-475b-9893-1134e75c81d5	1f20591c-b0f6-49f6-a10e-0157be2954dc	ed498670-c5a3-464f-abd0-400e4d2fafa4	20.000	800.000	Actif	2025-11-28 09:28:22.249228+00	2025-11-28 09:28:22.249236+00	e3c24054-8402-4e93-a330-27c4b3a83bf4
778925ae-4cf3-42ab-b07f-0eba36c978b4	1f20591c-b0f6-49f6-a10e-0157be2954dc	ed498670-c5a3-464f-abd0-400e4d2fafa4	40.000	1600.000	Actif	2025-11-28 09:28:22.249264+00	2025-11-28 09:28:22.249271+00	e3c24054-8402-4e93-a330-27c4b3a83bf4
301f7bb5-b639-45b6-8713-29dc5e09f7d2	1f20591c-b0f6-49f6-a10e-0157be2954dc	ed498670-c5a3-464f-abd0-400e4d2fafa4	50.000	2000.000	Actif	2025-11-28 09:28:22.249292+00	2025-11-28 09:28:22.249299+00	e3c24054-8402-4e93-a330-27c4b3a83bf4
\.


--
-- TOC entry 4867 (class 0 OID 34291)
-- Dependencies: 254
-- Data for Name: bilan_initial; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.bilan_initial (id, compagnie_id, date_bilan_initial, est_valide, est_verifie, commentaire, created_at, updated_at, valeur_totale_stocks, nombre_elements, statut, utilisateur_validation_id, date_validation, date_bilan) FROM stdin;
\.


--
-- TOC entry 4900 (class 0 OID 35221)
-- Dependencies: 287
-- Data for Name: bilan_initial_lignes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.bilan_initial_lignes (id, bilan_initial_id, created_at, type_element, element_id, description_element, quantite, unite_mesure, prix_unitaire, valeur_totale, taux_tva, montant_tva, montant_ht) FROM stdin;
\.


--
-- TOC entry 4886 (class 0 OID 34815)
-- Dependencies: 273
-- Data for Name: bons_commande; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.bons_commande (id, numero_bon, fournisseur_id, date_bon, total, observation, type_bon, compagnie_id, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4842 (class 0 OID 33714)
-- Dependencies: 229
-- Data for Name: carburants; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.carburants (id, code, libelle, type, compagnie_id, prix_achat, prix_vente, statut, created_at, updated_at) FROM stdin;
e3f55502-be82-45e8-ae32-c18b872aaede	Gasoil	Gasoil	Gasoil	e3c24054-8402-4e93-a330-27c4b3a83bf4	4800.0000	4900.0000	Actif	2025-11-28 05:56:30.951112+00	2025-11-28 05:56:30.951142+00
311ae924-6fee-47b2-9bc1-3a6d75da0ecb	SP95	Essence	Essence	e3c24054-8402-4e93-a330-27c4b3a83bf4	5800.0000	5900.0000	Actif	2025-11-28 06:03:29.275474+00	2025-11-28 06:03:29.275481+00
\.


--
-- TOC entry 4916 (class 0 OID 35578)
-- Dependencies: 303
-- Data for Name: cartes_carburant; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.cartes_carburant (id, client_id, numero_carte, date_activation, date_expiration, solde_carte, plafond_mensuel, statut, utilisateur_creation_id, utilisateur_blocage_id, motif_blocage, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4844 (class 0 OID 33761)
-- Dependencies: 231
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.clients (id, code, nom, adresse, telephone, nif, email, compagnie_id, station_ids, type_tiers_id, statut, nb_jrs_creance, solde_comptable, solde_confirme, date_dernier_rapprochement, devise_facturation, created_at, updated_at) FROM stdin;
b52abfaf-cc68-4e6e-a13b-e89fbf7f3b0b	CL001	TIKO					e3c24054-8402-4e93-a330-27c4b3a83bf4	[]	a5604e3a-a761-41ce-ad61-1c30e809e8ee	Actif	3	0.00	0.00	\N	MGA	2025-11-28 13:15:05.785824+00	2025-11-28 13:15:05.78584+00
\.


--
-- TOC entry 4834 (class 0 OID 33560)
-- Dependencies: 221
-- Data for Name: compagnies; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.compagnies (id, code, nom, adresse, telephone, email, nif, statut, pays_id, devise_principale, created_at, updated_at) FROM stdin;
e3c24054-8402-4e93-a330-27c4b3a83bf4	CP001	LIVEX	Antsirabe	034 15 988 77	livex@test.com	5454545	Actif	db298448-f19a-4b75-9815-b50b0b792317	MGA	2025-11-26 14:15:04.68817+00	2025-11-27 12:24:53.950252+00
\.


--
-- TOC entry 4839 (class 0 OID 33645)
-- Dependencies: 226
-- Data for Name: configurations_pays; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.configurations_pays (id, pays_id, cle_configuration, valeur_configuration, description, est_systeme, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4917 (class 0 OID 35613)
-- Dependencies: 304
-- Data for Name: contrats_clients; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.contrats_clients (id, client_id, type_contrat, libelle, description, date_debut, date_fin, volume_garanti, prix_contractuel, frequence_livraison, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4913 (class 0 OID 35510)
-- Dependencies: 300
-- Data for Name: contrats_maintenance; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.contrats_maintenance (id, station_id, fournisseur_id, type_contrat, libelle, description, date_debut, date_fin, cout_mensuel, frequence, prochaine_intervention, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4914 (class 0 OID 35537)
-- Dependencies: 301
-- Data for Name: controle_interne; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.controle_interne (id, type_controle, element_controle, date_controle, utilisateur_controle_id, resultat, montant_ecart, commentaire, statut, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4857 (class 0 OID 34097)
-- Dependencies: 244
-- Data for Name: conversions_unite; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.conversions_unite (id, unite_origine_id, unite_destination_id, facteur_conversion, est_actif, created_at) FROM stdin;
\.


--
-- TOC entry 4919 (class 0 OID 35665)
-- Dependencies: 306
-- Data for Name: couts_logistique; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.couts_logistique (id, type_cout, description, montant, date_cout, carburant_id, station_id, fournisseur_id, utilisateur_saisie_id, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4940 (class 0 OID 36873)
-- Dependencies: 327
-- Data for Name: couts_logistique_stocks_initial; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.couts_logistique_stocks_initial (id, type_cout, description, montant, date_cout, article_id, cuve_id, station_id, fournisseur_id, utilisateur_saisie_id, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4923 (class 0 OID 35752)
-- Dependencies: 310
-- Data for Name: cuve_stocks; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.cuve_stocks (id, cuve_id, station_id, stock_theorique, stock_reel, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4924 (class 0 OID 35780)
-- Dependencies: 311
-- Data for Name: cuve_stocks_mouvements; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.cuve_stocks_mouvements (id, cuve_stock_id, cuve_id, station_id, type_mouvement, quantite, prix_unitaire, date_mouvement, reference_operation, utilisateur_id, commentaire, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4851 (class 0 OID 33936)
-- Dependencies: 238
-- Data for Name: cuves; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.cuves (id, station_id, code, capacite, carburant_id, compagnie_id, statut, created_at, updated_at, temperature) FROM stdin;
1f20591c-b0f6-49f6-a10e-0157be2954dc	ed498670-c5a3-464f-abd0-400e4d2fafa4	C020	20000.000	e3f55502-be82-45e8-ae32-c18b872aaede	e3c24054-8402-4e93-a330-27c4b3a83bf4	Actif	2025-11-28 06:45:44.837848+00	2025-11-28 06:45:44.837865+00	0.00
\.


--
-- TOC entry 4906 (class 0 OID 35336)
-- Dependencies: 293
-- Data for Name: declarations_fiscales; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.declarations_fiscales (id, type_declaration, periode_debut, periode_fin, montant_total, montant_declare, date_depot, statut, fichier_joint, utilisateur_depose_id, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4893 (class 0 OID 35003)
-- Dependencies: 280
-- Data for Name: depenses; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.depenses (id, categorie, libelle, montant, date_depense, mode_paiement, tresorerie_id, fournisseur_id, utilisateur_id, projet, statut, reference_piece, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4898 (class 0 OID 35169)
-- Dependencies: 285
-- Data for Name: depot_garantie; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.depot_garantie (id, client_id, montant, date_enregistrement, mode_paiement, reference_paiement, utilisateur_enregistre_id, statut, commentaire, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4874 (class 0 OID 34443)
-- Dependencies: 261
-- Data for Name: dettes_fournisseurs; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.dettes_fournisseurs (id, fournisseur_id, achat_id, montant_achat, montant_paye, solde, date_creation, reference_facture, compagnie_id, nb_jrs_creance, date_prevu_paiement, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4868 (class 0 OID 34308)
-- Dependencies: 255
-- Data for Name: ecarts_soldes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.ecarts_soldes (id, tiers_type, tiers_id, solde_fiche, solde_reel, statut, utilisateur_detecte_id, utilisateur_traite_id, date_detection, date_traitement, motif, created_at) FROM stdin;
\.


--
-- TOC entry 4845 (class 0 OID 33790)
-- Dependencies: 232
-- Data for Name: employes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.employes (id, code, nom, prenom, adresse, telephone, poste, salaire_base, station_ids, compagnie_id, statut, created_at, updated_at, avances, creances) FROM stdin;
ace9cd0a-4da0-4e70-9843-8e0a747e14a7	P001	RAKOTONIAINA	Jaque	Antsirabe	034 12 788 88	Pompiste	250000.00	["ed498670-c5a3-464f-abd0-400e4d2fafa4"]	e3c24054-8402-4e93-a330-27c4b3a83bf4	Actif	2025-11-28 13:31:56.736964+00	2025-11-28 13:31:56.73698+00	0.00	0.00
\.


--
-- TOC entry 4932 (class 0 OID 36010)
-- Dependencies: 319
-- Data for Name: etat_caisse; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.etat_caisse (id, date_etat, tresorerie_id, solde_initial, encaissements, decaissements, solde_final, ecart, observation, statut, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4933 (class 0 OID 36027)
-- Dependencies: 320
-- Data for Name: etat_comptable; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.etat_comptable (id, date_etat, compte_id, solde_initial, debit_periode, credit_periode, solde_final, observation, statut, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4931 (class 0 OID 35993)
-- Dependencies: 318
-- Data for Name: etat_stock; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.etat_stock (id, date_etat, article_id, station_id, stock_initial, entrees, sorties, stock_final, valeur_stock, observation, statut, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4860 (class 0 OID 34141)
-- Dependencies: 247
-- Data for Name: evenements_securite; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.evenements_securite (id, type_evenement, description, utilisateur_id, ip_utilisateur, poste_utilisateur, session_id, donnees_supplementaires, statut, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4840 (class 0 OID 33663)
-- Dependencies: 227
-- Data for Name: familles_articles; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.familles_articles (id, code, libelle, compagnie_id, statut, parent_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4894 (class 0 OID 35036)
-- Dependencies: 281
-- Data for Name: fiches_paie; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.fiches_paie (id, employe_id, mois_paie, annee_paie, date_paie, salaire_base, avances, autres_deductions, cotisations_sociales, autres_retenues, commentaire, utilisateur_calcul_id, utilisateur_paye_id, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4843 (class 0 OID 33733)
-- Dependencies: 230
-- Data for Name: fournisseurs; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.fournisseurs (id, code, nom, adresse, telephone, nif, email, compagnie_id, station_ids, type_tiers_id, statut, nb_jrs_creance, solde_comptable, solde_confirme, date_dernier_rapprochement, created_at, updated_at) FROM stdin;
808ab40a-af16-47f7-acf9-fb72e25b17df	FRN0001	VIVO	Antananarivo				e3c24054-8402-4e93-a330-27c4b3a83bf4	[]	e78cbe48-77f5-4444-a34d-93b91db68064	Actif	2	0.00	0.00	\N	2025-11-28 13:17:53.056406+00	2025-11-28 13:17:53.056421+00
\.


--
-- TOC entry 4921 (class 0 OID 35713)
-- Dependencies: 308
-- Data for Name: historique_actions_utilisateurs; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.historique_actions_utilisateurs (id, utilisateur_id, action, module, sous_module, objet_id, donnees_avant, donnees_apres, ip_utilisateur, poste_utilisateur, session_id, statut_action, commentaire, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4865 (class 0 OID 34243)
-- Dependencies: 252
-- Data for Name: historique_index_pistolets; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.historique_index_pistolets (id, pistolet_id, index_releve, date_releve, utilisateur_id, observation, statut, created_at) FROM stdin;
\.


--
-- TOC entry 4889 (class 0 OID 34905)
-- Dependencies: 276
-- Data for Name: historique_paiements_clients; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.historique_paiements_clients (id, client_id, montant_paye, date_paiement, mode_paiement, reference_paiement, utilisateur_id, commentaire, created_at) FROM stdin;
\.


--
-- TOC entry 4863 (class 0 OID 34205)
-- Dependencies: 250
-- Data for Name: historique_prix_articles; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.historique_prix_articles (id, article_id, prix_achat, prix_vente, date_application, utilisateur_id, created_at) FROM stdin;
\.


--
-- TOC entry 4864 (class 0 OID 34224)
-- Dependencies: 251
-- Data for Name: historique_prix_carburants; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.historique_prix_carburants (id, carburant_id, prix_achat, prix_vente, date_application, utilisateur_id, created_at) FROM stdin;
\.


--
-- TOC entry 4895 (class 0 OID 35073)
-- Dependencies: 282
-- Data for Name: immobilisations; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.immobilisations (id, code, libelle, categorie, date_achat, valeur_acquisition, valeur_nette_comptable, amortissement_annuel, duree_amortissement, date_fin_amortissement, fournisseur_id, tresorerie_id, utilisateur_achat_id, observation, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4908 (class 0 OID 35378)
-- Dependencies: 295
-- Data for Name: incidents_securite; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.incidents_securite (id, station_id, type_incident, date_incident, description, gravite, statut, utilisateur_declare_id, utilisateur_traite_id, action_corrective, date_resolution, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4927 (class 0 OID 35911)
-- Dependencies: 314
-- Data for Name: inventaire; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.inventaire (id, numero, date_inventaire, heure_debut, heure_fin, utilisateur_id, station_id, type_inventaire, observation, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4935 (class 0 OID 36059)
-- Dependencies: 322
-- Data for Name: inventaire_details; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.inventaire_details (id, inventaire_id, article_id, cuve_id, stock_theorique, stock_reel, ecart, observation, statut, created_at) FROM stdin;
\.


--
-- TOC entry 4890 (class 0 OID 34924)
-- Dependencies: 277
-- Data for Name: inventaires; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.inventaires (id, station_id, type_inventaire, date_inventaire, utilisateur_id, statut, commentaire, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4884 (class 0 OID 34753)
-- Dependencies: 271
-- Data for Name: journal_entries; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.journal_entries (id, date_ecriture, libelle, type_operation, reference_operation, compagnie_id, pays_id, created_at, statut, created_by, est_valide, valide_par, date_validation, type_document_origine, document_origine_id, est_ouverture, bilan_initial_id) FROM stdin;
\.


--
-- TOC entry 4885 (class 0 OID 34793)
-- Dependencies: 272
-- Data for Name: journal_lines; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.journal_lines (id, entry_id, compte_num, compte_id, debit, credit) FROM stdin;
\.


--
-- TOC entry 4930 (class 0 OID 35979)
-- Dependencies: 317
-- Data for Name: journaux; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.journaux (id, code, libelle, type_journal, observation, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4905 (class 0 OID 35304)
-- Dependencies: 292
-- Data for Name: kpi_operations; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.kpi_operations (id, station_id, periode, type_carburant, litres_vendus, marge_brute, nombre_clients_servis, volume_moyen_transaction, rendement_pompiste, productivite_horaires, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4892 (class 0 OID 34978)
-- Dependencies: 279
-- Data for Name: mesures_inventaire_articles; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mesures_inventaire_articles (id, inventaire_id, article_id, stock_reel, stock_theorique, utilisateur_id, commentaire, created_at) FROM stdin;
\.


--
-- TOC entry 4891 (class 0 OID 34953)
-- Dependencies: 278
-- Data for Name: mesures_inventaire_cuves; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mesures_inventaire_cuves (id, inventaire_id, cuve_id, hauteur_reelle, volume_reel, stock_reel, stock_theorique, utilisateur_id, commentaire, created_at) FROM stdin;
\.


--
-- TOC entry 4876 (class 0 OID 34496)
-- Dependencies: 263
-- Data for Name: mesures_livraison; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mesures_livraison (id, achat_id, cuve_id, mesure_avant_livraison, mesure_apres_livraison, utilisateur_id, commentaire, created_at) FROM stdin;
\.


--
-- TOC entry 4837 (class 0 OID 33616)
-- Dependencies: 224
-- Data for Name: methode_paiment; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.methode_paiment (id, type_tresorerie, mode_paiement, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4904 (class 0 OID 35287)
-- Dependencies: 291
-- Data for Name: modeles_rapports; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.modeles_rapports (id, code_modele, libelle_modele, pays_id, type_rapport, format_sortie, contenu_modele, est_actif, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4861 (class 0 OID 34162)
-- Dependencies: 248
-- Data for Name: modifications_sensibles; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.modifications_sensibles (id, utilisateur_id, type_operation, objet_modifie, objet_id, ancienne_valeur, nouvelle_valeur, seuil_alerte, commentaire, ip_utilisateur, poste_utilisateur, statut, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4832 (class 0 OID 33534)
-- Dependencies: 219
-- Data for Name: modules; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.modules (id, libelle, statut) FROM stdin;
f670a4a2-bcea-42af-b891-4ceb3f2f668b	ventes	Actif
b162711b-5831-429c-8225-a41e744f219d	achats	Actif
0ef8e464-5298-4c6e-b3fe-0014feaf199e	stocks	Actif
89873825-8374-4661-a12e-c730fc20bcc8	utilisateurs	Actif
85c1530b-2a12-44a7-8a5c-f3a12935ba3d	rapports	Actif
552d0781-59ad-4fa4-aac6-bcdabc5ce93b	comptabilite	Actif
06570866-dc4f-4bc3-a9df-01533494b94c	tresorerie	Actif
c4a244ea-2e8d-4ba1-bbb9-90b2380a5e5f	stations	Actif
\.


--
-- TOC entry 4896 (class 0 OID 35109)
-- Dependencies: 283
-- Data for Name: mouvements_immobilisations; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mouvements_immobilisations (id, immobilisation_id, type_mouvement, date_mouvement, valeur_mouvement, commentaire, utilisateur_id, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4926 (class 0 OID 35872)
-- Dependencies: 313
-- Data for Name: mouvements_stock; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mouvements_stock (id, numero, type_mouvement, article_id, station_id, fournisseur_id, client_id, utilisateur_id, date_mouvement, quantite, prix_unitaire, valeur_totale, observation, reference_externe, compagnie_id, pays_id, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4934 (class 0 OID 36044)
-- Dependencies: 321
-- Data for Name: mouvements_stock_details; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mouvements_stock_details (id, mouvement_id, article_id, cuve_id, quantite, prix_unitaire, valeur_totale, statut, created_at) FROM stdin;
\.


--
-- TOC entry 4879 (class 0 OID 34600)
-- Dependencies: 266
-- Data for Name: mouvements_tresorerie; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mouvements_tresorerie (id, tresorerie_id, type_mouvement, sous_type_mouvement, montant, reference_operation, utilisateur_id, commentaire, date_mouvement, date_enregistrement, statut, mouvement_origine_id, compagnie_id) FROM stdin;
\.


--
-- TOC entry 4929 (class 0 OID 35964)
-- Dependencies: 316
-- Data for Name: mouvements_tresorerie_details; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.mouvements_tresorerie_details (id, mouvement_id, compte_comptable_id, type_operation, montant, statut, created_at) FROM stdin;
\.


--
-- TOC entry 4831 (class 0 OID 33520)
-- Dependencies: 218
-- Data for Name: pays; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.pays (id, code_pays, nom_pays, devise_principale, taux_tva_par_defaut, systeme_comptable, date_application_tva, statut, created_at, updated_at) FROM stdin;
db298448-f19a-4b75-9815-b50b0b792317	MG 	Madagascar	MGA	20.00	OHADA	\N	Actif	2025-11-26 14:08:08.832843+00	2025-11-26 14:08:08.832855+00
\.


--
-- TOC entry 4901 (class 0 OID 35239)
-- Dependencies: 288
-- Data for Name: periodes_comptables; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.periodes_comptables (id, annee, mois, date_debut, date_fin, est_cloture, est_exercice, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4848 (class 0 OID 33855)
-- Dependencies: 235
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.permissions (id, libelle, description, module_id, statut, created_at) FROM stdin;
ebd7207d-c8d9-4af5-9beb-cf2dd0e867c1	lire_ventes	Lire les détails des ventes	f670a4a2-bcea-42af-b891-4ceb3f2f668b	Actif	2025-11-25 08:39:26.088805+00
55fc5914-1acb-4329-9526-ba78d596880a	creer_vente	Créer une nouvelle vente	f670a4a2-bcea-42af-b891-4ceb3f2f668b	Actif	2025-11-25 08:39:26.088805+00
89bf9c51-4f16-4e31-bc67-167a77c0cb1e	modifier_stock	Modifier manuellement les stocks	0ef8e464-5298-4c6e-b3fe-0014feaf199e	Actif	2025-11-25 08:39:26.088805+00
ec33fd6d-8a9d-4c52-a681-0c368bfdfbf0	modifier_vente	Modifier une vente existante	f670a4a2-bcea-42af-b891-4ceb3f2f668b	Actif	2025-11-26 14:42:23.932589+00
9b015436-c6dc-493a-a0b3-67003d3d9f58	supprimer_vente	Supprimer une vente	f670a4a2-bcea-42af-b891-4ceb3f2f668b	Actif	2025-11-26 14:42:41.215452+00
bbac9a44-0c43-46ca-98b1-5f1afa9dce35	annuler_vente	Annuler une vente	f670a4a2-bcea-42af-b891-4ceb3f2f668b	Actif	2025-11-26 14:42:58.749516+00
4e528619-5191-4ea5-9631-b8f7165fea69	lire_achats	Lire les détails des achats	b162711b-5831-429c-8225-a41e744f219d	Actif	2025-11-26 14:43:17.224723+00
a7e62f40-c56f-4f5b-acbd-a0a9d0b2d62d	creer_achat	Créer un nouvel achat	b162711b-5831-429c-8225-a41e744f219d	Actif	2025-11-26 14:43:35.099335+00
934d40f9-faec-4cca-a9cf-be4634e592c0	modifier_achat	Modifier un achat existant	b162711b-5831-429c-8225-a41e744f219d	Actif	2025-11-26 14:43:52.279556+00
5bc9fa84-1980-4256-b0b5-38086bf91e48	supprimer_achat	Supprimer un achat	b162711b-5831-429c-8225-a41e744f219d	Actif	2025-11-26 14:44:07.239545+00
230520e3-f621-48c6-9ddf-6203e36fede1	valider_achat	Valider un achat	b162711b-5831-429c-8225-a41e744f219d	Actif	2025-11-26 14:44:24.043087+00
bab1a99f-20c3-4b03-88ab-1542408176eb	lire_stocks	Lire les informations de stock	0ef8e464-5298-4c6e-b3fe-0014feaf199e	Actif	2025-11-26 14:44:40.03345+00
7735c249-f791-4bd9-af20-f4de6b323d0b	creer_mouvement_stock	Créer un mouvement de stock	0ef8e464-5298-4c6e-b3fe-0014feaf199e	Actif	2025-11-26 14:44:55.042154+00
0518644d-0a5e-45f4-8684-6f94ca742955	supprimer_mouvement_stock	Supprimer un mouvement de stock	0ef8e464-5298-4c6e-b3fe-0014feaf199e	Actif	2025-11-26 14:45:11.505514+00
2145717a-e305-421f-9843-527e902f99ff	inventaire_stock	Effectuer un inventaire	0ef8e464-5298-4c6e-b3fe-0014feaf199e	Actif	2025-11-26 14:45:26.178482+00
5014541a-99d2-4823-a1f8-662b9681b481	lire_utilisateurs	Lire les détails des utilisateurs	89873825-8374-4661-a12e-c730fc20bcc8	Actif	2025-11-26 14:45:42.105163+00
0e9bc45e-bb1c-4cdc-a4f3-40b5662c4dc4	creer_utilisateur	Créer un nouvel utilisateur	89873825-8374-4661-a12e-c730fc20bcc8	Actif	2025-11-26 14:46:09.276243+00
9fc488f1-f8b4-4823-b00c-df255fab529b	modifier_utilisateur	Modifier un utilisateur existant	89873825-8374-4661-a12e-c730fc20bcc8	Actif	2025-11-26 14:46:30.235296+00
b042f187-dd0f-4e88-9f38-a796f4f94cd8	supprimer_utilisateur	Supprimer un utilisateur	89873825-8374-4661-a12e-c730fc20bcc8	Actif	2025-11-26 14:46:49.392301+00
8c857420-a2a4-452a-806e-a8f48fa361e1	desactiver_utilisateur	Désactiver un utilisateur	89873825-8374-4661-a12e-c730fc20bcc8	Actif	2025-11-26 14:47:11.537404+00
5c2781ad-5931-4a62-8612-471581ba1ff4	generer_rapport_ventes	Générer un rapport des ventes	85c1530b-2a12-44a7-8a5c-f3a12935ba3d	Actif	2025-11-26 14:47:24.346407+00
12e9014d-2c80-4d95-8ba3-b8636a443d3c	generer_rapport_stocks	Générer un rapport des stocks	85c1530b-2a12-44a7-8a5c-f3a12935ba3d	Actif	2025-11-26 14:47:38.022491+00
d2ce500a-1f04-41c8-8dd6-b18b5d1fd5ca	generer_rapport_financier	Générer un rapport financier	85c1530b-2a12-44a7-8a5c-f3a12935ba3d	Actif	2025-11-26 14:47:53.837321+00
960dbbd5-d311-46e0-84f8-145b5ed5520f	generer_rapport_utilisateurs	Générer un rapport des utilisateurs	85c1530b-2a12-44a7-8a5c-f3a12935ba3d	Actif	2025-11-26 14:48:09.278642+00
3284a1f2-7768-484f-9acd-157b26a07fc8	lire_ecritures	Lire les écritures comptables	552d0781-59ad-4fa4-aac6-bcdabc5ce93b	Actif	2025-11-26 14:48:23.352243+00
4fbaa3b5-68c7-4019-bcf7-12128c5a1b77	creer_ecriture	Créer une écriture comptable	552d0781-59ad-4fa4-aac6-bcdabc5ce93b	Actif	2025-11-26 14:48:37.150712+00
c5412dea-d43a-4768-9f9f-73d8f04248ad	modifier_ecriture	Modifier une écriture comptable	552d0781-59ad-4fa4-aac6-bcdabc5ce93b	Actif	2025-11-26 14:48:51.856732+00
7fc5d9d2-8573-4814-9205-fbf0d894c0a7	generer_bilan	Générer un bilan	552d0781-59ad-4fa4-aac6-bcdabc5ce93b	Actif	2025-11-26 14:49:07.041213+00
e5b5684a-ec1f-41b2-8cf5-9c8d3dcd25fb	generer_compte_resultat	Générer un compte de résultat	552d0781-59ad-4fa4-aac6-bcdabc5ce93b	Actif	2025-11-26 14:49:19.760365+00
717cb551-c914-4194-b83c-6b9021507834	lire_tresorerie	Lire les mouvements de trésorerie	06570866-dc4f-4bc3-a9df-01533494b94c	Actif	2025-11-26 14:49:32.313633+00
274bf276-8502-48d8-a726-a8cc9ce58f1b	creer_mouvement_tresorerie	Créer un mouvement de trésorerie	06570866-dc4f-4bc3-a9df-01533494b94c	Actif	2025-11-26 14:49:47.840221+00
01e2fc08-37fa-4841-835f-e7a1b2309870	modifier_mouvement_tresorerie	Modifier un mouvement de trésorerie	06570866-dc4f-4bc3-a9df-01533494b94c	Actif	2025-11-26 14:50:06.580419+00
96ef2ea6-775b-46e8-9a98-c8f16ecd30df	rapprocher_tresorerie	Effectuer un rapprochement de trésorerie	06570866-dc4f-4bc3-a9df-01533494b94c	Actif	2025-11-26 14:50:20.096717+00
10de071f-3045-45ac-b9ab-e92ee39ee0e8	lire_stations	Lire les détails des stations	c4a244ea-2e8d-4ba1-bbb9-90b2380a5e5f	Actif	2025-11-26 16:40:36.423517+00
234906b2-499f-4654-a9b6-f61501bcbd89	creer_stations	Créer une nouvelle station	c4a244ea-2e8d-4ba1-bbb9-90b2380a5e5f	Actif	2025-11-26 16:41:09.710772+00
48f22f7a-fc56-47f2-a693-e7000d792953	modifier_stations	Modifier une station existante	c4a244ea-2e8d-4ba1-bbb9-90b2380a5e5f	Actif	2025-11-26 16:41:40.649099+00
\.


--
-- TOC entry 4883 (class 0 OID 34735)
-- Dependencies: 270
-- Data for Name: permissions_tresorerie; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.permissions_tresorerie (id, utilisateur_id, tresorerie_id, droits, created_at) FROM stdin;
\.


--
-- TOC entry 4856 (class 0 OID 34072)
-- Dependencies: 243
-- Data for Name: pistolets; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.pistolets (id, code, pompe_id, cuve_id, index_initiale, compagnie_id, statut, created_at) FROM stdin;
5855dca8-6479-4093-9457-16a8ca36236c	P001	\N	1f20591c-b0f6-49f6-a10e-0157be2954dc	1200.000	e3c24054-8402-4e93-a330-27c4b3a83bf4	Actif	2025-11-28 07:25:23.662336+00
\.


--
-- TOC entry 4841 (class 0 OID 33685)
-- Dependencies: 228
-- Data for Name: plan_comptable; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.plan_comptable (id, numero, intitule, classe, type_compte, sens_solde, compte_parent_id, description, statut, est_compte_racine, est_compte_de_resultat, est_compte_actif, pays_id, est_specifique_pays, code_pays, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4922 (class 0 OID 35734)
-- Dependencies: 309
-- Data for Name: plan_comptable_pays; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.plan_comptable_pays (id, plan_comptable_id, pays_id, numero_compte_local, intitule_local, est_compte_obligatoire, created_at) FROM stdin;
\.


--
-- TOC entry 4862 (class 0 OID 34184)
-- Dependencies: 249
-- Data for Name: politiques_securite; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.politiques_securite (id, nom_politique, description, type_politique, valeur_parametre, seuil_valeur, est_actif, commentaire, utilisateur_config_id, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4850 (class 0 OID 33915)
-- Dependencies: 237
-- Data for Name: pompes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.pompes (id, station_id, code, compagnie_id, statut, created_at) FROM stdin;
\.


--
-- TOC entry 4911 (class 0 OID 35457)
-- Dependencies: 298
-- Data for Name: prevision_demande; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.prevision_demande (id, carburant_id, station_id, date_prevision, quantite_prevue, methode_prevision, confiance_prevision, commentaire, utilisateur_prevision_id, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4869 (class 0 OID 34332)
-- Dependencies: 256
-- Data for Name: profil_permissions; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.profil_permissions (id, profil_id, permission_id) FROM stdin;
\.


--
-- TOC entry 4847 (class 0 OID 33836)
-- Dependencies: 234
-- Data for Name: profils; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.profils (id, code, libelle, compagnie_id, description, statut, created_at, updated_at, type_profil) FROM stdin;
24dd5beb-8831-4bc5-8f3f-04dadd3692d6	Gérant	Gérant compagnie	e3c24054-8402-4e93-a330-27c4b3a83bf4		Actif	2025-11-26 15:07:42.099814+00	2025-11-26 15:07:42.099826+00	gerant_compagnie
\.


--
-- TOC entry 4915 (class 0 OID 35560)
-- Dependencies: 302
-- Data for Name: programme_fidelite; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.programme_fidelite (id, libelle, description, type_programme, seuil_activation, benefice, date_debut, date_fin, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4918 (class 0 OID 35635)
-- Dependencies: 305
-- Data for Name: qualite_carburant; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.qualite_carburant (id, carburant_id, cuve_id, date_controle, utilisateur_controle_id, type_controle, valeur_relevee, valeur_standard, resultat, observation, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4939 (class 0 OID 36843)
-- Dependencies: 326
-- Data for Name: qualite_carburant_initial; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.qualite_carburant_initial (id, cuve_id, carburant_id, date_analyse, utilisateur_id, densite, indice_octane, soufre_ppm, type_additif, commentaire_qualite, resultat_qualite, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4903 (class 0 OID 35273)
-- Dependencies: 290
-- Data for Name: rapports_financiers; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.rapports_financiers (id, type_rapport, periode_debut, periode_fin, contenu, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4925 (class 0 OID 35838)
-- Dependencies: 312
-- Data for Name: reglements; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.reglements (id, numero, client_id, utilisateur_id, station_id, date_reglement, montant, type_paiement, reference_paiement, observation, compagnie_id, pays_id, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4866 (class 0 OID 34264)
-- Dependencies: 253
-- Data for Name: reinitialisation_index_pistolets; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.reinitialisation_index_pistolets (id, pistolet_id, ancien_index, nouvel_index, utilisateur_demande_id, utilisateur_autorise_id, motif, date_demande, date_autorisation, statut, created_at) FROM stdin;
\.


--
-- TOC entry 4912 (class 0 OID 35487)
-- Dependencies: 299
-- Data for Name: services_annexes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.services_annexes (id, station_id, type_service, libelle, description, prix_unitaire, unite_mesure, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4902 (class 0 OID 35254)
-- Dependencies: 289
-- Data for Name: soldes_comptables; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.soldes_comptables (id, compte_numero, date_solde, solde_debit, solde_credit, compagnie_id, periode_id, created_at) FROM stdin;
\.


--
-- TOC entry 4838 (class 0 OID 33629)
-- Dependencies: 225
-- Data for Name: specifications_locales; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.specifications_locales (id, pays_id, type_specification, code_specification, libelle_specification, valeur_specification, taux_specification, est_actif, date_debut_validite, date_fin_validite, commentaire, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4836 (class 0 OID 33593)
-- Dependencies: 223
-- Data for Name: stations; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.stations (id, compagnie_id, code, nom, telephone, email, adresse, pays_id, statut, created_at) FROM stdin;
ed498670-c5a3-464f-abd0-400e4d2fafa4	e3c24054-8402-4e93-a330-27c4b3a83bf4	ST001	AKORANDRIKA	034 15 788 99		Andranomanelatra	db298448-f19a-4b75-9815-b50b0b792317	Actif	2025-11-27 12:28:41.548156+00
\.


--
-- TOC entry 4877 (class 0 OID 34521)
-- Dependencies: 264
-- Data for Name: stocks; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.stocks (id, article_id, cuve_id, station_id, stock_theorique, stock_reel, compagnie_id, est_initial, created_at, updated_at, date_initialisation, utilisateur_initialisation, observation_initialisation, stock_minimal, stock_maximal, prix_unitaire) FROM stdin;
\.


--
-- TOC entry 4878 (class 0 OID 34555)
-- Dependencies: 265
-- Data for Name: stocks_mouvements; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.stocks_mouvements (id, stock_id, article_id, cuve_id, station_id, type_mouvement, quantite, prix_unitaire, date_mouvement, reference_operation, utilisateur_id, commentaire, compagnie_id, valeur_stock_avant, valeur_stock_apres, cout_unitaire_moyen_apres, created_at, est_initial, operation_initialisation_id) FROM stdin;
\.


--
-- TOC entry 4907 (class 0 OID 35358)
-- Dependencies: 294
-- Data for Name: suivi_conformite; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.suivi_conformite (id, type_norme, libelle, description, date_prevue, date_realisee, resultat, responsable_id, observation, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4870 (class 0 OID 34350)
-- Dependencies: 257
-- Data for Name: taux_changes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.taux_changes (id, devise_source, devise_cible, taux, date_application, heure_application, est_actuel, utilisateur_id, commentaire, created_at) FROM stdin;
\.


--
-- TOC entry 4937 (class 0 OID 36165)
-- Dependencies: 324
-- Data for Name: tentatives_acces_non_autorise; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.tentatives_acces_non_autorise (id, utilisateur_id, endpoint_accesse, endpoint_autorise, ip_connexion, statut, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4859 (class 0 OID 34128)
-- Dependencies: 246
-- Data for Name: tentatives_connexion; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.tentatives_connexion (id, login, ip_connexion, resultat_connexion, utilisateur_id, created_at, type_endpoint, type_utilisateur) FROM stdin;
ae49fe23-0d2a-4c49-b94d-8f42d7afd6f8	super	\N	Reussie	12a6f9cd-bdd4-41b3-96fb-373ca232bb3c	2025-11-26 13:53:16.579553+00	administrateur	super_administrateur
74ed2dbb-7505-405e-b03b-057946b853a1	super	\N	Reussie	12a6f9cd-bdd4-41b3-96fb-373ca232bb3c	2025-11-26 14:25:42.26749+00	administrateur	super_administrateur
3144ac10-11cd-4ad3-97d5-9192c1645dab	super	\N	Reussie	12a6f9cd-bdd4-41b3-96fb-373ca232bb3c	2025-11-26 15:03:23.627324+00	administrateur	super_administrateur
bf0137fe-962f-4558-a493-3cccc3938a1d	tojo	\N	Echouee	\N	2025-11-26 15:25:02.106845+00	utilisateur	utilisateur_compagnie
e8fc9717-67c2-4d50-a297-2fe8a36b80c7	tojo	\N	Echouee	\N	2025-11-26 15:31:25.42286+00	utilisateur	utilisateur_compagnie
6688134e-fd54-4788-9139-7e56285b6c89	tojo	\N	Echouee	\N	2025-11-26 15:31:38.749073+00	utilisateur	utilisateur_compagnie
79af4183-98f5-4d43-bae7-19da23c2abac	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-26 15:32:35.549035+00	utilisateur	gerant_compagnie
a8510f41-682f-4184-8fc5-3c970bacae1b	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-26 16:12:08.378556+00	utilisateur	gerant_compagnie
c9d57355-d7e8-42a7-806f-acfe9010841f	super	\N	Reussie	12a6f9cd-bdd4-41b3-96fb-373ca232bb3c	2025-11-26 16:28:21.679871+00	utilisateur	super_administrateur
070fc42c-fbd7-4c98-a88e-05fb4af77029	super	\N	Reussie	12a6f9cd-bdd4-41b3-96fb-373ca232bb3c	2025-11-26 16:29:39.824519+00	utilisateur	super_administrateur
063d3de4-b555-4037-8dfd-87850da104f3	super	\N	Reussie	12a6f9cd-bdd4-41b3-96fb-373ca232bb3c	2025-11-26 16:34:22.104717+00	administrateur	super_administrateur
75377bc3-6135-4644-bec0-13e052a8877b	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-26 16:44:31.776116+00	utilisateur	gerant_compagnie
967007ba-b9c9-44dc-8fa0-e7a8aabd9fc0	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 09:10:00.055601+00	utilisateur	gerant_compagnie
f684a159-b95f-4b4c-bedf-5b5a8435b0c9	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 09:12:36.270231+00	utilisateur	gerant_compagnie
3dacc121-6549-4f31-8b4b-0318d6046ae5	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 10:20:04.661071+00	utilisateur	gerant_compagnie
c8516685-8809-42a0-bede-ae911795d924	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 10:22:10.434743+00	utilisateur	gerant_compagnie
0a3cb4c3-112d-4d8c-94a8-5c51359055ea	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 10:31:46.87052+00	utilisateur	gerant_compagnie
009cd301-4049-47a5-bebf-1ea15745307e	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 10:39:21.307347+00	utilisateur	gerant_compagnie
26caa4a3-c2ea-45af-85bf-62d8dd99e65f	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 11:24:10.009482+00	utilisateur	gerant_compagnie
a8fd62bc-2ec3-41ee-b69c-96e1932fa40f	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 12:00:11.300294+00	utilisateur	gerant_compagnie
db05ead0-6ad8-411e-aa70-f9cf7090b705	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 12:03:20.429892+00	utilisateur	gerant_compagnie
e6b5f0c4-02d8-4a5b-ae08-b1867def25f6	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 12:22:33.780767+00	utilisateur	gerant_compagnie
8b4a19d2-7668-4cf6-b44b-413a7e9d7140	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 13:09:57.284562+00	utilisateur	gerant_compagnie
b1e74828-a77b-4810-adfe-26ebde759ada	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 15:07:52.648699+00	utilisateur	gerant_compagnie
2572a6b0-7220-493b-8d00-0fc35e64c351	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 15:17:28.223752+00	utilisateur	gerant_compagnie
9d8a23dc-114b-4f15-be78-bd788d687616	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 15:38:50.954891+00	utilisateur	gerant_compagnie
00b6ab98-fcb1-4d27-b9cd-db138cfaf9da	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 16:41:09.347052+00	utilisateur	gerant_compagnie
ac9697de-578d-41c0-b1d2-af8f98ed31eb	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-27 16:47:24.502357+00	utilisateur	gerant_compagnie
6db0f473-eb8c-48e6-b792-89bb2e280e64	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 05:49:14.417513+00	utilisateur	gerant_compagnie
72ee3ff7-daa1-4158-84e8-ba79abb6e1ec	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 06:37:10.701941+00	utilisateur	gerant_compagnie
2435b3ca-16ed-4bb2-b136-88db2db31da9	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 07:23:10.192568+00	utilisateur	gerant_compagnie
c53bc7a4-9bfe-46de-a732-81f9d31ceeba	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 07:23:46.748913+00	utilisateur	gerant_compagnie
0a5ec928-7392-404c-b867-610c935dbe24	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 08:28:01.069871+00	utilisateur	gerant_compagnie
98ee2c11-8e5f-417f-afda-5a8099bd799b	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 08:39:38.039539+00	utilisateur	gerant_compagnie
af177ba4-584d-4388-ba17-b679f0ad807c	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 09:16:24.913659+00	utilisateur	gerant_compagnie
39bae205-f3ce-4018-990a-31b764af62a3	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 10:17:21.534433+00	utilisateur	gerant_compagnie
9f13830d-9afa-434d-9ee4-9bb51afa815f	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 13:05:51.367293+00	utilisateur	gerant_compagnie
dd727fef-f3ca-4c6b-bcba-ee9b393a9d4b	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 13:26:06.394162+00	utilisateur	gerant_compagnie
23640667-706e-45fe-be37-2508e0f39b41	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 13:27:44.898961+00	utilisateur	gerant_compagnie
e07d4603-fa5f-4756-8ff9-de07c26c3953	tojo	\N	Echouee	\N	2025-11-28 13:33:47.988083+00	utilisateur	utilisateur_compagnie
74075c96-51d7-411d-aad4-cfccd670ed72	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 13:34:42.896993+00	utilisateur	gerant_compagnie
7cf02b0a-7b77-475d-b0b9-f1b39fc96651	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 13:34:52.699631+00	utilisateur	gerant_compagnie
10a70041-edee-4466-93cf-6f0768e81803	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 13:55:38.561126+00	utilisateur	gerant_compagnie
c0049e4b-70f2-4ee1-8eeb-deb9854479c4	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 14:19:17.524749+00	utilisateur	gerant_compagnie
1156b6d5-805f-4ffd-b488-184b42ab3472	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 14:34:10.723532+00	utilisateur	gerant_compagnie
9dfbebc7-88ab-41df-8bc2-9021c8ad6667	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 14:48:35.512462+00	utilisateur	gerant_compagnie
c9b293cb-cb09-4d6e-9644-0212eaaff1c6	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 14:51:50.517509+00	utilisateur	gerant_compagnie
a37e0dc1-1592-4e42-b8d0-49d34a493b6b	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 14:58:59.816166+00	utilisateur	gerant_compagnie
c71841ab-8eb4-41a0-ab44-beea22806ec2	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 15:15:44.071408+00	utilisateur	gerant_compagnie
53545835-af15-42b4-a82a-542aa6f3e08f	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 15:35:39.150038+00	utilisateur	gerant_compagnie
1adf8c34-65ef-4410-ae3a-442e8581198d	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 15:50:00.048134+00	utilisateur	gerant_compagnie
fdeb3fa1-cb08-4413-ab61-58dc7106b72d	tojo	\N	Reussie	0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	2025-11-28 15:50:07.445013+00	utilisateur	gerant_compagnie
\.


--
-- TOC entry 4887 (class 0 OID 34842)
-- Dependencies: 274
-- Data for Name: tickets_caisse; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.tickets_caisse (id, numero_ticket, station_id, caissier_id, date_ticket, heure_debut, heure_fin, montant_initial, montant_final_theorique, montant_final_reel, ecart, commentaire, compagnie_id, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4852 (class 0 OID 33964)
-- Dependencies: 239
-- Data for Name: tranches_taxes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.tranches_taxes (id, type_taxe_id, borne_inferieure, borne_superieure, taux, est_actif, created_at) FROM stdin;
\.


--
-- TOC entry 4928 (class 0 OID 35935)
-- Dependencies: 315
-- Data for Name: transfert_stock; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.transfert_stock (id, numero, date_transfert, heure_transfert, utilisateur_id, station_origine_id, station_destination_id, observation, statut, compagnie_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4936 (class 0 OID 36076)
-- Dependencies: 323
-- Data for Name: transfert_stock_details; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.transfert_stock_details (id, transfert_id, article_id, cuve_origine_id, cuve_destination_id, quantite, prix_unitaire, valeur_totale, statut, created_at) FROM stdin;
\.


--
-- TOC entry 4854 (class 0 OID 34003)
-- Dependencies: 241
-- Data for Name: tresoreries; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.tresoreries (id, code, libelle, compagnie_id, station_ids, solde, devise_code, taux_change, fournisseur_id, type_tresorerie, methode_paiement, statut, solde_theorique, solde_reel, date_dernier_rapprochement, utilisateur_dernier_rapprochement, type_tresorerie_libelle, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4835 (class 0 OID 33580)
-- Dependencies: 222
-- Data for Name: type_tiers; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.type_tiers (id, type, libelle, num_compte, created_at, updated_at) FROM stdin;
c1ee3d3c-8571-4903-93d1-efa362b53d9c	client	Particulier	411A00	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
a5604e3a-a761-41ce-ad61-1c30e809e8ee	client	Professionnel	411A01	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
fd616efe-030f-46c8-981f-b238d16dc4e9	client	Grand compte	411A02	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
c7b9ebdb-ddce-42a4-bab2-ed881e068b35	client	Client fidèle	411A03	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
2b56a527-3128-4d5e-89d2-4ba24621a9ca	client	Société partenaire	411A04	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
172cf9c3-2103-4582-9b1e-1d87e99f82cc	client	Organisation gouvernementale	411A05	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
e78cbe48-77f5-4444-a34d-93b91db68064	fournisseur	Fournisseur carburant	401A00	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
1a5aee09-b84b-43a8-ac8c-15d19d2f7c83	fournisseur	Distributeur boutique	401A01	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
bf33296b-3e99-485a-bd43-3631b8793c8b	fournisseur	Maintenance	401A02	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
b1a469dd-5da6-478b-9cc6-a7a27d61ce64	fournisseur	Prestataire de service	401A03	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
3fcbc768-0bcb-44c3-8386-65b7e70aca71	fournisseur	Fournisseur logistique	401A04	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
9a860f43-222d-4b74-8b02-5d8f1b7acb79	fournisseur	Fournisseur d'équipement	401A05	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
af12c9b4-c0ac-4775-ad70-7f408aae45d4	employe	Pompiste	628A00	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
429914a0-07aa-40ba-bba3-c8d5a9268ba4	employe	Caissier	628A01	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
d9c93234-72ff-4e32-9c57-be27acbf9792	employe	Responsable station	628A02	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
b074867c-5139-4043-ad2e-c82ee9ecd872	employe	Technicien	628A03	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
3e354d66-d243-444f-8b24-ebe517f2cfd0	employe	Administratif	628A04	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
86f4028a-5b01-441d-bcae-79d5c94e8dcb	employe	Gestionnaire	628A05	2025-11-28 12:26:25.708018+00	2025-11-28 12:26:25.708018+00
\.


--
-- TOC entry 4846 (class 0 OID 33811)
-- Dependencies: 233
-- Data for Name: types_taxes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.types_taxes (id, code_taxe, libelle_taxe, description, pays_id, taux_par_defaut, type_calcul, compte_comptable, est_actif, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4833 (class 0 OID 33544)
-- Dependencies: 220
-- Data for Name: unites_mesure; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.unites_mesure (id, code_unite, libelle_unite, pays_id, est_standard, est_utilisee, created_at) FROM stdin;
\.


--
-- TOC entry 4853 (class 0 OID 33978)
-- Dependencies: 240
-- Data for Name: utilisateurs; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.utilisateurs (id, login, mot_de_passe, nom, profil_id, email, telephone, stations_user, statut, last_login, compagnie_id, created_at, updated_at, type_utilisateur) FROM stdin;
12a6f9cd-bdd4-41b3-96fb-373ca232bb3c	super	$2b$12$uWeddF1Cc.DKR0lKqCWbAuBXN39DcOtQba.sSKMSlYgPUJccGxjOa	Super	\N	\N	\N	[]	Actif	2025-11-26 16:34:21.173153+00	\N	2025-11-26 13:52:51.017442+00	2025-11-26 16:34:21.324845+00	super_administrateur
0a7ae1cb-cd18-4cb1-929f-695ef5c6f3a8	tojo	$2b$12$uWeddF1Cc.DKR0lKqCWbAuBXN39DcOtQba.sSKMSlYgPUJccGxjOa	Tojo Eugène	24dd5beb-8831-4bc5-8f3f-04dadd3692d6	tojo@test.com	034 15 720 11	[]	Actif	2025-11-28 15:50:07.436568+00	e3c24054-8402-4e93-a330-27c4b3a83bf4	2025-11-26 15:17:58.118321+00	2025-11-28 15:50:05.718695+00	gerant_compagnie
\.


--
-- TOC entry 4899 (class 0 OID 35196)
-- Dependencies: 286
-- Data for Name: utilisation_depot_garantie; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.utilisation_depot_garantie (id, depot_garantie_id, type_utilisation, montant_utilise, reference_operation, utilisateur_utilise_id, date_utilisation, commentaire, compagnie_id, created_at) FROM stdin;
\.


--
-- TOC entry 4920 (class 0 OID 35699)
-- Dependencies: 307
-- Data for Name: validations_hierarchiques; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.validations_hierarchiques (id, operation_type, seuil_montant, niveau_validation, profil_autorise_id, statut) FROM stdin;
\.


--
-- TOC entry 4880 (class 0 OID 34633)
-- Dependencies: 267
-- Data for Name: ventes; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.ventes (id, client_id, date_vente, total_ht, total_ttc, total_tva, reference_facture, observation, type_vente, type_transaction, compagnie_id, pays_id, devise_code, taux_change, journal_entry_id, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4881 (class 0 OID 34669)
-- Dependencies: 268
-- Data for Name: ventes_details; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.ventes_details (id, vente_id, article_id, pistolet_id, index_debut, index_fin, quantite, prix_unitaire_ht, prix_unitaire_ttc, taux_tva, taxes_detaillees, station_id, utilisateur_id, created_at) FROM stdin;
\.


--
-- TOC entry 4882 (class 0 OID 34711)
-- Dependencies: 269
-- Data for Name: ventes_tresorerie; Type: TABLE DATA; Schema: public; Owner: energixdb_k3c4_user
--

COPY public.ventes_tresorerie (id, vente_id, tresorerie_id, montant, note_paiement, statut, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4246 (class 2606 OID 34427)
-- Name: achats_details achats_details_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_details
    ADD CONSTRAINT achats_details_pkey PRIMARY KEY (id);


--
-- TOC entry 4240 (class 2606 OID 34382)
-- Name: achats achats_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats
    ADD CONSTRAINT achats_pkey PRIMARY KEY (id);


--
-- TOC entry 4242 (class 2606 OID 34406)
-- Name: achats_stations achats_stations_achat_id_station_id_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_stations
    ADD CONSTRAINT achats_stations_achat_id_station_id_key UNIQUE (achat_id, station_id);


--
-- TOC entry 4244 (class 2606 OID 34404)
-- Name: achats_stations achats_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_stations
    ADD CONSTRAINT achats_stations_pkey PRIMARY KEY (id);


--
-- TOC entry 4250 (class 2606 OID 34485)
-- Name: achats_tresorerie achats_tresorerie_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_tresorerie
    ADD CONSTRAINT achats_tresorerie_pkey PRIMARY KEY (id);


--
-- TOC entry 4304 (class 2606 OID 35143)
-- Name: ajustements_stock ajustements_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ajustements_stock
    ADD CONSTRAINT ajustements_stock_pkey PRIMARY KEY (id);


--
-- TOC entry 4401 (class 2606 OID 36827)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4330 (class 2606 OID 35441)
-- Name: analyse_commerciale analyse_commerciale_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.analyse_commerciale
    ADD CONSTRAINT analyse_commerciale_pkey PRIMARY KEY (id);


--
-- TOC entry 4284 (class 2606 OID 34889)
-- Name: arrets_compte_caissier arrets_compte_caissier_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.arrets_compte_caissier
    ADD CONSTRAINT arrets_compte_caissier_pkey PRIMARY KEY (id);


--
-- TOC entry 4175 (class 2606 OID 33892)
-- Name: articles articles_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_code_key UNIQUE (code);


--
-- TOC entry 4177 (class 2606 OID 33894)
-- Name: articles articles_codebarre_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_codebarre_key UNIQUE (codebarre);


--
-- TOC entry 4179 (class 2606 OID 33890)
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- TOC entry 4328 (class 2606 OID 35422)
-- Name: assurances assurances_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.assurances
    ADD CONSTRAINT assurances_pkey PRIMARY KEY (id);


--
-- TOC entry 4206 (class 2606 OID 34122)
-- Name: auth_tokens auth_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT auth_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 4200 (class 2606 OID 34056)
-- Name: barremage_cuves barremage_cuves_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.barremage_cuves
    ADD CONSTRAINT barremage_cuves_pkey PRIMARY KEY (id);


--
-- TOC entry 4310 (class 2606 OID 35228)
-- Name: bilan_initial_lignes bilan_initial_lignes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bilan_initial_lignes
    ADD CONSTRAINT bilan_initial_lignes_pkey PRIMARY KEY (id);


--
-- TOC entry 4227 (class 2606 OID 34302)
-- Name: bilan_initial bilan_initial_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bilan_initial
    ADD CONSTRAINT bilan_initial_pkey PRIMARY KEY (id);


--
-- TOC entry 4276 (class 2606 OID 34831)
-- Name: bons_commande bons_commande_numero_bon_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bons_commande
    ADD CONSTRAINT bons_commande_numero_bon_key UNIQUE (numero_bon);


--
-- TOC entry 4278 (class 2606 OID 34829)
-- Name: bons_commande bons_commande_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bons_commande
    ADD CONSTRAINT bons_commande_pkey PRIMARY KEY (id);


--
-- TOC entry 4149 (class 2606 OID 33727)
-- Name: carburants carburants_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.carburants
    ADD CONSTRAINT carburants_code_key UNIQUE (code);


--
-- TOC entry 4151 (class 2606 OID 33725)
-- Name: carburants carburants_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.carburants
    ADD CONSTRAINT carburants_pkey PRIMARY KEY (id);


--
-- TOC entry 4342 (class 2606 OID 35592)
-- Name: cartes_carburant cartes_carburant_numero_carte_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cartes_carburant
    ADD CONSTRAINT cartes_carburant_numero_carte_key UNIQUE (numero_carte);


--
-- TOC entry 4344 (class 2606 OID 35590)
-- Name: cartes_carburant cartes_carburant_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cartes_carburant
    ADD CONSTRAINT cartes_carburant_pkey PRIMARY KEY (id);


--
-- TOC entry 4157 (class 2606 OID 33779)
-- Name: clients clients_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_code_key UNIQUE (code);


--
-- TOC entry 4159 (class 2606 OID 33777)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- TOC entry 4125 (class 2606 OID 33574)
-- Name: compagnies compagnies_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.compagnies
    ADD CONSTRAINT compagnies_code_key UNIQUE (code);


--
-- TOC entry 4127 (class 2606 OID 33572)
-- Name: compagnies compagnies_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.compagnies
    ADD CONSTRAINT compagnies_pkey PRIMARY KEY (id);


--
-- TOC entry 4139 (class 2606 OID 33657)
-- Name: configurations_pays configurations_pays_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.configurations_pays
    ADD CONSTRAINT configurations_pays_pkey PRIMARY KEY (id);


--
-- TOC entry 4346 (class 2606 OID 35624)
-- Name: contrats_clients contrats_clients_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.contrats_clients
    ADD CONSTRAINT contrats_clients_pkey PRIMARY KEY (id);


--
-- TOC entry 4336 (class 2606 OID 35521)
-- Name: contrats_maintenance contrats_maintenance_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.contrats_maintenance
    ADD CONSTRAINT contrats_maintenance_pkey PRIMARY KEY (id);


--
-- TOC entry 4338 (class 2606 OID 35549)
-- Name: controle_interne controle_interne_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.controle_interne
    ADD CONSTRAINT controle_interne_pkey PRIMARY KEY (id);


--
-- TOC entry 4204 (class 2606 OID 34104)
-- Name: conversions_unite conversions_unite_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.conversions_unite
    ADD CONSTRAINT conversions_unite_pkey PRIMARY KEY (id);


--
-- TOC entry 4350 (class 2606 OID 35673)
-- Name: couts_logistique couts_logistique_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique
    ADD CONSTRAINT couts_logistique_pkey PRIMARY KEY (id);


--
-- TOC entry 4405 (class 2606 OID 36881)
-- Name: couts_logistique_stocks_initial couts_logistique_stocks_initial_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique_stocks_initial
    ADD CONSTRAINT couts_logistique_stocks_initial_pkey PRIMARY KEY (id);


--
-- TOC entry 4360 (class 2606 OID 35791)
-- Name: cuve_stocks_mouvements cuve_stocks_mouvements_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks_mouvements
    ADD CONSTRAINT cuve_stocks_mouvements_pkey PRIMARY KEY (id);


--
-- TOC entry 4358 (class 2606 OID 35764)
-- Name: cuve_stocks cuve_stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks
    ADD CONSTRAINT cuve_stocks_pkey PRIMARY KEY (id);


--
-- TOC entry 4185 (class 2606 OID 33946)
-- Name: cuves cuves_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuves
    ADD CONSTRAINT cuves_pkey PRIMARY KEY (id);


--
-- TOC entry 4187 (class 2606 OID 33948)
-- Name: cuves cuves_station_id_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuves
    ADD CONSTRAINT cuves_station_id_code_key UNIQUE (station_id, code);


--
-- TOC entry 4322 (class 2606 OID 35347)
-- Name: declarations_fiscales declarations_fiscales_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.declarations_fiscales
    ADD CONSTRAINT declarations_fiscales_pkey PRIMARY KEY (id);


--
-- TOC entry 4294 (class 2606 OID 35015)
-- Name: depenses depenses_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depenses
    ADD CONSTRAINT depenses_pkey PRIMARY KEY (id);


--
-- TOC entry 4306 (class 2606 OID 35180)
-- Name: depot_garantie depot_garantie_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depot_garantie
    ADD CONSTRAINT depot_garantie_pkey PRIMARY KEY (id);


--
-- TOC entry 4248 (class 2606 OID 34456)
-- Name: dettes_fournisseurs dettes_fournisseurs_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.dettes_fournisseurs
    ADD CONSTRAINT dettes_fournisseurs_pkey PRIMARY KEY (id);


--
-- TOC entry 4232 (class 2606 OID 34321)
-- Name: ecarts_soldes ecarts_soldes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ecarts_soldes
    ADD CONSTRAINT ecarts_soldes_pkey PRIMARY KEY (id);


--
-- TOC entry 4161 (class 2606 OID 33805)
-- Name: employes employes_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.employes
    ADD CONSTRAINT employes_code_key UNIQUE (code);


--
-- TOC entry 4163 (class 2606 OID 33803)
-- Name: employes employes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.employes
    ADD CONSTRAINT employes_pkey PRIMARY KEY (id);


--
-- TOC entry 4386 (class 2606 OID 36016)
-- Name: etat_caisse etat_caisse_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_caisse
    ADD CONSTRAINT etat_caisse_pkey PRIMARY KEY (id);


--
-- TOC entry 4388 (class 2606 OID 36033)
-- Name: etat_comptable etat_comptable_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_comptable
    ADD CONSTRAINT etat_comptable_pkey PRIMARY KEY (id);


--
-- TOC entry 4384 (class 2606 OID 35999)
-- Name: etat_stock etat_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_stock
    ADD CONSTRAINT etat_stock_pkey PRIMARY KEY (id);


--
-- TOC entry 4213 (class 2606 OID 34151)
-- Name: evenements_securite evenements_securite_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.evenements_securite
    ADD CONSTRAINT evenements_securite_pkey PRIMARY KEY (id);


--
-- TOC entry 4141 (class 2606 OID 33674)
-- Name: familles_articles familles_articles_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.familles_articles
    ADD CONSTRAINT familles_articles_code_key UNIQUE (code);


--
-- TOC entry 4143 (class 2606 OID 33672)
-- Name: familles_articles familles_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.familles_articles
    ADD CONSTRAINT familles_articles_pkey PRIMARY KEY (id);


--
-- TOC entry 4296 (class 2606 OID 35052)
-- Name: fiches_paie fiches_paie_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fiches_paie
    ADD CONSTRAINT fiches_paie_pkey PRIMARY KEY (id);


--
-- TOC entry 4153 (class 2606 OID 33750)
-- Name: fournisseurs fournisseurs_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fournisseurs
    ADD CONSTRAINT fournisseurs_code_key UNIQUE (code);


--
-- TOC entry 4155 (class 2606 OID 33748)
-- Name: fournisseurs fournisseurs_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fournisseurs
    ADD CONSTRAINT fournisseurs_pkey PRIMARY KEY (id);


--
-- TOC entry 4354 (class 2606 OID 35723)
-- Name: historique_actions_utilisateurs historique_actions_utilisateurs_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_actions_utilisateurs
    ADD CONSTRAINT historique_actions_utilisateurs_pkey PRIMARY KEY (id);


--
-- TOC entry 4223 (class 2606 OID 34253)
-- Name: historique_index_pistolets historique_index_pistolets_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_index_pistolets
    ADD CONSTRAINT historique_index_pistolets_pkey PRIMARY KEY (id);


--
-- TOC entry 4286 (class 2606 OID 34913)
-- Name: historique_paiements_clients historique_paiements_clients_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_paiements_clients
    ADD CONSTRAINT historique_paiements_clients_pkey PRIMARY KEY (id);


--
-- TOC entry 4219 (class 2606 OID 34213)
-- Name: historique_prix_articles historique_prix_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_prix_articles
    ADD CONSTRAINT historique_prix_articles_pkey PRIMARY KEY (id);


--
-- TOC entry 4221 (class 2606 OID 34232)
-- Name: historique_prix_carburants historique_prix_carburants_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_prix_carburants
    ADD CONSTRAINT historique_prix_carburants_pkey PRIMARY KEY (id);


--
-- TOC entry 4298 (class 2606 OID 35088)
-- Name: immobilisations immobilisations_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_code_key UNIQUE (code);


--
-- TOC entry 4300 (class 2606 OID 35086)
-- Name: immobilisations immobilisations_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_pkey PRIMARY KEY (id);


--
-- TOC entry 4326 (class 2606 OID 35390)
-- Name: incidents_securite incidents_securite_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.incidents_securite
    ADD CONSTRAINT incidents_securite_pkey PRIMARY KEY (id);


--
-- TOC entry 4392 (class 2606 OID 36065)
-- Name: inventaire_details inventaire_details_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire_details
    ADD CONSTRAINT inventaire_details_pkey PRIMARY KEY (id);


--
-- TOC entry 4370 (class 2606 OID 35919)
-- Name: inventaire inventaire_numero_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire
    ADD CONSTRAINT inventaire_numero_key UNIQUE (numero);


--
-- TOC entry 4372 (class 2606 OID 35917)
-- Name: inventaire inventaire_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire
    ADD CONSTRAINT inventaire_pkey PRIMARY KEY (id);


--
-- TOC entry 4288 (class 2606 OID 34937)
-- Name: inventaires inventaires_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaires
    ADD CONSTRAINT inventaires_pkey PRIMARY KEY (id);


--
-- TOC entry 4272 (class 2606 OID 34767)
-- Name: journal_entries journal_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_pkey PRIMARY KEY (id);


--
-- TOC entry 4274 (class 2606 OID 34804)
-- Name: journal_lines journal_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_lines
    ADD CONSTRAINT journal_lines_pkey PRIMARY KEY (id);


--
-- TOC entry 4380 (class 2606 OID 35987)
-- Name: journaux journaux_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journaux
    ADD CONSTRAINT journaux_code_key UNIQUE (code);


--
-- TOC entry 4382 (class 2606 OID 35985)
-- Name: journaux journaux_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journaux
    ADD CONSTRAINT journaux_pkey PRIMARY KEY (id);


--
-- TOC entry 4320 (class 2606 OID 35315)
-- Name: kpi_operations kpi_operations_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.kpi_operations
    ADD CONSTRAINT kpi_operations_pkey PRIMARY KEY (id);


--
-- TOC entry 4292 (class 2606 OID 34987)
-- Name: mesures_inventaire_articles mesures_inventaire_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_articles
    ADD CONSTRAINT mesures_inventaire_articles_pkey PRIMARY KEY (id);


--
-- TOC entry 4290 (class 2606 OID 34962)
-- Name: mesures_inventaire_cuves mesures_inventaire_cuves_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_cuves
    ADD CONSTRAINT mesures_inventaire_cuves_pkey PRIMARY KEY (id);


--
-- TOC entry 4252 (class 2606 OID 34505)
-- Name: mesures_livraison mesures_livraison_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_livraison
    ADD CONSTRAINT mesures_livraison_pkey PRIMARY KEY (id);


--
-- TOC entry 4135 (class 2606 OID 33628)
-- Name: methode_paiment methode_paiment_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.methode_paiment
    ADD CONSTRAINT methode_paiment_pkey PRIMARY KEY (id);


--
-- TOC entry 4318 (class 2606 OID 35298)
-- Name: modeles_rapports modeles_rapports_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.modeles_rapports
    ADD CONSTRAINT modeles_rapports_pkey PRIMARY KEY (id);


--
-- TOC entry 4215 (class 2606 OID 34173)
-- Name: modifications_sensibles modifications_sensibles_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.modifications_sensibles
    ADD CONSTRAINT modifications_sensibles_pkey PRIMARY KEY (id);


--
-- TOC entry 4117 (class 2606 OID 33543)
-- Name: modules modules_libelle_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.modules
    ADD CONSTRAINT modules_libelle_key UNIQUE (libelle);


--
-- TOC entry 4119 (class 2606 OID 33541)
-- Name: modules modules_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.modules
    ADD CONSTRAINT modules_pkey PRIMARY KEY (id);


--
-- TOC entry 4302 (class 2606 OID 35118)
-- Name: mouvements_immobilisations mouvements_immobilisations_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_immobilisations
    ADD CONSTRAINT mouvements_immobilisations_pkey PRIMARY KEY (id);


--
-- TOC entry 4390 (class 2606 OID 36048)
-- Name: mouvements_stock_details mouvements_stock_details_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock_details
    ADD CONSTRAINT mouvements_stock_details_pkey PRIMARY KEY (id);


--
-- TOC entry 4366 (class 2606 OID 35880)
-- Name: mouvements_stock mouvements_stock_numero_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_numero_key UNIQUE (numero);


--
-- TOC entry 4368 (class 2606 OID 35878)
-- Name: mouvements_stock mouvements_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_pkey PRIMARY KEY (id);


--
-- TOC entry 4378 (class 2606 OID 35968)
-- Name: mouvements_tresorerie_details mouvements_tresorerie_details_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie_details
    ADD CONSTRAINT mouvements_tresorerie_details_pkey PRIMARY KEY (id);


--
-- TOC entry 4262 (class 2606 OID 34612)
-- Name: mouvements_tresorerie mouvements_tresorerie_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie
    ADD CONSTRAINT mouvements_tresorerie_pkey PRIMARY KEY (id);


--
-- TOC entry 4113 (class 2606 OID 33533)
-- Name: pays pays_code_pays_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pays
    ADD CONSTRAINT pays_code_pays_key UNIQUE (code_pays);


--
-- TOC entry 4115 (class 2606 OID 33531)
-- Name: pays pays_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pays
    ADD CONSTRAINT pays_pkey PRIMARY KEY (id);


--
-- TOC entry 4312 (class 2606 OID 35248)
-- Name: periodes_comptables periodes_comptables_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.periodes_comptables
    ADD CONSTRAINT periodes_comptables_pkey PRIMARY KEY (id);


--
-- TOC entry 4173 (class 2606 OID 33865)
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4270 (class 2606 OID 34742)
-- Name: permissions_tresorerie permissions_tresorerie_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.permissions_tresorerie
    ADD CONSTRAINT permissions_tresorerie_pkey PRIMARY KEY (id);


--
-- TOC entry 4202 (class 2606 OID 34081)
-- Name: pistolets pistolets_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pistolets
    ADD CONSTRAINT pistolets_pkey PRIMARY KEY (id);


--
-- TOC entry 4145 (class 2606 OID 33703)
-- Name: plan_comptable plan_comptable_numero_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.plan_comptable
    ADD CONSTRAINT plan_comptable_numero_key UNIQUE (numero);


--
-- TOC entry 4356 (class 2606 OID 35741)
-- Name: plan_comptable_pays plan_comptable_pays_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.plan_comptable_pays
    ADD CONSTRAINT plan_comptable_pays_pkey PRIMARY KEY (id);


--
-- TOC entry 4147 (class 2606 OID 33701)
-- Name: plan_comptable plan_comptable_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.plan_comptable
    ADD CONSTRAINT plan_comptable_pkey PRIMARY KEY (id);


--
-- TOC entry 4217 (class 2606 OID 34194)
-- Name: politiques_securite politiques_securite_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.politiques_securite
    ADD CONSTRAINT politiques_securite_pkey PRIMARY KEY (id);


--
-- TOC entry 4181 (class 2606 OID 33925)
-- Name: pompes pompes_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pompes
    ADD CONSTRAINT pompes_code_key UNIQUE (code);


--
-- TOC entry 4183 (class 2606 OID 33923)
-- Name: pompes pompes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pompes
    ADD CONSTRAINT pompes_pkey PRIMARY KEY (id);


--
-- TOC entry 4332 (class 2606 OID 35466)
-- Name: prevision_demande prevision_demande_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.prevision_demande
    ADD CONSTRAINT prevision_demande_pkey PRIMARY KEY (id);


--
-- TOC entry 4234 (class 2606 OID 34337)
-- Name: profil_permissions profil_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.profil_permissions
    ADD CONSTRAINT profil_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4236 (class 2606 OID 34339)
-- Name: profil_permissions profil_permissions_profil_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.profil_permissions
    ADD CONSTRAINT profil_permissions_profil_id_permission_id_key UNIQUE (profil_id, permission_id);


--
-- TOC entry 4169 (class 2606 OID 33849)
-- Name: profils profils_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.profils
    ADD CONSTRAINT profils_code_key UNIQUE (code);


--
-- TOC entry 4171 (class 2606 OID 33847)
-- Name: profils profils_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.profils
    ADD CONSTRAINT profils_pkey PRIMARY KEY (id);


--
-- TOC entry 4340 (class 2606 OID 35572)
-- Name: programme_fidelite programme_fidelite_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.programme_fidelite
    ADD CONSTRAINT programme_fidelite_pkey PRIMARY KEY (id);


--
-- TOC entry 4403 (class 2606 OID 36852)
-- Name: qualite_carburant_initial qualite_carburant_initial_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant_initial
    ADD CONSTRAINT qualite_carburant_initial_pkey PRIMARY KEY (id);


--
-- TOC entry 4348 (class 2606 OID 35644)
-- Name: qualite_carburant qualite_carburant_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant
    ADD CONSTRAINT qualite_carburant_pkey PRIMARY KEY (id);


--
-- TOC entry 4316 (class 2606 OID 35281)
-- Name: rapports_financiers rapports_financiers_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.rapports_financiers
    ADD CONSTRAINT rapports_financiers_pkey PRIMARY KEY (id);


--
-- TOC entry 4362 (class 2606 OID 35846)
-- Name: reglements reglements_numero_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reglements
    ADD CONSTRAINT reglements_numero_key UNIQUE (numero);


--
-- TOC entry 4364 (class 2606 OID 35844)
-- Name: reglements reglements_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reglements
    ADD CONSTRAINT reglements_pkey PRIMARY KEY (id);


--
-- TOC entry 4225 (class 2606 OID 34275)
-- Name: reinitialisation_index_pistolets reinitialisation_index_pistolets_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reinitialisation_index_pistolets
    ADD CONSTRAINT reinitialisation_index_pistolets_pkey PRIMARY KEY (id);


--
-- TOC entry 4334 (class 2606 OID 35499)
-- Name: services_annexes services_annexes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.services_annexes
    ADD CONSTRAINT services_annexes_pkey PRIMARY KEY (id);


--
-- TOC entry 4314 (class 2606 OID 35262)
-- Name: soldes_comptables soldes_comptables_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.soldes_comptables
    ADD CONSTRAINT soldes_comptables_pkey PRIMARY KEY (id);


--
-- TOC entry 4137 (class 2606 OID 33639)
-- Name: specifications_locales specifications_locales_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.specifications_locales
    ADD CONSTRAINT specifications_locales_pkey PRIMARY KEY (id);


--
-- TOC entry 4131 (class 2606 OID 33605)
-- Name: stations stations_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_code_key UNIQUE (code);


--
-- TOC entry 4133 (class 2606 OID 33603)
-- Name: stations stations_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_pkey PRIMARY KEY (id);


--
-- TOC entry 4260 (class 2606 OID 34569)
-- Name: stocks_mouvements stocks_mouvements_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks_mouvements
    ADD CONSTRAINT stocks_mouvements_pkey PRIMARY KEY (id);


--
-- TOC entry 4256 (class 2606 OID 34534)
-- Name: stocks stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_pkey PRIMARY KEY (id);


--
-- TOC entry 4324 (class 2606 OID 35367)
-- Name: suivi_conformite suivi_conformite_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.suivi_conformite
    ADD CONSTRAINT suivi_conformite_pkey PRIMARY KEY (id);


--
-- TOC entry 4238 (class 2606 OID 34360)
-- Name: taux_changes taux_changes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.taux_changes
    ADD CONSTRAINT taux_changes_pkey PRIMARY KEY (id);


--
-- TOC entry 4399 (class 2606 OID 36173)
-- Name: tentatives_acces_non_autorise tentatives_acces_non_autorise_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tentatives_acces_non_autorise
    ADD CONSTRAINT tentatives_acces_non_autorise_pkey PRIMARY KEY (id);


--
-- TOC entry 4211 (class 2606 OID 34135)
-- Name: tentatives_connexion tentatives_connexion_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tentatives_connexion
    ADD CONSTRAINT tentatives_connexion_pkey PRIMARY KEY (id);


--
-- TOC entry 4280 (class 2606 OID 34859)
-- Name: tickets_caisse tickets_caisse_numero_ticket_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tickets_caisse
    ADD CONSTRAINT tickets_caisse_numero_ticket_key UNIQUE (numero_ticket);


--
-- TOC entry 4282 (class 2606 OID 34857)
-- Name: tickets_caisse tickets_caisse_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tickets_caisse
    ADD CONSTRAINT tickets_caisse_pkey PRIMARY KEY (id);


--
-- TOC entry 4189 (class 2606 OID 33972)
-- Name: tranches_taxes tranches_taxes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tranches_taxes
    ADD CONSTRAINT tranches_taxes_pkey PRIMARY KEY (id);


--
-- TOC entry 4394 (class 2606 OID 36080)
-- Name: transfert_stock_details transfert_stock_details_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock_details
    ADD CONSTRAINT transfert_stock_details_pkey PRIMARY KEY (id);


--
-- TOC entry 4374 (class 2606 OID 35943)
-- Name: transfert_stock transfert_stock_numero_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock
    ADD CONSTRAINT transfert_stock_numero_key UNIQUE (numero);


--
-- TOC entry 4376 (class 2606 OID 35941)
-- Name: transfert_stock transfert_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock
    ADD CONSTRAINT transfert_stock_pkey PRIMARY KEY (id);


--
-- TOC entry 4196 (class 2606 OID 34024)
-- Name: tresoreries tresoreries_code_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tresoreries
    ADD CONSTRAINT tresoreries_code_key UNIQUE (code);


--
-- TOC entry 4198 (class 2606 OID 34022)
-- Name: tresoreries tresoreries_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tresoreries
    ADD CONSTRAINT tresoreries_pkey PRIMARY KEY (id);


--
-- TOC entry 4129 (class 2606 OID 33587)
-- Name: type_tiers type_tiers_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.type_tiers
    ADD CONSTRAINT type_tiers_pkey PRIMARY KEY (id);


--
-- TOC entry 4165 (class 2606 OID 33825)
-- Name: types_taxes types_taxes_code_taxe_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.types_taxes
    ADD CONSTRAINT types_taxes_code_taxe_key UNIQUE (code_taxe);


--
-- TOC entry 4167 (class 2606 OID 33823)
-- Name: types_taxes types_taxes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.types_taxes
    ADD CONSTRAINT types_taxes_pkey PRIMARY KEY (id);


--
-- TOC entry 4121 (class 2606 OID 33554)
-- Name: unites_mesure unites_mesure_code_unite_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.unites_mesure
    ADD CONSTRAINT unites_mesure_code_unite_key UNIQUE (code_unite);


--
-- TOC entry 4123 (class 2606 OID 33552)
-- Name: unites_mesure unites_mesure_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.unites_mesure
    ADD CONSTRAINT unites_mesure_pkey PRIMARY KEY (id);


--
-- TOC entry 4192 (class 2606 OID 33992)
-- Name: utilisateurs utilisateurs_login_key; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisateurs
    ADD CONSTRAINT utilisateurs_login_key UNIQUE (login);


--
-- TOC entry 4194 (class 2606 OID 33990)
-- Name: utilisateurs utilisateurs_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisateurs
    ADD CONSTRAINT utilisateurs_pkey PRIMARY KEY (id);


--
-- TOC entry 4308 (class 2606 OID 35205)
-- Name: utilisation_depot_garantie utilisation_depot_garantie_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisation_depot_garantie
    ADD CONSTRAINT utilisation_depot_garantie_pkey PRIMARY KEY (id);


--
-- TOC entry 4352 (class 2606 OID 35707)
-- Name: validations_hierarchiques validations_hierarchiques_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.validations_hierarchiques
    ADD CONSTRAINT validations_hierarchiques_pkey PRIMARY KEY (id);


--
-- TOC entry 4266 (class 2606 OID 34685)
-- Name: ventes_details ventes_details_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_details
    ADD CONSTRAINT ventes_details_pkey PRIMARY KEY (id);


--
-- TOC entry 4264 (class 2606 OID 34653)
-- Name: ventes ventes_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes
    ADD CONSTRAINT ventes_pkey PRIMARY KEY (id);


--
-- TOC entry 4268 (class 2606 OID 34724)
-- Name: ventes_tresorerie ventes_tresorerie_pkey; Type: CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_tresorerie
    ADD CONSTRAINT ventes_tresorerie_pkey PRIMARY KEY (id);


--
-- TOC entry 4207 (class 1259 OID 36164)
-- Name: idx_auth_tokens_endpoint; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_auth_tokens_endpoint ON public.auth_tokens USING btree (type_endpoint);


--
-- TOC entry 4228 (class 1259 OID 36934)
-- Name: idx_bilan_initial_compagnie; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_bilan_initial_compagnie ON public.bilan_initial USING btree (compagnie_id);


--
-- TOC entry 4229 (class 1259 OID 36935)
-- Name: idx_bilan_initial_date; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_bilan_initial_date ON public.bilan_initial USING btree (date_bilan);


--
-- TOC entry 4230 (class 1259 OID 36936)
-- Name: idx_bilan_initial_statut; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_bilan_initial_statut ON public.bilan_initial USING btree (statut);


--
-- TOC entry 4406 (class 1259 OID 36932)
-- Name: idx_couts_logistique_initial_article; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_couts_logistique_initial_article ON public.couts_logistique_stocks_initial USING btree (article_id);


--
-- TOC entry 4407 (class 1259 OID 36933)
-- Name: idx_couts_logistique_initial_date; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_couts_logistique_initial_date ON public.couts_logistique_stocks_initial USING btree (date_cout);


--
-- TOC entry 4253 (class 1259 OID 36840)
-- Name: idx_stocks_date_initialisation; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_stocks_date_initialisation ON public.stocks USING btree (date_initialisation);


--
-- TOC entry 4254 (class 1259 OID 36839)
-- Name: idx_stocks_est_initial; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_stocks_est_initial ON public.stocks USING btree (est_initial);


--
-- TOC entry 4257 (class 1259 OID 36841)
-- Name: idx_stocks_mouvements_est_initial; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_stocks_mouvements_est_initial ON public.stocks_mouvements USING btree (est_initial);


--
-- TOC entry 4258 (class 1259 OID 36842)
-- Name: idx_stocks_mouvements_operation; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_stocks_mouvements_operation ON public.stocks_mouvements USING btree (operation_initialisation_id);


--
-- TOC entry 4395 (class 1259 OID 36184)
-- Name: idx_tentatives_acces_non_autorise_date; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_tentatives_acces_non_autorise_date ON public.tentatives_acces_non_autorise USING btree (created_at);


--
-- TOC entry 4396 (class 1259 OID 36186)
-- Name: idx_tentatives_acces_non_autorise_endpoint; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_tentatives_acces_non_autorise_endpoint ON public.tentatives_acces_non_autorise USING btree (endpoint_accesse);


--
-- TOC entry 4397 (class 1259 OID 36185)
-- Name: idx_tentatives_acces_non_autorise_utilisateur; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_tentatives_acces_non_autorise_utilisateur ON public.tentatives_acces_non_autorise USING btree (utilisateur_id);


--
-- TOC entry 4208 (class 1259 OID 36191)
-- Name: idx_tentatives_connexion_endpoint; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_tentatives_connexion_endpoint ON public.tentatives_connexion USING btree (type_endpoint);


--
-- TOC entry 4209 (class 1259 OID 36192)
-- Name: idx_tentatives_connexion_type; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_tentatives_connexion_type ON public.tentatives_connexion USING btree (type_utilisateur);


--
-- TOC entry 4190 (class 1259 OID 36161)
-- Name: idx_utilisateurs_type; Type: INDEX; Schema: public; Owner: energixdb_k3c4_user
--

CREATE INDEX idx_utilisateurs_type ON public.utilisateurs USING btree (type_utilisateur);


--
-- TOC entry 4682 (class 2620 OID 36938)
-- Name: stocks trigger_prevent_initial_stock_modification; Type: TRIGGER; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TRIGGER trigger_prevent_initial_stock_modification BEFORE UPDATE ON public.stocks FOR EACH ROW EXECUTE FUNCTION public.prevent_initial_stock_modification();


--
-- TOC entry 4684 (class 2620 OID 36940)
-- Name: bilan_initial_lignes trigger_update_bilan_initial_totals; Type: TRIGGER; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TRIGGER trigger_update_bilan_initial_totals AFTER INSERT OR DELETE OR UPDATE ON public.bilan_initial_lignes FOR EACH ROW EXECUTE FUNCTION public.update_bilan_initial_totals();


--
-- TOC entry 4681 (class 2620 OID 35835)
-- Name: dettes_fournisseurs trigger_update_fournisseur_solde; Type: TRIGGER; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TRIGGER trigger_update_fournisseur_solde AFTER INSERT OR DELETE OR UPDATE ON public.dettes_fournisseurs FOR EACH ROW EXECUTE FUNCTION public.update_fournisseur_solde();


--
-- TOC entry 4683 (class 2620 OID 35837)
-- Name: mouvements_tresorerie trigger_update_solde_tresorerie; Type: TRIGGER; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TRIGGER trigger_update_solde_tresorerie AFTER INSERT OR DELETE OR UPDATE ON public.mouvements_tresorerie FOR EACH ROW EXECUTE FUNCTION public.update_solde_tresorerie();


--
-- TOC entry 4685 (class 2620 OID 36931)
-- Name: bilan_initial_lignes trigger_update_valeur_totale_bilan_initial_lignes; Type: TRIGGER; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TRIGGER trigger_update_valeur_totale_bilan_initial_lignes BEFORE INSERT OR UPDATE ON public.bilan_initial_lignes FOR EACH ROW EXECUTE FUNCTION public.update_valeur_totale_bilan_initial_lignes();


--
-- TOC entry 4680 (class 2620 OID 36194)
-- Name: utilisateurs update_utilisateurs_updated_at; Type: TRIGGER; Schema: public; Owner: energixdb_k3c4_user
--

CREATE TRIGGER update_utilisateurs_updated_at BEFORE UPDATE ON public.utilisateurs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4476 (class 2606 OID 34388)
-- Name: achats achats_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats
    ADD CONSTRAINT achats_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4481 (class 2606 OID 34428)
-- Name: achats_details achats_details_achat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_details
    ADD CONSTRAINT achats_details_achat_id_fkey FOREIGN KEY (achat_id) REFERENCES public.achats(id) ON DELETE CASCADE;


--
-- TOC entry 4482 (class 2606 OID 34438)
-- Name: achats_details achats_details_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_details
    ADD CONSTRAINT achats_details_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE SET NULL;


--
-- TOC entry 4483 (class 2606 OID 34433)
-- Name: achats_details achats_details_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_details
    ADD CONSTRAINT achats_details_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4477 (class 2606 OID 34383)
-- Name: achats achats_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats
    ADD CONSTRAINT achats_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id) ON DELETE SET NULL;


--
-- TOC entry 4478 (class 2606 OID 34393)
-- Name: achats achats_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats
    ADD CONSTRAINT achats_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4479 (class 2606 OID 34407)
-- Name: achats_stations achats_stations_achat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_stations
    ADD CONSTRAINT achats_stations_achat_id_fkey FOREIGN KEY (achat_id) REFERENCES public.achats(id) ON DELETE CASCADE;


--
-- TOC entry 4480 (class 2606 OID 34412)
-- Name: achats_stations achats_stations_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_stations
    ADD CONSTRAINT achats_stations_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4487 (class 2606 OID 34486)
-- Name: achats_tresorerie achats_tresorerie_achat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_tresorerie
    ADD CONSTRAINT achats_tresorerie_achat_id_fkey FOREIGN KEY (achat_id) REFERENCES public.achats(id) ON DELETE CASCADE;


--
-- TOC entry 4488 (class 2606 OID 34491)
-- Name: achats_tresorerie achats_tresorerie_tresorerie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.achats_tresorerie
    ADD CONSTRAINT achats_tresorerie_tresorerie_id_fkey FOREIGN KEY (tresorerie_id) REFERENCES public.tresoreries(id) ON DELETE SET NULL;


--
-- TOC entry 4560 (class 2606 OID 35144)
-- Name: ajustements_stock ajustements_stock_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ajustements_stock
    ADD CONSTRAINT ajustements_stock_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- TOC entry 4561 (class 2606 OID 35164)
-- Name: ajustements_stock ajustements_stock_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ajustements_stock
    ADD CONSTRAINT ajustements_stock_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4562 (class 2606 OID 35149)
-- Name: ajustements_stock ajustements_stock_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ajustements_stock
    ADD CONSTRAINT ajustements_stock_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4563 (class 2606 OID 35154)
-- Name: ajustements_stock ajustements_stock_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ajustements_stock
    ADD CONSTRAINT ajustements_stock_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4564 (class 2606 OID 35159)
-- Name: ajustements_stock ajustements_stock_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ajustements_stock
    ADD CONSTRAINT ajustements_stock_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4591 (class 2606 OID 35452)
-- Name: analyse_commerciale analyse_commerciale_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.analyse_commerciale
    ADD CONSTRAINT analyse_commerciale_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4592 (class 2606 OID 35442)
-- Name: analyse_commerciale analyse_commerciale_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.analyse_commerciale
    ADD CONSTRAINT analyse_commerciale_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4593 (class 2606 OID 35447)
-- Name: analyse_commerciale analyse_commerciale_utilisateur_analyse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.analyse_commerciale
    ADD CONSTRAINT analyse_commerciale_utilisateur_analyse_id_fkey FOREIGN KEY (utilisateur_analyse_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4531 (class 2606 OID 34900)
-- Name: arrets_compte_caissier arrets_compte_caissier_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.arrets_compte_caissier
    ADD CONSTRAINT arrets_compte_caissier_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4532 (class 2606 OID 34890)
-- Name: arrets_compte_caissier arrets_compte_caissier_ticket_caisse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.arrets_compte_caissier
    ADD CONSTRAINT arrets_compte_caissier_ticket_caisse_id_fkey FOREIGN KEY (ticket_caisse_id) REFERENCES public.tickets_caisse(id);


--
-- TOC entry 4533 (class 2606 OID 34895)
-- Name: arrets_compte_caissier arrets_compte_caissier_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.arrets_compte_caissier
    ADD CONSTRAINT arrets_compte_caissier_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4428 (class 2606 OID 33910)
-- Name: articles articles_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4429 (class 2606 OID 33895)
-- Name: articles articles_famille_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_famille_id_fkey FOREIGN KEY (famille_id) REFERENCES public.familles_articles(id) ON DELETE SET NULL;


--
-- TOC entry 4430 (class 2606 OID 33900)
-- Name: articles articles_unite_principale_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_unite_principale_fkey FOREIGN KEY (unite_principale) REFERENCES public.unites_mesure(code_unite);


--
-- TOC entry 4431 (class 2606 OID 33905)
-- Name: articles articles_unite_stock_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_unite_stock_fkey FOREIGN KEY (unite_stock) REFERENCES public.unites_mesure(code_unite);


--
-- TOC entry 4589 (class 2606 OID 35428)
-- Name: assurances assurances_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.assurances
    ADD CONSTRAINT assurances_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4590 (class 2606 OID 35423)
-- Name: assurances assurances_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.assurances
    ADD CONSTRAINT assurances_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4452 (class 2606 OID 34123)
-- Name: auth_tokens auth_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT auth_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4444 (class 2606 OID 34067)
-- Name: barremage_cuves barremage_cuves_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.barremage_cuves
    ADD CONSTRAINT barremage_cuves_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4445 (class 2606 OID 34057)
-- Name: barremage_cuves barremage_cuves_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.barremage_cuves
    ADD CONSTRAINT barremage_cuves_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4446 (class 2606 OID 34062)
-- Name: barremage_cuves barremage_cuves_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.barremage_cuves
    ADD CONSTRAINT barremage_cuves_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4469 (class 2606 OID 34303)
-- Name: bilan_initial bilan_initial_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bilan_initial
    ADD CONSTRAINT bilan_initial_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4571 (class 2606 OID 35229)
-- Name: bilan_initial_lignes bilan_initial_lignes_bilan_initial_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bilan_initial_lignes
    ADD CONSTRAINT bilan_initial_lignes_bilan_initial_id_fkey FOREIGN KEY (bilan_initial_id) REFERENCES public.bilan_initial(id) ON DELETE CASCADE;


--
-- TOC entry 4470 (class 2606 OID 36916)
-- Name: bilan_initial bilan_initial_utilisateur_validation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bilan_initial
    ADD CONSTRAINT bilan_initial_utilisateur_validation_id_fkey FOREIGN KEY (utilisateur_validation_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4526 (class 2606 OID 34837)
-- Name: bons_commande bons_commande_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bons_commande
    ADD CONSTRAINT bons_commande_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4527 (class 2606 OID 34832)
-- Name: bons_commande bons_commande_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.bons_commande
    ADD CONSTRAINT bons_commande_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id) ON DELETE SET NULL;


--
-- TOC entry 4418 (class 2606 OID 33728)
-- Name: carburants carburants_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.carburants
    ADD CONSTRAINT carburants_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4606 (class 2606 OID 35593)
-- Name: cartes_carburant cartes_carburant_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cartes_carburant
    ADD CONSTRAINT cartes_carburant_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 4607 (class 2606 OID 35608)
-- Name: cartes_carburant cartes_carburant_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cartes_carburant
    ADD CONSTRAINT cartes_carburant_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4608 (class 2606 OID 35603)
-- Name: cartes_carburant cartes_carburant_utilisateur_blocage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cartes_carburant
    ADD CONSTRAINT cartes_carburant_utilisateur_blocage_id_fkey FOREIGN KEY (utilisateur_blocage_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4609 (class 2606 OID 35598)
-- Name: cartes_carburant cartes_carburant_utilisateur_creation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cartes_carburant
    ADD CONSTRAINT cartes_carburant_utilisateur_creation_id_fkey FOREIGN KEY (utilisateur_creation_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4421 (class 2606 OID 33780)
-- Name: clients clients_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4422 (class 2606 OID 33785)
-- Name: clients clients_type_tiers_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_type_tiers_id_fkey FOREIGN KEY (type_tiers_id) REFERENCES public.type_tiers(id) ON DELETE SET NULL;


--
-- TOC entry 4409 (class 2606 OID 33575)
-- Name: compagnies compagnies_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.compagnies
    ADD CONSTRAINT compagnies_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4413 (class 2606 OID 33658)
-- Name: configurations_pays configurations_pays_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.configurations_pays
    ADD CONSTRAINT configurations_pays_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4610 (class 2606 OID 35625)
-- Name: contrats_clients contrats_clients_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.contrats_clients
    ADD CONSTRAINT contrats_clients_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 4611 (class 2606 OID 35630)
-- Name: contrats_clients contrats_clients_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.contrats_clients
    ADD CONSTRAINT contrats_clients_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4600 (class 2606 OID 35532)
-- Name: contrats_maintenance contrats_maintenance_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.contrats_maintenance
    ADD CONSTRAINT contrats_maintenance_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4601 (class 2606 OID 35527)
-- Name: contrats_maintenance contrats_maintenance_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.contrats_maintenance
    ADD CONSTRAINT contrats_maintenance_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id);


--
-- TOC entry 4602 (class 2606 OID 35522)
-- Name: contrats_maintenance contrats_maintenance_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.contrats_maintenance
    ADD CONSTRAINT contrats_maintenance_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4603 (class 2606 OID 35555)
-- Name: controle_interne controle_interne_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.controle_interne
    ADD CONSTRAINT controle_interne_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4604 (class 2606 OID 35550)
-- Name: controle_interne controle_interne_utilisateur_controle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.controle_interne
    ADD CONSTRAINT controle_interne_utilisateur_controle_id_fkey FOREIGN KEY (utilisateur_controle_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4450 (class 2606 OID 34110)
-- Name: conversions_unite conversions_unite_unite_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.conversions_unite
    ADD CONSTRAINT conversions_unite_unite_destination_id_fkey FOREIGN KEY (unite_destination_id) REFERENCES public.unites_mesure(id);


--
-- TOC entry 4451 (class 2606 OID 34105)
-- Name: conversions_unite conversions_unite_unite_origine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.conversions_unite
    ADD CONSTRAINT conversions_unite_unite_origine_id_fkey FOREIGN KEY (unite_origine_id) REFERENCES public.unites_mesure(id);


--
-- TOC entry 4616 (class 2606 OID 35674)
-- Name: couts_logistique couts_logistique_carburant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique
    ADD CONSTRAINT couts_logistique_carburant_id_fkey FOREIGN KEY (carburant_id) REFERENCES public.carburants(id);


--
-- TOC entry 4617 (class 2606 OID 35694)
-- Name: couts_logistique couts_logistique_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique
    ADD CONSTRAINT couts_logistique_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4618 (class 2606 OID 35684)
-- Name: couts_logistique couts_logistique_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique
    ADD CONSTRAINT couts_logistique_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id);


--
-- TOC entry 4619 (class 2606 OID 35679)
-- Name: couts_logistique couts_logistique_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique
    ADD CONSTRAINT couts_logistique_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4674 (class 2606 OID 36882)
-- Name: couts_logistique_stocks_initial couts_logistique_stocks_initial_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique_stocks_initial
    ADD CONSTRAINT couts_logistique_stocks_initial_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id);


--
-- TOC entry 4675 (class 2606 OID 36907)
-- Name: couts_logistique_stocks_initial couts_logistique_stocks_initial_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique_stocks_initial
    ADD CONSTRAINT couts_logistique_stocks_initial_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4676 (class 2606 OID 36887)
-- Name: couts_logistique_stocks_initial couts_logistique_stocks_initial_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique_stocks_initial
    ADD CONSTRAINT couts_logistique_stocks_initial_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);


--
-- TOC entry 4677 (class 2606 OID 36897)
-- Name: couts_logistique_stocks_initial couts_logistique_stocks_initial_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique_stocks_initial
    ADD CONSTRAINT couts_logistique_stocks_initial_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id);


--
-- TOC entry 4678 (class 2606 OID 36892)
-- Name: couts_logistique_stocks_initial couts_logistique_stocks_initial_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique_stocks_initial
    ADD CONSTRAINT couts_logistique_stocks_initial_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4679 (class 2606 OID 36902)
-- Name: couts_logistique_stocks_initial couts_logistique_stocks_initial_utilisateur_saisie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique_stocks_initial
    ADD CONSTRAINT couts_logistique_stocks_initial_utilisateur_saisie_id_fkey FOREIGN KEY (utilisateur_saisie_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4620 (class 2606 OID 35689)
-- Name: couts_logistique couts_logistique_utilisateur_saisie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.couts_logistique
    ADD CONSTRAINT couts_logistique_utilisateur_saisie_id_fkey FOREIGN KEY (utilisateur_saisie_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4626 (class 2606 OID 35775)
-- Name: cuve_stocks cuve_stocks_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks
    ADD CONSTRAINT cuve_stocks_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4627 (class 2606 OID 35765)
-- Name: cuve_stocks cuve_stocks_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks
    ADD CONSTRAINT cuve_stocks_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4629 (class 2606 OID 35812)
-- Name: cuve_stocks_mouvements cuve_stocks_mouvements_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks_mouvements
    ADD CONSTRAINT cuve_stocks_mouvements_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4630 (class 2606 OID 35797)
-- Name: cuve_stocks_mouvements cuve_stocks_mouvements_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks_mouvements
    ADD CONSTRAINT cuve_stocks_mouvements_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4631 (class 2606 OID 35792)
-- Name: cuve_stocks_mouvements cuve_stocks_mouvements_cuve_stock_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks_mouvements
    ADD CONSTRAINT cuve_stocks_mouvements_cuve_stock_id_fkey FOREIGN KEY (cuve_stock_id) REFERENCES public.cuve_stocks(id) ON DELETE CASCADE;


--
-- TOC entry 4632 (class 2606 OID 35802)
-- Name: cuve_stocks_mouvements cuve_stocks_mouvements_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks_mouvements
    ADD CONSTRAINT cuve_stocks_mouvements_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4633 (class 2606 OID 35807)
-- Name: cuve_stocks_mouvements cuve_stocks_mouvements_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks_mouvements
    ADD CONSTRAINT cuve_stocks_mouvements_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4628 (class 2606 OID 35770)
-- Name: cuve_stocks cuve_stocks_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuve_stocks
    ADD CONSTRAINT cuve_stocks_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4434 (class 2606 OID 33954)
-- Name: cuves cuves_carburant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuves
    ADD CONSTRAINT cuves_carburant_id_fkey FOREIGN KEY (carburant_id) REFERENCES public.carburants(id) ON DELETE SET NULL;


--
-- TOC entry 4435 (class 2606 OID 33959)
-- Name: cuves cuves_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuves
    ADD CONSTRAINT cuves_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4436 (class 2606 OID 33949)
-- Name: cuves cuves_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.cuves
    ADD CONSTRAINT cuves_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4581 (class 2606 OID 35353)
-- Name: declarations_fiscales declarations_fiscales_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.declarations_fiscales
    ADD CONSTRAINT declarations_fiscales_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4582 (class 2606 OID 35348)
-- Name: declarations_fiscales declarations_fiscales_utilisateur_depose_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.declarations_fiscales
    ADD CONSTRAINT declarations_fiscales_utilisateur_depose_id_fkey FOREIGN KEY (utilisateur_depose_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4545 (class 2606 OID 35031)
-- Name: depenses depenses_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depenses
    ADD CONSTRAINT depenses_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4546 (class 2606 OID 35021)
-- Name: depenses depenses_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depenses
    ADD CONSTRAINT depenses_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id) ON DELETE SET NULL;


--
-- TOC entry 4547 (class 2606 OID 35016)
-- Name: depenses depenses_tresorerie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depenses
    ADD CONSTRAINT depenses_tresorerie_id_fkey FOREIGN KEY (tresorerie_id) REFERENCES public.tresoreries(id);


--
-- TOC entry 4548 (class 2606 OID 35026)
-- Name: depenses depenses_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depenses
    ADD CONSTRAINT depenses_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4565 (class 2606 OID 35181)
-- Name: depot_garantie depot_garantie_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depot_garantie
    ADD CONSTRAINT depot_garantie_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 4566 (class 2606 OID 35191)
-- Name: depot_garantie depot_garantie_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depot_garantie
    ADD CONSTRAINT depot_garantie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4567 (class 2606 OID 35186)
-- Name: depot_garantie depot_garantie_utilisateur_enregistre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.depot_garantie
    ADD CONSTRAINT depot_garantie_utilisateur_enregistre_id_fkey FOREIGN KEY (utilisateur_enregistre_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4484 (class 2606 OID 34462)
-- Name: dettes_fournisseurs dettes_fournisseurs_achat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.dettes_fournisseurs
    ADD CONSTRAINT dettes_fournisseurs_achat_id_fkey FOREIGN KEY (achat_id) REFERENCES public.achats(id);


--
-- TOC entry 4485 (class 2606 OID 34467)
-- Name: dettes_fournisseurs dettes_fournisseurs_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.dettes_fournisseurs
    ADD CONSTRAINT dettes_fournisseurs_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4486 (class 2606 OID 34457)
-- Name: dettes_fournisseurs dettes_fournisseurs_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.dettes_fournisseurs
    ADD CONSTRAINT dettes_fournisseurs_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id);


--
-- TOC entry 4471 (class 2606 OID 34322)
-- Name: ecarts_soldes ecarts_soldes_utilisateur_detecte_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ecarts_soldes
    ADD CONSTRAINT ecarts_soldes_utilisateur_detecte_id_fkey FOREIGN KEY (utilisateur_detecte_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4472 (class 2606 OID 34327)
-- Name: ecarts_soldes ecarts_soldes_utilisateur_traite_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ecarts_soldes
    ADD CONSTRAINT ecarts_soldes_utilisateur_traite_id_fkey FOREIGN KEY (utilisateur_traite_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4423 (class 2606 OID 33806)
-- Name: employes employes_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.employes
    ADD CONSTRAINT employes_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4657 (class 2606 OID 36022)
-- Name: etat_caisse etat_caisse_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_caisse
    ADD CONSTRAINT etat_caisse_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4658 (class 2606 OID 36017)
-- Name: etat_caisse etat_caisse_tresorerie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_caisse
    ADD CONSTRAINT etat_caisse_tresorerie_id_fkey FOREIGN KEY (tresorerie_id) REFERENCES public.tresoreries(id);


--
-- TOC entry 4659 (class 2606 OID 36039)
-- Name: etat_comptable etat_comptable_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_comptable
    ADD CONSTRAINT etat_comptable_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4660 (class 2606 OID 36034)
-- Name: etat_comptable etat_comptable_compte_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_comptable
    ADD CONSTRAINT etat_comptable_compte_id_fkey FOREIGN KEY (compte_id) REFERENCES public.plan_comptable(id);


--
-- TOC entry 4655 (class 2606 OID 36005)
-- Name: etat_stock etat_stock_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_stock
    ADD CONSTRAINT etat_stock_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4656 (class 2606 OID 36000)
-- Name: etat_stock etat_stock_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.etat_stock
    ADD CONSTRAINT etat_stock_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4454 (class 2606 OID 34157)
-- Name: evenements_securite evenements_securite_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.evenements_securite
    ADD CONSTRAINT evenements_securite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4455 (class 2606 OID 34152)
-- Name: evenements_securite evenements_securite_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.evenements_securite
    ADD CONSTRAINT evenements_securite_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4414 (class 2606 OID 33675)
-- Name: familles_articles familles_articles_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.familles_articles
    ADD CONSTRAINT familles_articles_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4415 (class 2606 OID 33680)
-- Name: familles_articles familles_articles_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.familles_articles
    ADD CONSTRAINT familles_articles_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.familles_articles(id);


--
-- TOC entry 4549 (class 2606 OID 35068)
-- Name: fiches_paie fiches_paie_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fiches_paie
    ADD CONSTRAINT fiches_paie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4550 (class 2606 OID 35053)
-- Name: fiches_paie fiches_paie_employe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fiches_paie
    ADD CONSTRAINT fiches_paie_employe_id_fkey FOREIGN KEY (employe_id) REFERENCES public.employes(id);


--
-- TOC entry 4551 (class 2606 OID 35058)
-- Name: fiches_paie fiches_paie_utilisateur_calcul_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fiches_paie
    ADD CONSTRAINT fiches_paie_utilisateur_calcul_id_fkey FOREIGN KEY (utilisateur_calcul_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4552 (class 2606 OID 35063)
-- Name: fiches_paie fiches_paie_utilisateur_paye_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fiches_paie
    ADD CONSTRAINT fiches_paie_utilisateur_paye_id_fkey FOREIGN KEY (utilisateur_paye_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4419 (class 2606 OID 33751)
-- Name: fournisseurs fournisseurs_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fournisseurs
    ADD CONSTRAINT fournisseurs_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4420 (class 2606 OID 33756)
-- Name: fournisseurs fournisseurs_type_tiers_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.fournisseurs
    ADD CONSTRAINT fournisseurs_type_tiers_id_fkey FOREIGN KEY (type_tiers_id) REFERENCES public.type_tiers(id) ON DELETE SET NULL;


--
-- TOC entry 4622 (class 2606 OID 35729)
-- Name: historique_actions_utilisateurs historique_actions_utilisateurs_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_actions_utilisateurs
    ADD CONSTRAINT historique_actions_utilisateurs_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4623 (class 2606 OID 35724)
-- Name: historique_actions_utilisateurs historique_actions_utilisateurs_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_actions_utilisateurs
    ADD CONSTRAINT historique_actions_utilisateurs_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4464 (class 2606 OID 34254)
-- Name: historique_index_pistolets historique_index_pistolets_pistolet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_index_pistolets
    ADD CONSTRAINT historique_index_pistolets_pistolet_id_fkey FOREIGN KEY (pistolet_id) REFERENCES public.pistolets(id);


--
-- TOC entry 4465 (class 2606 OID 34259)
-- Name: historique_index_pistolets historique_index_pistolets_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_index_pistolets
    ADD CONSTRAINT historique_index_pistolets_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4534 (class 2606 OID 34914)
-- Name: historique_paiements_clients historique_paiements_clients_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_paiements_clients
    ADD CONSTRAINT historique_paiements_clients_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 4535 (class 2606 OID 34919)
-- Name: historique_paiements_clients historique_paiements_clients_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_paiements_clients
    ADD CONSTRAINT historique_paiements_clients_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4460 (class 2606 OID 34214)
-- Name: historique_prix_articles historique_prix_articles_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_prix_articles
    ADD CONSTRAINT historique_prix_articles_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- TOC entry 4461 (class 2606 OID 34219)
-- Name: historique_prix_articles historique_prix_articles_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_prix_articles
    ADD CONSTRAINT historique_prix_articles_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4462 (class 2606 OID 34233)
-- Name: historique_prix_carburants historique_prix_carburants_carburant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_prix_carburants
    ADD CONSTRAINT historique_prix_carburants_carburant_id_fkey FOREIGN KEY (carburant_id) REFERENCES public.carburants(id) ON DELETE CASCADE;


--
-- TOC entry 4463 (class 2606 OID 34238)
-- Name: historique_prix_carburants historique_prix_carburants_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.historique_prix_carburants
    ADD CONSTRAINT historique_prix_carburants_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4553 (class 2606 OID 35104)
-- Name: immobilisations immobilisations_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4554 (class 2606 OID 35089)
-- Name: immobilisations immobilisations_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id) ON DELETE SET NULL;


--
-- TOC entry 4555 (class 2606 OID 35094)
-- Name: immobilisations immobilisations_tresorerie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_tresorerie_id_fkey FOREIGN KEY (tresorerie_id) REFERENCES public.tresoreries(id);


--
-- TOC entry 4556 (class 2606 OID 35099)
-- Name: immobilisations immobilisations_utilisateur_achat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_utilisateur_achat_id_fkey FOREIGN KEY (utilisateur_achat_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4585 (class 2606 OID 35406)
-- Name: incidents_securite incidents_securite_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.incidents_securite
    ADD CONSTRAINT incidents_securite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4586 (class 2606 OID 35391)
-- Name: incidents_securite incidents_securite_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.incidents_securite
    ADD CONSTRAINT incidents_securite_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4587 (class 2606 OID 35396)
-- Name: incidents_securite incidents_securite_utilisateur_declare_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.incidents_securite
    ADD CONSTRAINT incidents_securite_utilisateur_declare_id_fkey FOREIGN KEY (utilisateur_declare_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4588 (class 2606 OID 35401)
-- Name: incidents_securite incidents_securite_utilisateur_traite_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.incidents_securite
    ADD CONSTRAINT incidents_securite_utilisateur_traite_id_fkey FOREIGN KEY (utilisateur_traite_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4645 (class 2606 OID 35930)
-- Name: inventaire inventaire_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire
    ADD CONSTRAINT inventaire_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4663 (class 2606 OID 36071)
-- Name: inventaire_details inventaire_details_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire_details
    ADD CONSTRAINT inventaire_details_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);


--
-- TOC entry 4664 (class 2606 OID 36066)
-- Name: inventaire_details inventaire_details_inventaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire_details
    ADD CONSTRAINT inventaire_details_inventaire_id_fkey FOREIGN KEY (inventaire_id) REFERENCES public.inventaire(id);


--
-- TOC entry 4646 (class 2606 OID 35925)
-- Name: inventaire inventaire_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire
    ADD CONSTRAINT inventaire_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4647 (class 2606 OID 35920)
-- Name: inventaire inventaire_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaire
    ADD CONSTRAINT inventaire_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4536 (class 2606 OID 34948)
-- Name: inventaires inventaires_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaires
    ADD CONSTRAINT inventaires_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4537 (class 2606 OID 34938)
-- Name: inventaires inventaires_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaires
    ADD CONSTRAINT inventaires_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4538 (class 2606 OID 34943)
-- Name: inventaires inventaires_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.inventaires
    ADD CONSTRAINT inventaires_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4519 (class 2606 OID 34788)
-- Name: journal_entries journal_entries_bilan_initial_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_bilan_initial_id_fkey FOREIGN KEY (bilan_initial_id) REFERENCES public.bilan_initial(id);


--
-- TOC entry 4520 (class 2606 OID 34768)
-- Name: journal_entries journal_entries_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4521 (class 2606 OID 34778)
-- Name: journal_entries journal_entries_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4522 (class 2606 OID 34773)
-- Name: journal_entries journal_entries_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4523 (class 2606 OID 34783)
-- Name: journal_entries journal_entries_valide_par_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_valide_par_fkey FOREIGN KEY (valide_par) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4524 (class 2606 OID 34810)
-- Name: journal_lines journal_lines_compte_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_lines
    ADD CONSTRAINT journal_lines_compte_id_fkey FOREIGN KEY (compte_id) REFERENCES public.plan_comptable(id);


--
-- TOC entry 4525 (class 2606 OID 34805)
-- Name: journal_lines journal_lines_entry_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journal_lines
    ADD CONSTRAINT journal_lines_entry_id_fkey FOREIGN KEY (entry_id) REFERENCES public.journal_entries(id) ON DELETE CASCADE;


--
-- TOC entry 4654 (class 2606 OID 35988)
-- Name: journaux journaux_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.journaux
    ADD CONSTRAINT journaux_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4577 (class 2606 OID 35331)
-- Name: kpi_operations kpi_operations_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.kpi_operations
    ADD CONSTRAINT kpi_operations_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4578 (class 2606 OID 35326)
-- Name: kpi_operations kpi_operations_rendement_pompiste_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.kpi_operations
    ADD CONSTRAINT kpi_operations_rendement_pompiste_fkey FOREIGN KEY (rendement_pompiste) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4579 (class 2606 OID 35316)
-- Name: kpi_operations kpi_operations_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.kpi_operations
    ADD CONSTRAINT kpi_operations_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4580 (class 2606 OID 35321)
-- Name: kpi_operations kpi_operations_type_carburant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.kpi_operations
    ADD CONSTRAINT kpi_operations_type_carburant_fkey FOREIGN KEY (type_carburant) REFERENCES public.carburants(id);


--
-- TOC entry 4542 (class 2606 OID 34993)
-- Name: mesures_inventaire_articles mesures_inventaire_articles_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_articles
    ADD CONSTRAINT mesures_inventaire_articles_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id);


--
-- TOC entry 4543 (class 2606 OID 34988)
-- Name: mesures_inventaire_articles mesures_inventaire_articles_inventaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_articles
    ADD CONSTRAINT mesures_inventaire_articles_inventaire_id_fkey FOREIGN KEY (inventaire_id) REFERENCES public.inventaires(id) ON DELETE CASCADE;


--
-- TOC entry 4544 (class 2606 OID 34998)
-- Name: mesures_inventaire_articles mesures_inventaire_articles_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_articles
    ADD CONSTRAINT mesures_inventaire_articles_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4539 (class 2606 OID 34968)
-- Name: mesures_inventaire_cuves mesures_inventaire_cuves_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_cuves
    ADD CONSTRAINT mesures_inventaire_cuves_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);


--
-- TOC entry 4540 (class 2606 OID 34963)
-- Name: mesures_inventaire_cuves mesures_inventaire_cuves_inventaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_cuves
    ADD CONSTRAINT mesures_inventaire_cuves_inventaire_id_fkey FOREIGN KEY (inventaire_id) REFERENCES public.inventaires(id) ON DELETE CASCADE;


--
-- TOC entry 4541 (class 2606 OID 34973)
-- Name: mesures_inventaire_cuves mesures_inventaire_cuves_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_inventaire_cuves
    ADD CONSTRAINT mesures_inventaire_cuves_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4489 (class 2606 OID 34506)
-- Name: mesures_livraison mesures_livraison_achat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_livraison
    ADD CONSTRAINT mesures_livraison_achat_id_fkey FOREIGN KEY (achat_id) REFERENCES public.achats(id) ON DELETE CASCADE;


--
-- TOC entry 4490 (class 2606 OID 34511)
-- Name: mesures_livraison mesures_livraison_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_livraison
    ADD CONSTRAINT mesures_livraison_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4491 (class 2606 OID 34516)
-- Name: mesures_livraison mesures_livraison_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mesures_livraison
    ADD CONSTRAINT mesures_livraison_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4576 (class 2606 OID 35299)
-- Name: modeles_rapports modeles_rapports_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.modeles_rapports
    ADD CONSTRAINT modeles_rapports_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4456 (class 2606 OID 34179)
-- Name: modifications_sensibles modifications_sensibles_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.modifications_sensibles
    ADD CONSTRAINT modifications_sensibles_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4457 (class 2606 OID 34174)
-- Name: modifications_sensibles modifications_sensibles_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.modifications_sensibles
    ADD CONSTRAINT modifications_sensibles_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4557 (class 2606 OID 35129)
-- Name: mouvements_immobilisations mouvements_immobilisations_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_immobilisations
    ADD CONSTRAINT mouvements_immobilisations_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4558 (class 2606 OID 35119)
-- Name: mouvements_immobilisations mouvements_immobilisations_immobilisation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_immobilisations
    ADD CONSTRAINT mouvements_immobilisations_immobilisation_id_fkey FOREIGN KEY (immobilisation_id) REFERENCES public.immobilisations(id) ON DELETE CASCADE;


--
-- TOC entry 4559 (class 2606 OID 35124)
-- Name: mouvements_immobilisations mouvements_immobilisations_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_immobilisations
    ADD CONSTRAINT mouvements_immobilisations_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4639 (class 2606 OID 35891)
-- Name: mouvements_stock mouvements_stock_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 4640 (class 2606 OID 35901)
-- Name: mouvements_stock mouvements_stock_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4661 (class 2606 OID 36054)
-- Name: mouvements_stock_details mouvements_stock_details_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock_details
    ADD CONSTRAINT mouvements_stock_details_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);


--
-- TOC entry 4662 (class 2606 OID 36049)
-- Name: mouvements_stock_details mouvements_stock_details_mouvement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock_details
    ADD CONSTRAINT mouvements_stock_details_mouvement_id_fkey FOREIGN KEY (mouvement_id) REFERENCES public.mouvements_stock(id);


--
-- TOC entry 4641 (class 2606 OID 35886)
-- Name: mouvements_stock mouvements_stock_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id);


--
-- TOC entry 4642 (class 2606 OID 35906)
-- Name: mouvements_stock mouvements_stock_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4643 (class 2606 OID 35881)
-- Name: mouvements_stock mouvements_stock_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4644 (class 2606 OID 35896)
-- Name: mouvements_stock mouvements_stock_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_stock
    ADD CONSTRAINT mouvements_stock_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4503 (class 2606 OID 34628)
-- Name: mouvements_tresorerie mouvements_tresorerie_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie
    ADD CONSTRAINT mouvements_tresorerie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4652 (class 2606 OID 35974)
-- Name: mouvements_tresorerie_details mouvements_tresorerie_details_compte_comptable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie_details
    ADD CONSTRAINT mouvements_tresorerie_details_compte_comptable_id_fkey FOREIGN KEY (compte_comptable_id) REFERENCES public.plan_comptable(id);


--
-- TOC entry 4653 (class 2606 OID 35969)
-- Name: mouvements_tresorerie_details mouvements_tresorerie_details_mouvement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie_details
    ADD CONSTRAINT mouvements_tresorerie_details_mouvement_id_fkey FOREIGN KEY (mouvement_id) REFERENCES public.mouvements_tresorerie(id);


--
-- TOC entry 4504 (class 2606 OID 34623)
-- Name: mouvements_tresorerie mouvements_tresorerie_mouvement_origine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie
    ADD CONSTRAINT mouvements_tresorerie_mouvement_origine_id_fkey FOREIGN KEY (mouvement_origine_id) REFERENCES public.mouvements_tresorerie(id);


--
-- TOC entry 4505 (class 2606 OID 34613)
-- Name: mouvements_tresorerie mouvements_tresorerie_tresorerie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie
    ADD CONSTRAINT mouvements_tresorerie_tresorerie_id_fkey FOREIGN KEY (tresorerie_id) REFERENCES public.tresoreries(id);


--
-- TOC entry 4506 (class 2606 OID 34618)
-- Name: mouvements_tresorerie mouvements_tresorerie_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.mouvements_tresorerie
    ADD CONSTRAINT mouvements_tresorerie_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4572 (class 2606 OID 35249)
-- Name: periodes_comptables periodes_comptables_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.periodes_comptables
    ADD CONSTRAINT periodes_comptables_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4427 (class 2606 OID 33866)
-- Name: permissions permissions_module_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_module_id_fkey FOREIGN KEY (module_id) REFERENCES public.modules(id);


--
-- TOC entry 4517 (class 2606 OID 34748)
-- Name: permissions_tresorerie permissions_tresorerie_tresorerie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.permissions_tresorerie
    ADD CONSTRAINT permissions_tresorerie_tresorerie_id_fkey FOREIGN KEY (tresorerie_id) REFERENCES public.tresoreries(id);


--
-- TOC entry 4518 (class 2606 OID 34743)
-- Name: permissions_tresorerie permissions_tresorerie_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.permissions_tresorerie
    ADD CONSTRAINT permissions_tresorerie_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4447 (class 2606 OID 34092)
-- Name: pistolets pistolets_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pistolets
    ADD CONSTRAINT pistolets_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4448 (class 2606 OID 34087)
-- Name: pistolets pistolets_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pistolets
    ADD CONSTRAINT pistolets_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4449 (class 2606 OID 34082)
-- Name: pistolets pistolets_pompe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pistolets
    ADD CONSTRAINT pistolets_pompe_id_fkey FOREIGN KEY (pompe_id) REFERENCES public.pompes(id);


--
-- TOC entry 4416 (class 2606 OID 33704)
-- Name: plan_comptable plan_comptable_compte_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.plan_comptable
    ADD CONSTRAINT plan_comptable_compte_parent_id_fkey FOREIGN KEY (compte_parent_id) REFERENCES public.plan_comptable(id) ON DELETE SET NULL;


--
-- TOC entry 4417 (class 2606 OID 33709)
-- Name: plan_comptable plan_comptable_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.plan_comptable
    ADD CONSTRAINT plan_comptable_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4624 (class 2606 OID 35747)
-- Name: plan_comptable_pays plan_comptable_pays_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.plan_comptable_pays
    ADD CONSTRAINT plan_comptable_pays_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4625 (class 2606 OID 35742)
-- Name: plan_comptable_pays plan_comptable_pays_plan_comptable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.plan_comptable_pays
    ADD CONSTRAINT plan_comptable_pays_plan_comptable_id_fkey FOREIGN KEY (plan_comptable_id) REFERENCES public.plan_comptable(id);


--
-- TOC entry 4458 (class 2606 OID 34200)
-- Name: politiques_securite politiques_securite_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.politiques_securite
    ADD CONSTRAINT politiques_securite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4459 (class 2606 OID 34195)
-- Name: politiques_securite politiques_securite_utilisateur_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.politiques_securite
    ADD CONSTRAINT politiques_securite_utilisateur_config_id_fkey FOREIGN KEY (utilisateur_config_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4432 (class 2606 OID 33931)
-- Name: pompes pompes_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pompes
    ADD CONSTRAINT pompes_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4433 (class 2606 OID 33926)
-- Name: pompes pompes_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.pompes
    ADD CONSTRAINT pompes_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4594 (class 2606 OID 35467)
-- Name: prevision_demande prevision_demande_carburant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.prevision_demande
    ADD CONSTRAINT prevision_demande_carburant_id_fkey FOREIGN KEY (carburant_id) REFERENCES public.carburants(id);


--
-- TOC entry 4595 (class 2606 OID 35482)
-- Name: prevision_demande prevision_demande_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.prevision_demande
    ADD CONSTRAINT prevision_demande_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4596 (class 2606 OID 35472)
-- Name: prevision_demande prevision_demande_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.prevision_demande
    ADD CONSTRAINT prevision_demande_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4597 (class 2606 OID 35477)
-- Name: prevision_demande prevision_demande_utilisateur_prevision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.prevision_demande
    ADD CONSTRAINT prevision_demande_utilisateur_prevision_id_fkey FOREIGN KEY (utilisateur_prevision_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4473 (class 2606 OID 34345)
-- Name: profil_permissions profil_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.profil_permissions
    ADD CONSTRAINT profil_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- TOC entry 4474 (class 2606 OID 34340)
-- Name: profil_permissions profil_permissions_profil_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.profil_permissions
    ADD CONSTRAINT profil_permissions_profil_id_fkey FOREIGN KEY (profil_id) REFERENCES public.profils(id) ON DELETE CASCADE;


--
-- TOC entry 4426 (class 2606 OID 33850)
-- Name: profils profils_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.profils
    ADD CONSTRAINT profils_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id) ON DELETE SET NULL;


--
-- TOC entry 4605 (class 2606 OID 35573)
-- Name: programme_fidelite programme_fidelite_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.programme_fidelite
    ADD CONSTRAINT programme_fidelite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4612 (class 2606 OID 35645)
-- Name: qualite_carburant qualite_carburant_carburant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant
    ADD CONSTRAINT qualite_carburant_carburant_id_fkey FOREIGN KEY (carburant_id) REFERENCES public.carburants(id);


--
-- TOC entry 4613 (class 2606 OID 35660)
-- Name: qualite_carburant qualite_carburant_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant
    ADD CONSTRAINT qualite_carburant_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4614 (class 2606 OID 35650)
-- Name: qualite_carburant qualite_carburant_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant
    ADD CONSTRAINT qualite_carburant_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);


--
-- TOC entry 4670 (class 2606 OID 36858)
-- Name: qualite_carburant_initial qualite_carburant_initial_carburant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant_initial
    ADD CONSTRAINT qualite_carburant_initial_carburant_id_fkey FOREIGN KEY (carburant_id) REFERENCES public.carburants(id);


--
-- TOC entry 4671 (class 2606 OID 36868)
-- Name: qualite_carburant_initial qualite_carburant_initial_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant_initial
    ADD CONSTRAINT qualite_carburant_initial_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4672 (class 2606 OID 36853)
-- Name: qualite_carburant_initial qualite_carburant_initial_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant_initial
    ADD CONSTRAINT qualite_carburant_initial_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);


--
-- TOC entry 4673 (class 2606 OID 36863)
-- Name: qualite_carburant_initial qualite_carburant_initial_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant_initial
    ADD CONSTRAINT qualite_carburant_initial_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4615 (class 2606 OID 35655)
-- Name: qualite_carburant qualite_carburant_utilisateur_controle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.qualite_carburant
    ADD CONSTRAINT qualite_carburant_utilisateur_controle_id_fkey FOREIGN KEY (utilisateur_controle_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4575 (class 2606 OID 35282)
-- Name: rapports_financiers rapports_financiers_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.rapports_financiers
    ADD CONSTRAINT rapports_financiers_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4634 (class 2606 OID 35847)
-- Name: reglements reglements_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reglements
    ADD CONSTRAINT reglements_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 4635 (class 2606 OID 35862)
-- Name: reglements reglements_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reglements
    ADD CONSTRAINT reglements_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4636 (class 2606 OID 35867)
-- Name: reglements reglements_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reglements
    ADD CONSTRAINT reglements_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4637 (class 2606 OID 35857)
-- Name: reglements reglements_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reglements
    ADD CONSTRAINT reglements_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4638 (class 2606 OID 35852)
-- Name: reglements reglements_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reglements
    ADD CONSTRAINT reglements_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4466 (class 2606 OID 34276)
-- Name: reinitialisation_index_pistolets reinitialisation_index_pistolets_pistolet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reinitialisation_index_pistolets
    ADD CONSTRAINT reinitialisation_index_pistolets_pistolet_id_fkey FOREIGN KEY (pistolet_id) REFERENCES public.pistolets(id);


--
-- TOC entry 4467 (class 2606 OID 34286)
-- Name: reinitialisation_index_pistolets reinitialisation_index_pistolets_utilisateur_autorise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reinitialisation_index_pistolets
    ADD CONSTRAINT reinitialisation_index_pistolets_utilisateur_autorise_id_fkey FOREIGN KEY (utilisateur_autorise_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4468 (class 2606 OID 34281)
-- Name: reinitialisation_index_pistolets reinitialisation_index_pistolets_utilisateur_demande_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.reinitialisation_index_pistolets
    ADD CONSTRAINT reinitialisation_index_pistolets_utilisateur_demande_id_fkey FOREIGN KEY (utilisateur_demande_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4598 (class 2606 OID 35505)
-- Name: services_annexes services_annexes_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.services_annexes
    ADD CONSTRAINT services_annexes_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4599 (class 2606 OID 35500)
-- Name: services_annexes services_annexes_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.services_annexes
    ADD CONSTRAINT services_annexes_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4573 (class 2606 OID 35263)
-- Name: soldes_comptables soldes_comptables_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.soldes_comptables
    ADD CONSTRAINT soldes_comptables_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4574 (class 2606 OID 35268)
-- Name: soldes_comptables soldes_comptables_periode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.soldes_comptables
    ADD CONSTRAINT soldes_comptables_periode_id_fkey FOREIGN KEY (periode_id) REFERENCES public.periodes_comptables(id);


--
-- TOC entry 4412 (class 2606 OID 33640)
-- Name: specifications_locales specifications_locales_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.specifications_locales
    ADD CONSTRAINT specifications_locales_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4410 (class 2606 OID 33606)
-- Name: stations stations_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4411 (class 2606 OID 33611)
-- Name: stations stations_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4492 (class 2606 OID 34535)
-- Name: stocks stocks_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- TOC entry 4493 (class 2606 OID 34550)
-- Name: stocks stocks_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4494 (class 2606 OID 34540)
-- Name: stocks stocks_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4497 (class 2606 OID 34575)
-- Name: stocks_mouvements stocks_mouvements_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks_mouvements
    ADD CONSTRAINT stocks_mouvements_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- TOC entry 4498 (class 2606 OID 34595)
-- Name: stocks_mouvements stocks_mouvements_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks_mouvements
    ADD CONSTRAINT stocks_mouvements_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4499 (class 2606 OID 34580)
-- Name: stocks_mouvements stocks_mouvements_cuve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks_mouvements
    ADD CONSTRAINT stocks_mouvements_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id) ON DELETE CASCADE;


--
-- TOC entry 4500 (class 2606 OID 34585)
-- Name: stocks_mouvements stocks_mouvements_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks_mouvements
    ADD CONSTRAINT stocks_mouvements_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4501 (class 2606 OID 34570)
-- Name: stocks_mouvements stocks_mouvements_stock_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks_mouvements
    ADD CONSTRAINT stocks_mouvements_stock_id_fkey FOREIGN KEY (stock_id) REFERENCES public.stocks(id) ON DELETE CASCADE;


--
-- TOC entry 4502 (class 2606 OID 34590)
-- Name: stocks_mouvements stocks_mouvements_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks_mouvements
    ADD CONSTRAINT stocks_mouvements_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4495 (class 2606 OID 34545)
-- Name: stocks stocks_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4496 (class 2606 OID 36831)
-- Name: stocks stocks_utilisateur_initialisation_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_utilisateur_initialisation_fkey FOREIGN KEY (utilisateur_initialisation) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4583 (class 2606 OID 35373)
-- Name: suivi_conformite suivi_conformite_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.suivi_conformite
    ADD CONSTRAINT suivi_conformite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4584 (class 2606 OID 35368)
-- Name: suivi_conformite suivi_conformite_responsable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.suivi_conformite
    ADD CONSTRAINT suivi_conformite_responsable_id_fkey FOREIGN KEY (responsable_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4475 (class 2606 OID 34361)
-- Name: taux_changes taux_changes_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.taux_changes
    ADD CONSTRAINT taux_changes_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4668 (class 2606 OID 36179)
-- Name: tentatives_acces_non_autorise tentatives_acces_non_autorise_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tentatives_acces_non_autorise
    ADD CONSTRAINT tentatives_acces_non_autorise_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4669 (class 2606 OID 36174)
-- Name: tentatives_acces_non_autorise tentatives_acces_non_autorise_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tentatives_acces_non_autorise
    ADD CONSTRAINT tentatives_acces_non_autorise_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4453 (class 2606 OID 34136)
-- Name: tentatives_connexion tentatives_connexion_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tentatives_connexion
    ADD CONSTRAINT tentatives_connexion_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4528 (class 2606 OID 34865)
-- Name: tickets_caisse tickets_caisse_caissier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tickets_caisse
    ADD CONSTRAINT tickets_caisse_caissier_id_fkey FOREIGN KEY (caissier_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4529 (class 2606 OID 34870)
-- Name: tickets_caisse tickets_caisse_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tickets_caisse
    ADD CONSTRAINT tickets_caisse_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4530 (class 2606 OID 34860)
-- Name: tickets_caisse tickets_caisse_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tickets_caisse
    ADD CONSTRAINT tickets_caisse_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- TOC entry 4437 (class 2606 OID 33973)
-- Name: tranches_taxes tranches_taxes_type_taxe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tranches_taxes
    ADD CONSTRAINT tranches_taxes_type_taxe_id_fkey FOREIGN KEY (type_taxe_id) REFERENCES public.types_taxes(id);


--
-- TOC entry 4648 (class 2606 OID 35959)
-- Name: transfert_stock transfert_stock_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock
    ADD CONSTRAINT transfert_stock_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4665 (class 2606 OID 36091)
-- Name: transfert_stock_details transfert_stock_details_cuve_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock_details
    ADD CONSTRAINT transfert_stock_details_cuve_destination_id_fkey FOREIGN KEY (cuve_destination_id) REFERENCES public.cuves(id);


--
-- TOC entry 4666 (class 2606 OID 36086)
-- Name: transfert_stock_details transfert_stock_details_cuve_origine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock_details
    ADD CONSTRAINT transfert_stock_details_cuve_origine_id_fkey FOREIGN KEY (cuve_origine_id) REFERENCES public.cuves(id);


--
-- TOC entry 4667 (class 2606 OID 36081)
-- Name: transfert_stock_details transfert_stock_details_transfert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock_details
    ADD CONSTRAINT transfert_stock_details_transfert_id_fkey FOREIGN KEY (transfert_id) REFERENCES public.transfert_stock(id);


--
-- TOC entry 4649 (class 2606 OID 35954)
-- Name: transfert_stock transfert_stock_station_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock
    ADD CONSTRAINT transfert_stock_station_destination_id_fkey FOREIGN KEY (station_destination_id) REFERENCES public.stations(id);


--
-- TOC entry 4650 (class 2606 OID 35949)
-- Name: transfert_stock transfert_stock_station_origine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock
    ADD CONSTRAINT transfert_stock_station_origine_id_fkey FOREIGN KEY (station_origine_id) REFERENCES public.stations(id);


--
-- TOC entry 4651 (class 2606 OID 35944)
-- Name: transfert_stock transfert_stock_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.transfert_stock
    ADD CONSTRAINT transfert_stock_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4440 (class 2606 OID 34025)
-- Name: tresoreries tresoreries_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tresoreries
    ADD CONSTRAINT tresoreries_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4441 (class 2606 OID 34030)
-- Name: tresoreries tresoreries_fournisseur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tresoreries
    ADD CONSTRAINT tresoreries_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id) ON DELETE SET NULL;


--
-- TOC entry 4442 (class 2606 OID 34035)
-- Name: tresoreries tresoreries_type_tresorerie_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tresoreries
    ADD CONSTRAINT tresoreries_type_tresorerie_fkey FOREIGN KEY (type_tresorerie) REFERENCES public.methode_paiment(id);


--
-- TOC entry 4443 (class 2606 OID 34040)
-- Name: tresoreries tresoreries_utilisateur_dernier_rapprochement_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.tresoreries
    ADD CONSTRAINT tresoreries_utilisateur_dernier_rapprochement_fkey FOREIGN KEY (utilisateur_dernier_rapprochement) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4424 (class 2606 OID 33831)
-- Name: types_taxes types_taxes_compte_comptable_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.types_taxes
    ADD CONSTRAINT types_taxes_compte_comptable_fkey FOREIGN KEY (compte_comptable) REFERENCES public.plan_comptable(numero);


--
-- TOC entry 4425 (class 2606 OID 33826)
-- Name: types_taxes types_taxes_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.types_taxes
    ADD CONSTRAINT types_taxes_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4408 (class 2606 OID 33555)
-- Name: unites_mesure unites_mesure_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.unites_mesure
    ADD CONSTRAINT unites_mesure_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4438 (class 2606 OID 33998)
-- Name: utilisateurs utilisateurs_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisateurs
    ADD CONSTRAINT utilisateurs_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4439 (class 2606 OID 33993)
-- Name: utilisateurs utilisateurs_profil_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisateurs
    ADD CONSTRAINT utilisateurs_profil_id_fkey FOREIGN KEY (profil_id) REFERENCES public.profils(id) ON DELETE SET NULL;


--
-- TOC entry 4568 (class 2606 OID 35216)
-- Name: utilisation_depot_garantie utilisation_depot_garantie_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisation_depot_garantie
    ADD CONSTRAINT utilisation_depot_garantie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4569 (class 2606 OID 35206)
-- Name: utilisation_depot_garantie utilisation_depot_garantie_depot_garantie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisation_depot_garantie
    ADD CONSTRAINT utilisation_depot_garantie_depot_garantie_id_fkey FOREIGN KEY (depot_garantie_id) REFERENCES public.depot_garantie(id);


--
-- TOC entry 4570 (class 2606 OID 35211)
-- Name: utilisation_depot_garantie utilisation_depot_garantie_utilisateur_utilise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.utilisation_depot_garantie
    ADD CONSTRAINT utilisation_depot_garantie_utilisateur_utilise_id_fkey FOREIGN KEY (utilisateur_utilise_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4621 (class 2606 OID 35708)
-- Name: validations_hierarchiques validations_hierarchiques_profil_autorise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.validations_hierarchiques
    ADD CONSTRAINT validations_hierarchiques_profil_autorise_id_fkey FOREIGN KEY (profil_autorise_id) REFERENCES public.profils(id);


--
-- TOC entry 4507 (class 2606 OID 34654)
-- Name: ventes ventes_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes
    ADD CONSTRAINT ventes_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE SET NULL;


--
-- TOC entry 4508 (class 2606 OID 34659)
-- Name: ventes ventes_compagnie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes
    ADD CONSTRAINT ventes_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);


--
-- TOC entry 4510 (class 2606 OID 34691)
-- Name: ventes_details ventes_details_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_details
    ADD CONSTRAINT ventes_details_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE SET NULL;


--
-- TOC entry 4511 (class 2606 OID 34696)
-- Name: ventes_details ventes_details_pistolet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_details
    ADD CONSTRAINT ventes_details_pistolet_id_fkey FOREIGN KEY (pistolet_id) REFERENCES public.pistolets(id) ON DELETE SET NULL;


--
-- TOC entry 4512 (class 2606 OID 34701)
-- Name: ventes_details ventes_details_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_details
    ADD CONSTRAINT ventes_details_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id) ON DELETE CASCADE;


--
-- TOC entry 4513 (class 2606 OID 34706)
-- Name: ventes_details ventes_details_utilisateur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_details
    ADD CONSTRAINT ventes_details_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);


--
-- TOC entry 4514 (class 2606 OID 34686)
-- Name: ventes_details ventes_details_vente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_details
    ADD CONSTRAINT ventes_details_vente_id_fkey FOREIGN KEY (vente_id) REFERENCES public.ventes(id) ON DELETE CASCADE;


--
-- TOC entry 4509 (class 2606 OID 34664)
-- Name: ventes ventes_pays_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes
    ADD CONSTRAINT ventes_pays_id_fkey FOREIGN KEY (pays_id) REFERENCES public.pays(id);


--
-- TOC entry 4515 (class 2606 OID 34730)
-- Name: ventes_tresorerie ventes_tresorerie_tresorerie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_tresorerie
    ADD CONSTRAINT ventes_tresorerie_tresorerie_id_fkey FOREIGN KEY (tresorerie_id) REFERENCES public.tresoreries(id) ON DELETE SET NULL;


--
-- TOC entry 4516 (class 2606 OID 34725)
-- Name: ventes_tresorerie ventes_tresorerie_vente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: energixdb_k3c4_user
--

ALTER TABLE ONLY public.ventes_tresorerie
    ADD CONSTRAINT ventes_tresorerie_vente_id_fkey FOREIGN KEY (vente_id) REFERENCES public.ventes(id) ON DELETE CASCADE;


-- Completed on 2025-11-28 18:57:41

--
-- PostgreSQL database dump complete
--

