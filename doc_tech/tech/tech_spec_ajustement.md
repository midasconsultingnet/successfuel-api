# Technical Specification - Module d'Ajustements

## 1. Contexte & Objectif du Sprint

### Description métier
Le module d'ajustements permet de gérer les corrections de stock et les réinitialisations d'index dans une station-service. Il permet de traiter les situations exceptionnelles telles que la sortie des produits périmés ou cassés de la boutique, et la réinitialisation sécurisée des index des pistolets. Le module assure également un suivi rigoureux des validations hiérarchiques et une journalisation complète des actions critiques.

### Problème à résoudre
Sans un module dédié aux ajustements, les stations-service ne pourraient pas gérer efficacement les situations exceptionnelles de stock et d'index, ce qui entraînerait:
- Des difficultés à gérer les produits périmés ou cassés
- Des problèmes de cohérence entre les index de pistolets et les stocks
- L'absence de contrôle hiérarchique sur les ajustements critiques
- Un manque de traçabilité des modifications importantes
- Des incohérences dans les rapports de stock et les analyses

### Définition du périmètre
Le périmètre du sprint couvre:
- Gestion des sorties de stock boutique (périmés, cassés)
- Analyse des causes de péremption
- Réinitialisation sécurisée des index de pistolets
- Système de validation hiérarchique
- Journalisation des actions critiques

## 2. User Stories & Critères d'acceptation

### US-AJ-001: En tant que gestionnaire, je veux gérer les sorties de stock boutique pour les produits périmés
**Critères d'acceptation :**
- Saisie des articles concernés avec quantités
- Indication de la date de péremption
- Classification de la cause de péremption
- Génération automatique d'un mouvement de stock de sortie
- Historique des sorties
- Lien avec une trésorerie pour la valorisation de la perte

### US-AJ-002: En tant que gestionnaire, je veux gérer les sorties de stock boutique pour les produits cassés
**Critères d'acceptation :**
- Saisie des articles concernés avec quantités
- Classification de la cause de casse
- Génération automatique d'un mouvement de stock de sortie
- Historique des sorties de casse
- Lien avec une trésorerie pour la valorisation de la perte

### US-AJ-003: En tant que gestionnaire, je veux analyser les causes de péremption
**Critères d'acceptation :**
- Regroupement des sorties par type de cause
- Analyse des tendances de péremption
- Identification des articles les plus concernés
- Calcul des ratios de péremption
- Représentation graphique des données
- Génération de rapports d'analyse

### US-AJ-004: En tant que gestionnaire, je veux effectuer une réinitialisation sécurisée des index de pistolets
**Critères d'acceptation :**
- Validation par un utilisateur autorisé
- Enregistrement de la date et de l'utilisateur effectuant la réinitialisation
- Saisie de l'index après réinitialisation
- Historique des réinitialisations
- Lien avec la cuve concernée
- Journalisation de l'action

### US-AJ-005: En tant que gestionnaire, je veux que les ajustements soient soumis à validation hiérarchique
**Critères d'acceptation :**
- Différents niveaux de validation selon le type et le montant
- Système de workflow de validation
- Historique des validations
- Alertes pour les validations en attente
- Journalisation des validations
- Contrôle des permissions

### US-AJ-006: En tant que gestionnaire, je veux que toutes les actions critiques soient journalisées
**Critères d'acceptation :**
- Journalisation des sorties de stock
- Journalisation des réinitialisations d'index
- Journalisation des validations
- Journalisation des modifications critiques
- Conservation des historiques
- Accès sécurisé aux journaux

### US-AJ-007: En tant que gestionnaire, je veux générer des rapports sur les ajustements
**Critères d'acceptation :**
- Rapport des sorties de stock avec motifs
- Rapport des réinitialisations d'index
- Rapport des validations effectuées
- Export des rapports
- Filtrage par période, station, utilisateur
- Représentation graphique

### US-AJ-008: En tant que gestionnaire, je veux contrôler les seuils d'ajustement
**Critères d'acceptation :**
- Définition de seuils pour les sorties de stock
- Définition de seuils pour les réinitialisations
- Alertes automatiques pour les ajustements importants
- Processus de validation renforcé au-delà des seuils
- Configuration par station

