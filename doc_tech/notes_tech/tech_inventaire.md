# Technical Specification - Inventaires

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de contrôler les stocks de la station-service SuccessFuel. Cela inclut l'inventaire physique des stocks de carburant (mesure de hauteur dans les cuves avec calcul via barème) et des stocks de produits boutique, avec une comparaison systématique entre les stocks réels mesurés et les stocks théoriques du système, ainsi que l'analyse et la justification des écarts.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet d'inventaire qui permet :
- De mesurer la hauteur de carburant dans les cuves
- De calculer le volume via le barème de jauge
- De comparer les stocks réels avec les stocks théoriques
- De justifier les écarts constatés
- De suivre les tendances d'écart
- De gérer les inventaires boutique
- De produire des rapports d'analyse des écarts

### Définition du périmètre
Le périmètre inclut :
- Gestion des inventaires de carburant (mesure de hauteur, calcul via barème)
- Gestion des inventaires boutique (saisie de quantités réelles)
- Comparaison écart réel/théorique
- Analyse des écarts anormaux
- Suivi des températures (pour la correction volumétrique)
- Inventaires partiels ou complets
- Justification des écarts
- Analyse des tendances d'écart
- Génération de rapports d'inventaire

## 2. User Stories & Critères d'acceptation

### US-INV-001: En tant que gestionnaire, je veux mesurer la hauteur dans les cuves de carburant
- **Critères d'acceptation :**
  - Pouvoir saisir la hauteur mesurée dans chaque cuve
  - Pouvoir associer la mesure à une date et heure précise
  - Pouvoir saisir la température du carburant pour correction
  - Le système doit enregistrer l'utilisateur ayant effectué la mesure
  - Le système doit utiliser le barème de jauge pour calculer le volume

### US-INV-002: En tant que gestionnaire, je veux calculer le volume via le barème de jauge
- **Critères d'acceptation :**
  - Le système doit utiliser le barème spécifique à chaque cuve
  - Le calcul doit être automatique à partir de la hauteur mesurée
  - Le système doit appliquer les corrections de température si applicable
  - Le volume calculé doit être enregistré dans l'inventaire
  - Le système doit valider que le volume ne dépasse pas la capacité de la cuve

### US-INV-003: En tant que gestionnaire, je veux comparer les stocks réels et théoriques
- **Critères d'acceptation :**
  - Le système doit afficher le stock réel mesuré
  - Le système doit afficher le stock théorique du système
  - Le système doit calculer automatiquement l'écart (réel - théorique)
  - Le système doit indiquer si l'écart est acceptable ou anormal
  - Le système doit permettre de visualiser l'évolution des écarts

### US-INV-004: En tant que gestionnaire, je veux effectuer des inventaires boutique
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités réelles de produits en boutique
  - Pouvoir scanner les codes-barres pour facilitation
  - Le système doit calculer les écarts avec les stocks théoriques
  - Le système doit permettre de filtrer par famille de produits
  - Le système doit valider la saisie des quantités

### US-INV-005: En tant que gestionnaire, je veux justifier les écarts d'inventaire
- **Critères d'acceptation :**
  - Pouvoir commenter les écarts constatés
  - Pouvoir classer les écarts selon leur cause (perte, casse, vol, etc.)
  - Pouvoir joindre des justificatifs si nécessaire
  - Le système doit enregistrer la personne responsable de la justification
  - Le système doit permettre de valider la justification

### US-INV-006: En tant que gestionnaire, je veux analyser les tendances d'écart
- **Critères d'acceptation :**
  - Pouvoir visualiser l'évolution des écarts dans le temps
  - Pouvoir comparer les écarts entre différentes périodes
  - Pouvoir identifier les articles ou cuves avec écarts récurrents
  - Pouvoir exporter les analyses d'écart
  - Le système doit proposer des indicateurs de performance

### US-INV-007: En tant que gestionnaire, je veux effectuer des inventaires partiels
- **Critères d'acceptation :**
  - Pouvoir sélectionner uniquement certaines cuves/article pour l'inventaire
  - Pouvoir planifier des inventaires partiels réguliers
  - Le système doit distinguer les inventaires partiels des complets
  - Pouvoir combiner plusieurs inventaires partiels dans une période

