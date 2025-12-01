# Technical Specification - Gestion des ventes

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer toutes les ventes effectuées dans la station-service SuccessFuel. Cela inclut les ventes de carburant (avec index de pistolets), les ventes de produits en boutique, et les services annexes, avec une intégration complète du processus de paiement, des mouvements de stock, des écritures comptables, et des analyses de performance des employés.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet de gestion des ventes qui permet :
- De suivre les ventes de carburant avec les index de pistolets
- De gérer les paiements clients (cash, crédit, écart pompiste)
- De générer les écritures comptables automatiques
- De suivre les performances des pompistes/caissiers
- De produire des tickets de caisse
- De faire les arrêts de compte caissier
- De surveiller les écarts anormaux
- De gérer les ventes de services annexes

### Définition du périmètre
Le périmètre inclut :
- Gestion des ventes de carburant avec index de pistolet
- Gestion des ventes en boutique
- Gestion des ventes de services
- Processus de paiement intégré
- Génération automatique des écritures comptables
- Mise à jour des stocks après vente
- Génération des tickets de caisse
- Arrêts de compte caissier
- Suivi des performances des employés
- Suivi des écarts anormaux
- Analyse de la productivité

## 2. User Stories & Critères d'acceptation

### US-VENTE-001: En tant que caissier, je veux créer une vente de carburant
- **Critères d'acceptation :**
  - Pouvoir spécifier le client (optionnel)
  - Pouvoir sélectionner le pistolet de distribution
  - Pouvoir saisir l'index de départ et d'arrivée
  - Pouvoir calculer automatiquement la quantité vendue
  - Pouvoir spécifier le prix unitaire et les taxes applicables
  - Le système doit vérifier la disponibilité du stock
  - Le système doit permettre de valider la vente

### US-VENTE-002: En tant que caissier, je veux créer une vente de produits boutique
- **Critères d'acceptation :**
  - Pouvoir ajouter des articles à la vente
  - Pouvoir modifier quantités et prix
  - Pouvoir appliquer des réductions ou taxes
  - Le système doit calculer automatiquement les totaux
  - Le système doit vérifier la disponibilité du stock
  - Le système doit permettre d'émettre un ticket de caisse

### US-VENTE-003: En tant que caissier, je veux gérer les paiements
- **Critères d'acceptation :**
  - Pouvoir enregistrer un paiement en espèces
  - Pouvoir gérer les paiements par carte ou chèque
  - Pouvoir gérer les ventes à crédit
  - Pouvoir gérer les écarts de caisse
  - Les modes de paiement doivent être cohérents avec les trésoreries
  - Le système doit enregistrer les détails du paiement

### US-VENTE-004: En tant que gestionnaire, je veux suivre les performances des pompistes
- **Critères d'acceptation :**
  - Pouvoir visualiser les ventes par pompiste
  - Pouvoir analyser la productivité horaire
  - Pouvoir comparer les performances entre employés
  - Pouvoir détecter les écarts anormaux
  - Pouvoir exporter les rapports de performance

### US-VENTE-005: En tant que gestionnaire, je veux générer des tickets de caisse
- **Critères d'acceptation :**
  - Le ticket doit contenir toutes les informations de la vente
  - Le ticket doit être numéroté automatiquement
  - Le système doit permettre l'impression ou l'export
  - Le ticket doit inclure le nom de la station
  - Le ticket doit inclure les informations fiscales

### US-VENTE-006: En tant que gestionnaire, je veux effectuer un arrêt de compte caissier
- **Critères d'acceptation :**
  - Pouvoir fermer la caisse avec le montant réel
  - Pouvoir comparer avec le montant théorique
  - Pouvoir justifier les écarts
  - Pouvoir enregistrer l'arrêt de compte
  - Le système doit bloquer la caisse après arrêt

### US-VENTE-007: En tant que gestionnaire, je veux suivre les écarts anormaux
- **Critères d'acceptation :**
  - Le système doit détecter les écarts suspects
  - Pouvoir analyser les écarts par employé ou période
  - Pouvoir classer les écarts par gravité
  - Pouvoir signaler les écarts anormaux
  - Pouvoir investiguer les causes des écarts