### US-AJ-009: En tant que gestionnaire, je veux que les ajustements affectent les écritures comptables
**Critères d'acceptation :**
- Génération automatique des écritures comptables
- Lien avec les comptes appropriés
- Validation comptable des ajustements
- Intégration avec les modules financiers
- Suivi des coûts

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `utilisateurs` - données des utilisateurs effectuant les ajustements
- `articles` - données des articles de boutique
- `pistolets` - données des pistolets
- `cuves` - données des cuves
- `stations` - données des stations
- `stocks` - données des stocks
- `stocks_mouvements` - données des mouvements de stock
- `ecritures_comptables` - données des écritures comptables
- `tresoreries` - données des trésoreries
- `comptes_comptables` - données des comptes comptables
- `causes_ajustements` - causes d'ajustement (à créer)

### Nouvelles tables à créer

```sql
-- Table pour les causes d'ajustement
CREATE TABLE IF NOT EXISTS causes_ajustements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_cause VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    type_cause VARCHAR(50) NOT NULL, -- 'peremption', 'casse', 'erreur_reception', 'erreur_vente', 'reinitialisation_index', etc.
    description TEXT,
    est_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les ajustements de stock boutique
CREATE TABLE IF NOT EXISTS ajustements_stock_boutique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_ajustement VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id),
    type_ajustement VARCHAR(20) NOT NULL CHECK (type_ajustement IN ('peremption', 'casse', 'autre')), -- Type d'ajustement
    date_ajustement DATE NOT NULL,
    date_validation DATE,
    statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'EnAttente', 'Valide', 'Rejete')),
    commentaire TEXT,
    utilisateur_modification_id UUID REFERENCES utilisateurs(id),
    date_modification TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les détails des ajustements de stock boutique
CREATE TABLE IF NOT EXISTS details_ajustements_stock_boutique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ajustement_id UUID REFERENCES ajustements_stock_boutique(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id),
    quantite_ajustee NUMERIC(18,3) NOT NULL, -- Quantité à retirer
    prix_unitaire NUMERIC(18,4) NOT NULL, -- Prix à la date de l'ajustement
    montant_total NUMERIC(18,2) GENERATED ALWAYS AS (quantite_ajustee * prix_unitaire) STORED,
    cause_ajustement_id UUID REFERENCES causes_ajustements(id),
    date_peremption DATE, -- Pour les produits périmés
    commentaire_detail TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les réinitialisations d'index de pistolets
CREATE TABLE IF NOT EXISTS reinitialisations_index_pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_reinit VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    pistolet_id UUID REFERENCES pistolets(id),
    cuve_id UUID REFERENCES cuves(id),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id),
    date_reinitialisation DATE NOT NULL,
    heure_reinitialisation TIME NOT NULL,
    index_avant_reinit NUMERIC(18,3) NOT NULL, -- Index avant la réinitialisation
    index_apres_reinit NUMERIC(18,3) NOT NULL, -- Index après la réinitialisation
    ecart_index NUMERIC(18,3) GENERATED ALWAYS AS (index_avant_reinit - index_apres_reinit) STORED, -- Écart de la réinitialisation
    date_validation DATE,
    statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'EnAttente', 'Valide', 'Rejete')),
    motif_reinitialisation TEXT,
    utilisateur_modification_id UUID REFERENCES utilisateurs(id),
    date_modification TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les validations hiérarchiques
CREATE TABLE IF NOT EXISTS validations_hierarchiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objet_type VARCHAR(50) NOT NULL, -- 'ajustement_stock', 'reinit_index', etc.
    objet_id UUID NOT NULL, -- ID de l'objet à valider
    niveau_validation INTEGER NOT NULL, -- Niveau de validation (1, 2, 3, etc.)
    utilisateur_responsable_id UUID REFERENCES utilisateurs(id), -- Utilisateur responsable de la validation
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a effectué la validation
    date_validation DATE,
    statut_validation VARCHAR(20) DEFAULT 'EnAttente' CHECK (statut_validation IN ('EnAttente', 'Accepte', 'Rejete')),
    commentaire_validation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les seuils d'ajustement
CREATE TABLE IF NOT EXISTS seuils_ajustements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_ajustement VARCHAR(50) NOT NULL, -- 'ajustement_stock', 'reinit_index', etc.
    seuil_minimal NUMERIC(18,2), -- Montant minimal pour déclencher une validation
    seuil_maximal NUMERIC(18,2), -- Montant maximal autorisé sans validation renforcée
    niveau_validation_requis INTEGER DEFAULT 1, -- Niveau de validation requis
    station_id UUID REFERENCES stations(id), -- NULL pour s'appliquer à toutes les stations
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour la journalisation des actions critiques
CREATE TABLE IF NOT EXISTS journaux_actions_critiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_action VARCHAR(50) NOT NULL, -- 'ajustement_stock', 'reinit_index', 'validation', etc.
    objet_type VARCHAR(50), -- Type de l'objet concerné
    objet_id UUID, -- ID de l'objet concerné
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    donnees_avant JSONB, -- État avant l'action
    donnees_apres JSONB, -- État après l'action
    commentaire TEXT,
    statut VARCHAR(20) DEFAULT 'Enregistre' CHECK (statut IN ('Enregistre', 'Enquete', 'Traite', 'Ferme')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les ajustements de stock boutique
CREATE INDEX IF NOT EXISTS idx_ajustements_stock_station ON ajustements_stock_boutique(station_id);
CREATE INDEX IF NOT EXISTS idx_ajustements_stock_date ON ajustements_stock_boutique(date_ajustement);
CREATE INDEX IF NOT EXISTS idx_ajustements_stock_statut ON ajustements_stock_boutique(statut);
CREATE INDEX IF NOT EXISTS idx_ajustements_stock_createur ON ajustements_stock_boutique(utilisateur_createur_id);
CREATE INDEX IF NOT EXISTS idx_ajustements_stock_validateur ON ajustements_stock_boutique(utilisateur_validateur_id);

-- Index pour les détails des ajustements
CREATE INDEX IF NOT EXISTS idx_details_ajustements_ajustement ON details_ajustements_stock_boutique(ajustement_id);
CREATE INDEX IF NOT EXISTS idx_details_ajustements_article ON details_ajustements_stock_boutique(article_id);
CREATE INDEX IF NOT EXISTS idx_details_ajustements_cause ON details_ajustements_stock_boutique(cause_ajustement_id);

-- Index pour les réinitialisations d'index
CREATE INDEX IF NOT EXISTS idx_reinit_index_station ON reinitialisations_index_pistolets(station_id);
CREATE INDEX IF NOT EXISTS idx_reinit_index_pistolet ON reinitialisations_index_pistolets(pistolet_id);
CREATE INDEX IF NOT EXISTS idx_reinit_index_date ON reinitialisations_index_pistolets(date_reinitialisation);
CREATE INDEX IF NOT EXISTS idx_reinit_index_statut ON reinitialisations_index_pistolets(statut);

-- Index pour les validations hiérarchiques
CREATE INDEX IF NOT EXISTS idx_validations_objet ON validations_hierarchiques(objet_id);
CREATE INDEX IF NOT EXISTS idx_validations_responsable ON validations_hierarchiques(utilisateur_responsable_id);
CREATE INDEX IF NOT EXISTS idx_validations_validateur ON validations_hierarchiques(utilisateur_validateur_id);
CREATE INDEX IF NOT EXISTS idx_validations_statut ON validations_hierarchiques(statut_validation);

-- Index pour les seuils d'ajustements
CREATE INDEX IF NOT EXISTS idx_seuils_type ON seuils_ajustements(type_ajustement);
CREATE INDEX IF NOT EXISTS idx_seuils_station ON seuils_ajustements(station_id);

-- Index pour les journaux d'actions critiques
CREATE INDEX IF NOT EXISTS idx_journaux_objet ON journaux_actions_critiques(objet_id);
CREATE INDEX IF NOT EXISTS idx_journaux_utilisateur ON journaux_actions_critiques(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_journaux_station ON journaux_actions_critiques(station_id);
CREATE INDEX IF NOT EXISTS idx_journaux_type ON journaux_actions_critiques(type_action);
CREATE INDEX IF NOT EXISTS idx_journaux_date ON journaux_actions_critiques(created_at);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour générer automatiquement le numéro d'ajustement
CREATE OR REPLACE FUNCTION generate_numero_ajustement()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : AJST-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_ajustement, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_ajustement FROM 6 FOR 8) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM ajustements_stock_boutique
    WHERE SUBSTRING(numero_ajustement FROM 6 FOR 8) = date_str;
    
    numero := 'AJST-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    NEW.numero_ajustement := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_ajustement
    BEFORE INSERT ON ajustements_stock_boutique
    FOR EACH ROW EXECUTE FUNCTION generate_numero_ajustement();

-- Trigger pour générer automatiquement le numéro de réinitialisation
CREATE OR REPLACE FUNCTION generate_numero_reinit()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : RINIT-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_reinitialisation, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_reinit FROM 7 FOR 8) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM reinitialisations_index_pistolets
    WHERE SUBSTRING(numero_reinit FROM 7 FOR 8) = date_str;
    
    numero := 'RINIT-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    NEW.numero_reinit := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_reinit
    BEFORE INSERT ON reinitialisations_index_pistolets
    FOR EACH ROW EXECUTE FUNCTION generate_numero_reinit();

-- Trigger pour empêcher la modification d'un ajustement validé
CREATE OR REPLACE FUNCTION prevent_ajustement_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'un ajustement validé ou rejeté
    IF OLD.statut = 'Valide' OR OLD.statut = 'Rejete' THEN
        RAISE EXCEPTION 'Impossible de modifier un ajustement déjà validé ou rejeté';
    END IF;

    NEW.updated_at := now();
    NEW.utilisateur_modification_id := NEW.utilisateur_createur_id; -- Devrait être mis à jour avec l'utilisateur réel

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_ajustement_modification
    BEFORE UPDATE ON ajustements_stock_boutique
    FOR EACH ROW EXECUTE FUNCTION prevent_ajustement_modification();

-- Trigger pour empêcher la modification d'une réinitialisation validée
CREATE OR REPLACE FUNCTION prevent_reinit_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'une réinitialisation validée ou rejetée
    IF OLD.statut = 'Valide' OR OLD.statut = 'Rejete' THEN
        RAISE EXCEPTION 'Impossible de modifier une réinitialisation déjà validée ou rejetée';
    END IF;

    NEW.updated_at := now();
    NEW.utilisateur_modification_id := NEW.utilisateur_createur_id; -- Devrait être mis à jour avec l'utilisateur réel

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_reinit_modification
    BEFORE UPDATE ON reinitialisations_index_pistolets
    FOR EACH ROW EXECUTE FUNCTION prevent_reinit_modification();

-- Trigger pour créer automatiquement un mouvement de stock lors d'un ajustement
CREATE OR REPLACE FUNCTION create_stock_movement_from_ajustement()
RETURNS TRIGGER AS $$
DECLARE
    detail RECORD;
BEGIN
    -- Créer un mouvement de stock pour chaque détail de l'ajustement
    FOR detail IN SELECT * FROM details_ajustements_stock_boutique WHERE ajustement_id = NEW.id
    LOOP
        INSERT INTO stocks_mouvements (
            stock_id, -- Devra être mis à jour avec le stock correspondant
            article_id,
            cuve_id,
            station_id,
            type_mouvement,
            quantite,
            prix_unitaire,
            date_mouvement,
            reference_operation,
            utilisateur_id,
            commentaire,
            compagnie_id
        )
        SELECT 
            s.id, -- ID du stock correspondant
            detail.article_id,
            NULL, -- Pas de cuve pour les articles de boutique
            NEW.station_id,
            'SortieAjustement', -- Type de mouvement spécifique
            -detail.quantite_ajustee, -- Quantité négative pour une sortie
            detail.prix_unitaire,
            NEW.date_ajustement,
            NEW.numero_ajustement,
            NEW.utilisateur_createur_id,
            'Ajustement de stock: ' || detail.commentaire_detail,
            NEW.utilisateur_createur_id -- Devra être mis à jour avec la compagnie réelle
        FROM stocks s
        WHERE s.article_id = detail.article_id AND s.station_id = NEW.station_id;
    END LOOP;

    -- Mettre à jour le stock théorique
    FOR detail IN SELECT * FROM details_ajustements_stock_boutique WHERE ajustement_id = NEW.id
    LOOP
        UPDATE stocks
        SET stock_theorique = stock_theorique - detail.quantite_ajustee
        WHERE article_id = detail.article_id AND station_id = NEW.station_id;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_stock_movement_from_ajustement
    AFTER UPDATE OF statut ON ajustements_stock_boutique
    FOR EACH ROW
    WHEN (NEW.statut = 'Valide')
    EXECUTE FUNCTION create_stock_movement_from_ajustement();
```

