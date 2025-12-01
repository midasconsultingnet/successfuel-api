# Technical Specification - Module de Rapports

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de rapports permet de générer des documents comptables et de gestion pour les stations-service. Il fournit aux gestionnaires et aux responsables des outils d'analyse pour évaluer la performance, la conformité, et les tendances de l'exploitation. Les rapports couvrent à la fois la comptabilité (bilan, grand livre, balance, journal) et la gestion opérationnelle (rendement pompiste, analyse des stocks, KPIs, etc.).

### Problème à résoudre
Sans un module de rapports complet, le système SuccessFuel ne permettrait pas aux gestionnaires de prendre des décisions éclairées basées sur des données précises et actualisées. Il est nécessaire de disposer d'outils de reporting pour répondre aux obligations comptables, fiscales, et pour optimiser la gestion des stations.

### Définition du périmètre
Le périmètre du sprint couvre :
- Génération des rapports comptables (bilan, grand livre, balance, journal)
- Génération des déclarations fiscales
- Suivi de la conformité
- Analyse de la consommation, rendement pompiste/caissier
- Analyse des stocks, dettes/créances, rentabilité
- Calcul des indicateurs KPIs
- Prévisions et analyse des tendances
- Analyse comparative entre périodes ou stations

## 2. User Stories & Critères d'acceptation

### US-REPORT-001: En tant que gestionnaire, je veux générer le bilan comptable
**Critères d'acceptation :**
- Génération du bilan à une date spécifique
- Présentation des actifs, passifs et capitaux propres
- Calcul automatique des soldes et des totaux
- Export au format PDF et Excel
- Intégration avec les écritures comptables existantes
- Validation de la cohérence des données

### US-REPORT-002: En tant que gestionnaire, je veux générer le grand livre
**Critères d'acceptation :**
- Affichage de toutes les écritures comptables par compte
- Tri par date, numéro de compte ou type d'écriture
- Filtrage par période, station ou compagnie
- Affichage du solde initial et final pour chaque compte
- Export au format PDF et Excel
- Pagination pour les grandes quantités de données

### US-REPORT-003: En tant que gestionnaire, je veux générer la balance des comptes
**Critères d'acceptation :**
- Affichage des soldes de tous les comptes à une date donnée
- Distinction entre les soldes débiteurs et créditeurs
- Calcul du total des soldes débiteurs et créditeurs
- Vérification de l'équilibre comptable
- Export au format PDF et Excel
- Comparaison avec la balance de l'exercice précédent

### US-REPORT-004: En tant que gestionnaire, je veux générer le journal des écritures
**Critères d'acceptation :**
- Affichage de toutes les écritures dans l'ordre chronologique
- Présentation structurée des écritures (date, pièce, compte, libellé, débit, crédit)
- Tri et filtrage par période, type d'opération ou station
- Pagination pour les grandes quantités de données
- Export au format PDF et Excel
- Validation de la complétude des écritures

### US-REPORT-005: En tant que gestionnaire, je veux générer les déclarations fiscales
**Critères d'acceptation :**
- Calcul automatique des impôts dus selon les taux fiscaux
- Génération des déclarations conformes aux normes fiscales locales
- Prise en compte des régimes fiscaux spécifiques
- Export au format PDF conforme aux exigences fiscales
- Historique des déclarations générées
- Intégration avec les données de ventes et d'achats

### US-REPORT-006: En tant que gestionnaire, je veux suivre la conformité fiscale
**Critères d'acceptation :**
- Suivi des obligations fiscales en cours
- Alertes pour les échéances fiscales
- Vérification de la complétude des déclarations
- Historique des contrôles de conformité
- Export des données de conformité
- Intégration avec les calendriers fiscaux

### US-REPORT-007: En tant que gestionnaire, je veux analyser la consommation
**Critères d'acceptation :**
- Analyse de la consommation par type de carburant
- Évolution de la consommation sur différentes périodes
- Comparaison entre stations
- Analyse par client (si applicable)
- Représentation graphique des tendances
- Export des résultats pour analyse complémentaire

### US-REPORT-008: En tant que gestionnaire, je veux analyser le rendement des pompistes/caissiers
**Critères d'acceptation :**
- Calcul des indicateurs de performance (volume vendu, montant, etc.)
- Analyse comparative entre employés
- Suivi de la productivité dans le temps
- Identification des écarts de performance
- Génération de rapports individuels
- Intégration avec les données d'identité des employés