### US-VENTE-008: En tant que comptable, je veux que les ventes génèrent des écritures comptables
- **Critères d'acceptation :**
  - Chaque vente valide génère automatiquement des écritures comptables
  - Les écritures respectent le plan comptable local (OHADA)
  - Les taxes sont correctement comptabilisées
  - Les écritures sont associées à des journaux spécifiques (vente, trésorerie)
  - Les écritures sont numérotées automatiquement

### US-VENTE-009: En tant que gestionnaire, je veux analyser la productivité
- **Critères d'acceptation :**
  - Pouvoir suivre les indicateurs de performance
  - Pouvoir analyser les tendances de vente
  - Pouvoir comparer les performances entre périodes
  - Pouvoir identifier les heures de pointe
  - Pouvoir exporter les analyses

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: ventes (existe déjà, extension requise)
```sql
-- Extension de la table ventes existante pour inclure plus de détails sur les écarts et les validations
ALTER TABLE ventes 
ADD COLUMN IF NOT EXISTS type_validation VARCHAR(20) DEFAULT 'Automatique' CHECK (type_validation IN ('Automatique', 'Manuelle', 'Hierarchique')),
ADD COLUMN IF NOT EXISTS utilisateur_validation_id UUID REFERENCES utilisateurs(id),
ADD COLUMN IF NOT EXISTS date_validation TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS est_ecart_anormal BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS motif_ecart TEXT,
ADD COLUMN IF NOT EXISTS utilisateur_detecte_ecart_id UUID REFERENCES utilisateurs(id),
ADD COLUMN IF NOT EXISTS quantite_theorique NUMERIC(18,3), -- Pour comparaison avec la quantité réelle
ADD COLUMN IF NOT EXISTS quantite_reelle NUMERIC(18,3),    -- Pour les vérifications de stock
ADD COLUMN IF NOT EXISTS est_reconciliee BOOLEAN DEFAULT FALSE;

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_ventes_date_validation ON ventes(date_validation);
CREATE INDEX IF NOT EXISTS idx_ventes_est_ecart_anormal ON ventes(est_ecart_anormal);
CREATE INDEX IF NOT EXISTS idx_ventes_utilisateur ON ventes(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_ventes_station ON ventes(station_id);
```

#### Table: ventes_details (existe déjà, extension requise)
```sql
-- Extension de la table ventes_details existante
ALTER TABLE ventes_details
ADD COLUMN IF NOT EXISTS taux_remise NUMERIC(5,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS montant_remise NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht * (taux_remise / 100)) STORED,
ADD COLUMN IF NOT EXISTS montant_net_ht NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht - montant_remise) STORED,
ADD COLUMN IF NOT EXISTS est_promotion BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS id_promotion UUID, -- Référence vers une éventuelle promotion
ADD COLUMN IF NOT EXISTS utilisateur_validation_id UUID REFERENCES utilisateurs(id),
ADD COLUMN IF NOT EXISTS date_validation TIMESTAMPTZ;

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_ventes_details_pistolet ON ventes_details(pistolet_id);
CREATE INDEX IF NOT EXISTS idx_ventes_details_article ON ventes_details(article_id);
CREATE INDEX IF NOT EXISTS idx_ventes_details_est_promotion ON ventes_details(est_promotion);
```