## 4. API Backend

### 4.1 Gestion des ajustements de stock boutique

#### POST /api/ajustements/stock-boutique
**Description:** Créer un nouvel ajustement de stock boutique

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "station_id": "uuid",
  "type_ajustement": "peremption|casse|autre",
  "date_ajustement": "date (format YYYY-MM-DD)",
  "commentaire": "string (optionnel)",
  "details": [
    {
      "article_id": "uuid",
      "quantite_ajustee": "decimal (max 18,3)",
      "prix_unitaire": "decimal (max 18,4)",
      "cause_ajustement_id": "uuid",
      "date_peremption": "date (format YYYY-MM-DD) (optionnel)",
      "commentaire_detail": "string (optionnel)"
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
    "numero_ajustement": "string",
    "station_id": "uuid",
    "type_ajustement": "string",
    "date_ajustement": "date",
    "statut": "string",
    "commentaire": "string",
    "utilisateur_createur_id": "uuid",
    "details": [
      {
        "id": "uuid",
        "article_id": "uuid",
        "quantite_ajustee": "decimal",
        "prix_unitaire": "decimal",
        "montant_total": "decimal",
        "cause_ajustement_id": "uuid",
        "date_peremption": "date",
        "commentaire_detail": "string"
      }
    ],
    "created_at": "datetime"
  },
  "message": "Ajustement de stock boutique créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Ajustement créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station/article/cause non trouvé
- 409: Quantité à ajuster supérieure au stock disponible
- 500: Erreur interne du serveur

#### POST /api/ajustements/stock-boutique/{id}/valider
**Description:** Valider un ajustement de stock boutique

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
    "numero_ajustement": "string",
    "statut": "Valide",
    "utilisateur_validateur_id": "uuid",
    "date_validation": "date"
  },
  "message": "Ajustement de stock boutique validé avec succès"
}
```

**HTTP Status Codes:**
- 200: Ajustement validé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé (permissions de validation requises)
- 404: Ajustement non trouvé
- 409: Ajustement déjà validé ou rejeté
- 500: Erreur interne du serveur

### 4.2 Gestion des réinitialisations d'index

#### POST /api/ajustements/reinitialisations-index
**Description:** Créer une réinitialisation d'index de pistolet

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "station_id": "uuid",
  "pistolet_id": "uuid",
  "cuve_id": "uuid",
  "date_reinitialisation": "date (format YYYY-MM-DD)",
  "heure_reinitialisation": "time (format HH:MM:SS)",
  "index_avant_reinit": "decimal (max 18,3)",
  "index_apres_reinit": "decimal (max 18,3)",
  "motif_reinitialisation": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_reinit": "string",
    "station_id": "uuid",
    "pistolet_id": "uuid",
    "cuve_id": "uuid",
    "date_reinitialisation": "date",
    "heure_reinitialisation": "time",
    "index_avant_reinit": "decimal",
    "index_apres_reinit": "decimal",
    "ecart_index": "decimal",
    "statut": "string",
    "motif_reinitialisation": "text",
    "utilisateur_createur_id": "uuid",
    "created_at": "datetime"
  },
  "message": "Réinitialisation d'index créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Réinitialisation créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station/pistolet/cuve non trouvé
- 409: Index avant inférieur à l'index après
- 500: Erreur interne du serveur

#### POST /api/ajustements/reinitialisations-index/{id}/valider
**Description:** Valider une réinitialisation d'index

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
    "numero_reinit": "string",
    "statut": "Valide",
    "utilisateur_validateur_id": "uuid",
    "date_validation": "date"
  },
  "message": "Réinitialisation d'index validée avec succès"
}
```

