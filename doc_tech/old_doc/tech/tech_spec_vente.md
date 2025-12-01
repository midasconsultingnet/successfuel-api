# Technical Specification - Module de Gestion des Ventes

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de gestion des ventes permet de gérer toutes les ventes effectuées dans une station-service, y compris les ventes de carburant, de produits de boutique et de services. Il couvre l'ensemble du processus de vente : de la création de la vente à la validation du paiement, en passant par la mise à jour des stocks et des trésoreries. Le module assure également le suivi des performances des pompistes et caissiers, l'analyse des écarts anormaux et la génération des rapports de productivité.

### Problème à résoudre
Sans un module dédié à la gestion des ventes, les stations-service ne pourraient pas suivre efficacement leurs activités commerciales, ce qui entraînerait des difficultés à:
- Contrôler les ventes effectuées
- Suivre la performance des employés (pompistes, caissiers)
- Analyser les écarts entre les index de pistolets et les ventes enregistrées
- Gérer les stocks de manière précise
- Respecter les obligations comptables et fiscales
- Optimiser les performances de l'équipe
- Mettre en place des contrôles d'accès différenciés selon les types d'utilisateurs (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)

### Définition du périmètre
Le périmètre du sprint couvre:
- Gestion des ventes de carburant (processus complet)
- Gestion des ventes de produits de boutique (tickets de caisse)
- Gestion des ventes de services
- Saisie des index de pistolet
- Gestion des paiements (cash, crédit, écart pompiste)
- Mise à jour de la trésorerie
- Mise à jour des stocks
- Génération automatique des écritures comptables
- Modification/annulation des ventes
- Suivi des performances pompistes
- Analyse de rendement
- Suivi des écarts anormaux
- Génération des tickets de caisse
- Arrêt de compte caissier
- Contrôles d'accès selon le type d'utilisateur
- Validation hiérarchique selon le montant ou le type d'opération

## 2. User Stories & Critères d'acceptation

### US-VENTE-001: En tant que pompiste, je veux créer une vente de carburant
**Critères d'acceptation :**
- Saisie des informations de base (pistolet, quantité, prix unitaire)
- Lien avec les données de carburant de la cuve
- Calcul automatique du montant
- Association avec l'utilisateur pompiste
- Enregistrement de l'heure de début et de fin
- Génération automatique d'un numéro de référence unique

### US-VENTE-002: En tant que pompiste, je veux enregistrer les index de pistolet
**Critères d'acceptation :**
- Saisie de l'index de début avant la distribution
- Saisie de l'index de fin après la distribution
- Calcul automatique du volume distribué
- Validation que l'écart est cohérent avec la vente enregistrée
- Historique des index pour chaque pistolet
- Lien avec la cuve correspondante

### US-VENTE-003: En tant que gestionnaire, je veux gérer le paiement d'une vente
**Critères d'acceptation :**
- Association d'un mode de paiement (espèces, crédit, écart pompiste)
- Enregistrement du montant payé et de la date
- Suivi des paiements partiels
- Gestion des écarts de paiement (si montant reçu diffère du montant dû)
- Mise à jour automatique de la trésorerie
- Génération d'une écriture comptable

### US-VENTE-004: En tant que gestionnaire, je veux que le stock soit mis à jour automatiquement
**Critères d'acceptation :**
- Mouvement de stock créé automatiquement lors de la vente
- Mise à jour du stock théorique
- Historique des mouvements de stock
- Lien avec la vente origine
- Génération des écritures comptables correspondantes

### US-VENTE-005: En tant que gestionnaire, je veux que la trésorerie soit mise à jour
**Critères d'acceptation :**
- Crédit de la trésorerie lors du paiement en espèces
- Suivi des mouvements de trésorerie par vente
- Mise à jour des soldes
- Lien avec les modes de paiement
- Historique des transactions

### US-VENTE-006: En tant que gestionnaire, je veux que les écritures comptables soient générées automatiquement
**Critères d'acceptation :**
- Génération automatique des écritures pour chaque vente
- Prise en compte des paiements
- Respect des règles comptables en vigueur
- Lien avec les comptes appropriés
- Validation comptable des écritures générées

### US-VENTE-007: En tant que gestionnaire, je veux pouvoir modifier ou annuler une vente
**Critères d'acceptation :**
- Possibilité de modifier une vente non confirmée
- Possibilité d'annuler une vente (avec motif autorisé)
- Historique des modifications/annulations
- Contrôle des permissions pour modification/annulation
- Impact sur les écritures comptables, trésorerie, dette et stocks