#### Table: ventes_tresorerie (existe déjà, extension requise)
```sql
-- Extension de la table ventes_tresorerie existante
ALTER TABLE ventes_tresorerie
ADD COLUMN IF NOT EXISTS reference_paiement VARCHAR(100), -- Numéro de chèque, transaction CB, etc.
ADD COLUMN IF NOT EXISTS statut_paiement VARCHAR(20) DEFAULT 'En attente' CHECK (statut_paiement IN ('En attente', 'Confirme', 'Rejete', 'Rembourse')),
ADD COLUMN IF NOT EXISTS frais_transaction NUMERIC(18,2) DEFAULT 0, -- Frais pour les paiements électroniques
ADD COLUMN IF NOT EXISTS date_prevue_encaissement DATE, -- Pour les paiements différés
ADD COLUMN IF NOT EXISTS utilisateur_enregistrement_id UUID REFERENCES utilisateurs(id);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_ventes_tresorerie_statut ON ventes_tresorerie(statut_paiement);
CREATE INDEX IF NOT EXISTS idx_ventes_tresorerie_date_prevue ON ventes_tresorerie(date_prevue_encaissement);
```

#### Table: performances_employes
```sql
CREATE TABLE IF NOT EXISTS performances_employes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employe_id UUID NOT NULL REFERENCES employes(id),
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    type_vente VARCHAR(20) NOT NULL CHECK (type_vente IN ('Carburant', 'Boutique', 'Service', 'Toutes')), -- Type de vente concerné
    nbre_ventes INTEGER DEFAULT 0,
    volume_total NUMERIC(18,3) DEFAULT 0, -- Pour les ventes de carburant
    montant_total NUMERIC(18,2) DEFAULT 0, -- Pour les ventes totales
    taux_conversion NUMERIC(5,2) DEFAULT 0, -- Pourcentage de conversion
    moyenne_panier NUMERIC(18,2) DEFAULT 0, -- Valeur moyenne par vente
    heures_travaillees NUMERIC(6,2) DEFAULT 0, -- Nombre d'heures travaillées
    rendement_horaire NUMERIC(18,3) GENERATED ALWAYS AS (CASE WHEN heures_travaillees > 0 THEN montant_total / heures_travaillees ELSE 0 END) STORED,
    taux_ecart NUMERIC(5,2) DEFAULT 0, -- Pourcentage d'écarts sur les ventes
    date_evaluation DATE NOT NULL DEFAULT CURRENT_DATE,
    utilisateur_evaluateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    statut_evaluation VARCHAR(20) DEFAULT 'En attente' CHECK (statut_evaluation IN ('En attente', 'En cours', 'Terminee', 'Classee')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_performances_employes_employe ON performances_employes(employe_id);
CREATE INDEX idx_performances_employes_periode ON performances_employes(periode_debut, periode_fin);
CREATE INDEX idx_performances_employes_type_vente ON performances_employes(type_vente);
CREATE INDEX idx_performances_employes_date_evaluation ON performances_employes(date_evaluation);
```

#### Table: suivis_ecarts_vente
```sql
CREATE TABLE IF NOT EXISTS suivis_ecarts_vente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id),
    vente_detail_id UUID REFERENCES ventes_details(id),
    type_ecart VARCHAR(50) NOT NULL, -- 'ecart_index', 'ecart_stock', 'ecart_paiement', 'ecart_quantite'
    description TEXT NOT NULL,
    montant_ecart NUMERIC(18,2) DEFAULT 0, -- Valeur de l'écart en devise
    quantite_ecart NUMERIC(18,3) DEFAULT 0, -- Quantité écartée
    utilisateur_detecte_id UUID REFERENCES utilisateurs(id),
    utilisateur_traite_id UUID REFERENCES utilisateurs(id),
    statut_ecart VARCHAR(20) DEFAULT 'Identifie' CHECK (statut_ecart IN ('Identifie', 'Enquete', 'Corrige', 'Rejete', 'Ferme')),
    gravite_ecart INTEGER DEFAULT 1 CHECK (gravite_ecart BETWEEN 1 AND 5), -- 1 = mineur, 5 = majeur
    commentaire_traitement TEXT,
    date_detection TIMESTAMPTZ DEFAULT now(),
    date_traitement TIMESTAMPTZ,
    est_anormal BOOLEAN DEFAULT FALSE, -- Indique si l'écart est considéré comme anormal
    seuil_alerte NUMERIC(18,2) DEFAULT 0, -- Seuil qui a déclenché l'alerte
    reference_operation_origine VARCHAR(100), -- Référence de l'opération d'origine
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_suivis_ecarts_vente_vente ON suivis_ecarts_vente(vente_id);
CREATE INDEX idx_suivis_ecarts_vente_type ON suivis_ecarts_vente(type_ecart);
CREATE INDEX idx_suivis_ecarts_vente_statut ON suivis_ecarts_vente(statut_ecart);
CREATE INDEX idx_suivis_ecarts_vente_utilisateur ON suivis_ecarts_vente(utilisateur_detecte_id);
CREATE INDEX idx_suivis_ecarts_vente_est_anormal ON suivis_ecarts_vente(est_anormal);
```

