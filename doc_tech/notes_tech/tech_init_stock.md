# Technical Specification - Initialisation des stocks (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de configurer les stocks au démarrage du système SuccessFuel. Cela inclut l'initialisation des stocks de carburant dans les cuves avec les index des pistolets, ainsi que l'initialisation des stocks de produits dans la boutique. L'objectif est de permettre une prise en main rapide et correcte du système par les gestionnaires de station-service.

### Problème à résoudre
Actuellement, il n'existe pas de mécanisme permettant d'initialiser les stocks réels de la station-service dans le système informatique. Cela pose problème car :
- Les mouvements de stock ne peuvent pas être correctement suivis sans un point de départ
- Les rapports de gestion ne reflètent pas la réalité des stocks
- Les calculs de rentabilité sont biaisés
- L'historique des stocks n'est pas disponible

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des initialisations que sur les données appartenant à sa compagnie. Le **super administrateur** n'aura pas accès aux opérations d'initialisation des stocks et ne pourra effectuer que les opérations de gestion globale du système.

### Définition du périmètre
Le périmètre inclut :
- Initialisation des stocks de carburant par cuve
- Initialisation des index des pistolets
- Historisation automatique des stocks initiaux
- Analyse de la qualité du carburant initial
- Initialisation des stocks de produits boutique
- Valorisation initiale des stocks
- Analyse des coûts logistique initiaux
- Génération des écritures comptables pour l'initialisation
- Contrôle de la cohérence des données initiales

## 2. User Stories & Critères d'acceptation

### US-INIT-001: En tant que gestionnaire, je veux initialiser les stocks de carburant
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités initiales de carburant par cuve
  - Pouvoir spécifier la date d'initialisation
  - Pouvoir associer des informations sur la qualité du carburant
  - Vérifier la cohérence avec les mesures de hauteur dans la cuve
  - Générer automatiquement les écritures comptables d'ouverture
  - Conserver un historique des données initiales
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer l'initialisation
  - Les gérants de compagnie peuvent initialiser les stocks pour toutes les stations de leur compagnie

### US-INIT-002: En tant que gestionnaire, je veux initialiser les index des pistolets
- **Critères d'acceptation :**
  - Pouvoir saisir les index initiaux pour chaque pistolet
  - Associer les index aux pistolets et cuves appropriés
  - Vérifier la cohérence avec les stocks de carburant correspondants
  - Enregistrer les index comme point de départ pour les futures ventes
  - Les gérants de compagnie peuvent initialiser tous les index pour leur compagnie

### US-INIT-003: En tant que gestionnaire, je veux initialiser les stocks de produits boutique
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités initiales pour chaque produit
  - Pouvoir spécifier les prix d'achat et de vente initiaux
  - Valoriser les stocks selon la méthode appropriée
  - Générer les écritures comptables correspondantes
  - Conserver l'historique des mouvements d'initialisation
  - Les gérants de compagnie peuvent initialiser les stocks boutique pour toutes les stations de leur compagnie

### US-INIT-004: En tant que gestionnaire, je veux analyser la qualité du carburant initial
- **Critères d'acceptation :**
  - Pouvoir enregistrer les paramètres de qualité du carburant
  - Associer les analyses de qualité aux stocks de carburant
  - Suivre les spécifications techniques du carburant
  - Générer des rapports sur la qualité du stock initial
  - Les gérants de compagnie peuvent effectuer toutes les analyses de qualité pour leur compagnie

### US-INIT-005: En tant que gestionnaire, je veux contrôler la cohérence des données initiales
- **Critères d'acceptation :**
  - Vérifier la cohérence entre les différentes initialisations
  - Identifier les incohérences possibles
  - Proposer des corrections pour les anomalies détectées
  - Valider l'ensemble des données avant validation finale
  - Les gérants de compagnie peuvent contrôler la cohérence pour leur compagnie

## 3. Modèle de Données

### Tables existantes utilisées (avec éventuelles modifications)
```sql
-- Table pour les stocks (amélioration pour l'initialisation)
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS est_initial BOOLEAN DEFAULT FALSE;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS date_initialisation DATE;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS utilisateur_initialisation UUID REFERENCES utilisateurs(id);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS observation_initialisation TEXT;

-- Table pour les mouvements de stock (déjà existante mais optimisée)
-- Ajout de champs pour lier aux opérations d'initialisation
ALTER TABLE stocks_mouvements ADD COLUMN IF NOT EXISTS est_initial BOOLEAN DEFAULT FALSE;
ALTER TABLE stocks_mouvements ADD COLUMN IF NOT EXISTS operation_initialisation_id UUID;

-- Table pour l'analyse de la qualité du carburant initial
CREATE TABLE IF NOT EXISTS qualite_carburant_initial (
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
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'analyse des coûts logistiques initiaux
CREATE TABLE IF NOT EXISTS couts_logistique_stocks_initial (
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
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le bilan initial global
CREATE TABLE IF NOT EXISTS bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID REFERENCES compagnies(id),
    date_bilan DATE NOT NULL,
    commentaire TEXT,
    valeur_totale_stocks NUMERIC(18,2) DEFAULT 0,
    nombre_elements INTEGER DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'En cours', 'Termine', 'Validé')),
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    est_valide BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les lignes du bilan initial
CREATE TABLE IF NOT EXISTS bilan_initial_lignes (
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
```

### Index recommandés
```sql
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
```

### Triggers et règles d'intégrité
```sql
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
```

## 4. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès aux fonctionnalités de gestion globale du système (pays, compagnies, modules, profils, administrateurs, gérants de compagnie, plan comptable, configurations_pays, specifications_locales, paramètres système) mais PAS aux opérations d'initialisation des stocks
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations d'initialisation pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les stations concernées doivent appartenir à la même compagnie que l'utilisateur
- Les super administrateurs n'ont pas accès aux données d'initialisation des stocks des compagnies

## 5. Dépendances avec d'autres modules

### Module des structures
- Les initialisations sont liées aux cuves, pistolets, stations et produits
- Les données des structures sont utilisées pour les validations

### Module comptable
- L'initialisation génère des écritures comptables d'ouverture
- Le plan comptable est utilisé pour les écritures d'initialisation

### Module des stocks
- Les données d'initialisation deviennent le point de départ pour le suivi des stocks
- L'historique des mouvements commence à partir des données initiales

## 6. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités d'initialisation pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les écritures comptables sont générées correctement