# Technical Specification - Module de Gestion des Inventaires

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de gestion des inventaires permet de contrôler les stocks physiques d'une station-service, tant pour le carburant que pour les produits de la boutique. Il permet de comparer les stocks réels mesurés physiquement avec les stocks théoriques enregistrés dans le système, d'identifier les écarts et d'analyser leurs causes. Le module assure également le suivi des températures pour la correction volumétrique du carburant.

### Problème à résoudre
Sans un module dédié à la gestion des inventaires, les stations-service ne pourraient pas effectuer de contrôles réguliers de leur stock physique, ce qui entraînerait:
- Des écarts non détectés entre le stock théorique et réel
- Des difficultés à identifier les sources de perte ou de vol
- Des erreurs dans les calculs de consommation
- Des problèmes de gestion des stocks (ruptures ou surstocks)
- Des difficultés à évaluer la performance des opérations
- Des incohérences dans les rapports financiers

### Définition du périmètre
Le périmètre du sprint couvre:
- Gestion des inventaires de carburant (mesure de hauteur, calcul via barème, suivi des températures)
- Gestion des inventaires de produits de boutique (saisie des quantités réelles)
- Calcul des écarts entre le stock réel et théorique
- Gestion des inventaires partiels ou complets
- Analyse des écarts anormaux
- Système de justification des écarts
- Analyse des tendances d'écart
- Suivi et correction des températures

## 2. User Stories & Critères d'acceptation

### US-INV-001: En tant que gestionnaire, je veux mesurer la hauteur dans les cuves de carburant
**Critères d'acceptation :**
- Saisie de la hauteur mesurée dans chaque cuve
- Lien avec les informations de la cuve
- Enregistrement de la date et de l'heure de la mesure
- Enregistrement de l'utilisateur effectuant la mesure
- Prise en compte des températures pour la correction volumétrique
- Historique des mesures de hauteur

### US-INV-002: En tant que gestionnaire, je veux calculer le volume de carburant via le barème de jauge
**Critères d'acceptation :**
- Utilisation du barème spécifique de chaque cuve
- Calcul automatique du volume à partir de la hauteur mesurée
- Application des corrections de température si applicable
- Calcul de la valeur du stock basé sur le prix du carburant
- Affichage des résultats avec précision

### US-INV-003: En tant que gestionnaire, je veux comparer l'écart entre le stock réel et théorique
**Critères d'acceptation :**
- Calcul automatique de l'écart (réel - théorique)
- Affichage des écarts en volume et en valeur
- Saisie de seuils d'alerte pour les écarts anormaux
- Alertes visuelles pour les écarts dépassant les seuils
- Historique des écarts par période

### US-INV-004: En tant que gestionnaire, je veux effectuer un inventaire partiel ou complet
**Critères d'acceptation :**
- Possibilité de choisir entre inventaire partiel ou complet
- Sélection des cuves/articles à inventorier dans le cas d'un inventaire partiel
- Validation de la complétude des mesures
- Génération automatique d'un numéro d'inventaire
- Enregistrement de la date et de l'utilisateur responsable

### US-INV-005: En tant que gestionnaire, je veux analyser les écarts anormaux
**Critères d'acceptation :**
- Détection automatique des écarts dépassant les seuils configurés
- Classification des écarts par gravité
- Historique des écarts anormaux
- Identification des tendances récurrentes
- Génération de rapports d'analyse
- Suivi des actions correctives

### US-INV-006: En tant que gestionnaire, je veux suivre les températures dans les cuves
**Critères d'acceptation :**
- Saisie de la température dans chaque cuve
- Correction volumétrique basée sur la température
- Historique des températures
- Alertes pour les températures anormales
- Intégration avec le calcul du volume

### US-INV-007: En tant que gestionnaire, je veux saisir les quantités réelles pour les produits de boutique
**Critères d'acceptation :**
- Saisie des quantités physiquement présentes
- Association avec les articles existants
- Gestion des unités de mesure
- Enregistrement de la date et de l'utilisateur
- Contrôle de validité des saisies