### US-VENTE-008: En tant que gestionnaire, je veux suivre les performances des pompistes
**Critères d'acceptation :**
- Calcul des ventes totales par pompiste
- Calcul des volumes vendus par pompiste
- Calcul des indicateurs de productivité
- Analyse comparative entre pompistes
- Historique des performances
- Génération de rapports de performance

### US-VENTE-009: En tant que gestionnaire, je veux analyser le rendement des pompistes
**Critères d'acceptation :**
- Calcul des KPIs de rendement
- Analyse des écarts entre index de pistolets et ventes
- Calcul des taux de conversion
- Identification des anomalies
- Représentation graphique des données
- Suivi évolutif des performances

### US-VENTE-010: En tant que gestionnaire, je veux suivre les écarts anormaux
**Critères d'acceptation :**
- Détection automatique des écarts anormaux
- Définition de seuils d'écart acceptables
- Alertes pour les écarts significatifs
- Historique des écarts
- Investigation et classement des écarts
- Rapports de suivi des écarts

### US-VENTE-011: En tant que caissier, je veux émettre un ticket de caisse pour les ventes boutique
**Critères d'acceptation :**
- Création automatique d'un ticket de caisse
- Détail des produits vendus
- Montant total et mode de paiement
- Numérotation unique du ticket
- Date et heure d'émission
- Signature numérique ou nom du caissier

### US-VENTE-012: En tant que gestionnaire, je veux effectuer l'arrêt de compte caissier
**Critères d'acceptation :**
- Calcul des totaux de vente pour la période
- Comparaison avec les recettes effectives
- Identification des écarts éventuels
- Validation des écarts
- Clôture de la caisse pour la période
- Historique des arrêts de compte

### US-VENTE-013: En tant que gestionnaire, je veux gérer les ventes de services
**Critères d'acceptation :**
- Création de ventes pour des services (lavages, réparations, etc.)
- Association avec un client si applicable
- Gestion du personnel affecté
- Suivi de la productivité des services
- Calcul des coûts et marges pour les services

### US-VENTE-014: En tant que gestionnaire, je veux analyser la productivité
**Critères d'acceptation :**
- Calcul des indicateurs de productivité
- Analyse comparative entre différentes périodes
- Analyse par type de vente (carburant, boutique, services)
- Identification des tendances
- Représentation graphique
- Export des données pour analyse

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `utilisateurs` - données des utilisateurs (pompistes, caissiers)
- `pompistes` - données spécifiques des pompistes
- `caissiers` - données spécifiques des caissiers
- `cuves` - données des cuves
- `carburants` - données des carburants
- `pistolets` - données des pistolets
- `articles` - données des articles de boutique
- `clients` - données des clients
- `stations` - données des stations
- `tresoreries` - données des trésoreries
- `mode_paiements` - données des modes de paiement
- `comptes_comptables` - données des comptes comptables
- `ecritures_comptables` - données des écritures comptables
- `stocks` - données des stocks
- `stocks_mouvements` - données des mouvements de stock

### Nouvelles tables à créer