### US-INV-008: En tant que gestionnaire, je veux être alerté des écarts anormaux
- **Critères d'acceptation :**
  - Le système doit détecter les écarts dépassant un seuil défini
  - Le système doit envoyer une alerte aux responsables
  - Le système doit permettre de définir les seuils d'alerte
  - Le système doit classifier les écarts par gravité

### US-INV-009: En tant que gestionnaire, je veux générer des rapports d'inventaire
- **Critères d'acceptation :**
  - Pouvoir générer des rapports par période
  - Pouvoir filtrer par station, type d'inventaire ou utilisateur
  - Pouvoir exporter les rapports dans différents formats
  - Pouvoir inclure les justifications des écarts dans le rapport
  - Pouvoir planifier la génération automatique de rapports

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: inventaires (existe déjà, extension requise)
```sql
-- Extension de la table inventaires existante
ALTER TABLE inventaires
ADD COLUMN IF NOT EXISTS seuil_alerte_ecart NUMERIC(10,3) DEFAULT 100, -- seuil en unité de mesure (litres, unités)
ADD COLUMN IF NOT EXISTS type_inventaire_detaille VARCHAR(30) DEFAULT 'Complexe' CHECK (type_inventaire_detaille IN ('Complexe', 'Simple', 'Partiel')),
ADD COLUMN IF NOT EXISTS responsable_validation_id UUID REFERENCES utilisateurs(id),
ADD COLUMN IF NOT EXISTS date_validation TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS observation_generale TEXT,
ADD COLUMN IF NOT EXISTS temperature_moyenne NUMERIC(5,2), -- température moyenne pendant l'inventaire
ADD COLUMN IF NOT EXISTS est_cloture BOOLEAN DEFAULT FALSE; -- indique si l'inventaire est cloturé

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_inventaires_cloture ON inventaires(est_cloture);
CREATE INDEX IF NOT EXISTS idx_inventaires_date_validation ON inventaires(date_validation);
CREATE INDEX IF NOT EXISTS idx_inventaires_type_detaille ON inventaires(type_inventaire_detaille);
```

#### Table: mesures_inventaire_cuves (existe déjà, extension requise)
```sql
-- Extension de la table mesures_inventaire_cuves existante
ALTER TABLE mesures_inventaire_cuves
ADD COLUMN IF NOT EXISTS temperature_mesure NUMERIC(5,2), -- température au moment de la mesure
ADD COLUMN IF NOT EXISTS correction_temperature NUMERIC(18,3) DEFAULT 0, -- correction appliquée
ADD COLUMN IF NOT EXISTS volume_corrigee NUMERIC(18,3) GENERATED ALWAYS AS (volume_reel + correction_temperature) STORED, -- volume corrigé
ADD COLUMN IF NOT EXISTS densite_carburant NUMERIC(5,3), -- densité mesurée
ADD COLUMN IF NOT EXISTS type_controle VARCHAR(20) DEFAULT 'Inventaire' CHECK (type_controle IN ('Inventaire', 'Qualite', 'Securite')),
ADD COLUMN IF NOT EXISTS est_ecart_anormal BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS seuil_gravite INTEGER DEFAULT 1 CHECK (seuil_gravite BETWEEN 1 AND 5), -- 1 = mineur, 5 = majeur
ADD COLUMN IF NOT EXISTS utilisateur_controle_id UUID REFERENCES utilisateurs(id);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_cuves_anormal ON mesures_inventaire_cuves(est_ecart_anormal);
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_cuves_gravite ON mesures_inventaire_cuves(seuil_gravite);
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_cuves_controle ON mesures_inventaire_cuves(utilisateur_controle_id);
```

#### Table: mesures_inventaire_articles (existe déjà, extension requise)
```sql
-- Extension de la table mesures_inventaire_articles existante
ALTER TABLE mesures_inventaire_articles
ADD COLUMN IF NOT EXISTS unite_mesure VARCHAR(10) DEFAULT 'Unite', -- unité de mesure
ADD COLUMN IF NOT EXISTS prix_unitaire_reel NUMERIC(18,4), -- prix unitaire au moment de l'inventaire
ADD COLUMN IF NOT EXISTS valeur_reelle NUMERIC(18,2) GENERATED ALWAYS AS (stock_reel * prix_unitaire_reel) STORED, -- valeur totale
ADD COLUMN IF NOT EXISTS est_ecart_anormal BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS seuil_gravite INTEGER DEFAULT 1 CHECK (seuil_gravite BETWEEN 1 AND 5), -- 1 = mineur, 5 = majeur
ADD COLUMN IF NOT EXISTS motif_ecart TEXT, -- motif de l'écart (perte, casse, vol, etc.)
ADD COLUMN IF NOT EXISTS utilisateur_controle_id UUID REFERENCES utilisateurs(id);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_articles_anormal ON mesures_inventaire_articles(est_ecart_anormal);
CREATE INDEX IF NOT EXISTS idx_mesures_inventaire_articles_gravite ON mesures_inventaire_articles(seuil_gravite);
```