### US-REPORT-009: En tant que gestionnaire, je veux analyser les stocks
**Critères d'acceptation :**
- Évaluation de la valeur des stocks à une date donnée
- Analyse des mouvements de stock (entrée, sortie, ajustement)
- Identification des stocks périmés ou en surstock
- Calcul des ratios de rotation de stock
- Suivi des écarts entre théorique et physique
- Intégration avec les modules d'inventaire

### US-REPORT-010: En tant que gestionnaire, je veux analyser les dettes/créances
**Critères d'acceptation :**
- Évaluation du portefeuille client
- Analyse des créances âgées
- Suivi des engagements de paiement
- Calcul des ratios de recouvrement
- Évaluation des risques de crédit
- Intégration avec les données clients

### US-REPORT-011: En tant que gestionnaire, je veux analyser la rentabilité
**Critères d'acceptation :**
- Calcul des marges bénéficiaires par produit/cuve
- Analyse des coûts directs et indirects
- Calcul des indicateurs de rentabilité (ROI, ROE, etc.)
- Analyse comparative entre stations
- Évolution de la rentabilité dans le temps
- Intégration avec les données comptables

### US-REPORT-012: En tant que gestionnaire, je veux calculer les indicateurs KPIs
**Critères d'acceptation :**
- Calcul automatisé des KPIs clés (CA, marge, productivité, etc.)
- Personnalisation des KPIs selon les besoins
- Visualisation sous forme de tableaux de bord
- Suivi d'évolution des KPIs dans le temps
- Seuils d'alerte configurables
- Export des KPIs pour reporting

### US-REPORT-013: En tant que gestionnaire, je veux accéder aux prévisions
**Critères d'acceptation :**
- Analyse prédictive basée sur les données historiques
- Prévisions de volume de ventes
- Prévisions de revenus et de coûts
- Modèles de prévision configurables
- Évaluation de la fiabilité des prévisions
- Intégration avec les données de tendance

### US-REPORT-014: En tant que gestionnaire, je veux accéder à l'analyse des tendances
**Critères d'acceptation :**
- Identification des tendances de consommation
- Analyse saisonnière des ventes
- Suivi des évolutions de prix
- Identification des anomalies
- Représentation graphique des tendances
- Intégration avec les données historiques

### US-REPORT-015: En tant que gestionnaire, je veux accéder à l'analyse comparative
**Critères d'acceptation :**
- Comparaison entre différentes stations
- Comparaison des performances sur différentes périodes
- Analyse des écarts de performance
- Représentation graphique des comparaisons
- Indicateurs de benchmarking
- Export des résultats de comparaison

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `ventes` - données des ventes
- `achats` - données des achats
- `stocks` - données des stocks
- `stocks_mouvements` - mouvements de stocks
- `utilisateurs` - données des utilisateurs/employés
- `stations` - données des stations
- `caisses` - données des caisses
- `pompistes` - données des pompistes
- `clients` - données des clients
- `fournisseurs` - données des fournisseurs
- `articles` - données des articles/produits
- `tresoreries` - données des trésoreries
- `ecritures_comptables` - données des écritures comptables
- `comptes_comptables` - données des comptes comptables

### Nouvelles tables à créer

