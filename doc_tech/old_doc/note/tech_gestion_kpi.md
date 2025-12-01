# Technical Specification - Gestion des indicateurs de performance

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer les indicateurs de performance du système SuccessFuel. Cela inclut les KPIs opérationnels, les indicateurs fiscaux, comptables, les obligations réglementaires, les risques opérationnels, l'analyse prévisionnelle, les services annexes, les contrôles internes, les relations clients avancées, l'optimisation de la gestion de carburant, le plan comptable et les écritures automatiques.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet de gestion des indicateurs de performance qui permet :
- De calculer et suivre les KPIs opérationnels
- De gérer les obligations fiscales et réglementaires
- De surveiller les risques opérationnels
- D'effectuer des analyses prévisionnelles
- De gérer les services annexes
- De contrôler les opérations internes
- D'optimiser la relation client
- D'optimiser la gestion de carburant
- D'intégrer le plan comptable et les écritures automatiques

### Définition du périmètre
Le périmètre inclut :
- Calcul des KPIs opérationnels (litres vendus, marge brute, rendement pompiste, productivité)
- Gestion des obligations fiscales et calcul automatique des taxes
- Suivi des risques opérationnels et incidents de sécurité
- Analyse prévisionnelle et tendances commerciales
- Gestion des services annexes et contrats de maintenance
- Contrôle interne et validation hiérarchisée
- Gestion avancée des relations clients
- Optimisation de la gestion de carburant
- Gestion du plan comptable et écritures automatiques
- Historisation des actions utilisateurs

## 2. User Stories & Critères d'acceptation

### US-KPI-001: En tant que gestionnaire, je veux calculer et visualiser les KPIs opérationnels
- **Critères d'acceptation :**
  - Pouvoir visualiser les litres vendus par type de carburant
  - Pouvoir calculer la marge brute par produit
  - Pouvoir suivre le rendement des pompistes
  - Pouvoir analyser les indicateurs de productivité
  - Pouvoir effectuer des analyses comparatives de performances
  - Les KPIs doivent être calculés par station et par période

### US-KPI-002: En tant que gestionnaire, je veux gérer les obligations fiscales et calculer automatiquement les taxes
- **Critères d'acceptation :**
  - Pouvoir gérer les obligations fiscales (TVA, autres taxes)
  - Pouvoir intégrer les obligations de déclaration
  - Pouvoir calculer automatiquement les taxes dues selon les réglementations locales
  - Pouvoir suivre les échéances fiscales
  - Pouvoir générer les rapports exigés par les autorités fiscales
  - Les calculs doivent respecter les spécifications locales (ex: OHADA)

### US-KPI-003: En tant que gestionnaire, je veux surveiller les risques opérationnels
- **Critères d'acceptation :**
  - Pouvoir suivre les écarts anormaux
  - Pouvoir gérer les assurances
  - Pouvoir suivre les incidents de sécurité
  - Pouvoir contrôler les accès aux cuves et aux pompes
  - Pouvoir alerter les situations à risque

### US-KPI-004: En tant que gestionnaire, je veux effectuer des analyses prévisionnelles
- **Critères d'acceptation :**
  - Pouvoir analyser les tendances de vente
  - Pouvoir prévoir la demande de carburant
  - Pouvoir optimiser les prix
  - Pouvoir analyser la clientèle fidèle vs occasionnelle
  - Les prévisions doivent être basées sur des historiques de données

### US-KPI-005: En tant que gestionnaire, je veux gérer les services annexes
- **Critères d'acceptation :**
  - Pouvoir gérer les services de station-service
  - Pouvoir comptabiliser les services rendus
  - Pouvoir suivre les contrats de maintenance
  - Pouvoir gérer les coûts associés aux services

### US-KPI-006: En tant que gestionnaire, je veux contrôler les opérations internes
- **Critères d'acceptation :**
  - Pouvoir contrôler les écarts de caisse automatiques
  - Pouvoir suivre les opérations suspectes
  - Pouvoir valider hiérarchiquement les transactions importantes
  - Pouvoir journaliser les modifications critiques
  - Pouvoir effectuer des contrôles internes périodiques

### US-KPI-007: En tant que gestionnaire, je veux optimiser la relation client
- **Critères d'acceptation :**
  - Pouvoir gérer les programmes de fidélisation
  - Pouvoir gérer les cartes de carburant
  - Pouvoir gérer les contrats de ravitaillement à long terme
  - Pouvoir suivre un système de notation des clients