#### Table: analyses_ecarts_inventaire
```sql
CREATE TABLE IF NOT EXISTS analyses_ecarts_inventaire (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventaire_id UUID NOT NULL REFERENCES inventaires(id),
    type_ecart VARCHAR(20) NOT NULL CHECK (type_ecart IN ('Carburant', 'Boutique', 'Complet')), -- type de stock concerné
    type_operation VARCHAR(50) NOT NULL, -- 'vente', 'achat', 'ajustement', etc.
    periode_analyse DATE NOT NULL, -- période concernée par l'analyse
    ecart_total NUMERIC(18,3) DEFAULT 0, -- écart total sur la période
    ecart_moyen NUMERIC(18,3) DEFAULT 0, -- écart moyen
    ecart_max NUMERIC(18,3) DEFAULT 0, -- écart maximum
    ecart_min NUMERIC(18,3) DEFAULT 0, -- écart minimum
    nombre_ecarts INTEGER DEFAULT 0, -- nombre total d'écarts
    nombre_ecarts_anormaux INTEGER DEFAULT 0, -- nombre d'écarts anormaux
    taux_anormalite NUMERIC(5,2) GENERATED ALWAYS AS (CASE WHEN nombre_ecarts > 0 THEN (nombre_ecarts_anormaux * 100.0 / nombre_ecarts) ELSE 0 END) STORED,
    tendance_ecart VARCHAR(20) DEFAULT 'Stable' CHECK (tendance_ecart IN ('Croissante', 'Decroissante', 'Stable', 'Variable')), -- tendance de l'écart
    analyse_automatique TEXT, -- analyse générée automatiquement
    recommandations TEXT, -- recommandations de l'analyse
    utilisateur_analyste_id UUID REFERENCES utilisateurs(id),
    date_analyse TIMESTAMPTZ NOT NULL DEFAULT now(),
    statut_analyse VARCHAR(20) DEFAULT 'En cours' CHECK (statut_analyse IN ('En cours', 'Terminee', 'Validee', 'Archivee')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_analyses_ecarts_inventaire_inventaire ON analyses_ecarts_inventaire(inventaire_id);
CREATE INDEX idx_analyses_ecarts_inventaire_periode ON analyses_ecarts_inventaire(periode_analyse);
CREATE INDEX idx_analyses_ecarts_inventaire_type ON analyses_ecarts_inventaire(type_ecart);
CREATE INDEX idx_analyses_ecarts_inventaire_tendance ON analyses_ecarts_inventaire(tendance_ecart);
```

#### Table: justifications_ecarts_inventaire
```sql
CREATE TABLE IF NOT EXISTS justifications_ecarts_inventaire (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mesure_cuves_id UUID REFERENCES mesures_inventaire_cuves(id), -- référence à la mesure d'écart
    mesure_articles_id UUID REFERENCES mesures_inventaire_articles(id), -- référence à la mesure d'écart
    type_justification VARCHAR(50) NOT NULL, -- 'perte', 'casse', 'vol', 'erreur saisie', etc.
    description_justification TEXT,
    utilisateur_justification_id UUID NOT NULL REFERENCES utilisateurs(id),
    date_justification TIMESTAMPTZ NOT NULL DEFAULT now(),
    est_valide BOOLEAN DEFAULT FALSE,
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    date_validation TIMESTAMPTZ,
    pieces_jointes JSONB DEFAULT '[]'::jsonb, -- fichier(s) de justificatif
    statut_justification VARCHAR(20) DEFAULT 'En attente' CHECK (statut_justification IN ('En attente', 'Validee', 'Rejetee', 'Enquete')),
    observation TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_justifications_ecarts_cuves ON justifications_ecarts_inventaire(mesure_cuves_id);
CREATE INDEX idx_justifications_ecarts_articles ON justifications_ecarts_inventaire(mesure_articles_id);
CREATE INDEX idx_justifications_ecarts_utilisateur ON justifications_ecarts_inventaire(utilisateur_justification_id);
CREATE INDEX idx_justifications_ecarts_valide ON justifications_ecarts_inventaire(est_valide);
```