```sql
-- Table pour les rapports comptables (bilan, grand livre, balance, journal)
CREATE TABLE IF NOT EXISTS rapports_comptables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_rapport VARCHAR(50) NOT NULL, -- 'bilan', 'grand_livre', 'balance', 'journal'
    nom_rapport VARCHAR(100) NOT NULL,
    description TEXT,
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    date_generation TIMESTAMPTZ NOT NULL DEFAULT now(),
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    parametres_generation JSONB, -- Paramètres spécifiques à la génération
    statut VARCHAR(20) DEFAULT 'Genere' CHECK (statut IN ('Genere', 'EnCours', 'Erreur', 'Archive')),
    fichier_export_path VARCHAR(255), -- Chemin vers le fichier exporté
    taille_fichier INTEGER, -- Taille du fichier en octets
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les déclarations fiscales
CREATE TABLE IF NOT EXISTS declarations_fiscales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_declaration VARCHAR(50) NOT NULL, -- 'TVA', 'IRSA', 'IS', etc.
    periode_declaration DATE NOT NULL, -- Mois/année concernée
    date_generation TIMESTAMPTZ NOT NULL DEFAULT now(),
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    montant_total NUMERIC(18,2),
    taux_applicable NUMERIC(5,2),
    montant_du NUMERIC(18,2),
    montant_paye NUMERIC(18,2) DEFAULT 0,
    date_paiement DATE,
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Genere', 'Soumis', 'Paye', 'Erreur')),
    fichier_declaration_path VARCHAR(255),
    fichier_releve_path VARCHAR(255),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi de la conformité
CREATE TABLE IF NOT EXISTS suivi_conformite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_conformite VARCHAR(50) NOT NULL, -- 'fiscale', 'comptable', 'reglementaire'
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_echeance DATE NOT NULL,
    date_realisation DATE,
    utilisateur_responsable_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'EnAttente' CHECK (statut IN ('EnAttente', 'EnCours', 'Realise', 'EnRetard', 'Exempte')),
    priorite INTEGER DEFAULT 1 CHECK (priorite BETWEEN 1 AND 5), -- 1 = basse, 5 = haute
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les indicateurs KPIs
CREATE TABLE IF NOT EXISTS indicateurs_kpi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_kpi VARCHAR(50) NOT NULL, -- Identifiant unique du KPI
    libelle_kpi VARCHAR(100) NOT NULL,
    description TEXT,
    categorie_kpi VARCHAR(50) NOT NULL, -- 'commercial', 'financier', 'operationnel', 'logistique'
    unite_mesure VARCHAR(20), -- '%', 'litres', 'ariary', 'nombre', etc.
    calcul_kpi TEXT, -- Expression SQL ou formule de calcul
    seuil_alerte_bas NUMERIC(18,4), -- Seuil bas d'alerte
    seuil_alerte_haut NUMERIC(18,4), -- Seuil haut d'alerte
    statut VARCHAR(15) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Archive')),
    est_personnalise BOOLEAN DEFAULT FALSE, -- TRUE si KPI personnalisé
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les valeurs des indicateurs KPIs
CREATE TABLE IF NOT EXISTS valeurs_indicateurs_kpi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicateur_kpi_id UUID REFERENCES indicateurs_kpi(id),
    valeur NUMERIC(18,4) NOT NULL,
    periode DATE NOT NULL, -- Date de référence pour la valeur
    station_id UUID REFERENCES stations(id),
    utilisateur_calcul_id UUID REFERENCES utilisateurs(id),
    date_calcul TIMESTAMPTZ NOT NULL DEFAULT now(),
    commentaire TEXT,
    est_previsionnel BOOLEAN DEFAULT FALSE,
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les prévisions
CREATE TABLE IF NOT EXISTS previsions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_prevision VARCHAR(50) NOT NULL, -- 'vente', 'ca', 'stock', 'rendement'
    libelle_prevision VARCHAR(100) NOT NULL,
    description TEXT,
    periode_prevision_debut DATE NOT NULL,
    periode_prevision_fin DATE NOT NULL,
    modele_utilise VARCHAR(100), -- Nom du modèle de prévision utilisé
    donnees_entrees JSONB, -- Données utilisées pour la prévision
    resultat_prevision JSONB, -- Résultat de la prévision
    precision_modele NUMERIC(5,2), -- Précision du modèle (en %)
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Calcule' CHECK (statut IN ('Calcule', 'Valide', 'Archive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les analyses
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_analyse VARCHAR(50) NOT NULL, -- 'tendance', 'comparative', 'performance'
    libelle_analyse VARCHAR(100) NOT NULL,
    description TEXT,
    periode_analyse_debut DATE NOT NULL,
    periode_analyse_fin DATE NOT NULL,
    donnees_analyse JSONB, -- Données brutes de l'analyse
    resultats_analyse JSONB, -- Résultats de l'analyse
    interpretations TEXT, -- Interprétations des résultats
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Termine' CHECK (statut IN ('EnCours', 'Termine', 'Archive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les rapports comptables
CREATE INDEX IF NOT EXISTS idx_rapports_comptables_type ON rapports_comptables(type_rapport);
CREATE INDEX IF NOT EXISTS idx_rapports_comptables_periode ON rapports_comptables(periode_debut, periode_fin);
CREATE INDEX IF NOT EXISTS idx_rapports_comptables_utilisateur ON rapports_comptables(utilisateur_generateur_id);
CREATE INDEX IF NOT EXISTS idx_rapports_comptables_station ON rapports_comptables(station_id);

-- Index pour les déclarations fiscales
CREATE INDEX IF NOT EXISTS idx_declarations_fiscales_type ON declarations_fiscales(type_declaration);
CREATE INDEX IF NOT EXISTS idx_declarations_fiscales_periode ON declarations_fiscales(periode_declaration);
CREATE INDEX IF NOT EXISTS idx_declarations_fiscales_station ON declarations_fiscales(station_id);

-- Index pour le suivi de la conformité
CREATE INDEX IF NOT EXISTS idx_suivi_conformite_type ON suivi_conformite(type_conformite);
CREATE INDEX IF NOT EXISTS idx_suivi_conformite_echeance ON suivi_conformite(date_echeance);
CREATE INDEX IF NOT EXISTS idx_suivi_conformite_statut ON suivi_conformite(statut);

-- Index pour les indicateurs KPIs
CREATE INDEX IF NOT EXISTS idx_indicateurs_kpi_code ON indicateurs_kpi(code_kpi);
CREATE INDEX IF NOT EXISTS idx_indicateurs_kpi_categorie ON indicateurs_kpi(categorie_kpi);
CREATE INDEX IF NOT EXISTS idx_indicateurs_kpi_actif ON indicateurs_kpi(statut);

-- Index pour les valeurs des indicateurs KPIs
CREATE INDEX IF NOT EXISTS idx_valeurs_kpi_indicateur ON valeurs_indicateurs_kpi(indicateur_kpi_id);
CREATE INDEX IF NOT EXISTS idx_valeurs_kpi_periode ON valeurs_indicateurs_kpi(periode);
CREATE INDEX IF NOT EXISTS idx_valeurs_kpi_station ON valeurs_indicateurs_kpi(station_id);

-- Index pour les prévisions
CREATE INDEX IF NOT EXISTS idx_previsions_type ON previsions(type_prevision);
CREATE INDEX IF NOT EXISTS idx_previsions_periode ON previsions(periode_prevision_debut, periode_prevision_fin);
CREATE INDEX IF NOT EXISTS idx_previsions_station ON previsions(station_id);

-- Index pour les analyses
CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(type_analyse);
CREATE INDEX IF NOT EXISTS idx_analyses_periode ON analyses(periode_analyse_debut, periode_analyse_fin);
CREATE INDEX IF NOT EXISTS idx_analyses_station ON analyses(station_id);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour empêcher la modification des rapports comptables générés
CREATE OR REPLACE FUNCTION prevent_rapport_comptable_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'un rapport déjà généré
    IF OLD.statut = 'Genere' OR OLD.statut = 'Archive' THEN
        RAISE EXCEPTION 'Impossible de modifier un rapport comptable déjà généré ou archivé';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_rapport_comptable_modification
    BEFORE UPDATE ON rapports_comptables
    FOR EACH ROW EXECUTE FUNCTION prevent_rapport_comptable_modification();

-- Trigger pour s'assurer que les déclarations fiscales sont conformes
CREATE OR REPLACE FUNCTION validate_declaration_fiscale()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier que le montant dû est positif
    IF NEW.montant_du < 0 THEN
        RAISE EXCEPTION 'Le montant dû ne peut pas être négatif';
    END IF;

    -- Si le statut est 'Paye', vérifier que la date de paiement est renseignée
    IF NEW.statut = 'Paye' AND NEW.date_paiement IS NULL THEN
        RAISE EXCEPTION 'La date de paiement doit être renseignée pour une déclaration payée';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_declaration_fiscale
    BEFORE INSERT OR UPDATE ON declarations_fiscales
    FOR EACH ROW EXECUTE FUNCTION validate_declaration_fiscale();

-- Trigger pour s'assurer de la cohérence des seuils d'alerte des KPIs
CREATE OR REPLACE FUNCTION validate_seuils_kpi()
RETURNS TRIGGER AS $$
BEGIN
    -- Si les seuils sont définis, vérifier que le seuil bas est inférieur au seuil haut
    IF NEW.seuil_alerte_bas IS NOT NULL AND NEW.seuil_alerte_haut IS NOT NULL THEN
        IF NEW.seuil_alerte_bas > NEW.seuil_alerte_haut THEN
            RAISE EXCEPTION 'Le seuil d''alerte bas doit être inférieur au seuil d''alerte haut';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_seuils_kpi
    BEFORE INSERT OR UPDATE ON indicateurs_kpi
    FOR EACH ROW EXECUTE FUNCTION validate_seuils_kpi();
```