### US-INV-008: En tant que gestionnaire, je veux calculer l'écart pour les produits de boutique
**Critères d'acceptation :**
- Calcul automatique de l'écart (réel - théorique)
- Calcul en unités et en valeur
- Justification obligatoire pour les écarts significatifs
- Historique des écarts par article
- Intégration avec les mouvements de stock

### US-INV-009: En tant que gestionnaire, je veux justifier les écarts constatés
**Critères d'acceptation :**
- Saisie d'une justification pour chaque écart significatif
- Classification des écarts par type (vol, perte, erreur de saisie, etc.)
- Historique des justifications
- Validation des justifications par un responsable
- Lien avec les écritures comptables d'ajustement

### US-INV-010: En tant que gestionnaire, je veux analyser les tendances d'écart
**Critères d'acceptation :**
- Analyse des écarts sur différentes périodes
- Identification des articles/cuves avec tendance aux écarts
- Représentation graphique des tendances
- Prédiction potentielle des écarts futurs
- Génération de rapports de tendance

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `utilisateurs` - données des utilisateurs effectuant les inventaires
- `cuves` - données des cuves pour les inventaires carburant
- `carburants` - données des carburants pour les calculs
- `articles` - données des articles pour les inventaires boutique
- `stations` - données des stations
- `stocks` - données des stocks théoriques
- `stocks_mouvements` - historique des mouvements de stock
- `unites_mesure` - unités de mesure pour les articles

### Nouvelles tables à créer