```sql
-- Table pour les ventes
CREATE TABLE IF NOT EXISTS ventes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_vente VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    type_vente VARCHAR(20) NOT NULL CHECK (type_vente IN ('carburant', 'boutique', 'service')),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id),
    date_vente DATE NOT NULL,
    heure_vente TIME NOT NULL,
    date_validation DATE,
    heure_validation TIME,
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Terminee', 'Payee', 'Annulee')),
    montant_ht NUMERIC(18,2) NOT NULL,
    montant_tva NUMERIC(18,2) NOT NULL,
    montant_ttc NUMERIC(18,2) NOT NULL,
    montant_paye NUMERIC(18,2) DEFAULT 0,
    ecart_paiement NUMERIC(18,2) DEFAULT 0, -- Écart entre montant TTC et montant payé
    commentaire TEXT,
    utilisateur_modification_id UUID REFERENCES utilisateurs(id),
    date_modification TIMESTAMPTZ,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    compagnie_id UUID REFERENCES utilisateurs(id)
);

-- Table pour les détails des ventes de carburant
CREATE TABLE IF NOT EXISTS ventes_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id) ON DELETE CASCADE,
    pistolet_id UUID REFERENCES pistolets(id),
    cuve_id UUID REFERENCES cuves(id),
    carburant_id UUID REFERENCES carburants(id),
    index_depart NUMERIC(18,3), -- Index avant la distribution
    index_fin NUMERIC(18,3), -- Index après la distribution
    volume_distribue NUMERIC(18,3) GENERATED ALWAYS AS (index_fin - index_depart) STORED,
    quantite_facturee NUMERIC(18,3) NOT NULL, -- Quantité facturée au client
    prix_unitaire_ht NUMERIC(18,4) NOT NULL,
    utilisateur_pompiste_id UUID REFERENCES utilisateurs(id),
    date_vente DATE NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    ecart_index NUMERIC(18,3) GENERATED ALWAYS AS (volume_distribue - quantite_facturee) STORED, -- Écart entre index et quantité facturée
    seuil_ecart_acceptable NUMERIC(18,3) DEFAULT 2, -- En litres, seuil configurable
    commentaire_ecart TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les détails des ventes de boutique
CREATE TABLE IF NOT EXISTS ventes_boutique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id),
    quantite_vendue NUMERIC(18,3) NOT NULL,
    prix_unitaire_ht NUMERIC(18,4) NOT NULL,
    taux_tva NUMERIC(5,2) NOT NULL,
    utilisateur_caissier_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les détails des ventes de services
CREATE TABLE IF NOT EXISTS ventes_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id) ON DELETE CASCADE,
    libelle_service VARCHAR(100) NOT NULL,
    description TEXT,
    prix_ht NUMERIC(18,2) NOT NULL,
    utilisateur_service_id UUID REFERENCES utilisateurs(id), -- Employé qui a effectué le service
    duree_service INTERVAL, -- Durée du service si applicable
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les paiements des ventes
CREATE TABLE IF NOT EXISTS paiements_ventes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id),
    mode_paiement_id UUID REFERENCES mode_paiements(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    montant_paiement NUMERIC(18,2) NOT NULL,
    date_paiement DATE NOT NULL,
    heure_paiement TIME NOT NULL,
    reference_paiement VARCHAR(100), -- Numéro de chèque, etc.
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les arrêts de compte caissier
CREATE TABLE IF NOT EXISTS arrets_compte_caissier (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    caissier_id UUID REFERENCES utilisateurs(id),
    date_arret DATE NOT NULL,
    heure_arret TIME NOT NULL,
    montant_theorique NUMERIC(18,2) NOT NULL, -- Montant total des ventes boutique
    montant_reel NUMERIC(18,2) NOT NULL, -- Montant réellement en caisse
    ecart NUMERIC(18,2) GENERATED ALWAYS AS (montant_reel - montant_theorique) STORED,
    commentaire_arret TEXT,
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Valide', 'Rejete')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les indicateurs de performance pompiste
CREATE TABLE IF NOT EXISTS indicateurs_performance_pompiste (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pompiste_id UUID REFERENCES utilisateurs(id),
    periode_statistique DATE NOT NULL, -- Première date de la période (jour, semaine ou mois)
    type_periode VARCHAR(10) NOT NULL CHECK (type_periode IN ('jour', 'semaine', 'mois')), -- Unité de la période
    ventes_total_ht NUMERIC(18,2) DEFAULT 0,
    volume_total_distribue NUMERIC(18,3) DEFAULT 0,
    nombre_ventes INTEGER DEFAULT 0,
    ecart_total_index NUMERIC(18,3) DEFAULT 0,
    nombre_ecarts INTEGER DEFAULT 0,
    taux_conversion NUMERIC(5,2) DEFAULT 0, -- En pourcentage
    indicateur_productivite NUMERIC(5,2) DEFAULT 0, -- Score de productivité
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi des écarts anormaux
CREATE TABLE IF NOT EXISTS suivis_ecarts_anormaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_ecart VARCHAR(50) NOT NULL, -- 'index_pistolet', 'caisse', etc.
    objet_id UUID NOT NULL, -- ID de la vente ou du pistolet concerné
    date_detection DATE NOT NULL,
    valeur_ecart NUMERIC(18,3) NOT NULL,
    seuil_alerte NUMERIC(18,3) NOT NULL,
    statut VARCHAR(20) DEFAULT 'Detecte' CHECK (statut IN ('Detecte', 'Enquete', 'Traite', 'Ferme')),
    utilisateur_detecteur_id UUID REFERENCES utilisateurs(id),
    utilisateur_traitant_id UUID REFERENCES utilisateurs(id),
    date_traitement DATE,
    motif_ecart TEXT,
    action_corrective TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les ventes
CREATE INDEX IF NOT EXISTS idx_ventes_station ON ventes(station_id);
CREATE INDEX IF NOT EXISTS idx_ventes_date ON ventes(date_vente);
CREATE INDEX IF NOT EXISTS idx_ventes_statut ON ventes(statut);
CREATE INDEX IF NOT EXISTS idx_ventes_type ON ventes(type_vente);
CREATE INDEX IF NOT EXISTS idx_ventes_utilisateur_createur ON ventes(utilisateur_createur_id);

-- Index pour les ventes de carburant
CREATE INDEX IF NOT EXISTS idx_ventes_carburant_vente ON ventes_carburant(vente_id);
CREATE INDEX IF NOT EXISTS idx_ventes_carburant_pistolet ON ventes_carburant(pistolet_id);
CREATE INDEX IF NOT EXISTS idx_ventes_carburant_cuve ON ventes_carburant(cuve_id);
CREATE INDEX IF NOT EXISTS idx_ventes_carburant_pompiste ON ventes_carburant(utilisateur_pompiste_id);

-- Index pour les ventes de boutique
CREATE INDEX IF NOT EXISTS idx_ventes_boutique_vente ON ventes_boutique(vente_id);
CREATE INDEX IF NOT EXISTS idx_ventes_boutique_article ON ventes_boutique(article_id);
CREATE INDEX IF NOT EXISTS idx_ventes_boutique_caissier ON ventes_boutique(utilisateur_caissier_id);

-- Index pour les ventes de services
CREATE INDEX IF NOT EXISTS idx_ventes_services_vente ON ventes_services(vente_id);
CREATE INDEX IF NOT EXISTS idx_ventes_services_utilisateur ON ventes_services(utilisateur_service_id);

-- Index pour les paiements des ventes
CREATE INDEX IF NOT EXISTS idx_paiements_ventes_vente ON paiements_ventes(vente_id);
CREATE INDEX IF NOT EXISTS idx_paiements_ventes_tresorerie ON paiements_ventes(tresorerie_id);
CREATE INDEX IF NOT EXISTS idx_paiements_ventes_date ON paiements_ventes(date_paiement);

-- Index pour les arrêts de compte caissier
CREATE INDEX IF NOT EXISTS idx_arrets_compte_caissier_caissier ON arrets_compte_caissier(caissier_id);
CREATE INDEX IF NOT EXISTS idx_arrets_compte_caissier_date ON arrets_compte_caissier(date_arret);

-- Index pour les indicateurs de performance pompiste
CREATE INDEX IF NOT EXISTS idx_indicateurs_pompiste_pompiste ON indicateurs_performance_pompiste(pompiste_id);
CREATE INDEX IF NOT EXISTS idx_indicateurs_pompiste_periode ON indicateurs_performance_pompiste(periode_statistique);

-- Index pour le suivi des écarts anormaux
CREATE INDEX IF NOT EXISTS idx_suivis_ecarts_type ON suivis_ecarts_anormaux(type_ecart);
CREATE INDEX IF NOT EXISTS idx_suivis_ecarts_date ON suivis_ecarts_anormaux(date_detection);
CREATE INDEX IF NOT EXISTS idx_suivis_ecarts_statut ON suivis_ecarts_anormaux(statut);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour générer automatiquement le numéro de vente
CREATE OR REPLACE FUNCTION generate_numero_vente()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : VTE-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_vente, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_vente FROM 5 FOR 3) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM ventes
    WHERE SUBSTRING(numero_vente FROM 5 FOR 8) = date_str;
    
    numero := 'VTE-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    NEW.numero_vente := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_vente
    BEFORE INSERT ON ventes
    FOR EACH ROW EXECUTE FUNCTION generate_numero_vente();

-- Trigger pour empêcher la modification d'une vente validée
CREATE OR REPLACE FUNCTION prevent_vente_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'une vente validée ou annulée
    IF OLD.statut = 'Payee' OR OLD.statut = 'Annulee' THEN
        RAISE EXCEPTION 'Impossible de modifier une vente déjà payée ou annulée';
    END IF;

    NEW.date_modification := now();
    NEW.utilisateur_modification_id := NEW.utilisateur_createur_id; -- Doit être mis à jour avec l'utilisateur réel

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_vente_modification
    BEFORE UPDATE ON ventes
    FOR EACH ROW EXECUTE FUNCTION prevent_vente_modification();

-- Trigger pour valider les écarts d'index de pistolet
CREATE OR REPLACE FUNCTION validate_ecart_index_pistolet()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier que l'écart entre index et quantité facturée est acceptable
    IF ABS(NEW.ecart_index) > NEW.seuil_ecart_acceptable THEN
        -- Enregistrer l'écart anormal dans la table de suivi
        INSERT INTO suivis_ecarts_anormaux (
            type_ecart,
            objet_id,
            date_detection,
            valeur_ecart,
            seuil_alerte,
            utilisateur_detecteur_id
        )
        VALUES (
            'index_pistolet',
            NEW.id,
            NEW.date_vente,
            NEW.ecart_index,
            NEW.seuil_ecart_acceptable,
            NEW.utilisateur_pompiste_id
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_ecart_index_pistolet
    AFTER INSERT OR UPDATE ON ventes_carburant
    FOR EACH ROW EXECUTE FUNCTION validate_ecart_index_pistolet();

-- Trigger pour mettre à jour les indicateurs de performance pompiste
CREATE OR REPLACE FUNCTION update_indicateurs_pompiste()
RETURNS TRIGGER AS $$
DECLARE
    periode DATE;
    type_periode VARCHAR(10);
BEGIN
    -- Déterminer la période (jour, semaine, mois) pour le calcul
    periode := DATE_TRUNC('day', NEW.date_vente)::DATE; -- Pour des indicateurs journaliers
    type_periode := 'jour';
    
    -- Mettre à jour ou insérer les indicateurs
    INSERT INTO indicateurs_performance_pompiste (
        pompiste_id,
        periode_statistique,
        type_periode,
        ventes_total_ht,
        volume_total_distribue,
        nombre_ventes,
        ecart_total_index,
        nombre_ecarts
    )
    VALUES (
        NEW.utilisateur_pompiste_id,
        periode,
        type_periode,
        NEW.quantite_facturee * NEW.prix_unitaire_ht,
        NEW.volume_distribue,
        1,
        ABS(NEW.ecart_index),
        CASE WHEN ABS(NEW.ecart_index) > NEW.seuil_ecart_acceptable THEN 1 ELSE 0 END
    )
    ON CONFLICT (pompiste_id, periode_statistique, type_periode)
    DO UPDATE SET
        ventes_total_ht = indicateurs_performance_pompiste.ventes_total_ht + (NEW.quantite_facturee * NEW.prix_unitaire_ht),
        volume_total_distribue = indicateurs_performance_pompiste.volume_total_distribue + NEW.volume_distribue,
        nombre_ventes = indicateurs_performance_pompiste.nombre_ventes + 1,
        ecart_total_index = indicateurs_performance_pompiste.ecart_total_index + ABS(NEW.ecart_index),
        nombre_ecarts = indicateurs_performance_pompiste.nombre_ecarts + 
                        CASE WHEN ABS(NEW.ecart_index) > NEW.seuil_ecart_acceptable THEN 1 ELSE 0 END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_indicateurs_pompiste
    AFTER INSERT ON ventes_carburant
    FOR EACH ROW EXECUTE FUNCTION update_indicateurs_pompiste();

-- Trigger pour mettre à jour la trésorerie après un paiement
CREATE OR REPLACE FUNCTION update_tresorerie_vente()
RETURNS TRIGGER AS $$
BEGIN
    -- Mettre à jour le solde de la trésorerie concernée
    UPDATE tresoreries
    SET 
        solde_theorique = solde_theorique + NEW.montant_paiement,
        solde_reel = solde_reel + NEW.montant_paiement
    WHERE id = NEW.tresorerie_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tresorerie_vente
    AFTER INSERT ON paiements_ventes
    FOR EACH ROW EXECUTE FUNCTION update_tresorerie_vente();
```