## 4. API Backend

### 4.1 Génération des rapports comptables

#### POST /api/rapports/comptables/bilan
**Description:** Générer un rapport de bilan comptable

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "nom_rapport": "Bilan au {date_fin}",
    "date_generation": "datetime",
    "statut": "Genere",
    "fichier_export_path": "string",
    "taille_fichier": "integer"
  },
  "message": "Rapport de bilan généré avec succès"
}
```

**HTTP Status Codes:**
- 200: Rapport généré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

#### POST /api/rapports/comptables/grand-livre
**Description:** Générer un rapport de grand livre

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "compte_id": "uuid (optionnel)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "nom_rapport": "Grand livre du {date_debut} au {date_fin}",
    "date_generation": "datetime",
    "statut": "Genere",
    "fichier_export_path": "string",
    "taille_fichier": "integer"
  },
  "message": "Rapport de grand livre généré avec succès"
}
```

**HTTP Status Codes:**
- 200: Rapport généré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Compte/station non trouvée
- 500: Erreur interne du serveur

#### POST /api/rapports/comptables/balance
**Description:** Générer un rapport de balance des comptes

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "nom_rapport": "Balance du {date_debut} au {date_fin}",
    "date_generation": "datetime",
    "statut": "Genere",
    "fichier_export_path": "string",
    "taille_fichier": "integer"
  },
  "message": "Rapport de balance généré avec succès"
}
```

**HTTP Status Codes:**
- 200: Rapport généré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

#### POST /api/rapports/comptables/journal
**Description:** Générer un rapport de journal des écritures

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "type_operation": "string (optionnel)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "nom_rapport": "Journal du {date_debut} au {date_fin}",
    "date_generation": "datetime",
    "statut": "Genere",
    "fichier_export_path": "string",
    "taille_fichier": "integer"
  },
  "message": "Rapport de journal généré avec succès"
}
```