```sql
-- Table pour les opérations d'inventaire
CREATE TABLE IF NOT EXISTS operations_inventaire (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_inventaire VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    type_inventaire VARCHAR(20) NOT NULL CHECK (type_inventaire IN ('complet', 'partiel')),
    type_stock VARCHAR(20) NOT NULL CHECK (type_stock IN ('carburant', 'boutique')),
    date_inventaire DATE NOT NULL,
    heure_inventaire TIME NOT NULL,
    utilisateur_responsable_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Termine', 'Valide', 'Cloture')),
    commentaire TEXT,
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les mesures d'inventaire des cuves
CREATE TABLE IF NOT EXISTS mesures_inventaire_cuves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_inventaire_id UUID REFERENCES operations_inventaire(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id),
    hauteur_mesuree NUMERIC(18,3) NOT NULL, -- Hauteur mesurée en mm
    temperature_mesuree NUMERIC(5,2), -- Température en degrés Celsius
    volume_calcule NUMERIC(18,3), -- Volume calculé via le barème
    volume_corrigé NUMERIC(18,3), -- Volume corrigé par la température
    stock_theorique NUMERIC(18,3), -- Stock théorique avant l'inventaire
    ecart_volume NUMERIC(18,3) GENERATED ALWAYS AS (volume_corrigé - stock_theorique) STORED,
    ecart_pourcentage NUMERIC(5,2) GENERATED ALWAYS AS (CASE WHEN stock_theorique > 0 THEN (ecart_volume / stock_theorique) * 100 ELSE 0 END) STORED,
    seuil_alerte_eccart NUMERIC(18,3) DEFAULT 100, -- En litres
    utilisateur_operateur_id UUID REFERENCES utilisateurs(id),
    commentaire_mesure TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les mesures d'inventaire des articles boutique
CREATE TABLE IF NOT EXISTS mesures_inventaire_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_inventaire_id UUID REFERENCES operations_inventaire(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id),
    quantite_reelle NUMERIC(18,3) NOT NULL,
    unite_reelle VARCHAR(10), -- Unité de mesure de la quantité réelle
    stock_theorique NUMERIC(18,3), -- Stock théorique avant l'inventaire
    ecart_quantite NUMERIC(18,3) GENERATED ALWAYS AS (quantite_reelle - stock_theorique) STORED,
    ecart_pourcentage NUMERIC(5,2) GENERATED ALWAYS AS (CASE WHEN stock_theorique > 0 THEN (ecart_quantite / stock_theorique) * 100 ELSE 0 END) STORED,
    seuil_alerte_eccart NUMERIC(18,3) DEFAULT 10, -- En unité de l'article
    utilisateur_operateur_id UUID REFERENCES utilisateurs(id),
    commentaire_mesure TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les justifications des écarts
CREATE TABLE IF NOT EXISTS justifications_ecarts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_inventaire_id UUID REFERENCES operations_inventaire(id),
    objet_type VARCHAR(20) NOT NULL CHECK (objet_type IN ('cuve', 'article')), -- Type de l'objet concerné
    objet_id UUID NOT NULL, -- ID de la cuve ou de l'article
    type_ecart VARCHAR(50) NOT NULL, -- 'vol', 'perte', 'erreur_saisie', etc.
    motif_justification TEXT NOT NULL,
    utilisateur_justifieur_id UUID REFERENCES utilisateurs(id),
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Valide', 'Rejete')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les barèmes de jauge des cuves
CREATE TABLE IF NOT EXISTS barèmes_jauge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_id UUID REFERENCES cuves(id),
    hauteur_mm INTEGER NOT NULL, -- Hauteur en mm
    volume_litre NUMERIC(18,3) NOT NULL, -- Volume correspondant en litres
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(cuve_id, hauteur_mm)
);

-- Table pour les écarts anormaux détectés
CREATE TABLE IF NOT EXISTS ecarts_anormaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objet_type VARCHAR(20) NOT NULL CHECK (objet_type IN ('cuve', 'article')),
    objet_id UUID NOT NULL,
    operation_inventaire_id UUID REFERENCES operations_inventaire(id),
    valeur_ecart NUMERIC(18,3) NOT NULL,
    seuil_alerte NUMERIC(18,3) NOT NULL,
    date_detection DATE NOT NULL,
    statut VARCHAR(20) DEFAULT 'Detecte' CHECK (statut IN ('Detecte', 'Enquete', 'Traite', 'Ferme')),
    utilisateur_detecteur_id UUID REFERENCES utilisateurs(id),
    utilisateur_traitant_id UUID REFERENCES utilisateurs(id),
    date_traitement DATE,
    motif_ecart TEXT,
    action_corrective TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'analyse des tendances d'écart
CREATE TABLE IF NOT EXISTS analyses_tendances_ecarts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objet_type VARCHAR(20) NOT NULL CHECK (objet_type IN ('cuve', 'article')),
    objet_id UUID NOT NULL,
    periode_analyse_debut DATE NOT NULL,
    periode_analyse_fin DATE NOT NULL,
    moyenne_ecarts NUMERIC(18,3) NOT NULL,
    ecart_type_ecarts NUMERIC(18,3) NOT NULL,
    nombre_occurrences INTEGER NOT NULL,
    tendance VARCHAR(20) NOT NULL CHECK (tendance IN ('hausse', 'baisse', 'stable')),
    indicateur_signification NUMERIC(5,2), -- Indicateur de significité (0-100)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les opérations d'inventaire
CREATE INDEX IF NOT EXISTS idx_operations_inventaire_station ON operations_inventaire(station_id);
CREATE INDEX IF NOT EXISTS idx_operations_inventaire_date ON operations_inventaire(date_inventaire);
CREATE INDEX IF NOT EXISTS idx_operations_inventaire_statut ON operations_inventaire(statut);
CREATE INDEX IF NOT EXISTS idx_operations_inventaire_type ON operations_inventaire(type_inventaire);

-- Index pour les mesures d'inventaire des cuves
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_cuves_operation ON mesures_inventaire_cuves(operation_inventaire_id);
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_cuves_cuve ON mesures_inventaire_cuves(cuve_id);

-- Index pour les mesures d'inventaire des articles
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_articles_operation ON mesures_inventaire_articles(operation_inventaire_id);
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_articles_article ON mesures_inventaire_articles(article_id);

-- Index pour les justifications d'écarts
CREATE INDEX IF NOT EXISTS idx_justifications_ecarts_operation ON justifications_ecarts(operation_inventaire_id);
CREATE INDEX IF NOT EXISTS idx_justifications_ecarts_objet ON justifications_ecarts(objet_id);
CREATE INDEX IF NOT EXISTS idx_justifications_ecarts_statut ON justifications_ecarts(statut);

-- Index pour les barèmes de jauge
CREATE INDEX IF NOT EXISTS idx_baremes_jauge_cuve ON barèmes_jauge(cuve_id);

-- Index pour les écarts anormaux
CREATE INDEX IF NOT EXISTS idx_ecarts_anormaux_objet ON ecarts_anormaux(objet_id);
CREATE INDEX IF NOT EXISTS idx_ecarts_anormaux_date ON ecarts_anormaux(date_detection);
CREATE INDEX IF NOT EXISTS idx_ecarts_anormaux_statut ON ecarts_anormaux(statut);

-- Index pour les analyses de tendances
CREATE INDEX IF NOT EXISTS idx_analyses_tendances_objet ON analyses_tendances_ecarts(objet_id);
CREATE INDEX IF NOT EXISTS idx_analyses_tendances_periode ON analyses_tendances_ecarts(periode_analyse_debut, periode_analyse_fin);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour générer automatiquement le numéro d'inventaire
CREATE OR REPLACE FUNCTION generate_numero_inventaire()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : INV-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_inventaire, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_inventaire FROM 5 FOR 8) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM operations_inventaire
    WHERE SUBSTRING(numero_inventaire FROM 5 FOR 8) = date_str;
    
    numero := 'INV-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    NEW.numero_inventaire := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_inventaire
    BEFORE INSERT ON operations_inventaire
    FOR EACH ROW EXECUTE FUNCTION generate_numero_inventaire();

-- Trigger pour calculer automatiquement le volume à partir de la hauteur et du barème
CREATE OR REPLACE FUNCTION calculate_volume_from_barem()
RETURNS TRIGGER AS $$
DECLARE
    volume_intermediaire NUMERIC(18,3);
    hauteur_prec INTEGER;
    hauteur_suiv INTEGER;
    volume_prec NUMERIC(18,3);
    volume_suiv NUMERIC(18,3);
BEGIN
    -- Récupérer les valeurs des hauteurs encadrant la hauteur mesurée
    SELECT hauteur_mm, volume_litre
    INTO hauteur_prec, volume_prec
    FROM barèmes_jauge
    WHERE cuve_id = NEW.cuve_id AND hauteur_mm <= NEW.hauteur_mesuree * 1000 -- Convertir en mm
    ORDER BY hauteur_mm DESC
    LIMIT 1;
    
    SELECT hauteur_mm, volume_litre
    INTO hauteur_suiv, volume_suiv
    FROM barèmes_jauge
    WHERE cuve_id = NEW.cuve_id AND hauteur_mm >= NEW.hauteur_mesuree * 1000 -- Convertir en mm
    ORDER BY hauteur_mm ASC
    LIMIT 1;
    
    -- Calculer le volume par interpolation linéaire
    IF hauteur_prec IS NOT NULL AND hauteur_suiv IS NOT NULL AND hauteur_prec != hauteur_suiv THEN
        volume_intermediaire := volume_prec + 
            ((NEW.hauteur_mesuree * 1000 - hauteur_prec) * (volume_suiv - volume_prec)) / 
            (hauteur_suiv - hauteur_prec);
    ELSIF hauteur_prec IS NOT NULL THEN
        volume_intermediaire := volume_prec;
    ELSIF hauteur_suiv IS NOT NULL THEN
        volume_intermediaire := volume_suiv;
    ELSE
        RAISE EXCEPTION 'Aucune donnée de barème trouvée pour la cuve %', NEW.cuve_id;
    END IF;
    
    NEW.volume_calcule := volume_intermediaire;
    
    -- Appliquer la correction de température si applicable
    IF NEW.temperature_mesuree IS NOT NULL THEN
        -- Formule de correction volumétrique basée sur le coefficient de dilatation
        -- Pour le carburant, coefficient approximatif de 0.001 par degré Celsius
        NEW.volume_corrigé := volume_intermediaire * (1 + 0.001 * (NEW.temperature_mesuree - 15));
    ELSE
        NEW.volume_corrigé := volume_intermediaire;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_volume_from_barem
    BEFORE INSERT OR UPDATE ON mesures_inventaire_cuves
    FOR EACH ROW EXECUTE FUNCTION calculate_volume_from_barem();

-- Trigger pour détecter les écarts anormaux
CREATE OR REPLACE FUNCTION detect_ecarts_anormaux()
RETURNS TRIGGER AS $$
DECLARE
    objet_id UUID;
    objet_type VARCHAR(20);
    valeur_ecart NUMERIC(18,3);
    seuil_alerte NUMERIC(18,3);
    operation_id UUID;
BEGIN
    -- Déterminer le type d'objet et les valeurs concernées
    IF TG_TABLE_NAME = 'mesures_inventaire_cuves' THEN
        objet_id := NEW.cuve_id;
        objet_type := 'cuve';
        valeur_ecart := NEW.ecart_volume;
        seuil_alerte := NEW.seuil_alerte_eccart;
        operation_id := NEW.operation_inventaire_id;
    ELSIF TG_TABLE_NAME = 'mesures_inventaire_articles' THEN
        objet_id := NEW.article_id;
        objet_type := 'article';
        valeur_ecart := NEW.ecart_quantite;
        seuil_alerte := NEW.seuil_alerte_eccart;
        operation_id := NEW.operation_inventaire_id;
    ELSE
        RETURN NEW;
    END IF;
    
    -- Vérifier si l'écart dépasse le seuil
    IF ABS(valeur_ecart) > seuil_alerte THEN
        -- Enregistrer l'écart anormal dans la table de suivi
        INSERT INTO ecarts_anormaux (
            objet_type,
            objet_id,
            operation_inventaire_id,
            valeur_ecart,
            seuil_alerte,
            date_detection,
            utilisateur_detecteur_id
        )
        VALUES (
            objet_type,
            objet_id,
            operation_id,
            valeur_ecart,
            seuil_alerte,
            NEW.date_inventaire, -- Supposant qu'on a accès à la date via la table parente
            NEW.utilisateur_operateur_id
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_detect_ecarts_anormaux_cuves
    AFTER INSERT OR UPDATE ON mesures_inventaire_cuves
    FOR EACH ROW EXECUTE FUNCTION detect_ecarts_anormaux();

CREATE TRIGGER trigger_detect_ecarts_anormaux_articles
    AFTER INSERT OR UPDATE ON mesures_inventaire_articles
    FOR EACH ROW EXECUTE FUNCTION detect_ecarts_anormaux();

-- Trigger pour empêcher la modification d'un inventaire validé
CREATE OR REPLACE FUNCTION prevent_inventaire_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'un inventaire validé ou clôturé
    IF OLD.statut = 'Valide' OR OLD.statut = 'Cloture' THEN
        RAISE EXCEPTION 'Impossible de modifier une opération d''inventaire déjà validée ou clôturée';
    END IF;

    NEW.updated_at := now();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_inventaire_modification
    BEFORE UPDATE ON operations_inventaire
    FOR EACH ROW EXECUTE FUNCTION prevent_inventaire_modification();
```

