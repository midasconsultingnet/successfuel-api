# Technical Specification - Module de Gestion des Achats

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de gestion des achats permet de gérer tous les approvisionnements d'une station-service, tant pour le carburant que pour les produits de la boutique. Il couvre l'ensemble du processus d'achat : de la création de l'achat à la livraison, en passant par la validation, le paiement, et la mise à jour des stocks. Le module assure également la gestion des coûts logistiques, l'analyse de la qualité du carburant reçu, et l'évaluation des fournisseurs.

### Problème à résoudre
Sans un module dédié à la gestion des achats, les stations-service ne pourraient pas suivre efficacement leurs approvisionnements, ce qui entraînerait des difficultés à:
- Contrôler les coûts d'approvisionnement
- Suivre la qualité des produits reçus
- Gérer les dettes fournisseurs
- Effectuer des analyses de performance
- Maintenir des niveaux de stock optimaux
- Respecter les obligations comptables et fiscales
- Mettre en place des contrôles d'accès différenciés selon les types d'utilisateurs (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)

### Définition du périmètre
Le périmètre du sprint couvre:
- Gestion des achats de carburant (processus complet)
- Gestion des achats de produits de boutique
- Validation des achats
- Gestion des paiements
- Suivi de la livraison avec mesures avant/après et calcul des écarts
- Mouvements de stock automatiques
- Génération automatique des écritures comptables
- Mise à jour de la trésorerie et des dettes
- Modification/annulation des achats
- Suivi des coûts logistiques
- Analyse de la qualité du carburant reçu
- Évaluation des fournisseurs
- Contrôles d'accès selon le type d'utilisateur
- Validation hiérarchique selon le montant ou le type d'opération

## 2. User Stories & Critères d'acceptation

### US-ACH-001: En tant que gestionnaire, je veux créer un achat de carburant
**Critères d'acceptation :**
- Saisie des informations de base (fournisseur, date, numéro de bon)
- Affectation à une cuve spécifique
- Saisie des quantités et prix
- Lien avec les données de carburant
- Validation que la cuve a suffisamment de place pour la livraison
- Génération automatique d'un numéro de référence unique
- Enregistrement de l'utilisateur créateur et de la date
- Contrôles d'accès selon le type d'utilisateur (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)

### US-ACH-002: En tant que gestionnaire, je veux créer un achat de produits de boutique
**Critères d'acceptation :**
- Saisie des informations de base (fournisseur, date, numéro de bon)
- Affectation à une ou plusieurs familles de produits
- Gestion des détails de produits (référence, quantité, prix)
- Association avec les articles existants ou création de nouveaux articles
- Validation des quantités et prix
- Génération automatique d'un numéro de référence unique
- Contrôles d'accès selon le type d'utilisateur (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)

### US-ACH-003: En tant que gestionnaire, je veux valider un achat
**Critères d'acceptation :**
- L'achat doit être complètement saisi
- La validation est effectuée par un utilisateur autorisé
- Enregistrement de l'utilisateur validateur et de la date
- Changement du statut de l'achat
- L'achat validé ne peut plus être modifié mais peut être annulé
- Contrôles d'accès selon le type d'utilisateur (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)
- Validation hiérarchique selon le montant ou le type d'opération

### US-ACH-004: En tant que gestionnaire, je veux gérer le paiement d'un achat
**Critères d'acceptation :**
- Association d'un mode de paiement (espèces, chèque, virement)
- Lien avec une trésorerie spécifique
- Enregistrement du montant payé et de la date
- Suivi des paiements partiels
- Mise à jour automatique de la dette fournisseur
- Génération d'une écriture comptable