#### Table: rapports_ventes
```sql
CREATE TABLE IF NOT EXISTS rapports_ventes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_rapport VARCHAR(50) NOT NULL, -- 'journal_vente', 'resume_quotidien', 'analyse_pompiste', 'analyse_produit'
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    contenu JSONB, -- Contenu du rapport au format JSON
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id),
    est_valide BOOLEAN DEFAULT FALSE,
    date_validation TIMESTAMPTZ,
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_rapports_ventes_type ON rapports_ventes(type_rapport);
CREATE INDEX idx_rapports_ventes_periode ON rapports_ventes(periode_debut, periode_fin);
CREATE INDEX idx_rapports_ventes_station ON rapports_ventes(station_id);
CREATE INDEX idx_rapports_ventes_est_valide ON rapports_ventes(est_valide);
```

#### Table: historique_index_pompiste (existe déjà mais renommée pour plus de clarté)
```sql
-- La table existe déjà sous le nom historique_index_pistolets, nous allons ajouter des informations
-- pour suivre les responsabilités des pompistes
ALTER TABLE historique_index_pistolets
ADD COLUMN IF NOT EXISTS utilisateur_responsable_id UUID REFERENCES utilisateurs(id), -- Pompiste responsable
ADD COLUMN IF NOT EXISTS statut_validation VARCHAR(20) DEFAULT 'En attente' CHECK (statut_validation IN ('En attente', 'Valide', 'Anomalie')),
ADD COLUMN IF NOT EXISTS commentaire_anomalie TEXT,
ADD COLUMN IF NOT EXISTS date_verification TIMESTAMPTZ;
```

## 4. API Backend

### 4.1 Ventes de carburant