## 4. API Backend

### 4.1 Gestion des opérations d'inventaire

#### POST /api/inventaire/operations
**Description:** Créer une nouvelle opération d'inventaire

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "station_id": "uuid",
  "type_inventaire": "complet|partiel",
  "type_stock": "carburant|boutique",
  "date_inventaire": "date (format YYYY-MM-DD)",
  "heure_inventaire": "time (format HH:MM:SS)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_inventaire": "string",
    "station_id": "uuid",
    "type_inventaire": "string",
    "type_stock": "string",
    "date_inventaire": "date",
    "heure_inventaire": "time",
    "statut": "string",
    "utilisateur_responsable_id": "uuid",
    "commentaire": "string",
    "created_at": "datetime"
  },
  "message": "Opération d'inventaire créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Opération d'inventaire créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

#### PUT /api/inventaire/operations/{id}
**Description:** Mettre à jour une opération d'inventaire

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_inventaire": "string",
    "statut": "string",
    "commentaire": "string",
    "updated_at": "datetime"
  },
  "message": "Opération d'inventaire mise à jour avec succès"
}
```

**HTTP Status Codes:**
- 200: Opération d'inventaire mise à jour avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Opération d'inventaire non trouvée
- 409: Impossible de modifier une opération déjà validée
- 500: Erreur interne du serveur

#### POST /api/inventaire/operations/{id}/valider
**Description:** Valider une opération d'inventaire

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
    "numero_inventaire": "string",
    "statut": "Valide",
    "utilisateur_validation_id": "uuid",
    "date_validation": "date"
  },
  "message": "Opération d'inventaire validée avec succès"
}
```