### US-ACH-005: En tant que gestionnaire, je veux gérer la livraison d'un achat
**Critères d'acceptation :**
- Enregistrement des mesures avant livraison (mesures d'index de cuve pour carburant)
- Enregistrement des mesures après livraison
- Calcul automatique de l'écart entre prévu et reçu
- Gestion des écarts acceptables (avec seuils configurables)
- Enregistrement de la date et de l'utilisateur responsable
- Validation de la qualité du carburant reçu (pour les achats de carburant)

### US-ACH-006: En tant que gestionnaire, je veux que le stock soit mis à jour automatiquement
**Critères d'acceptation :**
- Mouvement de stock créé automatiquement lors de la livraison
- Mise à jour du stock théorique
- Historique des mouvements de stock
- Lien avec l'achat origine
- Génération des écritures comptables correspondantes

### US-ACH-007: En tant que gestionnaire, je veux que les écritures comptables soient générées automatiquement
**Critères d'acceptation :**
- Génération automatique des écritures pour chaque achat
- Prise en compte des paiements et des dettes
- Respect des règles comptables en vigueur
- Lien avec les comptes appropriés
- Validation comptable des écritures générées

### US-ACH-008: En tant que gestionnaire, je veux que la trésorerie soit mise à jour
**Critères d'acceptation :**
- Débit de la trésorerie lors du paiement
- Suivi des mouvements de trésorerie par achat
- Mise à jour des soldes
- Lien avec les modes de paiement
- Historique des transactions

### US-ACH-009: En tant que gestionnaire, je veux que la dette soit mise à jour
**Critères d'acceptation :**
- Création d'une dette lors de la validation de l'achat (si paiement partiel ou différé)
- Mise à jour de la dette lors des paiements
- Suivi des dettes par fournisseur
- Alertes pour les dettes échues
- Historique des engagements de paiement

### US-ACH-010: En tant que gestionnaire, je veux pouvoir modifier ou annuler un achat
**Critères d'acceptation :**
- Possibilité de modifier un achat non validé
- Possibilité d'annuler un achat (avec motif)
- Historique des modifications/annulations
- Contrôle des permissions pour modification/annulation
- Impact sur les écritures comptables, trésorerie, dette et stocks

### US-ACH-011: En tant que gestionnaire, je veux suivre les coûts logistiques
**Critères d'acceptation :**
- Saisie des coûts liés à l'achat (transport, manutention, assurance)
- Association avec l'achat et le fournisseur
- Calcul du coût total d'approvisionnement
- Analyse comparative des coûts logistiques
- Impact sur les prix de revient

### US-ACH-012: En tant que gestionnaire, je veux analyser la qualité du carburant reçu
**Critères d'acceptation :**
- Saisie des paramètres de qualité (densité, indice d'octane, soufre, etc.)
- Analyse comparative avec les spécifications attendues
- Enregistrement des résultats d'analyse
- Validation de la conformité du carburant
- Historique des analyses qualité

### US-ACH-013: En tant que gestionnaire, je veux évaluer les fournisseurs
**Critères d'acceptation :**
- Calcul de la performance basé sur plusieurs critères
- Suivi de la qualité des livraisons
- Analyse des délais de livraison
- Évaluation de la fiabilité
- Historique des évaluations

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `fournisseurs` - données des fournisseurs
- `stations` - données des stations
- `cuves` - données des cuves
- `carburants` - données des carburants
- `articles` - données des articles de boutique
- `familles_articles` - données des familles d'articles
- `utilisateurs` - données des utilisateurs
- `tresoreries` - données des trésoreries
- `mode_paiements` - données des modes de paiement
- `comptes_comptables` - données des comptes comptables
- `ecritures_comptables` - données des écritures comptables
- `stocks` - données des stocks
- `stocks_mouvements` - données des mouvements de stock

### Nouvelles tables à créer

```sql
-- Table pour les achats
CREATE TABLE IF NOT EXISTS achats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_achat VARCHAR(50) UNIQUE NOT NULL,
    fournisseur_id UUID REFERENCES fournisseurs(id),
    station_id UUID REFERENCES stations(id),
    date_achat DATE NOT NULL,
    date_validation DATE,
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id),
    type_achat VARCHAR(20) NOT NULL CHECK (type_achat IN ('carburant', 'boutique')),
    statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'Valide', 'Livre', 'Paye', 'Annule')),
    montant_ht NUMERIC(18,2) NOT NULL,
    montant_tva NUMERIC(18,2) NOT NULL,
    montant_ttc NUMERIC(18,2) NOT NULL,
    montant_paye NUMERIC(18,2) DEFAULT 0,
    dette_restante NUMERIC(18,2) GENERATED ALWAYS AS (montant_ttc - montant_paye) STORED,
    commentaire TEXT,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_modification_id UUID REFERENCES utilisateurs(id),
    date_modification TIMESTAMPTZ,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    compagnie_id UUID REFERENCES utilisateurs(id)
);

-- Table pour les détails des achats de carburant
CREATE TABLE IF NOT EXISTS achats_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id),
    carburant_id UUID REFERENCES carburants(id),
    quantite_commandee NUMERIC(18,3) NOT NULL,
    quantite_livree NUMERIC(18,3), -- NULL jusqu'à la livraison
    prix_unitaire_ht NUMERIC(18,4) NOT NULL,
    mesure_avant_livraison NUMERIC(18,3), -- Mesure de la cuve avant livraison
    mesure_apres_livraison NUMERIC(18,3), -- Mesure de la cuve après livraison
    ecart_livraison NUMERIC(18,3) GENERATED ALWAYS AS (COALESCE(quantite_livree, 0) - COALESCE(mesure_apres_livraison, 0) + COALESCE(mesure_avant_livraison, 0)) STORED,
    seuil_ecart_acceptable NUMERIC(18,3) DEFAULT 100, -- En litres
    qualite_conforme BOOLEAN, -- NULL jusqu'à l'analyse de qualité
    date_livraison DATE,
    utilisateur_livreur_id UUID REFERENCES utilisateurs(id),
    commentaire_livraison TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les détails des achats de boutique
CREATE TABLE IF NOT EXISTS achats_boutique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id),
    quantite_commandee NUMERIC(18,3) NOT NULL,
    quantite_livree NUMERIC(18,3), -- NULL jusqu'à la livraison
    prix_unitaire_ht NUMERIC(18,4) NOT NULL,
    date_livraison DATE,
    utilisateur_livreur_id UUID REFERENCES utilisateurs(id),
    commentaire_livraison TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les paiements des achats
CREATE TABLE IF NOT EXISTS paiements_achats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id),
    mode_paiement_id UUID REFERENCES mode_paiements(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    montant_paiement NUMERIC(18,2) NOT NULL,
    date_paiement DATE NOT NULL,
    reference_paiement VARCHAR(100), -- Numéro de chèque, virement, etc.
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les analyses de qualité du carburant reçu
CREATE TABLE IF NOT EXISTS qualite_carburant_reception (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_carburant_id UUID REFERENCES achats_carburant(id),
    date_analyse DATE NOT NULL,
    utilisateur_analyste_id UUID REFERENCES utilisateurs(id),
    densite NUMERIC(8,4), -- Ex: 0.8350 kg/L
    indice_octane INTEGER, -- Ex: 95 pour SP95
    soufre_ppm NUMERIC(10,2), -- Partie par million
    type_additif VARCHAR(100), -- Type d'additif utilisé
    commentaire_qualite TEXT,
    resultat_qualite VARCHAR(20) CHECK (resultat_qualite IN ('Conforme', 'Non conforme', 'En attente')),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les coûts logistiques des achats
CREATE TABLE IF NOT EXISTS couts_logistique_achats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id),
    type_cout VARCHAR(50) NOT NULL, -- 'transport', 'stockage', 'manutention', 'assurance', 'autres'
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_cout DATE NOT NULL,
    fournisseur_id UUID REFERENCES fournisseurs(id),
    utilisateur_saisie_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'évaluation des fournisseurs
CREATE TABLE IF NOT EXISTS evaluations_fournisseurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    periode_evaluation DATE NOT NULL,
    delai_moyen_livraison INTEGER, -- En jours
    taux_livraison_conforme NUMERIC(5,2), -- Pourcentage
    qualite_moyenne NUMERIC(5,2), -- Sur 10
    score_ponctualite NUMERIC(5,2), -- Sur 10
    score_global NUMERIC(5,2) GENERATED ALWAYS AS ((taux_livraison_conforme + qualite_moyenne + score_ponctualite) / 3) STORED,
    commentaire TEXT,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les achats
CREATE INDEX IF NOT EXISTS idx_achats_fournisseur ON achats(fournisseur_id);
CREATE INDEX IF NOT EXISTS idx_achats_station ON achats(station_id);
CREATE INDEX IF NOT EXISTS idx_achats_date ON achats(date_achat);
CREATE INDEX IF NOT EXISTS idx_achats_statut ON achats(statut);
CREATE INDEX IF NOT EXISTS idx_achats_type ON achats(type_achat);

-- Index pour les achats de carburant
CREATE INDEX IF NOT EXISTS idx_achats_carburant_achat ON achats_carburant(achat_id);
CREATE INDEX IF NOT EXISTS idx_achats_carburant_cuve ON achats_carburant(cuve_id);
CREATE INDEX IF NOT EXISTS idx_achats_carburant_carburant ON achats_carburant(carburant_id);

-- Index pour les achats de boutique
CREATE INDEX IF NOT EXISTS idx_achats_boutique_achat ON achats_boutique(achat_id);
CREATE INDEX IF NOT EXISTS idx_achats_boutique_article ON achats_boutique(article_id);

-- Index pour les paiements des achats
CREATE INDEX IF NOT EXISTS idx_paiements_achats_achat ON paiements_achats(achat_id);
CREATE INDEX IF NOT EXISTS idx_paiements_achats_tresorerie ON paiements_achats(tresorerie_id);
CREATE INDEX IF NOT EXISTS idx_paiements_achats_date ON paiements_achats(date_paiement);

-- Index pour les analyses de qualité
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_reception_achat ON qualite_carburant_reception(achat_carburant_id);
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_reception_date ON qualite_carburant_reception(date_analyse);

-- Index pour les coûts logistiques
CREATE INDEX IF NOT EXISTS idx_couts_logistique_achats_achat ON couts_logistique_achats(achat_id);
CREATE INDEX IF NOT EXISTS idx_couts_logistique_achats_fournisseur ON couts_logistique_achats(fournisseur_id);

-- Index pour les évaluations des fournisseurs
CREATE INDEX IF NOT EXISTS idx_evaluations_fournisseurs_fournisseur ON evaluations_fournisseurs(fournisseur_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_fournisseurs_periode ON evaluations_fournisseurs(periode_evaluation);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour générer automatiquement le numéro d'achat
CREATE OR REPLACE FUNCTION generate_numero_achat()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : ACH-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_achat, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_achat FROM 10 FOR 3) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM achats
    WHERE SUBSTRING(numero_achat FROM 4 FOR 8) = date_str;
    
    numero := 'ACH-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    NEW.numero_achat := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_achat
    BEFORE INSERT ON achats
    FOR EACH ROW EXECUTE FUNCTION generate_numero_achat();

-- Trigger pour empêcher la modification d'un achat validé
CREATE OR REPLACE FUNCTION prevent_achat_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'un achat validé
    IF OLD.statut = 'Valide' OR OLD.statut = 'Livre' OR OLD.statut = 'Paye' THEN
        RAISE EXCEPTION 'Impossible de modifier un achat déjà validé, livré ou payé';
    END IF;

    NEW.date_modification := now();
    NEW.utilisateur_modification_id := NEW.utilisateur_createur_id; -- Doit être mis à jour avec l'utilisateur réel

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_achat_modification
    BEFORE UPDATE ON achats
    FOR EACH ROW EXECUTE FUNCTION prevent_achat_modification();

-- Trigger pour valider les mesures de livraison des cuves
CREATE OR REPLACE FUNCTION validate_mesures_cuve()
RETURNS TRIGGER AS $$
DECLARE
    capacite_cuve NUMERIC(18,3);
    stock_actuel NUMERIC(18,3);
BEGIN
    -- Vérifier les mesures de livraison pour les achats de carburant
    IF TG_TABLE_NAME = 'achats_carburant' THEN
        -- Récupérer la capacité de la cuve
        SELECT capacite INTO capacite_cuve
        FROM cuves
        WHERE id = NEW.cuve_id;

        -- Récupérer le stock actuel dans la cuve
        SELECT COALESCE(stock_theorique, 0) INTO stock_actuel
        FROM stocks
        WHERE cuve_id = NEW.cuve_id;

        -- Vérifier que la mesure après livraison ne dépasse pas la capacité
        IF NEW.mesure_apres_livraison > capacite_cuve THEN
            RAISE EXCEPTION 'La mesure après livraison dépasse la capacité de la cuve (% litres)', capacite_cuve;
        END IF;

        -- Vérifier que l'écart de livraison est dans les limites acceptables
        IF ABS(NEW.ecart_livraison) > NEW.seuil_ecart_acceptable THEN
            RAISE WARNING 'L''écart de livraison (% litres) dépasse le seuil acceptable (% litres)', 
                         NEW.ecart_livraison, NEW.seuil_ecart_acceptable;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_mesures_cuve
    BEFORE INSERT OR UPDATE ON achats_carburant
    FOR EACH ROW EXECUTE FUNCTION validate_mesures_cuve();

-- Trigger pour mettre à jour la dette restante après un paiement
CREATE OR REPLACE FUNCTION update_dette_achat()
RETURNS TRIGGER AS $$
DECLARE
    total_paiements NUMERIC(18,2);
BEGIN
    -- Calculer le total des paiements pour cet achat
    SELECT COALESCE(SUM(montant_paiement), 0)
    INTO total_paiements
    FROM paiements_achats
    WHERE achat_id = NEW.achat_id;

    -- Mettre à jour le montant payé et la dette restante dans la table des achats
    UPDATE achats
    SET 
        montant_paye = total_paiements,
        dette_restante = montant_ttc - total_paiements
    WHERE id = NEW.achat_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_dette_achat
    AFTER INSERT OR UPDATE OR DELETE ON paiements_achats
    FOR EACH ROW EXECUTE FUNCTION update_dette_achat();
```

## 4. API Backend

### 4.1 Gestion des achats de carburant

#### POST /api/achats/carburant
**Description:** Créer un nouvel achat de carburant

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "fournisseur_id": "uuid",
  "station_id": "uuid",
  "date_achat": "date (format YYYY-MM-DD)",
  "details": [
    {
      "cuve_id": "uuid",
      "carburant_id": "uuid",
      "quantite_commandee": "decimal (max 18,3)",
      "prix_unitaire_ht": "decimal (max 18,4)"
    }
  ],
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_achat": "string",
    "fournisseur_id": "uuid",
    "station_id": "uuid",
    "date_achat": "date",
    "statut": "string",
    "montant_ht": "decimal",
    "montant_tva": "decimal",
    "montant_ttc": "decimal",
    "commentaire": "string",
    "type_achat": "carburant",
    "date_creation": "datetime"
  },
  "message": "Achat de carburant créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Achat créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Fournisseur/station/cuve/carburant non trouvé
- 409: Conflit (par exemple, cuve pleine)
- 500: Erreur interne du serveur

#### PUT /api/achats/carburant/{id}
**Description:** Mettre à jour un achat de carburant

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "fournisseur_id": "uuid",
  "date_achat": "date (format YYYY-MM-DD)",
  "details": [
    {
      "id": "uuid (optionnel, pour mise à jour)",
      "cuve_id": "uuid",
      "carburant_id": "uuid",
      "quantite_commandee": "decimal (max 18,3)",
      "prix_unitaire_ht": "decimal (max 18,4)"
    }
  ],
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_achat": "string",
    "fournisseur_id": "uuid",
    "station_id": "uuid",
    "date_achat": "date",
    "statut": "string",
    "montant_ht": "decimal",
    "montant_tva": "decimal",
    "montant_ttc": "decimal",
    "commentaire": "string",
    "date_modification": "datetime"
  },
  "message": "Achat de carburant mis à jour avec succès"
}
```

**HTTP Status Codes:**
- 200: Achat mis à jour avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Achat non trouvé
- 409: Impossible de modifier un achat déjà validé
- 500: Erreur interne du serveur

#### POST /api/achats/carburant/{id}/valider
**Description:** Valider un achat de carburant

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:** Empty

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_achat": "string",
    "statut": "Valide",
    "date_validation": "date",
    "utilisateur_validateur_id": "uuid"
  },
  "message": "Achat de carburant validé avec succès"
}
```

