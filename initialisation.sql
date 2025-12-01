-- Script d'initialisation pour les tables manquantes dans la base de données
-- Ce script ne fait que créer les tables qui n'existent pas encore

-- Table pour l'analyse de la qualité du carburant initial (manquante dans la base)
CREATE TABLE IF NOT EXISTS public.qualite_carburant_initial (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cuve_id uuid,
    carburant_id uuid,
    date_analyse date NOT NULL,
    utilisateur_id uuid,
    densite numeric(8,4), -- Ex: 0.8350 kg/L
    indice_octane integer, -- Ex: 95 pour SP95
    soufre_ppm numeric(10,2), -- Partie par million
    type_additif character varying(100), -- Type d'additif utilisé
    commentaire_qualite text,
    resultat_qualite character varying(20) CHECK (resultat_qualite IN ('Conforme', 'Non conforme', 'En attente')),
    compagnie_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE public.qualite_carburant_initial OWNER TO energixdb_k3c4_user;

-- Créer les contraintes de clé étrangère pour la table qualite_carburant_initial
DO $$ 
BEGIN
    ALTER TABLE public.qualite_carburant_initial ADD CONSTRAINT qualite_carburant_initial_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.qualite_carburant_initial ADD CONSTRAINT qualite_carburant_initial_carburant_id_fkey FOREIGN KEY (carburant_id) REFERENCES public.carburants(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.qualite_carburant_initial ADD CONSTRAINT qualite_carburant_initial_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.qualite_carburant_initial ADD CONSTRAINT qualite_carburant_initial_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- Table pour l'analyse des coûts logistiques initiaux (manquante dans la base)
CREATE TABLE IF NOT EXISTS public.couts_logistique_stocks_initial (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    type_cout character varying(50) NOT NULL, -- 'transport', 'stockage', 'manutention', 'assurance', 'autres'
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

-- Créer les contraintes de clé étrangère pour la table couts_logistique_stocks_initial
DO $$ 
BEGIN
    ALTER TABLE public.couts_logistique_stocks_initial ADD CONSTRAINT couts_logistique_stocks_initial_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.couts_logistique_stocks_initial ADD CONSTRAINT couts_logistique_stocks_initial_cuve_id_fkey FOREIGN KEY (cuve_id) REFERENCES public.cuves(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.couts_logistique_stocks_initial ADD CONSTRAINT couts_logistique_stocks_initial_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.stations(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.couts_logistique_stocks_initial ADD CONSTRAINT couts_logistique_stocks_initial_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES public.fournisseurs(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.couts_logistique_stocks_initial ADD CONSTRAINT couts_logistique_stocks_initial_utilisateur_saisie_id_fkey FOREIGN KEY (utilisateur_saisie_id) REFERENCES public.utilisateurs(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE public.couts_logistique_stocks_initial ADD CONSTRAINT couts_logistique_stocks_initial_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);
    EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- Créer les index pour les nouvelles tables
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_initial_cuve ON public.qualite_carburant_initial(cuve_id);
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_initial_date ON public.qualite_carburant_initial(date_analyse);
CREATE INDEX IF NOT EXISTS idx_couts_logistique_initial_article ON public.couts_logistique_stocks_initial(article_id);
CREATE INDEX IF NOT EXISTS idx_couts_logistique_initial_date ON public.couts_logistique_stocks_initial(date_cout);
CREATE INDEX IF NOT EXISTS idx_bilan_initial_compagnie ON public.bilan_initial(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_bilan_initial_date ON public.bilan_initial(date_bilan);
CREATE INDEX IF NOT EXISTS idx_bilan_initial_statut ON public.bilan_initial(statut);

-- Index pour les stocks
CREATE INDEX IF NOT EXISTS idx_stocks_est_initial ON public.stocks(est_initial);
CREATE INDEX IF NOT EXISTS idx_stocks_date_initialisation ON public.stocks(date_initialisation);
CREATE INDEX IF NOT EXISTS idx_stocks_mouvements_est_initial ON public.stocks_mouvements(est_initial);
CREATE INDEX IF NOT EXISTS idx_stocks_mouvements_operation ON public.stocks_mouvements(operation_initialisation_id);

-- Fonction pour calculer automatiquement la valeur totale dans les lignes de bilan
CREATE OR REPLACE FUNCTION public.update_valeur_totale_bilan_initial_lignes()
RETURNS TRIGGER AS $$
BEGIN
    NEW.valeur_totale = NEW.quantite * NEW.prix_unitaire;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Créer un trigger pour recalculer automatiquement la valeur totale
CREATE TRIGGER trigger_update_valeur_totale_bilan_initial_lignes
    BEFORE INSERT OR UPDATE ON public.bilan_initial_lignes
    FOR EACH ROW EXECUTE FUNCTION public.update_valeur_totale_bilan_initial_lignes();

-- Trigger pour empêcher la modification d'un stock initialisé
CREATE OR REPLACE FUNCTION public.prevent_initial_stock_modification()
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
                capacite_cuve numeric(18,3);
            BEGIN
                SELECT capacite INTO capacite_cuve
                FROM public.cuves
                WHERE id = NEW.cuve_id;

                IF NEW.stock_theorique > capacite_cuve THEN
                    RAISE EXCEPTION 'La quantité initiale dépasse la capacité de la cuve (% litres)', capacite_cuve;
                END IF;
            END;
        END IF;

        -- Historisation automatique du mouvement initial
        INSERT INTO public.stocks_mouvements (
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
    BEFORE UPDATE ON public.stocks
    FOR EACH ROW EXECUTE FUNCTION public.prevent_initial_stock_modification();

-- Trigger pour calculer automatiquement les totaux du bilan initial
CREATE OR REPLACE FUNCTION public.update_bilan_initial_totals()
RETURNS TRIGGER AS $$
DECLARE
    total_valeur numeric(18,2);
    count_elements integer;
BEGIN
    CASE TG_OP
        WHEN 'INSERT', 'UPDATE' THEN
            -- Calculer le total et le nombre d'éléments
            SELECT
                COALESCE(SUM(valeur_totale), 0),
                COUNT(*)
            INTO total_valeur, count_elements
            FROM public.bilan_initial_lignes
            WHERE bilan_initial_id = NEW.bilan_initial_id;

        WHEN 'DELETE' THEN
            -- Récalculer après suppression
            SELECT
                COALESCE(SUM(valeur_totale), 0),
                COUNT(*)
            INTO total_valeur, count_elements
            FROM public.bilan_initial_lignes
            WHERE bilan_initial_id = OLD.bilan_initial_id;
    END CASE;

    -- Mettre à jour le bilan principal
    UPDATE public.bilan_initial
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
    AFTER INSERT OR UPDATE OR DELETE ON public.bilan_initial_lignes
    FOR EACH ROW EXECUTE FUNCTION public.update_bilan_initial_totals();