**HTTP Status Codes:**
- 200: Opération d'inventaire validée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Opération d'inventaire non trouvée
- 409: Opération déjà validée ou clôturée
- 500: Erreur interne du serveur

### 4.2 Inventaire de carburant

#### POST /api/inventaire/carburant/{operation_id}/mesures
**Description:** Enregistrer les mesures d'inventaire pour les cuves

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "mesures": [
    {
      "cuve_id": "uuid",
      "hauteur_mesuree": "decimal (max 18,3)",
      "temperature_mesuree": "decimal (max 5,2)",
      "commentaire_mesure": "string (optionnel)"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "mesures": [
      {
        "id": "uuid",
        "operation_inventaire_id": "uuid",
        "cuve_id": "uuid",
        "hauteur_mesuree": "decimal",
        "temperature_mesuree": "decimal",
        "volume_calcule": "decimal",
        "volume_corrigé": "decimal",
        "stock_theorique": "decimal",
        "ecart_volume": "decimal",
        "ecart_pourcentage": "decimal",
        "utilisateur_operateur_id": "uuid",
        "commentaire_mesure": "string"
      }
    ]
  },
  "message": "Mesures d'inventaire carburant enregistrées avec succès"
}
```

**HTTP Status Codes:**
- 200: Mesures enregistrées avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Opération d'inventaire/cuve non trouvée
- 500: Erreur interne du serveur

### 4.3 Inventaire boutique

#### POST /api/inventaire/boutique/{operation_id}/mesures
**Description:** Enregistrer les mesures d'inventaire pour les articles

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "mesures": [
    {
      "article_id": "uuid",
      "quantite_reelle": "decimal (max 18,3)",
      "unite_reelle": "string (max 10)",
      "commentaire_mesure": "string (optionnel)"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "mesures": [
      {
        "id": "uuid",
        "operation_inventaire_id": "uuid",
        "article_id": "uuid",
        "quantite_reelle": "decimal",
        "unite_reelle": "string",
        "stock_theorique": "decimal",
        "ecart_quantite": "decimal",
        "ecart_pourcentage": "decimal",
        "utilisateur_operateur_id": "uuid",
        "commentaire_mesure": "string"
      }
    ]
  },
  "message": "Mesures d'inventaire boutique enregistrées avec succès"
}
```