#### Table: rapports_inventaire
```sql
CREATE TABLE IF NOT EXISTS rapports_inventaire (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_rapport VARCHAR(50) NOT NULL, -- 'resume_quotidien', 'analyse_ecarts', 'comparatif_periode', etc.
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    contenu JSONB, -- contenu du rapport au format JSON
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    utilisateur_validateur_id UUID REFERENCES utilisateurs(id),
    date_validation TIMESTAMPTZ,
    est_valide BOOLEAN DEFAULT FALSE,
    statut_rapport VARCHAR(20) DEFAULT 'En cours' CHECK (statut_rapport IN ('En cours', 'Termine', 'Valide', 'Archive')),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id),
    format_sortie VARCHAR(20) DEFAULT 'PDF' CHECK (format_sortie IN ('PDF', 'EXCEL', 'CSV', 'JSON')),
    fichier_joint TEXT, -- chemin vers le fichier généré
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_rapports_inventaire_type ON rapports_inventaire(type_rapport);
CREATE INDEX idx_rapports_inventaire_periode ON rapports_inventaire(periode_debut, periode_fin);
CREATE INDEX idx_rapports_inventaire_valide ON rapports_inventaire(est_valide);
CREATE INDEX idx_rapports_inventaire_station ON rapports_inventaire(station_id);
```

## 4. API Backend

### 4.1 Inventaire de carburant

#### Endpoint: Créer un inventaire de carburant
- **Méthode:** POST
- **URL:** `/api/inventaires/carburant`
- **Payload (JSON):**
```json
{
  "station_id": "uuid-station",
  "date_inventaire": "2023-11-25",
  "type_inventaire": "Carburant",
  "type_inventaire_detaille": "Complexe",
  "seuil_alerte_ecart": 100.000,
  "temperature_moyenne": 25.5,
  "mesures": [
    {
      "cuve_id": "uuid-cuve",
      "hauteur_reelle": 250.500,
      "temperature_mesure": 26.0,
      "densite_carburant": 0.750,
      "commentaire": "Mesure effectuée à 8h30"
    }
  ],
  "observation_generale": "RAS - Tous les mesures effectuées conformément au protocole"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-inventaire",
    "statut": "En cours",
    "nbre_mesures": 5,
    "nbre_ecarts_anormaux": 1,
    "date_creation": "2023-11-25T08:30:00Z",
    "utilisateur_responsable": {
      "id": "uuid-utilisateur",
      "nom": "NOM Prénom"
    }
  }
}
```
- **Codes d'erreur possibles:**
  - 400: Données invalides (hauteur incorrecte, cuve inexistante)
  - 401: Non authentifié
  - 403: Accès refusé
  - 404: Station ou cuve non trouvée
  - 500: Erreur serveur

#### Endpoint: Clôturer un inventaire
- **Méthode:** PUT
- **URL:** `/api/inventaires/{id}/cloturer`
- **Payload (JSON):**
```json
{
  "responsable_validation_id": "uuid-utilisateur",
  "observation_generale": "Inventaire terminé, tous les écarts justifiés"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-inventaire",
    "statut": "Termine",
    "est_cloture": true,
    "date_validation": "2023-11-25T17:00:00Z",
    "responsable_validation": {
      "id": "uuid-utilisateur",
      "nom": "NOM Prénom"
    }
  }
}
```

#### Endpoint: Justifier un écart d'inventaire
- **Méthode:** POST
- **URL:** `/api/inventaires/{id}/justifier-ecart`
- **Payload (JSON):**
```json
{
  "mesure_cuves_id": "uuid-mesure-cuve", // ou mesure_articles_id
  "type_justification": "perte_normal",
  "description_justification": "Perte normale par évaporation",
  "pieces_jointes": ["facture_justificative.pdf"],
  "statut_justification": "En attente"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-justification",
    "statut_justification": "En attente",
    "est_valide": false
  }
}
```

### 4.2 Inventaire boutique