## 4. API Backend

### 4.1 Gestion des ventes de carburant

#### POST /api/ventes/carburant
**Description:** Créer une nouvelle vente de carburant

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "station_id": "uuid",
  "details": [
    {
      "pistolet_id": "uuid",
      "carburant_id": "uuid",
      "index_depart": "decimal (max 18,3)",
      "index_fin": "decimal (max 18,3)",
      "prix_unitaire_ht": "decimal (max 18,4)",
      "utilisateur_pompiste_id": "uuid"
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
    "numero_vente": "string",
    "station_id": "uuid",
    "date_vente": "date",
    "heure_vente": "time",
    "statut": "string",
    "montant_ht": "decimal",
    "montant_tva": "decimal",
    "montant_ttc": "decimal",
    "commentaire": "string",
    "type_vente": "carburant",
    "date_creation": "datetime"
  },
  "message": "Vente de carburant créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Vente créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station/pistolet/carburant non trouvé
- 409: Conflit (par exemple, index invalide)
- 500: Erreur interne du serveur

#### PUT /api/ventes/carburant/{id}
**Description:** Mettre à jour une vente de carburant

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "details": [
    {
      "id": "uuid (optionnel, pour mise à jour)",
      "pistolet_id": "uuid",
      "carburant_id": "uuid",
      "index_depart": "decimal (max 18,3)",
      "index_fin": "decimal (max 18,3)",
      "prix_unitaire_ht": "decimal (max 18,4)",
      "utilisateur_pompiste_id": "uuid"
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
    "numero_vente": "string",
    "station_id": "uuid",
    "date_vente": "date",
    "heure_vente": "time",
    "statut": "string",
    "montant_ht": "decimal",
    "montant_tva": "decimal",
    "montant_ttc": "decimal",
    "commentaire": "string",
    "date_modification": "datetime"
  },
  "message": "Vente de carburant mise à jour avec succès"
}
```

**HTTP Status Codes:**
- 200: Vente mise à jour avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Vente non trouvée
- 409: Impossible de modifier une vente terminée ou annulée
- 500: Erreur interne du serveur

### 4.2 Gestion des ventes de boutique

#### POST /api/ventes/boutique
**Description:** Créer une nouvelle vente de produits de boutique

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "station_id": "uuid",
  "utilisateur_caissier_id": "uuid",
  "details": [
    {
      "article_id": "uuid",
      "quantite_vendue": "decimal (max 18,3)",
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
    "numero_vente": "string",
    "station_id": "uuid",
    "utilisateur_caissier_id": "uuid",
    "date_vente": "date",
    "heure_vente": "time",
    "statut": "string",
    "montant_ht": "decimal",
    "montant_tva": "decimal",
    "montant_ttc": "decimal",
    "commentaire": "string",
    "type_vente": "boutique",
    "date_creation": "datetime"
  },
  "message": "Vente de boutique créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Vente créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station/article/caissier non trouvé
- 500: Erreur interne du serveur

### 4.3 Gestion des paiements

#### POST /api/ventes/{id}/paiements
**Description:** Enregistrer un paiement pour une vente

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
  "heure_paiement": "time (format HH:MM:SS)",
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
    "vente_id": "uuid",
    "mode_paiement_id": "uuid",
    "tresorerie_id": "uuid",
    "montant_paiement": "decimal",
    "date_paiement": "date",
    "heure_paiement": "time",
    "reference_paiement": "string",
    "commentaire": "string",
    "ecart_paiement": "decimal"
  },
  "message": "Paiement enregistré avec succès"
}
```

**HTTP Status Codes:**
- 200: Paiement enregistré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Vente/mode_paiement/tresorerie non trouvé
- 409: Montant du paiement supérieur au montant dû
- 500: Erreur interne du serveur

### 4.4 Arrêt de compte caissier

#### POST /api/caisses/arret-compte
**Description:** Enregistrer l'arrêt de compte d'un caissier

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "caissier_id": "uuid",
  "date_arret": "date (format YYYY-MM-DD)",
  "heure_arret": "time (format HH:MM:SS)",
  "montant_theorique": "decimal (max 18,2)",
  "montant_reel": "decimal (max 18,2)",
  "commentaire_arret": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "caissier_id": "uuid",
    "date_arret": "date",
    "heure_arret": "time",
    "montant_theorique": "decimal",
    "montant_reel": "decimal",
    "ecart": "decimal",
    "commentaire_arret": "string",
    "statut": "EnCours"
  },
  "message": "Arrêt de compte caissier enregistré avec succès"
}
```

**HTTP Status Codes:**
- 200: Arrêt de compte enregistré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Caissier non trouvé
- 500: Erreur interne du serveur

### 4.5 Suivi des performances

#### GET /api/performances/pompistes
**Description:** Obtenir les indicateurs de performance des pompistes

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- pompiste_id: uuid (optionnel)
- periode_debut: date (format YYYY-MM-DD)
- periode_fin: date (format YYYY-MM-DD)
- type_periode: jour|semaine|mois (default: jour)
- station_id: uuid (optionnel)

**Response:**
```json
{
  "success": true,
  "data": {
    "indicateurs": [
      {
        "id": "uuid",
        "pompiste_id": "uuid",
        "nom_pompiste": "string",
        "periode_statistique": "date",
        "type_periode": "string",
        "ventes_total_ht": "decimal",
        "volume_total_distribue": "decimal",
        "nombre_ventes": "integer",
        "ecart_total_index": "decimal",
        "nombre_ecarts": "integer",
        "taux_conversion": "decimal",
        "indicateur_productivite": "decimal"
      }
    ]
  },
  "message": "Indicateurs de performance récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 400: Paramètres invalides
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

### 4.6 Suivi des écarts anormaux

#### GET /api/suivi/ecarts-anormaux
**Description:** Obtenir le suivi des écarts anormaux

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- type_ecart: string (optionnel)
- statut: string (optionnel)
- date_debut: date (format YYYY-MM-DD)
- date_fin: date (format YYYY-MM-DD)
- objet_id: uuid (optionnel)

**Response:**
```json
{
  "success": true,
  "data": {
    "ecarts": [
      {
        "id": "uuid",
        "type_ecart": "string",
        "objet_id": "uuid",
        "date_detection": "date",
        "valeur_ecart": "decimal",
        "seuil_alerte": "decimal",
        "statut": "string",
        "utilisateur_detecteur_id": "uuid",
        "utilisateur_traitant_id": "uuid",
        "date_traitement": "date",
        "motif_ecart": "string",
        "action_corrective": "string"
      }
    ]
  },
  "message": "Écarts anormaux récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 400: Paramètres invalides
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de validation des ventes
1. La date de vente ne peut être dans le futur
2. Les quantités vendues doivent être positives
3. Pour les ventes de carburant, les index de pistolet doivent être cohérents
4. Les prix unitaires doivent être positifs
5. Les écarts d'index dépassant le seuil sont signalés
6. Seuls les utilisateurs autorisés peuvent valider les ventes

### Règles de calcul des prix
1. Le montant HT est la somme des (quantité * prix unitaire HT) pour tous les détails
2. La TVA est calculée selon les taux applicables aux articles/carburants
3. Le montant TTC est la somme du montant HT et de la TVA
4. Le prix unitaire TTC est calculé selon la formule: prix_HT * (1 + taux_TVA/100)

### Règles de gestion des paiements
1. Le montant payé ne peut pas dépasser le montant dû
2. Les écarts de paiement sont enregistrés pour suivi
3. Le paiement est lié à une trésorerie spécifique
4. Le mode de paiement doit être valide
5. Les paiements augmentent le solde de la trésorerie

### Règles de suivi des performances pompiste
1. Calcul des ventes totales par pompiste pour une période
2. Calcul du volume total distribué par pompiste
3. Calcul du nombre de ventes effectuées
4. Calcul du total des écarts d'index
5. Calcul des indicateurs de productivité et de taux de conversion

### Règles de gestion des écarts anormaux
1. Les écarts d'index dépassant le seuil sont automatiquement détectés
2. Les écarts sont classifiés par type (pistolet, caisse, etc.)
3. Les écarts nécessitent une enquête et une action corrective
4. Les seuils d'alerte sont configurables par type d'écart
5. L'historique des écarts est maintenu pour analyse

### Règles de modification/annulation
1. Les ventes en statut "EnCours" peuvent être modifiées
2. Les ventes en statut "Terminee", "Payee" ou "Annulee" ne peuvent être modifiées
3. Les ventes peuvent être annulées avec un motif (impact sur les écritures comptables, trésorerie, stock)
4. L'annulation d'une vente nécessite des droits spécifiques

### Règles de calcul des arrêts de compte caissier
1. Le montant théorique est la somme des ventes de boutique pour la période
2. L'écart est calculé comme la différence entre le montant réel et théorique
3. Les écarts importants nécessitent une validation supplémentaire
4. Les arrêts de compte sont historisés pour suivi

### Impacts sur d'autres modules
1. Le module de vente déclenche automatiquement des mises à jour dans:
   - Le module de stock (mouvements de stock)
   - Le module de trésorerie (enregistrement des paiements)
   - Le module comptable (génération des écritures)
   - Le module de reporting (indicateurs de performance)
   - Le module de sécurité (journalisation des actions sensibles)

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
utilisateurs ||--o{ ventes (createur)
utilisateurs ||--o{ ventes_carburant (pompiste)
utilisateurs ||--o{ ventes_boutique (caissier)
stations ||--o{ ventes
pistolets ||--o{ ventes_carburant
cuves ||--o{ ventes_carburant
carburants ||--o{ ventes_carburant
articles ||--o{ ventes_boutique
ventes ||--o{ paiements_ventes
ventes ||--o{ ventes_carburant
ventes ||--o{ ventes_boutique
ventes ||--o{ ventes_services
suivis_ecarts_anormaux }o--o{ ventes_carburant
indicateurs_performance_pompiste }o--o{ utilisateurs
arrets_compte_caissier }o--o{ utilisateurs
```

### Diagramme de séquence pour une vente de carburant
```
Pompiste -> API: POST /api/ventes/carburant
API -> Base de données: Créer la vente (statut: EnCours)
API -> Base de données: Enregistrer les détails de la vente
API -> Base de données: Calculer les écarts d'index
API -> Base de données: Détecter les écarts anormaux (si applicable)
API -> Gestionnaire: Alertes pour écarts anormaux (si applicable)
API -> Pompiste: Retourner la vente créée

Pompiste -> API: POST /api/ventes/{id}/paiements
API -> Base de données: Enregistrer le paiement
API -> Base de données: Mettre à jour la trésorerie
API -> API: Générer l'écriture comptable de vente
API -> API: Générer l'écriture comptable de paiement
API -> API: Générer le mouvement de stock
API -> Base de données: Mettre le statut à "Payee"
API -> Pompiste: Retourner confirmation de paiement
```

## 7. Tests Requis

### Tests unitaires
1. Test de la fonction de génération automatique de numéro de vente
2. Test des validations de données pour les différents endpoints
3. Test des calculs de montants (HT, TVA, TTC)
4. Test des calculs d'écarts d'index
5. Test des calculs d'écarts de trésorerie
6. Test des fonctions de mise à jour des indicateurs de performance

### Tests d'intégration
1. Test complet du processus de vente de carburant
2. Test complet du processus de vente de boutique
3. Test du processus d'arrêt de compte caissier
4. Test de la génération automatique des écritures comptables
5. Test de la mise à jour des stocks
6. Test de la mise à jour de la trésorerie
7. Test de la détection des écarts anormaux

### Tests de charge/performance
1. Test de performance pour des centaines de ventes simultanées
2. Test de performance pour des saisies d'index multiples
3. Test de performance pour des calculs de performance
4. Test de performance pour des arrêts de compte
5. Test de la génération d'écritures comptables pour de grands volumes

### Jeux de données de test
1. Données de ventes valides avec différentes configurations
2. Données de pompistes et caissiers avec différentes caractéristiques
3. Données de pistolets, cuves et carburants pour les tests de vente
4. Données d'articles pour les tests de vente de boutique
5. Données de trésoreries et de modes de paiement
6. Données de comptes comptables pour les tests d'écritures

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contrôles d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de gestion des ventes (validation, paiement, suivi)
6. [ ] Implémenter la logique de validation des données
7. [ ] Créer les utilitaires de génération d'écritures comptables
8. [ ] Implémenter la mise à jour automatique des stocks
9. [ ] Créer les algorithmes pour le calcul des performances pompiste
10. [ ] Créer les tests unitaires et d'intégration
11. [ ] Implémenter la gestion des erreurs et logs
12. [ ] Créer les vues frontend pour la gestion des ventes (si applicable)
13. [ ] Documenter les endpoints API
14. [ ] Intégrer la détection automatique des écarts anormaux

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base pour la création de ventes
3. Développer les fonctionnalités de modification et d'annulation
4. Implémenter la gestion des paiements
5. Créer les fonctionnalités de suivi des performances
6. Intégrer la détection et le suivi des écarts anormaux
7. Intégrer la génération automatique des écritures comptables
8. Intégrer la mise à jour des stocks et de la trésorerie
9. Créer les fonctionnalités d'arrêt de compte caissier
10. Créer les tests
11. Optimiser les performances
12. Documenter la solution

### Livrables attendus
1. Code source complet avec commentaires
2. Scripts de migration de base de données
3. Documentation API
4. Jeux de tests et résultats
5. Documentation technique détaillée
6. Guide d'installation et de déploiement

## 9. Risques & Points de vigilance

### Points sensibles
1. La complexité du calcul des écarts d'index de pistolet
2. La gestion des différentes configurations de TVA pour les articles
3. La mise à jour des stocks en temps réel lors des ventes
4. La sécurité des données financières dans les transactions
5. La performance des calculs pour de grands volumes de données
6. La précision de la détection des écarts anormaux

### Risques techniques
1. Risque d'incohérence entre les index de pistolet et les ventes enregistrées
2. Risque d'erreurs dans la génération des écritures comptables
3. Risque de décalage entre les données de stock théorique et physique
4. Risque de problèmes de performances avec de grands volumes
5. Risque de perte de données en cas de panne pendant les processus
6. Risque de manipulation des données par des utilisateurs non autorisés

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples règles de gestion
2. Risque de duplication de logique entre ventes carburant et boutique
3. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
4. Besoin de maintenance continue pour les règles de validation des écarts
5. Risque de dépendance excessive à des bibliothèques tierces pour les calculs complexes