**HTTP Status Codes:**
- 200: Achat validé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Achat non trouvé
- 409: Achat déjà validé
- 500: Erreur interne du serveur

#### POST /api/achats/carburant/{id}/livraison
**Description:** Enregistrer la livraison d'un achat de carburant

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "details_livraison": [
    {
      "detail_id": "uuid",
      "quantite_livree": "decimal (max 18,3)",
      "mesure_avant_livraison": "decimal (max 18,3)",
      "mesure_apres_livraison": "decimal (max 18,3)",
      "date_livraison": "date (format YYYY-MM-DD)",
      "commentaire_livraison": "string (optionnel)"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_achat": "string",
    "statut": "Livre",
    "date_livraison": "date"
  },
  "message": "Livraison d'achat de carburant enregistrée avec succès"
}
```

**HTTP Status Codes:**
- 200: Livraison enregistrée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Achat non trouvé
- 409: Achat non validé ou déjà livré
- 500: Erreur interne du serveur

### 4.2 Gestion des achats de boutique

#### POST /api/achats/boutique
**Description:** Créer un nouvel achat de produits de boutique

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "fournisseur_id": "uuid",
  "station_id": "uuid",
  "date_achat": "date (format YYYY-MM-DD)",
  "details": [
    {
      "article_id": "uuid",
      "quantite_commandee": "decimal (max 18,3)",
      "prix_unitaire_ht": "decimal (max 18,4)"
    }
  ],
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_achat": "string",
    "fournisseur_id": "uuid",
    "station_id": "uuid",
    "date_achat": "date",
    "statut": "string",
    "montant_ht": "decimal",
    "montant_tva": "decimal",
    "montant_ttc": "decimal",
    "commentaire": "string",
    "type_achat": "boutique",
    "date_creation": "datetime"
  },
  "message": "Achat de boutique créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Achat créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Fournisseur/station/article non trouvé
- 500: Erreur interne du serveur

#### POST /api/achats/boutique/{id}/livraison
**Description:** Enregistrer la livraison d'un achat de boutique

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "details_livraison": [
    {
      "detail_id": "uuid",
      "quantite_livree": "decimal (max 18,3)",
      "date_livraison": "date (format YYYY-MM-DD)",
      "commentaire_livraison": "string (optionnel)"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_achat": "string",
    "statut": "Livre",
    "date_livraison": "date"
  },
  "message": "Livraison d'achat de boutique enregistrée avec succès"
}
```