### US-KPI-008: En tant que gestionnaire, je veux optimiser la gestion de carburant
- **Critères d'acceptation :**
  - Pouvoir suivre les températures pour la correction volumétrique
  - Pouvoir gérer les mélanges d'additifs
  - Pouvoir suivre la qualité du carburant
  - Pouvoir analyser les coûts de transport et de stockage

### US-KPI-009: En tant que gestionnaire, je veux gérer le plan comptable et les écritures automatiques
- **Critères d'acceptation :**
  - Pouvoir gérer le plan comptable selon les systèmes locaux (OHADA, etc.)
  - Pouvoir générer automatiquement des écritures comptables pour chaque opération
  - Pouvoir valider les écritures selon les règles comptables
  - Pouvoir suivre les soldes des comptes

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: kpi_operations
```sql
CREATE TABLE kpi_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    periode DATE NOT NULL,
    type_carburant UUID REFERENCES carburants(id), -- NULL pour ensemble
    litres_vendus NUMERIC(18,3) DEFAULT 0,
    marge_brute NUMERIC(18,2) DEFAULT 0,
    nombre_clients_servis INTEGER DEFAULT 0,
    volume_moyen_transaction NUMERIC(18,3) DEFAULT 0,
    rendement_pompiste UUID REFERENCES utilisateurs(id), -- NULL pour ensemble
    productivite_horaires NUMERIC(18,3) DEFAULT 0, -- litres par heure
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: declarations_fiscales
```sql
CREATE TABLE declarations_fiscales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_declaration VARCHAR(50) NOT NULL, -- TVA, autres taxes
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    montant_total NUMERIC(18,2) NOT NULL,
    montant_declare NUMERIC(18,2) NOT NULL,
    ecart NUMERIC(18,2) GENERATED ALWAYS AS (montant_declare - montant_total) STORED,
    date_depot DATE,
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Soumis', 'Traite', 'Retour')),
    fichier_joint TEXT, -- Lien ou nom du fichier de déclaration
    utilisateur_depose_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: suivi_conformite
```sql
CREATE TABLE suivi_conformite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_norme VARCHAR(50) NOT NULL, -- sécurité, qualité, fiscalité
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_prevue DATE NOT NULL,
    date_realisee DATE,
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Non conforme', 'En attente', 'Non applicable')),
    responsable_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: incidents_securite
```sql
CREATE TABLE incidents_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_incident VARCHAR(50) NOT NULL CHECK (type_incident IN ('Fuite', 'Accident', 'Vol', 'Intrusion', 'Autre')),
    date_incident TIMESTAMPTZ NOT NULL,
    description TEXT NOT NULL,
    gravite INTEGER CHECK (gravite BETWEEN 1 AND 5), -- 1 = mineur, 5 = majeur
    statut VARCHAR(20) DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'En cours', 'Résolu', 'Fermé')),
    utilisateur_declare_id UUID REFERENCES utilisateurs(id),
    utilisateur_traite_id UUID REFERENCES utilisateurs(id),
    action_corrective TEXT,
    date_resolution TIMESTAMPTZ,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: assurances
