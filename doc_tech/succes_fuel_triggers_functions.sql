-- succes_fuel_triggers_functions.sql
-- Fichier contenant toutes les fonctions et triggers pour l'ERP SuccessFuel

-- Fonction pour calculer le solde disponible client
CREATE OR REPLACE FUNCTION solde_client_disponible(client_id UUID)
RETURNS NUMERIC(18,2) AS $$
DECLARE
    solde_de_base NUMERIC(18,2);
    montant_depot NUMERIC(18,2);
BEGIN
    -- Solde de base du client
    SELECT solde_comptable INTO solde_de_base
    FROM clients
    WHERE id = client_id;

    -- Montant des dépôts de garantie actifs
    SELECT COALESCE(SUM(montant), 0) INTO montant_depot
    FROM depot_garantie
    WHERE client_id = client_id AND statut = 'Actif';

    RETURN solde_de_base + montant_depot;
END;
$$ LANGUAGE plpgsql;

-- Procédure de rapprochement mensuel des soldes de tiers
CREATE OR REPLACE FUNCTION rapprochement_mensuel_tiers()
RETURNS TABLE (
    tiers_type VARCHAR(20),
    tiers_id UUID,
    tiers_nom VARCHAR(150),
    solde_fiche NUMERIC(18,2),
    solde_comptable NUMERIC(18,2),
    ecart NUMERIC(18,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        'Client'::VARCHAR as tiers_type,
        c.id as tiers_id,
        c.nom as tiers_nom,
        c.solde_comptable as solde_fiche,
        COALESCE(SUM(jl.debit - jl.credit), 0) as solde_comptable,
        c.solde_comptable - COALESCE(SUM(jl.debit - jl.credit), 0) as ecart
    FROM clients c
    LEFT JOIN journal_lines jl ON jl.compte_num IN (SELECT numero FROM plan_comptable WHERE type_compte = 'Client')
        AND jl.entry_id IN (SELECT id FROM journal_entries WHERE compagnie_id = c.compagnie_id)
    WHERE c.statut = 'Actif'
    GROUP BY c.id, c.nom, c.solde_comptable
    HAVING c.solde_comptable != COALESCE(SUM(jl.debit - jl.credit), 0)

    UNION ALL

    SELECT
        'Fournisseur'::VARCHAR as tiers_type,
        f.id as tiers_id,
        f.nom as tiers_nom,
        f.solde_comptable as solde_fiche,
        COALESCE(SUM(jl.debit - jl.credit), 0) as solde_comptable,
        f.solde_comptable - COALESCE(SUM(jl.debit - jl.credit), 0) as ecart
    FROM fournisseurs f
    LEFT JOIN journal_lines jl ON jl.compte_num IN (SELECT numero FROM plan_comptable WHERE type_compte = 'Fournisseur')
        AND jl.entry_id IN (SELECT id FROM journal_entries WHERE compagnie_id = f.compagnie_id)
    WHERE f.statut = 'Actif'
    GROUP BY f.id, f.nom, f.solde_comptable
    HAVING f.solde_comptable != COALESCE(SUM(jl.debit - jl.credit), 0);
END;
$$ LANGUAGE plpgsql;

-- Trigger pour les dettes fournisseurs
CREATE OR REPLACE FUNCTION update_fournisseur_solde()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE fournisseurs
        SET solde_comptable = solde_comptable + (NEW.montant_achat - NEW.montant_paye)
        WHERE id = NEW.fournisseur_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE fournisseurs
        SET solde_comptable = solde_comptable - (OLD.montant_achat - OLD.montant_paye)
        WHERE id = OLD.fournisseur_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_update_fournisseur_solde
    AFTER INSERT OR UPDATE OR DELETE ON dettes_fournisseurs
    FOR EACH ROW EXECUTE FUNCTION update_fournisseur_solde();

-- Fonction pour calculer le solde actuel d'une trésorerie
CREATE OR REPLACE FUNCTION calculer_solde_tresorerie(tresorerie_uuid UUID)
RETURNS NUMERIC(18,2) AS $$
DECLARE
    solde_calcule NUMERIC(18,2);
BEGIN
    SELECT COALESCE(SUM(
        CASE
            WHEN type_mouvement = 'Entree' THEN montant
            WHEN type_mouvement = 'Sortie' THEN -montant
            WHEN type_mouvement = 'Correction' THEN montant  -- Peut être positif ou négatif
            WHEN type_mouvement = 'Annulation' THEN -montant -- Annulation d'un mouvement précédent
            ELSE 0
        END
    ), 0)
    INTO solde_calcule
    FROM mouvements_tresorerie
    WHERE tresorerie_id = tresorerie_uuid
      AND statut IN ('Actif', 'Corrige') -- Exclure les mouvements annulés
      AND date_mouvement <= CURRENT_DATE; -- Pour les mouvements jusqu'à aujourd'hui

    RETURN solde_calcule;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour modifier un mouvement de trésorerie
CREATE OR REPLACE FUNCTION modifier_mouvement_tresorerie(
    mouvement_id UUID,
    nouveau_montant NUMERIC(18,2),
    utilisateur_action_id UUID,
    motif_modification TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    mouvement_original RECORD;
    difference_montant NUMERIC(18,2);
    mouvement_correction_id UUID;
BEGIN
    -- Récupérer le mouvement original
    SELECT * INTO mouvement_original
    FROM mouvements_tresorerie
    WHERE id = mouvement_id AND statut = 'Actif';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Mouvement non trouvé ou déjà annulé: %', mouvement_id;
    END IF;

    -- Calculer la différence
    difference_montant := nouveau_montant - mouvement_original.montant;

    -- Si pas de différence, pas besoin de correction
    IF difference_montant = 0 THEN
        RETURN TRUE;
    END IF;

    -- Créer un mouvement de correction
    INSERT INTO mouvements_tresorerie (
        tresorerie_id,
        type_mouvement,
        sous_type_mouvement,
        montant,
        reference_operation,
        utilisateur_id,
        commentaire,
        date_mouvement,
        mouvement_origine_id,  -- Référence au mouvement original
        statut,
        compagnie_id
    )
    VALUES (
        mouvement_original.tresorerie_id,
        'Correction',
        'Correction_' || mouvement_original.sous_type_mouvement,
        ABS(difference_montant),  -- Valeur absolue
        'CORR_' || mouvement_original.reference_operation,
        utilisateur_action_id,
        'Correction: ' || motif_modification || ' (Diff: ' || difference_montant || ')',
        CURRENT_DATE,
        mouvement_original.id,
        'Actif',
        (SELECT compagnie_id FROM utilisateurs WHERE id = utilisateur_action_id)
    )
    RETURNING id INTO mouvement_correction_id;

    -- Mettre à jour le statut du mouvement original pour indiquer qu'il a été corrigé
    UPDATE mouvements_tresorerie
    SET statut = CASE
        WHEN statut = 'Actif' THEN 'Corrige'
        ELSE statut
    END
    WHERE id = mouvement_original.id;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors de la modification du mouvement: %', SQLERRM;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour annuler une opération de trésorerie
CREATE OR REPLACE FUNCTION annuler_operation_trésorerie(
    reference_operation VARCHAR(100),
    utilisateur_action_id UUID,
    motif_annulation TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    mouvement_origine RECORD;
    mouvement_annulation_id UUID;
BEGIN
    -- Trouver le mouvement original
    SELECT * INTO mouvement_origine
    FROM mouvements_tresorerie
    WHERE reference_operation = reference_operation AND statut = 'Actif';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Aucun mouvement actif trouvé pour la référence: %', reference_operation;
    END IF;

    -- Créer un mouvement d'annulation
    INSERT INTO mouvements_tresorerie (
        tresorerie_id,
        type_mouvement,
        sous_type_mouvement,
        montant,
        reference_operation,
        utilisateur_id,
        commentaire,
        date_mouvement,
        mouvement_origine_id,
        statut,
        compagnie_id
    )
    VALUES (
        mouvement_origine.tresorerie_id,
        'Annulation',
        'Annulation_' || mouvement_origine.sous_type_mouvement,
        mouvement_origine.montant,
        'ANNULE_' || reference_operation,
        utilisateur_action_id,
        'Annulation: ' || motif_annulation,
        CURRENT_DATE,
        mouvement_origine.id,
        'Actif',
        (SELECT compagnie_id FROM utilisateurs WHERE id = utilisateur_action_id)
    )
    RETURNING id INTO mouvement_annulation_id;

    -- Mettre à jour le statut du mouvement original
    UPDATE mouvements_tresorerie
    SET statut = 'Annule'
    WHERE id = mouvement_origine.id;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors de l''annulation de l''opération: %', SQLERRM;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour le solde après chaque mouvement de trésorerie
CREATE OR REPLACE FUNCTION update_solde_tresorerie()
RETURNS TRIGGER AS $$
DECLARE
    nouveau_solde NUMERIC(18,2);
BEGIN
    -- Calculer le nouveau solde
    IF TG_OP = 'INSERT' THEN
        nouveau_solde := calculer_solde_tresorerie(NEW.tresorerie_id);
    ELSIF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
        nouveau_solde := calculer_solde_tresorerie(OLD.tresorerie_id);
    END IF;

    -- Mettre à jour le solde dans la table tresoreries
    UPDATE tresoreries
    SET solde = nouveau_solde
    WHERE id = (CASE
        WHEN TG_OP = 'INSERT' THEN NEW.tresorerie_id
        ELSE OLD.tresorerie_id
    END);

    RETURN CASE
        WHEN TG_OP = 'INSERT' THEN NEW
        WHEN TG_OP = 'UPDATE' THEN NEW
        ELSE OLD
    END;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_solde_tresorerie
    AFTER INSERT OR UPDATE OR DELETE ON mouvements_tresorerie
    FOR EACH ROW EXECUTE FUNCTION update_solde_tresorerie();