#### Endpoint: Créer une vente de carburant
- **Méthode:** POST
- **URL:** `/api/ventes/carburant`
- **Payload (JSON):**
```json
{
  "client_id": "uuid-client",
  "date_vente": "2023-11-25",
  "type_vente": "Carburant",
  "type_transaction": "Station",
  "pistolet_id": "uuid-pistolet",
  "index_debut": 1250.000,
  "index_fin": 1350.000,
  "carburant_id": "uuid-carburant",
  "prix_unitaire_ht": 4500.0000,
  "taux_tva": 18.00,
  "observation": "Vente au comptant",
  "paiements": [
    {
      "tresorerie_id": "uuid-tresorerie",
      "montant": 45000.00,
      "mode_paiement": "espece",
      "reference_paiement": "ESP-2023-11-0001"
    }
  ],
  "station_id": "uuid-station"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-vente",
    "reference_facture": "FV-2023-11-001",
    "statut": "Valide",
    "total_ttc": 53100.00,
    "total_ht": 45000.00,
    "total_tva": 8100.00,
    "quantite_vendue": 100.000,
    "client": {
      "id": "uuid-client",
      "nom": "Nom du client"
    },
    "paiements": [
      {
        "id": "uuid-vente-tresorerie",
        "montant": 45000.00,
        "statut_paiement": "Confirme"
      }
    ]
  }
}
```
- **Codes d'erreur possibles:**
  - 400: Données invalides (index incorrects, stock insuffisant)
  - 401: Non authentifié
  - 403: Accès refusé
  - 404: Pistolet, carburant ou client non trouvé
  - 409: Conflit (index non cohérent avec l'historique)
  - 500: Erreur serveur

#### Endpoint: Créer une vente boutique
- **Méthode:** POST
- **URL:** `/api/ventes/boutique`
- **Payload (JSON):**
```json
{
  "client_id": "uuid-client",
  "date_vente": "2023-11-25",
  "type_vente": "Boutique",
  "type_transaction": "Boutique",
  "observation": "Vente divers articles",
  "details": [
    {
      "article_id": "uuid-article",
      "quantite": 2,
      "prix_unitaire_ht": 5000.0000,
      "taux_tva": 18.00,
      "taux_remise": 5.00
    }
  ],
  "paiements": [
    {
      "tresorerie_id": "uuid-tresorerie",
      "montant": 10000.00,
      "mode_paiement": "espece",
      "reference_paiement": "ESP-2023-11-0002"
    }
  ],
  "station_id": "uuid-station"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-vente",
    "reference_facture": "FB-2023-11-002",
    "statut": "Valide",
    "total_ttc": 11790.00,
    "total_ht": 10000.00,
    "total_tva": 1790.00,
    "nombre_articles": 2,
    "client": {
      "id": "uuid-client",
      "nom": "Nom du client"
    }
  }
}
```

#### Endpoint: Valider un arrêt de compte caissier
- **Méthode:** POST
- **URL:** `/api/caisses/{id}/arret-compte`
- **Payload (JSON):**
```json
{
  "ticket_caisse_id": "uuid-ticket",
  "montant_reel": 150000.00,
  "commentaire": "Montant conforme",
  "details_paiements": {
    "especes": 120000.00,
    "carte_bancaire": 20000.00,
    "cheque": 5000.00,
    "autre": 5000.00
  },
  "ecart": 0.00
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-arret-caissier",
    "ticket_caisse_id": "uuid-ticket",
    "statut": "Ferme",
    "ecart": 0.00,
    "total_vente_total": 150000.00,
    "reconciliation": "OK"
  }
}
```

#### Endpoint: Liste des ventes avec filtres
- **Méthode:** GET
- **URL:** `/api/ventes?date_debut=2023-11-01&date_fin=2023-11-25&station_id=uuid-station&type_vente=Carburant&employe_id=uuid-employe`
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid-vente",
        "reference_facture": "FV-2023-11-001",
        "client": "Nom du client",
        "date_vente": "2023-11-25",
        "total_ttc": 53100.00,
        "type_vente": "Carburant",
        "statut": "Valide",
        "employe": {
          "id": "uuid-employe",
          "nom": "NOM Prénom"
        },
        "paiements": [
          {
            "mode": "Espèces",
            "montant": 53100.00
          }
        ]
      }
    ],
    "total": 150,
    "page": 1,
    "pages": 8
  }
}
```

### 4.2 Surveillance et analyses

#### Endpoint: Générer un rapport de performance employé
- **Méthode:** POST
- **URL:** `/api/rapports/performance-employe`
- **Payload (JSON):**
```json
{
  "type_rapport": "analyse_pompiste", // 'analyse_pompiste', 'resume_quotidien', 'journal_vente'
  "periode_debut": "2023-11-01",
  "periode_fin": "2023-11-25",
  "employe_id": "uuid-employe",
  "station_id": "uuid-station"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-rapport",
    "type": "analyse_pompiste",
    "periode": {
      "debut": "2023-11-01",
      "fin": "2023-11-25"
    },
    "contenu": {
      "nbre_ventes": 125,
      "montant_total": 2500000.00,
      "volume_total": 5000.000,
      "moyenne_panier": 20000.00,
      "rendement_horaire": 50000.00,
      "taux_ecart": 2.5
    },
    "fichier_telechargement": "/api/rapports/performance-employe/uuid-rapport/download"
  }
}
```

### 4.3 Suivi des écarts

#### Endpoint: Signaler un écart de vente
- **Méthode:** POST
- **URL:** `/api/ventes/{id}/ecart`
- **Payload (JSON):**
```json
{
  "type_ecart": "ecart_index",
  "description": "Différence entre index de départ et de fin anormale",
  "montant_ecart": 5000.00,
  "quantite_ecart": 10.000,
  "gravite_ecart": 3,
  "commentaire": "À vérifier avec le pompiste concerné"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-suivi-ecart",
    "statut_ecart": "Identifie",
    "type_ecart": "ecart_index",
    "montant_ecart": 5000.00,
    "gravite_ecart": 3,
    "est_anormal": true
  }
}
```

## 5. Logique Métier

### 5.1 Règles de validation des ventes

1. **Validation des données de vente:**
   - Le client, s'il est spécifié, doit être actif
   - La date de vente ne peut être dans le futur
   - Les index de pistolets doivent être valides et cohérents avec l'historique
   - Les articles/carburants doivent être actifs
   - Les quantités et prix doivent être positifs
   - Les totaux doivent être correctement calculés
   - Le stock disponible doit être suffisant

2. **Contrôle des index de pistolet:**
   - L'index de fin doit être supérieur ou égal à l'index de début
   - Les index doivent être en cohérence avec les relevés précédents
   - Les écarts d'index doivent être justifiés
   - Les écarts anormaux doivent être signalés

3. **Calcul de la quantité vendue:**
   - Pour les ventes de carburant: quantité = index_fin - index_debut
   - La quantité doit être positive et raisonnable
   - Comparaison avec les relevés de stock

4. **Calcul des taxes:**
   - Application des taux de TVA et autres taxes
   - Calcul des montants HT et TTC
   - Application des remises si applicable

5. **Contrôle des paiements:**
   - Le montant total payé doit correspondre au montant dû
   - Les modes de paiement doivent être autorisés pour la trésorerie
   - Génération des écritures de trésorerie

### 5.2 Workflows

1. **Workflow de vente de carburant:**
   - Saisie des index de pistolet
   - Calcul de la quantité vendue
   - Application du prix et des taxes
   - Validation de la disponibilité du stock
   - Enregistrement du paiement
   - Mise à jour du stock
   - Génération des écritures comptables
   - Émission du ticket de caisse

2. **Workflow de vente boutique:**
   - Ajout des articles au panier
   - Application des prix, taxes et éventuelles remises
   - Validation du stock disponible
   - Enregistrement du paiement
   - Mise à jour du stock
   - Génération des écritures comptables
   - Émission du ticket de caisse

3. **Workflow d'arrêt de compte:**
   - Calcul du montant théorique
   - Saisie du montant réel constaté
   - Calcul de l'écart
   - Justification des écarts
   - Validation de l'arrêt de compte
   - Fermeture de la caisse

### 5.3 Cas particuliers

1. **Vente à crédit:**
   - Création d'une créance client
   - Suivi des échéances de paiement
   - Mise à jour du solde client
   - Contrôle des plafonds de crédit

2. **Retour de marchandise:**
   - Annulation ou correction de la vente
   - Mise à jour des stocks
   - Remboursement ou avoir
   - Écritures de contre-passation

3. **Correction d'erreur:**
   - Possibilité de corriger certaines données
   - Enregistrement de l'historique des modifications
   - Validation hiérarchique pour les corrections importantes

### 5.4 Impacts sur d'autres modules

1. **Module de trésorerie:**
   - Création d'écritures de trésorerie
   - Mise à jour des soldes de trésorerie
   - Suivi des encaissements clients

2. **Module de comptabilité:**
   - Génération automatique des écritures de vente
   - Mise à jour des comptes de produits et taxes
   - Calcul des coûts de revient

3. **Module de stocks:**
   - Mise à jour des stocks après vente
   - Calcul des coûts de revient
   - Génération des mouvements de stock

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)

```
ventes (1) ----< (n) ventes_details
ventes (1) ----< (n) ventes_tresorerie
ventes (1) ----< (n) suivis_ecarts_vente