**HTTP Status Codes:**
- 200: Mesures enregistrées avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Opération d'inventaire/article non trouvé
- 500: Erreur interne du serveur

### 4.4 Justifications des écarts

#### POST /api/inventaire/{operation_id}/justifications
**Description:** Enregistrer une justification pour un écart

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "objet_type": "cuve|article",
  "objet_id": "uuid",
  "type_ecart": "vol|perte|erreur_saisie|etc.",
  "motif_justification": "text"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "operation_inventaire_id": "uuid",
    "objet_type": "string",
    "objet_id": "uuid",
    "type_ecart": "string",
    "motif_justification": "text",
    "statut": "EnCours",
    "utilisateur_justifieur_id": "uuid"
  },
  "message": "Justification d'écart enregistrée avec succès"
}
```

**HTTP Status Codes:**
- 200: Justification enregistrée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Opération d'inventaire/objet non trouvé
- 500: Erreur interne du serveur

### 4.5 Analyse des écarts anormaux

#### GET /api/inventaire/ecarts-anormaux
**Description:** Obtenir la liste des écarts anormaux

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- objet_type: cuve|article (optionnel)
- objet_id: uuid (optionnel)
- statut: Detecte|Enquete|Traite|Ferme (optionnel)
- date_debut: date (format YYYY-MM-DD) (optionnel)
- date_fin: date (format YYYY-MM-DD) (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "ecarts": [
      {
        "id": "uuid",
        "objet_type": "string",
        "objet_id": "uuid",
        "valeur_ecart": "decimal",
        "seuil_alerte": "decimal",
        "date_detection": "date",
        "statut": "string",
        "motif_ecart": "string",
        "action_corrective": "string"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Écarts anormaux récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

### 4.6 Analyse des tendances

#### GET /api/inventaire/tendances-ecarts
**Description:** Obtenir l'analyse des tendances d'écart

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- objet_type: cuve|article (optionnel)
- objet_id: uuid (optionnel)
- periode_debut: date (format YYYY-MM-DD) (optionnel)
- periode_fin: date (format YYYY-MM-DD) (optionnel)

**Response:**
```json
{
  "success": true,
  "data": {
    "tendances": [
      {
        "id": "uuid",
        "objet_type": "string",
        "objet_id": "uuid",
        "periode_analyse_debut": "date",
        "periode_analyse_fin": "date",
        "moyenne_ecarts": "decimal",
        "ecart_type_ecarts": "decimal",
        "nombre_occurrences": "integer",
        "tendance": "string",
        "indicateur_signification": "decimal"
      }
    ]
  },
  "message": "Analyses des tendances récupérées avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de calcul pour les inventaires de carburant
1. Le volume est calculé à partir de la hauteur mesurée en utilisant le barème de jauge spécifique à chaque cuve
2. Le volume est corrigé en fonction de la température mesurée
3. L'écart est calculé comme la différence entre le volume réel mesuré et le stock théorique
4. Les seuils d'alerte sont configurables par cuve ou de manière globale
5. La correction volumétrique s'applique selon un coefficient de dilatation thermique

### Règles de calcul pour les inventaires de boutique
1. L'écart est calculé comme la différence entre la quantité réelle mesurée et le stock théorique
2. Le calcul est effectué en unités physiques et en valeur
3. Les seuils d'alerte sont configurables par article ou de manière globale
4. La comparaison tient compte des unités de mesure

### Règles de gestion des seuils d'alerte
1. Les seuils peuvent être configurés de manière globale ou spécifique par cuve/article
2. Les seuils peuvent être exprimés en valeur absolue ou en pourcentage
3. Les seuils sont définis différemment pour les carburants et les articles de boutique
4. Les seuils peuvent être ajustés selon les types d'articles ou de carburants

### Règles de validation des mesures
1. Les hauteurs mesurées doivent être positives et inférieures à la hauteur maximale de la cuve
2. Les quantités mesurées pour les articles doivent être positives
3. Les températures doivent être dans des plages de valeurs réalistes
4. Les mesures doivent être effectuées par des utilisateurs autorisés

### Règles de justification des écarts
1. Les écarts dépassant les seuils doivent être justifiés
2. Les justifications doivent inclure un type d'écart et un motif détaillé
3. Les justifications peuvent nécessiter une validation par un gestionnaire
4. Les justifications doivent être liées aux écritures comptables d'ajustement

### Règles d'analyse des tendances
1. Les tendances sont calculées sur des périodes configurables
2. L'analyse statistique inclut la moyenne, l'écart-type et la tendance
3. L'indicateur de significité mesure la probabilité de la tendance
4. Les tendances peuvent être prédictionnelles pour identifier les problèmes futurs

### Impacts sur d'autres modules
1. Le module d'inventaire interagit avec le module de gestion des stocks pour les ajustements
2. Le module d'inventaire fournit des données au module de rapports pour les analyses
3. Le module d'inventaire peut déclencher des écritures comptables d'ajustement
4. Le module d'inventaire fournit des indicateurs de performance au module de gestion

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
utilisateurs ||--o{ operations_inventaire
utilisateurs ||--o{ mesures_inventaire_cuves
utilisateurs ||--o{ mesures_inventaire_articles
stations ||--o{ operations_inventaire
cuves ||--o{ mesures_inventaire_cuves
cuves ||--o{ barèmes_jauge
carburants ||--o{ mesures_inventaire_cuves
articles ||--o{ mesures_inventaire_articles
operations_inventaire ||--o{ mesures_inventaire_cuves
operations_inventaire ||--o{ mesures_inventaire_articles
operations_inventaire ||--o{ justifications_ecarts
ecarts_anormaux }o--o{ operations_inventaire
analyses_tendances_ecarts }o--o{ mesures_inventaire_cuves
analyses_tendances_ecarts }o--o{ mesures_inventaire_articles
```

### Diagramme de séquence pour un inventaire de carburant
```
Gestionnaire -> API: POST /api/inventaire/operations
API -> Base de données: Créer l'opération d'inventaire
API -> Gestionnaire: Retourner l'opération créée

Gestionnaire -> API: POST /api/inventaire/carburant/{id}/mesures
API -> Base de données: Enregistrer les mesures de hauteur
API -> Base de données: Calculer les volumes via les barèmes
API -> Base de données: Calculer les écarts
API -> Base de données: Détecter les écarts anormaux
API -> Gestionnaire: Retourner les mesures enregistrées

Gestionnaire -> API: POST /api/inventaire/{id}/valider
API -> Base de données: Valider l'opération d'inventaire
API -> API: Générer les écritures comptables d'ajustement (si nécessaire)
API -> Gestionnaire: Retourner confirmation de validation
```

## 7. Tests Requises

### Tests unitaires
1. Test de la fonction de génération automatique de numéro d'inventaire
2. Test des validations de données pour les différents endpoints
3. Test des calculs de volume à partir de la hauteur et du barème
4. Test des calculs d'écarts (volume, pourcentage)
5. Test des corrections de température
6. Test des fonctions de détection des écarts anormaux

### Tests d'intégration
1. Test complet du processus d'inventaire de carburant
2. Test complet du processus d'inventaire boutique
3. Test de la validation des opérations d'inventaire
4. Test de la génération automatique des écritures comptables
5. Test de l'analyse des tendances d'écart
6. Test de la détection des écarts anormaux

### Tests de charge/performance
1. Test de performance pour des inventaires avec de nombreuses mesures
2. Test de performance pour des calculs de volumes complexes
3. Test de performance pour des analyses de tendances sur de longues périodes
4. Test de la détection des écarts pour de grands volumes de données
5. Test de la génération de nombreux rapports d'analyse

### Jeux de données de test
1. Données d'inventaires valides avec différentes configurations
2. Données de cuves avec différents barèmes de jauge
3. Données d'articles de boutique avec différentes caractéristiques
4. Données de températures pour les tests de correction volumétrique
5. Données de seuils d'alerte configurés
6. Données historiques d'écart pour les tests de tendance

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contrôles d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de gestion des inventaires (mesures, calculs, validations)
6. [ ] Implémenter la logique de calcul des volumes via les barèmes
7. [ ] Créer les utilitaires de correction volumétrique
8. [ ] Implémenter la détection automatique des écarts anormaux
9. [ ] Créer les algorithmes pour l'analyse des tendances d'écart
10. [ ] Créer les tests unitaires et d'intégration
11. [ ] Implémenter la gestion des erreurs et logs
12. [ ] Créer les vues frontend pour la gestion des inventaires (si applicable)
13. [ ] Documenter les endpoints API
14. [ ] Intégrer avec le module de gestion des stocks pour les ajustements
15. [ ] Intégrer avec le module comptable pour les écritures d'ajustement

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base pour la gestion des opérations
3. Développer les fonctionnalités de mesure et de calcul
4. Implémenter la détection des écarts anormaux
5. Créer les fonctionnalités de justification des écarts
6. Développer les analyses de tendance
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
1. La précision des calculs de volume à partir des barèmes de jauge
2. La gestion des corrections de température pour la mesure du carburant
3. La détection fiable des écarts anormaux
4. La sécurité des données sensibles dans les justifications
5. La performance des calculs pour de grands volumes de données

### Risques techniques
1. Risque d'incohérence entre les données de barème et les mesures réelles
2. Risque d'erreurs dans les calculs de corrections volumétriques
3. Risque de non-détection des écarts anormaux
4. Risque de problèmes de performances avec de grands volumes
5. Risque de perte de données en cas de panne pendant les processus
6. Risque de manipulation des données par des utilisateurs non autorisés

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples règles de calcul
2. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
3. Besoin de maintenance continue pour les barèmes de jauge
4. Risque de dépendance excessive à des bibliothèques tierces pour les calculs complexes
5. Besoin d'ajustements fréquents des seuils d'alerte en fonction de l'expérience