**HTTP Status Codes:**
- 200: Livraison enregistrée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Achat non trouvé
- 409: Achat non validé ou déjà livré
- 500: Erreur interne du serveur

### 4.3 Gestion des paiements

#### POST /api/achats/{id}/paiements
**Description:** Enregistrer un paiement pour un achat

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "mode_paiement_id": "uuid",
  "tresorerie_id": "uuid",
  "montant_paiement": "decimal (max 18,2)",
  "date_paiement": "date (format YYYY-MM-DD)",
  "reference_paiement": "string (optionnel)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "achat_id": "uuid",
    "mode_paiement_id": "uuid",
    "tresorerie_id": "uuid",
    "montant_paiement": "decimal",
    "date_paiement": "date",
    "reference_paiement": "string",
    "commentaire": "string",
    "dette_restante": "decimal"
  },
  "message": "Paiement enregistré avec succès"
}
```

**HTTP Status Codes:**
- 200: Paiement enregistré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Achat/mode_paiement/tresorerie non trouvé
- 409: Montant du paiement supérieur à la dette restante
- 500: Erreur interne du serveur

### 4.4 Analyse de la qualité du carburant

#### POST /api/achats/carburant/{id}/qualite
**Description:** Enregistrer l'analyse de la qualité du carburant reçu

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "analyses": [
    {
      "achat_carburant_detail_id": "uuid",
      "date_analyse": "date (format YYYY-MM-DD)",
      "densite": "decimal (max 8,4)",
      "indice_octane": "integer",
      "soufre_ppm": "decimal (max 10,2)",
      "type_additif": "string (max 100)",
      "commentaire_qualite": "string (optionnel)",
      "resultat_qualite": "Conforme|Non conforme|En attente"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analyses": [
      {
        "id": "uuid",
        "achat_carburant_detail_id": "uuid",
        "date_analyse": "date",
        "densite": "decimal",
        "indice_octane": "integer",
        "soufre_ppm": "decimal",
        "type_additif": "string",
        "commentaire_qualite": "string",
        "resultat_qualite": "string"
      }
    ]
  },
  "message": "Analyses de qualité enregistrées avec succès"
}
```