utilisateurs (1) ----< (n) ventes (utilisateur caissier/pompiste)
utilisateurs (1) ----< (n) suivis_ecarts_vente (utilisateur détecteur/traitant)
employes (1) ----< (n) performances_employes

pistolets (1) ----< (n) ventes_details (ventes carburant)
articles (1) ----< (n) ventes_details (ventes boutique)
stocks (1) ----< (n) ventes_details

clients (1) ----< (n) ventes
tresoreries (1) ----< (n) ventes_tresorerie

performances_employes (1) ----< (n) rapports_ventes (pour analyse)
suivis_ecarts_vente (1) ----< (n) rapports_ventes (pour suivi)
```

### 6.2 Diagramme de séquence (textuel)

```
Caissier        Backend         Stock/Compta    Trésorerie
  |              |                |                |
  |---Créer Vente--->|             |                |
  |              |---Valider----->|                |
  |              |<---OK----------|                |
  |              |---Mouvement Stock|                |
  |              |<---OK----------|                |
  |              |---Écriture Compta|                |
  |              |<---OK----------|                |
  |              |---Trésorerie--->|                |
  |              |<---OK----------|                |
  |---Réponse----|                |                |
  |<-------------|                |                |
```

## 7. Tests Requis

### 7.1 Tests unitaires

1. **Test de validation des ventes:**
   - Tester la validation des données de vente
   - Tester les contraintes d'index de pistolet
   - Tester la validation des quantités et prix
   - Tester le calcul des taxes et remises

2. **Test du calcul des écarts:**
   - Tester le calcul des écarts d'index
   - Tester la détection des écarts anormaux
   - Tester la génération des alertes

3. **Test de performance des employés:**
   - Tester le calcul des indicateurs de performance
   - Tester le classement des employés
   - Tester les seuils d'alerte

### 7.2 Tests d'intégration

1. **Test complet de vente de carburant:**
   - Tester le workflow complet de vente
   - Vérifier la génération des écritures comptables
   - Vérifier la mise à jour des stocks
   - Vérifier la création des écritures de trésorerie

2. **Test de vente boutique:**
   - Tester le workflow de vente de produits
   - Vérifier la mise à jour des stocks boutique
   - Vérifier la génération des écritures comptables

3. **Test d'arrêt de compte:**
   - Tester le workflow complet d'arrêt de caisse
   - Vérifier la détection des écarts
   - Vérifier la fermeture de la caisse

### 7.3 Tests de charge/performance

1. **Charge élevée:**
   - Simuler 1000 ventes simultanées
   - Vérifier la stabilité du système
   - Mesurer les temps de réponse

2. **Accès concurrents:**
   - Tester plusieurs caissiers effectuant des ventes
   - Vérifier la cohérence des données
   - Tester la gestion des conflits

### 7.4 Jeux de données de test

1. **Données de base:**
   - Clients de test
   - Articles et carburants de test
   - Pistolets et stations de test
   - Plan comptable de test

2. **Scénarios de test:**
   - Ventes avec écarts
   - Ventes à crédit
   - Ventes avec remises
   - Arrêts de compte avec écarts

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées

1. **Implémentation des modèles de données:**
   - [ ] Étendre les tables existantes (ventes, ventes_details, etc.)
   - [ ] Créer les nouvelles tables (performances_employes, suivis_ecarts_vente, etc.)
   - [ ] Mettre à jour les relations entre tables existantes
   - [ ] Créer les indexes pour améliorer les performances
   - [ ] Implémenter les contraintes d'intégrité

2. **Développement des API:**
   - [ ] Créer les endpoints pour la gestion des ventes
   - [ ] Implémenter la validation des données d'entrée
   - [ ] Créer les endpoints pour les arrêts de compte
   - [ ] Développer les endpoints pour les rapports de performance
   - [ ] Créer les endpoints pour le suivi des écarts

3. **Logique métier:**
   - [ ] Implémenter le calcul des quantités vendues
   - [ ] Développer la logique de validation des index
   - [ ] Implémenter le calcul des taxes et remises
   - [ ] Créer les workflows de vente complétés
   - [ ] Gérer les cas particuliers (crédit, retours)

4. **Intégration comptable:**
   - [ ] Générer automatiquement les écritures comptables
   - [ ] Associer les taxes aux bons comptes
   - [ ] Créer les écritures de trésorerie
   - [ ] Gérer la mise à jour des soldes clients

5. **Mouvements de stock:**
   - [ ] Créer les mouvements de stock après vente
   - [ ] Calculer le CUMP pour les articles
   - [ ] Mettre à jour les stocks théoriques et réels
   - [ ] Générer les historiques de mouvements

6. **Sécurité et permissions:**
   - [ ] Implémenter les contrôles d'accès aux fonctionnalités
   - [ ] Créer les permissions spécifiques aux ventes
   - [ ] Gérer les restrictions par station
   - [ ] Journaliser les actions critiques

7. **Tests:**
   - [ ] Écrire les tests unitaires pour chaque fonctionnalité
   - [ ] Créer des tests d'intégration pour les workflows complets
   - [ ] Implémenter des tests de performance
   - [ ] Vérifier la couverture de test

8. **Documentation:**
   - [ ] Documenter les API endpoints
   - [ ] Créer les guides d'utilisation
   - [ ] Documenter les workflows métier
   - [ ] Préparer les guides de configuration

### 8.2 Ordre recommandé

1. Commencer par les modèles de données
2. Développer la logique métier de base
3. Implémenter les API pour les fonctionnalités principales
4. Intégrer la gestion des index de pistolet
5. Ajouter la gestion des performances employés
6. Intégrer la comptabilité et les mouvements de stock
7. Développer les rapports et analyses
8. Écrire et exécuter les tests
9. Finaliser la documentation

### 8.3 Livrables attendus

1. **Code source:**
   - Modèles de données complétés
   - Classes de service métier
   - API endpoints fonctionnels
   - Tests unitaires et d'intégration

2. **Documentation:**
   - Spécifications techniques mises à jour
   - Documentation API
   - Guides d'implémentation
   - Documentation utilisateur (partiellement)

3. **Scripts:**
   - Script de migration de base de données
   - Script de données de test
   - Script de configuration

## 9. Risques & Points de vigilance

### 9.1 Points sensibles

1. **Intégrité des données:**
   - Risque de données incohérentes entre ventes, stocks et comptabilité
   - Risque de duplication ou perte de données lors de la validation des ventes
   - Risque de calculs erronés des taxes ou des coûts

2. **Performance:**
   - Risque de ralentissement avec un grand volume de ventes
   - Risque de lenteur dans la génération des rapports
   - Risque de contention sur les données de stock

3. **Sécurité:**
   - Risque de modification non autorisée des données de vente
   - Risque de suppression accidentelle de ventes critiques
   - Risque d'accès non autorisé aux données sensibles

### 9.2 Risques techniques

1. **Complexité des calculs:**
   - Gestion du CUMP pour les articles avec différentes dates d'achat
   - Calcul des rendements horaires des employés
   - Gestion des corrections d'écarts et de leur impact comptable

2. **Synchronisation des données:**
   - Maintien de la cohérence entre stocks théoriques et réels
   - Synchronisation entre les modules de vente, stock et comptabilité
   - Gestion des accès concurrents aux mêmes données

3. **Évolutivité:**
   - Capacité du système à gérer un grand volume de transactions
   - Adaptabilité du système aux changements de besoins
   - Scalabilité horizontale des fonctionnalités

### 9.3 Dette technique potentielle

1. **Refactoring futur:**
   - Nécessité de simplifier les workflows de vente si des cas plus complexes émergent
   - Possibilité de revoir l'architecture si des modules additionnels sont prévus
   - Besoin d'optimiser les requêtes complexes pour les rapports

2. **Tests et documentation:**
   - Besoin de compléter la couverture de test
   - Nécessité de maintenir la documentation à jour
   - Besoin de créer des scénarios de test plus complets

3. **Sécurité:**
   - Ajout de contrôles d'accès plus fins si nécessaire
   - Mise en place de contrôles supplémentaires pour les validations critiques
   - Renforcement de la journalisation pour la traçabilité