```sql
CREATE TABLE assurances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_assurance VARCHAR(50) NOT NULL, -- responsabilité civile, incendie, vol, etc.
    compagnie_assurance VARCHAR(100) NOT NULL,
    numero_police VARCHAR(50) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    montant_couverture NUMERIC(18,2) NOT NULL,
    prime_annuelle NUMERIC(18,2) NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé')),
    fichier_joint TEXT, -- Lien ou nom du fichier de police
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: analyse_commerciale
```sql
CREATE TABLE analyse_commerciale (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_analyse VARCHAR(50) NOT NULL, -- tendance_vente, comportement_client, etc.
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    resultat JSONB, -- Données d'analyse au format JSON
    commentaire TEXT,
    utilisateur_analyse_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: prevision_demande
```sql
CREATE TABLE prevision_demande (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID REFERENCES carburants(id),
    station_id UUID REFERENCES stations(id),
    date_prevision DATE NOT NULL,
    quantite_prevue NUMERIC(18,3) NOT NULL, -- En litres
    methode_prevision VARCHAR(50) NOT NULL, -- historique, saisonnalité, etc.
    confiance_prevision NUMERIC(5,2) CHECK (confiance_prevision BETWEEN 0 AND 100),
    commentaire TEXT,
    utilisateur_prevision_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: services_annexes
```sql
CREATE TABLE services_annexes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_service VARCHAR(50) NOT NULL, -- lavage, atelier, restaurant
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    prix_unitaire NUMERIC(18,2) NOT NULL,
    unite_mesure VARCHAR(20) DEFAULT 'Unité',
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprimé')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: contrats_maintenance
```sql
CREATE TABLE contrats_maintenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    type_contrat VARCHAR(50) NOT NULL, -- pompe, cuve, caisse, etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    cout_mensuel NUMERIC(18,2) NOT NULL,
    frequence INT, -- En mois
    prochaine_intervention DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: controle_interne
```sql
CREATE TABLE controle_interne (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_controle VARCHAR(50) NOT NULL, -- controle_caisse, controle_stock, etc.
    element_controle VARCHAR(100), -- Numéro de caisse, cuve, etc.
    date_controle DATE NOT NULL,
    utilisateur_controle_id UUID REFERENCES utilisateurs(id),
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Anomalie', 'Non applicable')),
    montant_ecart NUMERIC(18,2) DEFAULT 0, -- Ecart constaté
    commentaire TEXT,
    statut VARCHAR(20) DEFAULT 'Terminé' CHECK (statut IN ('Planifié', 'En cours', 'Terminé', 'En attente')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: programme_fidelite
```sql
CREATE TABLE programme_fidelite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    type_programme VARCHAR(50) NOT NULL, -- points, réduction, etc.
    seuil_activation NUMERIC(18,2) DEFAULT 0, -- Montant/quantité requis
    benefice TEXT, -- Description du bénéfice
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Expiré')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: cartes_carburant
```sql
CREATE TABLE cartes_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    numero_carte VARCHAR(50) UNIQUE NOT NULL,
    date_activation DATE NOT NULL,
    date_expiration DATE,
    solde_carte NUMERIC(18,2) DEFAULT 0,
    plafond_mensuel NUMERIC(18,2), -- NULL pour illimité
    statut VARCHAR(20) DEFAULT 'Active' CHECK (statut IN ('Active', 'Inactive', 'Bloquee', 'Perdue', 'Remplacee')),
    utilisateur_creation_id UUID REFERENCES utilisateurs(id),
    utilisateur_blocage_id UUID REFERENCES utilisateurs(id), -- Qui a bloqué la carte
    motif_blocage TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: contrats_clients
```sql
CREATE TABLE contrats_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    type_contrat VARCHAR(50) NOT NULL, -- ravitaillement, stationnement, etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    volume_garanti NUMERIC(18,3), -- En litres
    prix_contractuel NUMERIC(18,4), -- Prix convenu
    frequence_livraison INTEGER, -- En jours
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé', 'Suspendu')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: qualite_carburant
```sql
CREATE TABLE qualite_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID REFERENCES carburants(id),
    cuve_id UUID REFERENCES cuves(id),
    date_controle DATE NOT NULL,
    utilisateur_controle_id UUID REFERENCES utilisateurs(id),
    type_controle VARCHAR(50) NOT NULL, -- densité, octane, etc.
    valeur_relevee VARCHAR(50), -- Valeur mesurée
    valeur_standard VARCHAR(50), -- Valeur attendue
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Non conforme')),
    observation TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: couts_logistique
```sql
CREATE TABLE couts_logistique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_cout VARCHAR(50) NOT NULL, -- transport, stockage, assurance, etc.
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_cout DATE NOT NULL,
    carburant_id UUID REFERENCES carburants(id),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    utilisateur_saisie_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: validations_hierarchiques
```sql
CREATE TABLE validations_hierarchiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(50) NOT NULL,  -- Ex: 'annulation_vente', 'modification_stock'
    seuil_montant NUMERIC(18,2),         -- Montant à partir duquel validation est requise
    niveau_validation INTEGER DEFAULT 1, -- Niveau hiérarchique requis pour validation
    profil_autorise_id UUID REFERENCES profils(id), -- Profil autorisé à valider
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);
```

#### Table: historique_actions_utilisateurs
```sql
CREATE TABLE historique_actions_utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    action VARCHAR(100) NOT NULL,       -- Ex: 'creation_vente', 'modification_stock'
    module VARCHAR(50) NOT NULL,        -- Ex: 'ventes', 'stocks'
    sous_module VARCHAR(50),            -- Ex: 'carburant', 'boutique'
    objet_id UUID,                      -- ID de l'objet affecté
    donnees_avant JSONB,                -- Données avant modification
    donnees_apres JSONB,                -- Données après modification
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    session_id VARCHAR(100),
    statut_action VARCHAR(20) DEFAULT 'Reussie' CHECK (statut_action IN ('Reussie', 'Echouee', 'Bloquee')),
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.2 Relations
- Les tables sont liées aux structures de base (compagnie, station, utilisateur)
- Les KPIs sont calculés à partir des données de ventes, stocks, et autres opérations
- Les obligations fiscales sont liées aux spécifications locales (specifications_locales)
- Les contrôles internes et validations sont intégrés avec le système de permissions

### 3.3 Index recommandés
```sql
-- Index pour les KPIs opérationnels
CREATE INDEX idx_kpi_operations_station_periode ON kpi_operations(station_id, periode);
CREATE INDEX idx_kpi_operations_type_carburant ON kpi_operations(type_carburant);
CREATE INDEX idx_kpi_operations_rendement_pompiste ON kpi_operations(rendement_pompiste);

-- Index pour les déclarations fiscales
CREATE INDEX idx_declarations_fiscales_periode ON declarations_fiscales(periode_debut, periode_fin);
CREATE INDEX idx_declarations_fiscales_type ON declarations_fiscales(type_declaration);

-- Index pour le suivi de conformité
CREATE INDEX idx_suivi_conformite_date_prevue ON suivi_conformite(date_prevue);
CREATE INDEX idx_suivi_conformite_type_norme ON suivi_conformite(type_norme);

-- Index pour les incidents de sécurité
CREATE INDEX idx_incidents_securite_station_date ON incidents_securite(station_id, date_incident);
CREATE INDEX idx_incidents_securite_type_severite ON incidents_securite(type_incident, gravite);

-- Index pour les assurances
CREATE INDEX idx_assurances_date_fin ON assurances(date_fin);
CREATE INDEX idx_assurances_station ON assurances(station_id);

-- Index pour l'analyse commerciale
CREATE INDEX idx_analyse_commerciale_periode ON analyse_commerciale(periode_debut, periode_fin);
CREATE INDEX idx_analyse_commerciale_station ON analyse_commerciale(station_id);

-- Index pour la prévision de la demande
CREATE INDEX idx_prevision_demande_date ON prevision_demande(date_prevision);
CREATE INDEX idx_prevision_demande_carburant_station ON prevision_demande(carburant_id, station_id);

-- Index pour les services annexes
CREATE INDEX idx_services_annexes_station ON services_annexes(station_id);
CREATE INDEX idx_services_annexes_type ON services_annexes(type_service);

-- Index pour les contrats de maintenance
CREATE INDEX idx_contrats_maintenance_dates ON contrats_maintenance(date_debut, date_fin);
CREATE INDEX idx_contrats_maintenance_fournisseur ON contrats_maintenance(fournisseur_id);

-- Index pour le contrôle interne
CREATE INDEX idx_controle_interne_date ON controle_interne(date_controle);
CREATE INDEX idx_controle_interne_type ON controle_interne(type_controle);

-- Index pour la gestion client
CREATE INDEX idx_cartes_carburant_client ON cartes_carburant(client_id);
CREATE INDEX idx_contrats_clients_client ON contrats_clients(client_id);

-- Index pour la qualité du carburant
CREATE INDEX idx_qualite_carburant_cuve_date ON qualite_carburant(cuve_id, date_controle);

-- Index pour les coûts logistique
CREATE INDEX idx_couts_logistique_date ON couts_logistique(date_cout);
CREATE INDEX idx_couts_logistique_carburant_station ON couts_logistique(carburant_id, station_id);

-- Index pour l'historique des actions
CREATE INDEX idx_historique_actions_utilisateur ON historique_actions_utilisateurs(utilisateur_id);
CREATE INDEX idx_historique_actions_date ON historique_actions_utilisateurs(created_at);
CREATE INDEX idx_historique_actions_module ON historique_actions_utilisateurs(module);
```

## 4. API Backend

### 4.1 Endpoints pour les KPIs opérationnels

#### GET /api/v1/kpis/operationnels
- **Description**: Récupérer les KPIs opérationnels pour une période
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_kpis'
- **Paramètres**:
  - `station_id` (UUID, optionnel): Filtrer par station
  - `periode_debut` (date, requis): Date de début de la période
  - `periode_fin` (date, requis): Date de fin de la période
  - `type_carburant` (UUID, optionnel): Filtrer par type de carburant
- **Réponse (200 OK)**:
```json
{
  "periode": {
    "debut": "2025-11-01",
    "fin": "2025-11-30"
  },
  "kpi_par_station": [
    {
      "station_id": "uuid_station",
      "station_nom": "Station A",
      "donnees": [
        {
          "type_carburant": "Essence 95",
          "litres_vendus": 15000.000,
          "marge_brute": 2500000.00,
          "nombre_clients_servis": 450,
          "volume_moyen_transaction": 33.333,
          "rendement_pompiste": 12500.000,
          "productivite_horaires": 208.333
        }
      ]
    }
  ],
  "total_lites_vendus": 45000.000,
  "total_marge_brute": 7500000.00
}
```

#### POST /api/v1/kpis/operationnels/calculate
- **Description**: Calculer les KPIs opérationnels pour une période donnée
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'calculer_kpis'
- **Payload**:
```json
{
  "periode_debut": "2025-11-01",
  "periode_fin": "2025-11-30",
  "station_id": "uuid_station",
  "type_carburant": "uuid_type_carburant"
}
```
- **Réponse (200 OK)**:
```json
{
  "success": true,
  "message": "KPIs calculés avec succès",
  "kpi_id": "uuid_du_kpi_calcule"
}
```

### 4.2 Endpoints pour la gestion fiscale

#### GET /api/v1/declarations/fiscales
- **Description**: Récupérer les déclarations fiscales
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_declarations_fiscales'
- **Paramètres**:
  - `periode_debut` (date, optionnel): Date de début
  - `periode_fin` (date, optionnel): Date de fin
  - `type_declaration` (string, optionnel): TVA, autres taxes
  - `statut` (string, optionnel): En attente, Soumis, Traite, Retour
- **Réponse (200 OK)**:
```json
{
  "declarations": [
    {
      "id": "uuid_declaration",
      "type_declaration": "TVA",
      "periode": {
        "debut": "2025-10-01",
        "fin": "2025-10-31"
      },
      "montant_total": 500000.00,
      "montant_declare": 495000.00,
      "ecart": -5000.00,
      "statut": "Soumis",
      "date_depot": "2025-11-15",
      "fichier_joint": "declaration_tva_oct2025.pdf",
      "utilisateur_depose": {
        "id": "uuid_utilisateur",
        "nom": "Nom de l'utilisateur"
      }
    }
  ]
}
```

#### POST /api/v1/declarations/fiscales
- **Description**: Créer ou soumettre une déclaration fiscale
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_declarations_fiscales'
- **Payload**:
```json
{
  "type_declaration": "TVA",
  "periode_debut": "2025-10-01",
  "periode_fin": "2025-10-31",
  "montant_declare": 495000.00,
  "fichier_joint": "declaration_tva_oct2025.pdf",
  "commentaire": "Déclaration pour le mois d'octobre 2025"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Déclaration fiscale enregistrée",
  "declaration_id": "uuid_declaration"
}
```

### 4.3 Endpoints pour la gestion des risques

#### GET /api/v1/incidents/securite
- **Description**: Récupérer les incidents de sécurité
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_incidents_securite'
- **Paramètres**:
  - `date_debut` (date, optionnel)
  - `date_fin` (date, optionnel)
  - `type_incident` (string, optionnel)
  - `gravite` (integer, optionnel, 1-5)
  - `statut` (string, optionnel)
  - `station_id` (UUID, optionnel)
- **Réponse (200 OK)**:
```json
{
  "incidents": [
    {
      "id": "uuid_incident",
      "station": {
        "id": "uuid_station",
        "nom": "Station A"
      },
      "type_incident": "Accident",
      "date_incident": "2025-11-20T08:30:00Z",
      "description": "Accident de la route survenu à proximité de la station",
      "gravite": 3,
      "statut": "En cours",
      "utilisateur_declare": {
        "id": "uuid_utilisateur",
        "nom": "Nom de l'utilisateur"
      },
      "utilisateur_traite": null,
      "action_corrective": "Installation de panneaux de signalisation supplémentaires",
      "date_resolution": null
    }
  ]
}
```

#### POST /api/v1/incidents/securite
- **Description**: Créer un incident de sécurité
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_incidents_securite'
- **Payload**:
```json
{
  "station_id": "uuid_station",
  "type_incident": "Accident",
  "description": "Accident de la route survenu à proximité de la station",
  "gravite": 3,
  "commentaire": "Nécessite une enquête approfondie"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Incident de sécurité enregistré",
  "incident_id": "uuid_incident"
}
```

### 4.4 Endpoints pour l'analyse prévisionnelle

#### GET /api/v1/prevision/demande
- **Description**: Récupérer les prévisions de demande
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_prevision_demande'
- **Paramètres**:
  - `date_prevision_debut` (date, optionnel)
  - `date_prevision_fin` (date, optionnel)
  - `carburant_id` (UUID, optionnel)
  - `station_id` (UUID, optionnel)
- **Réponse (200 OK)**:
```json
{
  "prevision_par_station": [
    {
      "station_id": "uuid_station",
      "station_nom": "Station A",
      "donnees": [
        {
          "carburant_id": "uuid_carburant",
          "carburant_libelle": "Essence 95",
          "prevision": [
            {
              "date_prevision": "2025-12-01",
              "quantite_prevue": 1200.000,
              "methode_prevision": "historique",
              "confiance_prevision": 85.00
            }
          ]
        }
      ]
    }
  ]
}
```

#### POST /api/v1/prevision/demande/generate
- **Description**: Générer des prévisions de demande
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'generer_prevision_demande'
- **Payload**:
```json
{
  "carburant_id": "uuid_carburant",
  "station_id": "uuid_station",
  "periode_prevision": {
    "debut": "2025-12-01",
    "fin": "2025-12-31"
  },
  "methode_prevision": "historique",
  "commentaire": "Prévision basée sur les ventes des 12 derniers mois"
}
```
- **Réponse (200 OK)**:
```json
{
  "success": true,
  "message": "Prévisions générées avec succès",
  "prevision_ids": ["uuid_prevision1", "uuid_prevision2"]
}
```

### 4.5 Endpoints pour la gestion des services annexes

#### GET /api/v1/services/annexes
- **Description**: Récupérer les services annexes
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_services_annexes'
- **Paramètres**:
  - `station_id` (UUID, optionnel)
  - `type_service` (string, optionnel)
  - `statut` (string, optionnel)
- **Réponse (200 OK)**:
```json
{
  "services": [
    {
      "id": "uuid_service",
      "station_id": "uuid_station",
      "station_nom": "Station A",
      "type_service": "Lavage",
      "libelle": "Lavage complet",
      "description": "Lavage extérieur et intérieur",
      "prix_unitaire": 15000.00,
      "unite_mesure": "Unité",
      "statut": "Actif"
    }
  ]
}
```

#### POST /api/v1/services/annexes
- **Description**: Créer un service annexe
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_services_annexes'
- **Payload**:
```json
{
  "station_id": "uuid_station",
  "type_service": "Lavage",
  "libelle": "Lavage complet",
  "description": "Lavage extérieur et intérieur",
  "prix_unitaire": 15000.00,
  "unite_mesure": "Unité"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Service annexe créé",
  "service_id": "uuid_service"
}
```

### 4.6 Endpoints pour les contrôles internes

#### GET /api/v1/controles/interne
- **Description**: Récupérer les contrôles internes
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_controles_interne'
- **Paramètres**:
  - `date_debut` (date, optionnel)
  - `date_fin` (date, optionnel)
  - `type_controle` (string, optionnel)
  - `statut` (string, optionnel)
- **Réponse (200 OK)**:
```json
{
  "controles": [
    {
      "id": "uuid_controle",
      "type_controle": "controle_caisse",
      "element_controle": "Caisse principale",
      "date_controle": "2025-11-20",
      "utilisateur_controle": {
        "id": "uuid_utilisateur",
        "nom": "Nom de l'utilisateur"
      },
      "resultat": "Conforme",
      "montant_ecart": 0.00,
      "commentaire": "Tout est conforme",
      "statut": "Terminé"
    }
  ]
}
```

#### POST /api/v1/controles/interne
- **Description**: Créer un contrôle interne
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_controles_interne'
- **Payload**:
```json
{
  "type_controle": "controle_caisse",
  "element_controle": "Caisse principale",
  "date_controle": "2025-11-20",
  "resultat": "Conforme",
  "montant_ecart": 0.00,
  "commentaire": "Tout est conforme",
  "statut": "Terminé"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Contrôle interne enregistré",
  "controle_id": "uuid_controle"
}
```

### 4.7 Endpoints pour la relation client avancée

#### GET /api/v1/cartes/carburant
- **Description**: Récupérer les cartes de carburant
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_cartes_carburant'
- **Paramètres**:
  - `client_id` (UUID, optionnel)
  - `statut` (string, optionnel)
  - `numero_carte` (string, optionnel)
- **Réponse (200 OK)**:
```json
{
  "cartes": [
    {
      "id": "uuid_carte",
      "numero_carte": "CC-2025-001234",
      "client": {
        "id": "uuid_client",
        "nom": "Client XYZ SARL"
      },
      "date_activation": "2025-01-15",
      "date_expiration": "2025-12-31",
      "solde_carte": 150000.00,
      "plafond_mensuel": 200000.00,
      "statut": "Active",
      "utilisateur_creation": {
        "id": "uuid_utilisateur",
        "nom": "Nom de l'utilisateur"
      }
    }
  ]
}
```

#### POST /api/v1/cartes/carburant
- **Description**: Créer une carte de carburant
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_cartes_carburant'
- **Payload**:
```json
{
  "client_id": "uuid_client",
  "date_activation": "2025-01-15",
  "date_expiration": "2025-12-31",
  "plafond_mensuel": 200000.00,
  "commentaire": "Carte pour véhicule de service"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Carte de carburant créée",
  "carte_id": "uuid_carte",
  "numero_carte": "CC-2025-001234"
}
```

## 5. Logique Métier

### 5.1 Règles de calcul des KPIs

#### Calcul des litres vendus par type de carburant
- Les litres vendus sont calculés à partir des ventes de carburant (type_vente = 'Carburant')
- Les quantités sont prises dans la table `ventes_details` où `pistolet_id` est spécifié
- Le calcul est effectué pour une période donnée et peut être filtré par station ou type de carburant
- La quantité est calculée à partir des différences d'index des pistolets

#### Calcul de la marge brute par produit
- La marge brute = (prix de vente - prix d'achat) * quantité vendue
- Les prix d'achat sont pris dans la table `historique_prix_articles` pour la période concernée
- Pour les carburants, les prix sont pris dans `historique_prix_carburants`
- La marge est calculée pour tous les produits vendus (carburant et boutique)

#### Calcul du rendement des pompistes
- Le rendement est mesuré en litres vendus par pompiste pour une période donnée
- Associé à l'utilisateur dans `ventes_details.utilisateur_id` qui correspond au pompiste
- Calculé par station et peut être comparé avec les performances moyennes

#### Calcul de la productivité horaire
- Productivité = litres vendus / heures de travail
- Les heures de travail sont basées sur les horaires de service des employés
- Calculé par pompiste et par station

### 5.2 Règles fiscales et réglementaires
- Les calculs fiscaux sont basés sur les spécifications locales stockées dans `specifications_locales`
- Les taux de TVA sont automatiquement récupérés du système
- Les seuils et obligations fiscales sont mis à jour selon les réglementations en vigueur
- Les déclarations sont générées selon les formats requis par les autorités

### 5.3 Gestion des risques opérationnels
- Les écarts anormaux sont détectés par comparaison entre données réelles et théoriques
- Les seuils d'alerte sont configurables dans `politiques_securite`
- Les incidents de sécurité sont classifiés par gravité (1-5) et suivis jusqu'à résolution
- Les assurances sont surveillées pour éviter les expirations

### 5.4 Analyse prévisionnelle
- Les prévisions sont basées sur les historiques de ventes
- Plusieurs méthodes sont disponibles : historique, saisonnalité, tendance
- Les prévisions sont évaluées par un taux de confiance
- Les résultats sont stockés pour suivi et comparaison avec les réalisations

### 5.5 Contrôles internes
- Les validations hiérarchiques sont configurées dans `validations_hierarchiques`
- Les seuils de montant déclencheurs sont paramétrables
- Les contrôles sont journalisés dans `historique_actions_utilisateurs`
- Les écarts sont automatiquement signalés aux responsables concernés

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)

```
Compagnie 1----* Station
Station 1----* Cuve
Station 1----* Pistolet
Station 1----* Vente
Station 1----* KPI_Operations
Station 1----* Incident_Securite
Station 1----* Service_Annexe
Station 1----* Contrat_Maintenance

Carburant 1----* Cuve
Carburant 1----* Historique_Prix_Carburants
Carburant 1----* KPI_Operations
Carburant 1----* Prevision_Demande
Carburant 1----* Qualite_Carburant
Carburant 1----* Cout_Logistique

Vente *----* Vente_Details
Vente_Details 1----* Pistolet
Vente_Details 1----* Article

Article 1----* Historique_Prix_Articles
Article 1----* KPI_Operations

Utilisateur 1----* KPI_Operations (rendement_pompiste)
Utilisateur 1----* Declaration_Fiscale (utilisateur_depose_id)
Utilisateur 1----* Incident_Securite (utilisateur_declare_id, utilisateur_traite_id)
Utilisateur 1----* Historique_Actions_Utilisateurs

Specification_Locale 1----* Declaration_Fiscale
```

### 6.2 Diagramme de séquence (textuel) pour le calcul des KPIs

```
Client -> API: POST /api/v1/kpis/operationnels/calculate
API -> DB: Récupérer les données de ventes pour la période
DB -> API: Retourner les données de ventes
API -> API: Calculer les KPIs opérationnels
API -> DB: Sauvegarder les résultats dans kpi_operations
DB -> API: Confirmation de sauvegarde
API -> Client: Retourner les résultats du calcul
```

## 7. Tests Requis

### 7.1 Tests unitaires

#### Tests des KPIs opérationnels
- Test du calcul des litres vendus par type de carburant
- Test du calcul de la marge brute
- Test du calcul du rendement des pompistes
- Test du calcul de la productivité horaire
- Test de la fonction de comparaison des performances

#### Tests de gestion fiscale
- Test du calcul automatique des taxes
- Test de la génération des déclarations fiscales
- Test de la validation des seuils fiscaux
- Test de la gestion des échéances fiscales

#### Tests de gestion des risques
- Test de détection des écarts anormaux
- Test de la journalisation des incidents de sécurité
- Test de la gestion des assurances
- Test de la classification par gravité

### 7.2 Tests d'intégration

#### Tests des workflows complets
- Test du workflow de création et de traitement d'un incident de sécurité
- Test du workflow de génération et de dépôt d'une déclaration fiscale
- Test du workflow de calcul et de visualisation des KPIs
- Test du workflow de gestion d'une carte de carburant

#### Tests des API
- Test des endpoints de KPIs opérationnels
- Test des endpoints de gestion fiscale
- Test des endpoints de gestion des risques
- Test des endpoints d'analyse prévisionnelle

### 7.3 Tests de charge/performance
- Test de performance pour le calcul des KPIs sur une période longue
- Test de performance pour la génération de prévisions pour plusieurs stations
- Test de performance pour la gestion simultanée de plusieurs déclarations fiscales
- Test de performance pour l'accès concurrent aux données de KPIs

### 7.4 Jeux de données de test
- Données de test pour une station avec plusieurs types de carburant
- Historiques de ventes pour la période de test (6 mois)
- Données de qualité de carburant et d'incidents de sécurité
- Données de coûts logistiques et de contrats de maintenance
- Données de clients avec cartes de carburant et contrats

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées

#### Phase 1: Modèle de données
- [ ] Créer les tables spécifiées dans la section 3
- [ ] Mettre en place les relations entre les tables
- [ ] Créer les indexes recommandés
- [ ] Valider les contraintes d'intégrité

#### Phase 2: Logique métier
- [ ] Implémenter les fonctions de calcul des KPIs
- [ ] Mettre en place les règles de gestion fiscale
- [ ] Implémenter les mécanismes de gestion des risques
- [ ] Développer les algorithmes d'analyse prévisionnelle

#### Phase 3: API Backend
- [ ] Créer les endpoints pour les KPIs opérationnels
- [ ] Développer les endpoints de gestion fiscale
- [ ] Mettre en place les endpoints pour la gestion des risques
- [ ] Créer les endpoints d'analyse prévisionnelle
- [ ] Développer les endpoints pour la gestion des services et contrôles
- [ ] Implémenter les endpoints pour la relation client

#### Phase 4: Sécurité et permissions
- [ ] Mettre en place les validations RBAC pour chaque endpoint
- [ ] Implémenter les contrôles d'accès par station et compagnie
- [ ] Assurer l'historisation des actions critiques
- [ ] Mettre en place les validations hiérarchiques

#### Phase 5: Tests
- [ ] Écrire les tests unitaires pour chaque fonctionnalité
- [ ] Créer les tests d'intégration pour les workflows
- [ ] Mettre en place les tests de performance
- [ ] Préparer les jeux de données de test

### 8.2 Ordre recommandé
1. Commencer par la création des tables de base (kpi_operations, declarations_fiscales)
2. Mettre en place la logique métier pour les KPIs
3. Développer les endpoints API pour les KPIs
4. Implémenter la gestion fiscale
5. Ajouter la gestion des risques et la sécurité
6. Intégrer les fonctionnalités d'analyse prévisionnelle
7. Finaliser avec les services annexes et contrôles internes
8. Mettre en place la relation client avancée
9. Effectuer les tests complets

### 8.3 Livrables attendus
- Ensemble complet de tables pour la gestion des KPIs
- API RESTful pour l'accès aux indicateurs de performance
- Documentation des endpoints API
- Jeux de tests unitaires et d'intégration
- Scripts de migration de base de données

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- Le calcul des KPIs nécessite des performances optimales sur de grandes quantités de données
- La gestion fiscale doit respecter les réglementations locales en vigueur
- La sécurité des données sensibles (cartes carburant, contrats clients) doit être garantie
- La validation hiérarchique des opérations critiques doit être fiable et tracée

### 9.2 Risques techniques
- Risque de performance pour les calculs de KPIs sur des périodes longues
- Risque de non-conformité fiscale en cas de changement de réglementation
- Risque de perte de données en cas de panne système
- Risque d'erreurs dans les prévisions commerciales

### 9.3 Dette technique potentielle
- Complexité accrue du système avec l'ajout de ces fonctionnalités
- Maintenance des règles fiscales et réglementaires
- Nécessité de mises à jour fréquentes des paramètres de prévision
- Intégration des mises à jour réglementaires dans les calculs automatiques