**HTTP Status Codes:**
- 200: Analyses enregistrées avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Détail d'achat de carburant non trouvé
- 500: Erreur interne du serveur

### 4.5 Évaluation des fournisseurs

#### POST /api/fournisseurs/{id}/evaluation
**Description:** Évaluer un fournisseur

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_evaluation": "date (format YYYY-MM-01)",
  "delai_moyen_livraison": "integer (en jours)",
  "taux_livraison_conforme": "decimal (max 5,2)",
  "qualite_moyenne": "decimal (max 5,2)",
  "score_ponctualite": "decimal (max 5,2)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "fournisseur_id": "uuid",
    "periode_evaluation": "date",
    "delai_moyen_livraison": "integer",
    "taux_livraison_conforme": "decimal",
    "qualite_moyenne": "decimal",
    "score_ponctualite": "decimal",
    "score_global": "decimal",
    "commentaire": "string"
  },
  "message": "Évaluation du fournisseur enregistrée avec succès"
}
```

**HTTP Status Codes:**
- 200: Évaluation enregistrée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Fournisseur non trouvé
- 409: Évaluation déjà existante pour cette période
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de validation des achats
1. La date d'achat ne peut être dans le futur
2. Les quantités commandées doivent être positives
3. Pour les achats de carburant, la capacité de la cuve doit permettre la livraison
4. Les prix unitaires doivent être positifs
5. Seuls les utilisateurs autorisés peuvent valider les achats

### Règles de calcul des prix
1. Le montant HT est la somme des (quantité * prix unitaire HT) pour tous les détails
2. La TVA est calculée selon les taux applicables aux articles/carburants
3. Le montant TTC est la somme du montant HT et de la TVA
4. Le prix unitaire TTC est calculé selon la formule: prix_HT * (1 + taux_TVA/100)

### Règles de gestion des livraisons
1. La livraison ne peut se faire que pour un achat validé
2. Pour les achats de carburant:
   - Les mesures avant/après livraison sont obligatoires
   - L'écart est calculé automatiquement
   - Des seuils d'écart acceptable sont configurables
3. Pour les achats de boutique, seule la quantité livrée est nécessaire
4. La date de livraison ne peut être antérieure à la date d'achat

### Règles de validation de la qualité
1. La densité du carburant doit être dans les limites spécifiées
2. L'indice d'octane doit correspondre au type de carburant
3. Le taux de soufre doit respecter les normes en vigueur
4. Les additifs doivent être conformes aux spécifications

### Règles de suivi des coûts logistiques
1. Les coûts logistiques s'ajoutent au prix d'achat pour le calcul du coût de revient
2. Les différents types de coûts sont catégorisés (transport, manutention, etc.)
3. Les coûts sont ventilés entre les différents articles/cuves de l'achat

### Règles de modification/annulation
1. Les achats en statut "Brouillon" peuvent être modifiés
2. Les achats en statut "Valide", "Livre" ou "Paye" ne peuvent être modifiés
3. Les achats peuvent être annulés avec un motif (impact sur les écritures comptables, trésorerie, dette et stocks)
4. L'annulation d'un achat livré nécessite une procédure spécifique

### Règles de calcul des évaluations fournisseurs
1. Le score global est la moyenne des scores de livraison, qualité et ponctualité
2. Les évaluations sont faites par période (généralement mensuelle)
3. Les scores sont normalisés sur 10 pour une comparaison équitable

### Impacts sur d'autres modules
1. Le module d'achat déclenche automatiquement des mises à jour dans:
   - Le module de stock (mouvements de stock)
   - Le module de trésorerie (enregistrement des paiements)
   - Le module comptable (génération des écritures)
   - Le module de reporting (indicateurs d'analyse)

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
fournisseurs ||--o{ achats
achats ||--o{ achats_carburant
achats ||--o{ achats_boutique
achats ||--o{ paiements_achats
achats_carburant ||--o{ qualite_carburant_reception
achats ||--o{ couts_logistique_achats
fournisseurs ||--o{ evaluations_fournisseurs
cuves ||--o{ achats_carburant
carburants ||--o{ achats_carburant
articles ||--o{ achats_boutique
utilisateurs ||--o{ achats (createur, validateur)
stations ||--o{ achats
```