#### Endpoint: Créer un inventaire boutique
- **Méthode:** POST
- **URL:** `/api/inventaires/boutique`
- **Payload (JSON):**
```json
{
  "station_id": "uuid-station",
  "date_inventaire": "2023-11-25",
  "type_inventaire": "Boutique",
  "type_inventaire_detaille": "Complexe",
  "mesures": [
    {
      "article_id": "uuid-article",
      "stock_reel": 150.000,
      "unite_mesure": "Unite",
      "commentaire": "Produit en bon état"
    }
  ],
  "observation_generale": "Inventaire effectué en présence du responsable de la boutique"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-inventaire",
    "statut": "En cours",
    "nbre_articles": 120,
    "nbre_ecarts_anormaux": 3,
    "date_creation": "2023-11-25T09:00:00Z"
  }
}
```

### 4.3 Analyse et rapports

#### Endpoint: Générer un rapport d'inventaire
- **Méthode:** POST
- **URL:** `/api/rapports/inventaire`
- **Payload (JSON):**
```json
{
  "type_rapport": "analyse_ecarts", // 'resume_quotidien', 'analyse_ecarts', 'comparatif_periode'
  "periode_debut": "2023-11-01",
  "periode_fin": "2023-11-25",
  "station_id": "uuid-station",
  "format_sortie": "PDF"
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-rapport",
    "type": "analyse_ecarts",
    "periode": {
      "debut": "2023-11-01",
      "fin": "2023-11-25"
    },
    "fichier_telechargement": "/api/rapports/inventaire/uuid-rapport/download",
    "statut_rapport": "En cours"
  }
}
```

#### Endpoint: Obtenir l'analyse des écarts
- **Méthode:** GET
- **URL:** `/api/inventaires/{id}/analyses-ecarts`
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-analyse",
    "inventaire_id": "uuid-inventaire",
    "type_ecart": "Carburant",
    "periode_analyse": "2023-11-25",
    "ecart_total": 150.000,
    "nombre_ecarts": 5,
    "nombre_ecarts_anormaux": 2,
    "taux_anormalite": 40.00,
    "tendance_ecart": "Croissante",
    "analyse_automatique": "Augmentation significative des écarts dans la cuve principale...",
    "recommandations": "Vérifier la calibration de la jauge et contrôler les pistolets..."
  }
}
```

## 5. Logique Métier

### 5.1 Règles de validation des inventaires

1. **Validation des mesures de hauteur:**
   - La hauteur mesurée ne doit pas être négative
   - La hauteur mesurée ne doit pas dépasser la hauteur maximale de la cuve
   - La température doit être dans des plages acceptables
   - Les mesures doivent être prises à des moments cohérents

2. **Calcul des volumes:**
   - Utilisation du barème de jauge spécifique à chaque cuve
   - Application des corrections de température si nécessaires
   - Vérification que le volume calculé ne dépasse pas la capacité de la cuve

3. **Calcul des écarts:**
   - Écart = Stock réel mesuré - Stock théorique du système
   - Pourcentage d'écart = (Écart / Stock théorique) * 100
   - Détection des écarts anormaux selon seuil prédéfini

4. **Validation des justifications:**
   - Les justifications doivent être complètes et cohérentes
   - Certaines justifications nécessitent une validation hiérarchique
   - Les justifications doivent correspondre à la nature de l'écart

### 5.2 Workflows

1. **Workflow d'inventaire de carburant:**
   - Préparation de l'inventaire
   - Mesure de la hauteur dans chaque cuve
   - Saisie des données (hauteur, température, densité)
   - Calcul automatique des volumes réels
   - Comparaison avec les stocks théoriques
   - Identification des écarts
   - Justification des écarts anormaux
   - Validation finale de l'inventaire

2. **Workflow d'inventaire boutique:**
   - Préparation de l'inventaire
   - Comptage physique des produits
   - Saisie des quantités réelles
   - Comparaison avec les stocks théoriques
   - Identification des écarts
   - Justification des écarts
   - Validation finale de l'inventaire

3. **Workflow de validation des écarts:**
   - Détection des écarts anormaux
   - Attribution d'une gravité à chaque écart
   - Analyse préliminaire automatique
   - Justification par l'utilisateur
   - Validation hiérarchique si nécessaire
   - Clôture de l'écriture

### 5.3 Cas particuliers

1. **Inventaire à chaud:**
   - Prise en compte des ventes en cours
   - Correction des stocks en temps réel
   - Synchronisation avec les systèmes de vente

2. **Inventaire partiel:**
   - Possibilité de sélectionner quelques cuves/articles
   - Agrégation des résultats avec les autres inventaires partiels
   - Maintien de la traceabilité

3. **Écarts récurrents:**
   - Détection des tendances
   - Mise en place de mesures correctrices
   - Analyse des causes profondes

### 5.4 Impacts sur d'autres modules

1. **Module de trésorerie:**
   - Ajustement des stocks peut impacter la valorisation
   - Mise à jour des mouvements de trésorerie
   - Génération d'écritures de régularisation

2. **Module de comptabilité:**
   - Génération d'écritures de régularisation de stock
   - Mise à jour des comptes de charges
   - Impact sur les résultats financiers

3. **Module de ventes:**
   - Mise à jour des stocks disponibles
   - Correction des écarts de pompe éventuels
   - Réajustement des indicateurs de performance

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)

```
inventaires (1) ----< (n) mesures_inventaire_cuves
inventaires (1) ----< (n) mesures_inventaire_articles
inventaires (1) ----< (n) analyses_ecarts_inventaire