**HTTP Status Codes:**
- 200: Rapport généré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

### 4.2 Génération des déclarations fiscales

#### POST /api/rapports/fiscaux/declaration
**Description:** Générer une déclaration fiscale

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_declaration": "TVA|IRSA|IS|etc.",
  "periode_declaration": "date (format YYYY-MM-01)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type_declaration": "string",
    "periode_declaration": "date",
    "montant_total": "decimal",
    "montant_du": "decimal",
    "date_generation": "datetime",
    "statut": "Genere",
    "fichier_declaration_path": "string"
  },
  "message": "Déclaration fiscale générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Déclaration générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

### 4.3 Suivi de la conformité

#### GET /api/rapports/conformite
**Description:** Obtenir le suivi des obligations de conformité

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- type_conformite: string (optionnel)
- statut: string (optionnel)
- date_echeance_debut: date (optionnel)
- date_echeance_fin: date (optionnel)
- station_id: uuid (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "conformites": [
      {
        "id": "uuid",
        "type_conformite": "string",
        "libelle": "string",
        "description": "string",
        "date_echeance": "date",
        "date_realisation": "date (nullable)",
        "statut": "string",
        "priorite": "integer",
        "commentaire": "string (nullable)"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Données de conformité récupérées avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

### 4.4 Analyse de la consommation

#### POST /api/rapports/analyse/consommation
**Description:** Générer une analyse de consommation

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "type_carburant": "string (optionnel)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "libelle_analyse": "Analyse de consommation du {date_debut} au {date_fin}",
    "resultats_analyse": {
      "donnees_brutes": {},
      "tendances": {},
      "comparaisons": {}
    },
    "interpretations": "string",
    "date_generation": "datetime"
  },
  "message": "Analyse de consommation générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Analyse générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

### 4.5 Analyse du rendement

#### POST /api/rapports/analyse/rendement
**Description:** Générer une analyse du rendement pompiste/caissier

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "type_analyse": "pompiste|caissier",
  "employe_id": "uuid (optionnel)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "libelle_analyse": "Analyse de rendement du {date_debut} au {date_fin}",
    "resultats_analyse": {
      "donnees_brutes": {},
      "comparaisons": {},
      "kpi_calculs": {}
    },
    "interpretations": "string",
    "date_generation": "datetime"
  },
  "message": "Analyse de rendement générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Analyse générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Employé/station non trouvée
- 500: Erreur interne du serveur

### 4.6 Analyse des stocks

#### POST /api/rapports/analyse/stocks
**Description:** Générer une analyse des stocks

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "type_produit": "carburant|boutique",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "libelle_analyse": "Analyse des stocks du {date_debut} au {date_fin}",
    "resultats_analyse": {
      "donnees_brutes": {},
      "evaluations": {},
      "mouvements": {},
      "ecarts": {}
    },
    "interpretations": "string",
    "date_generation": "datetime"
  },
  "message": "Analyse des stocks générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Analyse générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