### Diagramme de séquence pour un achat de carburant
```
Gestionnaire -> API: POST /api/achats/carburant
API -> Base de données: Créer l'achat (statut: Brouillon)
API -> Gestionnaire: Retourner l'achat créé

Gestionnaire -> API: POST /api/achats/{id}/valider
API -> Base de données: Valider l'achat (statut: Valide)
API -> Gestionnaire: Retourner l'achat validé

Gestionnaire -> API: POST /api/achats/{id}/livraison
API -> Base de données: Enregistrer les détails de livraison
API -> Base de données: Calculer les écarts
API -> API: Générer les mouvements de stock
API -> API: Générer les écritures comptables
API -> Base de données: Mettre le statut à "Livre"
API -> Gestionnaire: Retourner confirmation de livraison

Gestionnaire -> API: POST /api/achats/{id}/paiements
API -> Base de données: Enregistrer le paiement
API -> Base de données: Mettre à jour la dette
API -> API: Générer l'écriture comptable de paiement
API -> Gestionnaire: Retourner confirmation de paiement
```

## 7. Tests Requis

### Tests unitaires
1. Test de la fonction de génération automatique de numéro d'achat
2. Test des validations de données pour les différents endpoints
3. Test des calculs de montants (HT, TVA, TTC)
4. Test des calculs d'écarts de livraison
5. Test des calculs de scores d'évaluation des fournisseurs