utilisateurs (1) ----< (n) inventaires (responsable)
utilisateurs (1) ----< (n) mesures_inventaire_cuves (utilisateur_controle)
utilisateurs (1) ----< (n) justifications_ecarts_inventaire (utilisateur_justification)

cuves (1) ----< (n) mesures_inventaire_cuves
articles (1) ----< (n) mesures_inventaire_articles
stocks (1) ----< (n) mesures_inventaire_articles (stock_theorique)

mesures_inventaire_cuves (1) ----< (n) justifications_ecarts_inventaire
mesures_inventaire_articles (1) ----< (n) justifications_ecarts_inventaire

justifications_ecarts_inventaire (1) ----< (n) rapports_inventaire
analyses_ecarts_inventaire (1) ----< (n) rapports_inventaire
```

### 6.2 Diagramme de séquence (textuel)

```
Gestionnaire     Backend        Stock/Compta     Rapports
  |              |                |                |
  |---Démarrer Inventaire--->|    |                |
  |              |---Créer Inventaire--->|         |
  |              |<---OK-----------|                |
  |---Saisir Mesures-------->|    |                |
  |              |---Calculer Écarts---->|         |
  |              |<---Écarts Détectés----|         |
  |---Justifier Écarts------>|    |                |
  |              |---Valider Écarts----->|         |
  |              |<---OK-----------|                |
  |---Clôturer Inventaire--->|    |                |
  |              |---Écritures Compta--->|         |
  |              |<---OK-----------|                |
  |---Générer Rapport------->|                |
  |              |<---Rapport----|                |