### 4.7 Analyse des dettes/créances

#### POST /api/rapports/analyse/dettes-creances
**Description:** Générer une analyse des dettes/créances

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "type_analyse": "dettes|creances",
  "client_id": "uuid (optionnel)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "libelle_analyse": "Analyse des dettes/créances du {date_debut} au {date_fin}",
    "resultats_analyse": {
      "donnees_brutes": {},
      "evaluations": {},
      "suivi_delai": {},
      "risques": {}
    },
    "interpretations": "string",
    "date_generation": "datetime"
  },
  "message": "Analyse des dettes/créances générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Analyse générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Client/station non trouvée
- 500: Erreur interne du serveur

### 4.8 Analyse de la rentabilité

#### POST /api/rapports/analyse/rentabilite
**Description:** Générer une analyse de la rentabilité

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "periode_debut": "date (format YYYY-MM-DD)",
  "periode_fin": "date (format YYYY-MM-DD)",
  "type_analyse": "produit|station|global",
  "produit_id": "uuid (optionnel)",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "libelle_analyse": "Analyse de rentabilité du {date_debut} au {date_fin}",
    "resultats_analyse": {
      "donnees_brutes": {},
      "marges": {},
      "indicateurs": {},
      "comparaisons": {}
    },
    "interpretations": "string",
    "date_generation": "datetime"
  },
  "message": "Analyse de rentabilité générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Analyse générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Produit/station non trouvée
- 500: Erreur interne du serveur

### 4.9 Gestion des indicateurs KPIs