**HTTP Status Codes:**
- 200: Réinitialisation validée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé (permissions de validation requises)
- 404: Réinitialisation non trouvée
- 409: Réinitialisation déjà validée ou rejetée
- 500: Erreur interne du serveur

### 4.3 Analyses et rapports

#### GET /api/ajustements/analyses-peremption
**Description:** Obtenir l'analyse des causes de péremption

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- station_id: uuid (optionnel)
- periode_debut: date (format YYYY-MM-DD) (optionnel)
- periode_fin: date (format YYYY-MM-DD) (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "analyses": [
      {
        "id": "uuid",
        "cause_peremption": "string",
        "nombre_occurrences": "integer",
        "quantite_totale_perimee": "decimal",
        "valeur_totale_perimee": "decimal",
        "taux_peremption": "decimal"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Analyses de péremption récupérées avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de gestion des ajustements de stock
1. Les ajustements doivent être justifiés par une cause spécifique
2. Les ajustements peuvent nécessiter des validations selon le type et le montant
3. Les ajustements validés créent automatiquement des mouvements de stock
4. Les ajustements affectent le stock théorique et peuvent générer des écritures comptables
5. Les seuils de validation peuvent être configurés par type d'ajustement

### Règles de gestion des réinitialisations d'index
1. Les réinitialisations doivent être effectuées dans un ordre logique (index avant > index après)
2. Les réinitialisations doivent être validées par un utilisateur autorisé
3. Les réinitialisations sont journalisées pour traçabilité
4. Les écarts d'index sont calculés automatiquement
5. Les réinitialisations doivent être liées à un pistolet et une cuve spécifiques

### Règles de validation hiérarchique
1. Les validations sont organisées par niveaux de responsabilité
2. Les seuils de validation sont configurables
3. Les validations sont traitées selon un workflow défini
4. Les validations partielles sont possibles avant validation finale
5. Les validations sont historisées pour audit

### Règles de journalisation
1. Toutes les actions critiques sont journalisées
2. Les journaux contiennent les états avant et après modification
3. Les journaux sont protégés contre la modification
4. Les journaux sont consultables selon différents filtres
5. Les journaux sont conservés selon une politique de rétention

### Règles de calcul
1. Le montant total d'un ajustement est calculé comme quantité × prix unitaire
2. Les taux de péremption sont calculés comme (quantité ajustée / quantité totale) × 100
3. Les écarts d'index sont calculés comme (index avant - index après)
4. Les validations sont affectées automatiquement selon les seuils configurés
5. Les écritures comptables sont générées automatiquement pour les ajustements validés

### Impacts sur d'autres modules
1. Le module d'ajustements affecte le module de stock (mouvements de stock)
2. Le module d'ajustements affecte le module comptable (écritures de perte)
3. Le module d'ajustements fournit des données aux modules de reporting
4. Le module d'ajustements affecte les modules de sécurité (journalisation)
5. Le module d'ajustements affecte les modules d'analyse et d'évaluation

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
utilisateurs ||--o{ ajustements_stock_boutique
utilisateurs ||--o{ reinitialisations_index_pistolets
utilisateurs ||--o{ validations_hierarchiques
stations ||--o{ ajustements_stock_boutique
stations ||--o{ reinitialisations_index_pistolets
articles ||--o{ details_ajustements_stock_boutique
pistolets ||--o{ reinitialisations_index_pistolets
cuves ||--o{ reinitialisations_index_pistolets
causes_ajustements ||--o{ details_ajustements_stock_boutique
ajustements_stock_boutique ||--o{ details_ajustements_stock_boutique
ajustements_stock_boutique ||--o{ validations_hierarchiques (objet_type='ajustement_stock')
reinitialisations_index_pistolets ||--o{ validations_hierarchiques (objet_type='reinit_index')
journaux_actions_critiques }o--o{ utilisateurs
journaux_actions_critiques }o--o{ stations
```

### Diagramme de séquence pour un ajustement de stock
```
Gestionnaire -> API: POST /api/ajustements/stock-boutique
API -> Base de données: Créer l'ajustement (statut: Brouillon)
API -> Gestionnaire: Retourner l'ajustement créé

Gestionnaire -> API: POST /api/ajustements/stock-boutique/{id}/valider
API -> Base de données: Valider l'ajustement
API -> Base de données: Créer les mouvements de stock
API -> Base de données: Mettre à jour les stocks théoriques
API -> API: Générer les écritures comptables
API -> API: Journaliser l'action critique
API -> Gestionnaire: Retourner confirmation de validation
```

## 7. Tests Requises

### Tests unitaires
1. Test de la fonction de génération automatique de numéro d'ajustement
2. Test des validations de données pour les différents endpoints
3. Test des calculs de montants pour les ajustements
4. Test des calculs d'écarts pour les réinitialisations
5. Test des validations hiérarchiques
6. Test des fonctions de journalisation

### Tests d'intégration
1. Test complet du processus d'ajustement de stock boutique
2. Test complet du processus de réinitialisation d'index
3. Test du workflow de validation hiérarchique
4. Test de la génération automatique des écritures comptables
5. Test de la mise à jour des stocks
6. Test de la journalisation des actions critiques

### Tests de charge/performance
1. Test de performance pour des centaines d'ajustements simultanés
2. Test de performance pour des réinitialisations multiples
3. Test de performance pour des validations en cascade
4. Test de la journalisation pour de nombreux événements
5. Test de la génération d'écritures comptables pour de grands volumes

### Jeux de données de test
1. Données d'ajustements valides avec différentes configurations
2. Données de réinitialisations avec différents écarts
3. Données de causes d'ajustement variées
4. Données de seuils de validation configurés
5. Données d'utilisateurs avec différents niveaux de permissions
6. Données historiques pour les tests d'analyse

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contrôles d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de gestion des ajustements
6. [ ] Implémenter la logique de validation des données
7. [ ] Créer les utilitaires de génération d'écritures comptables
8. [ ] Implémenter le système de validation hiérarchique
9. [ ] Créer les algorithmes d'analyse des causes de péremption
10. [ ] Créer les tests unitaires et d'intégration
11. [ ] Implémenter la journalisation des actions critiques
12. [ ] Créer les vues frontend pour la gestion des ajustements (si applicable)
13. [ ] Documenter les endpoints API
14. [ ] Intégrer avec les modules de reporting pour les analyses
15. [ ] Intégrer avec le module de sécurité pour les validations

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base pour les ajustements
3. Développer les fonctionnalités de réinitialisation
4. Implémenter le système de validation hiérarchique
5. Créer les fonctionnalités d'analyse
6. Développer la journalisation des actions critiques
7. Intégrer avec les modules de stock et comptable
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
1. La sécurité des réinitialisations d'index (risque de manipulation frauduleuse)
2. La précision des calculs de perte pour les ajustements
3. La performance des validations hiérarchiques
4. La sécurité des données dans les journaux d'actions critiques
5. La cohérence des écritures comptables générées automatiquement

### Risques techniques
1. Risque d'erreurs dans les calculs de stock et de perte
2. Risque de contournement des validations hiérarchiques
3. Risque de problèmes de performances avec de grands volumes
4. Risque de perte de données en cas de panne pendant les processus
5. Risque de manipulation des données par des utilisateurs non autorisés
6. Risque de non-respect des seuils de validation configurés

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de validations hiérarchiques
2. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
3. Besoin de maintenance continue pour les règles de validation
4. Risque de dépendance excessive à des bibliothèques tierces pour les calculs complexes
5. Risque de complexité dans la gestion des différents types d'ajustements