```

## 7. Tests Requis

### 7.1 Tests unitaires

1. **Test de validation des mesures:**
   - Tester la validation des hauteurs mesurées
   - Tester les calculs de volume via barème
   - Tester les corrections de température
   - Tester les seuils d'écart

2. **Test de calcul des écarts:**
   - Tester le calcul automatique des écarts
   - Tester la détection des écarts anormaux
   - Tester les pourcentages d'écart
   - Tester les seuils de gravité

3. **Test de validation des justifications:**
   - Tester les validations hiérarchiques
   - Tester le workflow de justification
   - Tester les contraintes de justifications

### 7.2 Tests d'intégration

1. **Test complet d'inventaire de carburant:**
   - Tester le workflow complet d'inventaire
   - Vérifier la génération des écritures comptables
   - Vérifier la mise à jour des stocks
   - Vérifier la création des justifications

2. **Test d'inventaire boutique:**
   - Tester le workflow d'inventaire boutique
   - Vérifier la saisie et validation des quantités
   - Vérifier la détection des écarts

3. **Test d'analyse des écarts:**
   - Tester la génération des analyses
   - Vérifier les tendances calculées
   - Vérifier les recommandations

### 7.3 Tests de charge/performance

1. **Charge élevée:**
   - Simuler 1000 mesures d'inventaire simultanées
   - Vérifier la stabilité du système
   - Mesurer les temps de réponse

2. **Accès concurrents:**
   - Tester plusieurs gestionnaires effectuant des inventaires
   - Vérifier la cohérence des données
   - Tester la gestion des conflits

### 7.4 Jeux de données de test

1. **Données de base:**
   - Cuves avec barèmes de jauge
   - Articles de boutique
   - Stations et compagnies de test
   - Utilisateurs avec profils

2. **Scénarios de test:**
   - Inventaires complets et partiels
   - Écarts normaux et anormaux
   - Justifications avec validations
   - Analyses de tendances

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées

1. **Implémentation des modèles de données:**
   - [ ] Étendre les tables existantes (inventaires, mesures_inventaire_cuves, etc.)
   - [ ] Créer les nouvelles tables (analyses_ecarts_inventaire, justifications_ecarts_inventaire, etc.)
   - [ ] Mettre à jour les relations entre tables existantes
   - [ ] Créer les indexes pour améliorer les performances
   - [ ] Implémenter les contraintes d'intégrité

2. **Développement des API:**
   - [ ] Créer les endpoints pour la gestion des inventaires
   - [ ] Implémenter la validation des données d'entrée
   - [ ] Créer les endpoints pour la gestion des mesures
   - [ ] Développer les endpoints pour les justifications
   - [ ] Créer les endpoints pour les rapports

3. **Logique métier:**
   - [ ] Implémenter le calcul des volumes via barème
   - [ ] Développer la logique de détection des écarts
   - [ ] Implémenter le calcul des corrections de température
   - [ ] Créer les workflows d'inventaire complétés
   - [ ] Gérer les validations hiérarchiques

4. **Intégration comptable:**
   - [ ] Générer automatiquement les écritures de régularisation
   - [ ] Mettre à jour les soldes de stock
   - [ ] Créer les écritures de charges

5. **Sécurité et permissions:**
   - [ ] Implémenter les contrôles d'accès aux fonctionnalités
   - [ ] Créer les permissions spécifiques aux inventaires
   - [ ] Gérer les restrictions par station
   - [ ] Journaliser les actions critiques

6. **Tests:**
   - [ ] Écrire les tests unitaires pour chaque fonctionnalité
   - [ ] Créer des tests d'intégration pour les workflows complets
   - [ ] Implémenter des tests de performance
   - [ ] Vérifier la couverture de test

7. **Documentation:**
   - [ ] Documenter les API endpoints
   - [ ] Créer les guides d'utilisation
   - [ ] Documenter les workflows métier
   - [ ] Préparer les guides de configuration

### 8.2 Ordre recommandé

1. Commencer par les modèles de données
2. Développer la logique métier de base
3. Implémenter les API pour les fonctionnalités principales
4. Intégrer la gestion des mesures et calculs
5. Ajouter la gestion des justifications
6. Intégrer les analyses et rapports
7. Écrire et exécuter les tests
8. Finaliser la documentation

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
   - Risque de données incohérentes entre stocks réels et théoriques
   - Risque de calculs erronés des volumes via barème
   - Risque de pertes de données lors des mesures

2. **Performance:**
   - Risque de ralentissement lors de calculs complexes
   - Risque de lenteur dans la génération des rapports détaillés
   - Risque de contention sur les données de stock

3. **Sécurité:**
   - Risque de modification non autorisée des données d'inventaire
   - Risque de suppression accidentelle d'inventaires critiques
   - Risque d'accès non autorisé aux données sensibles

### 9.2 Risques techniques

1. **Complexité des calculs:**
   - Gestion des multiples barèmes de jauge
   - Corrections de température complexes
   - Calculs d'écarts avec seuils variables

2. **Synchronisation des données:**
   - Maintien de la cohérence entre stocks réels et théoriques
   - Synchronisation entre les modules d'inventaire, stock et comptabilité
   - Gestion des accès concurrents aux mêmes données

3. **Évolutivité:**
   - Capacité du système à gérer un grand volume d'inventaires
   - Adaptabilité du système aux changements de besoins
   - Scalabilité horizontale des fonctionnalités

### 9.3 Dette technique potentielle

1. **Refactoring futur:**
   - Nécessité de simplifier les workflows d'inventaire si des cas plus complexes émergent
   - Possibilité de revoir l'architecture si des modules additionnels sont prévus
   - Besoin d'optimiser les requêtes complexes pour les analyses

2. **Tests et documentation:**
   - Besoin de compléter la couverture de test
   - Nécessité de maintenir la documentation à jour
   - Besoin de créer des scénarios de test plus complets

3. **Sécurité:**
   - Ajout de contrôles d'accès plus fins si nécessaire
   - Mise en place de contrôles supplémentaires pour les validations critiques
   - Renforcement de la journalisation pour la traçabilité