### Tests d'intégration
1. Test complet du processus d'achat de carburant
2. Test complet du processus d'achat de boutique
3. Test de la génération automatique des écritures comptables
4. Test de la mise à jour des stocks
5. Test de la mise à jour de la trésorerie et des dettes

### Tests de charge/performance
1. Test de performance pour des centaines d'achats simultanés
2. Test de performance pour des livraisons multiples
3. Test de performance pour les calculs de qualité
4. Test de performance pour les évaluations fournisseurs
5. Test de la génération d'écritures comptables pour de grands volumes

### Jeux de données de test
1. Données d'achats valides avec différentes configurations
2. Données de fournisseurs avec différentes caractéristiques
3. Données de cuves et de carburants pour les tests de livraison
4. Données de trésoreries et de modes de paiement
5. Données de comptes comptables pour les tests d'écritures

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contraintes d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de gestion des achats (validation, livraison, paiement)
6. [ ] Implémenter la logique de validation des données
7. [ ] Créer les utilitaires de génération d'écritures comptables
8. [ ] Implémenter la mise à jour automatique des stocks
9. [ ] Créer les tests unitaires et d'intégration
10. [ ] Implémenter la gestion des erreurs et logs
11. [ ] Créer les vues frontend pour la gestion des achats (si applicable)
12. [ ] Documenter les endpoints API

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base pour la création d'achats
3. Développer les fonctionnalités de validation et de livraison
4. Implémenter la gestion des paiements
5. Créer les fonctionnalités de suivi de qualité et d'évaluation
6. Intégrer la génération automatique des écritures comptables
7. Intégrer la mise à jour des stocks et de la trésorerie
8. Créer les tests
9. Optimiser les performances
10. Documenter la solution

### Livrables attendus
1. Code source complet avec commentaires
2. Scripts de migration de base de données
3. Documentation API
4. Jeux de tests et résultats
5. Documentation technique détaillée
6. Guide d'installation et de déploiement

## 9. Risques & Points de vigilance

### Points sensibles
1. La complexité du calcul des écarts de livraison pour les cuves
2. La gestion des différentes configurations de TVA pour les articles
3. La mise à jour des stocks en temps réel lors des livraisons
4. La sécurité des données financières dans les transactions
5. La performance des calculs pour de grands volumes de données

### Risques techniques
1. Risque d'incohérence entre les mesures de cuve et la quantité livrée
2. Risque d'erreurs dans la génération des écritures comptables
3. Risque de décalage entre les données de stock théorique et physique
4. Risque de problèmes de performances avec de grands volumes
5. Risque de perte de données en cas de panne pendant les processus

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples règles de gestion
2. Risque de duplication de logique entre achats carburant et boutique
3. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
4. Besoin de maintenance continue pour les règles de validation
5. Risque de dépendance excessive à des bibliothèques tierces pour les calculs complexes