#### GET /api/rapports/kpi/indicateurs
**Description:** Obtenir la liste des indicateurs KPIs

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- categorie: string (optionnel)
- statut: string (optionnel)
- est_personnalise: boolean (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "indicateurs": [
      {
        "id": "uuid",
        "code_kpi": "string",
        "libelle_kpi": "string",
        "description": "string",
        "categorie_kpi": "string",
        "unite_mesure": "string",
        "seuil_alerte_bas": "decimal (nullable)",
        "seuil_alerte_haut": "decimal (nullable)",
        "statut": "string",
        "est_personnalise": "boolean"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Indicateurs KPIs récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Indicateurs récupérés avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

#### POST /api/rapports/kpi/indicateurs
**Description:** Créer un nouvel indicateur KPI

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "code_kpi": "string (unique, max 50)",
  "libelle_kpi": "string (max 100)",
  "description": "string (optionnel)",
  "categorie_kpi": "commercial|financier|operationnel|logistique",
  "unite_mesure": "string (max 20)",
  "calcul_kpi": "text (requete SQL ou formule)",
  "seuil_alerte_bas": "decimal (optionnel)",
  "seuil_alerte_haut": "decimal (optionnel)",
  "est_personnalise": "boolean (default: false)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code_kpi": "string",
    "libelle_kpi": "string",
    "description": "string",
    "categorie_kpi": "string",
    "unite_mesure": "string",
    "calcul_kpi": "text",
    "seuil_alerte_bas": "decimal (nullable)",
    "seuil_alerte_haut": "decimal (nullable)",
    "statut": "Actif",
    "est_personnalise": "boolean",
    "created_at": "datetime"
  },
  "message": "Indicateur KPI créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Indicateur créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 409: Code KPI déjà existant
- 500: Erreur interne du serveur

#### GET /api/rapports/kpi/valeurs/{indicateur_id}
**Description:** Obtenir les valeurs d'un indicateur KPI sur une période

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- periode_debut: date (format YYYY-MM-DD)
- periode_fin: date (format YYYY-MM-DD)
- station_id: uuid (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "kpi": {
      "id": "uuid",
      "code_kpi": "string",
      "libelle_kpi": "string",
      "unite_mesure": "string"
    },
    "valeurs": [
      {
        "id": "uuid",
        "valeur": "decimal",
        "periode": "date",
        "date_calcul": "datetime",
        "commentaire": "string (nullable)",
        "est_previsionnel": "boolean"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Valeurs de l'indicateur KPI récupérées avec succès"
}
```

**HTTP Status Codes:**
- 200: Valeurs récupérées avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Indicateur non trouvé
- 500: Erreur interne du serveur

### 4.10 Prévisions et analyses

#### POST /api/rapports/prevision
**Description:** Générer une prévision

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_prevision": "vente|ca|stock|rendement",
  "libelle_prevision": "string (max 100)",
  "periode_prevision_debut": "date (format YYYY-MM-DD)",
  "periode_prevision_fin": "date (format YYYY-MM-DD)",
  "modele_utilise": "string (nom du modèle)",
  "donnees_entrees": "jsonb",
  "station_id": "uuid (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type_prevision": "string",
    "libelle_prevision": "string",
    "periode_prevision_debut": "date",
    "periode_prevision_fin": "date",
    "modele_utilise": "string",
    "precision_modele": "decimal",
    "resultat_prevision": "jsonb",
    "date_generation": "datetime",
    "statut": "Calcule"
  },
  "message": "Prévision générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Prévision générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

#### POST /api/rapports/analyse
**Description:** Générer une analyse personnalisée

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "type_analyse": "tendance|comparative|performance",
  "libelle_analyse": "string (max 100)",
  "description": "string (optionnel)",
  "periode_analyse_debut": "date (format YYYY-MM-DD)",
  "periode_analyse_fin": "date (format YYYY-MM-DD)",
  "donnees_analyse": "jsonb",
  "resultats_analyse": "jsonb",
  "interpretations": "text",
  "station_id": "uuid (optionnel)",
  "format_export": "pdf|excel"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type_analyse": "string",
    "libelle_analyse": "string",
    "periode_analyse_debut": "date",
    "periode_analyse_fin": "date",
    "date_generation": "datetime",
    "statut": "Termine"
  },
  "message": "Analyse générée avec succès"
}
```

**HTTP Status Codes:**
- 200: Analyse générée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station non trouvée
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de calcul pour les rapports comptables
1. Le bilan s'appuie sur les soldes des comptes comptables à une date donnée
2. Le grand livre affiche toutes les écritures par ordre chronologique
3. La balance affiche les soldes de chaque compte avec distinction débit/crédit
4. Le journal affiche les écritures comptables avec leurs détails

### Règles de calcul pour les déclarations fiscales
1. Les montants sont calculés selon les taux fiscaux en vigueur
2. Les déclarations doivent respecter les formats standards requis
3. Les seuils et obligations fiscales sont vérifiés automatiquement
4. Les dates d'échéance sont calculées selon les réglementations en vigueur

### Règles de calcul pour les analyses
1. Analyse de consommation se base sur les volumes vendus
2. Analyse de rendement se base sur les performances des employés
3. Analyse des stocks se base sur les mouvements d'entrée/sortie
4. Analyse des dettes/créances se base sur les soldes clients/fournisseurs
5. Analyse de rentabilité se base sur les marges bénéficiaires

### Règles de calcul pour les KPIs
1. Les KPIs ont des formules de calcul spécifiques stockées dans la table
2. Les calculs s'effectuent pour des périodes définies
3. Les alertes se déclenchent quand les seuils sont dépassés
4. Les KPIs peuvent être personnalisés par utilisateur

### Règles de prévision
1. Les prévisions s'appuient sur des modèles statistiques
2. Les données historiques sont utilisées pour l'entraînement
3. La précision des modèles est évaluée automatiquement
4. Les prévisions sont mises à jour régulièrement

### Restrictions et validations
1. Les rapports ne peuvent être générés que pour des périodes valides
2. Les utilisateurs doivent avoir les permissions appropriées
3. Les données d'entrée doivent être complètes et valides
4. Les fichiers générés sont stockés temporairement puis archivés

### Impacts sur d'autres modules
1. Le module de reporting dépend des données des modules de vente, stock, etc.
2. Les modifications dans les modules de base affectent les rapports
3. Les nouveaux indicateurs peuvent nécessiter des modifications dans d'autres modules
4. Les contraintes de performance doivent être prises en compte pour les grandes quantités de données

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
utilisateurs ||--o{ rapports_comptables
utilisateurs ||--o{ declarations_fiscales
utilisateurs ||--o{ suivi_conformite
stations ||--o{ rapports_comptables
stations ||--o{ declarations_fiscales
rapports_comptables ||--o{ ecritures_comptables
declarations_fiscales ||--o{ ecritures_comptables
indicateurs_kpi ||--o{ valeurs_indicateurs_kpi
utilisateurs ||--o{ indicateurs_kpi
```

### Diagramme de séquence pour la génération d'un rapport
```
Utilisateur -> API: POST /api/rapports/comptables/bilan
API -> Base de données: Valider les paramètres
API -> Calculateur: Calculer les données du bilan
Calculateur -> Base de données: Récupérer les données comptables
Calculateur -> API: Retourner les données calculées
API -> Générateur PDF/Excel: Générer le fichier
Générateur -> API: Retourner le fichier généré
API -> Base de données: Enregistrer les détails du rapport
API -> Utilisateur: Retourner la réponse avec le lien du fichier
```

## 7. Tests Requis

### Tests unitaires
1. Test de validation des paramètres d'entrée pour chaque endpoint
2. Test des fonctions de calcul des KPIs
3. Test des fonctions de génération de rapports
4. Test des triggers de base de données
5. Test des fonctions de calcul de prévisions

### Tests d'intégration
1. Test complet de bout en bout de la génération d'un bilan
2. Test de la génération des déclarations fiscales avec les données comptables
3. Test de la mise à jour des valeurs KPIs
4. Test de la cohérence des données entre les modules
5. Test de la génération des exports PDF/Excel

### Tests de charge/performance
1. Test de génération de rapports avec de grandes quantités de données
2. Test de performance pour des périodes longues (années complètes)
3. Test de la génération simultanée de plusieurs rapports
4. Test de la pagination des résultats pour de grandes listes
5. Test de la vitesse de calcul des KPIs pour différentes périodes

### Jeux de données de test
1. Données comptables valides pour tester les rapports financiers
2. Données de ventes et d'achats pour tester les analyses
3. Données de stock pour tester les analyses de stock
4. Données d'employés pour tester les analyses de rendement
5. Données clients/fournisseurs pour tester les analyses de créances/dettes

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contraintes d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de calcul pour les rapports et analyses
6. [ ] Implémenter la logique de validation des données
7. [ ] Créer les utilitaires d'export PDF et Excel
8. [ ] Implémenter la pagination pour les grandes listes
9. [ ] Créer les tests unitaires et d'intégration
10. [ ] Implémenter la gestion des erreurs et logs
11. [ ] Créer les vues frontend pour les rapports (si applicable)
12. [ ] Documenter les endpoints API

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base (CRUD)
3. Développer les services de calcul
4. Créer les exports
5. Implémenter les tests
6. Optimiser les performances
7. Intégrer avec les autres modules
8. Documenter la solution

### Livrables attendus
1. Code source complet avec commentaires
2. Scripts de migration de base de données
3. Documentation API
4. Jeux de tests et résultats
5. Documentation technique détaillée
6. Guide d'installation et de déploiement

## 9. Risques & Points de vigilance

### Points sensibles
1. La performance de génération des rapports avec de grandes quantités de données
2. La précision des calculs pour les déclarations fiscales
3. La sécurité des données sensibles dans les rapports
4. La complexité des formules de calcul pour les KPIs personnalisés
5. La gestion des accès et permissions pour les différentes stations

### Risques techniques
1. Risque de surcharge du serveur lors de la génération de rapports volumineux
2. Risque d'erreurs de calcul dans les indicateurs KPIs
3. Risque de non-conformité des déclarations fiscales
4. Risque de perte de données en cas de panne pendant la génération
5. Risque de non-disponibilité des services pendant les pics d'utilisation

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples rapports
2. Risque de duplication de logique entre les différents types de rapports
3. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
4. Besoin de maintenance continue pour les formules de calcul
5. Risque de dépendance excessive à des bibliothèques tierces pour les exports