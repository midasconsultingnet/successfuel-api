# Technical Specification - Gestion des achats

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer tous les approvisionnements de la station-service dans le système SuccessFuel. Cela inclut la gestion des achats de carburant (processus complet avec mesures avant/après, écarts, qualité) et des achats de produits pour la boutique, avec des fonctionnalités de suivi des coûts logistique, d'évaluation des fournisseurs et d'intégration comptable.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet de gestion des achats qui permet :
- De suivre l'approvisionnement en carburant avec les mesures de cuve avant/après
- De gérer les écarts de livraison
- De contrôler la qualité du carburant reçu
- De suivre les coûts logistique
- D'évaluer les performances des fournisseurs
- D'intégrer automatiquement les achats dans le système comptable
- De gérer les achats de produits pour la boutique
- De produire des rapports d'analyse des achats

### Définition du périmètre
Le périmètre inclut :
- Gestion des achats de carburant avec mesures avant/après livraison
- Gestion des achats de produits pour la boutique
- Gestion des bons de commande
- Calcul et suivi des écarts de livraison
- Analyse de la qualité du carburant
- Suivi des coûts logistique
- Génération automatique des écritures comptables
- Gestion des paiements fournisseurs
- Mise à jour des stocks après livraison
- Évaluation des fournisseurs
- Historique des achats et rapports d'analyse

## 2. User Stories & Critères d'acceptation

### US-ACH-001: En tant que gestionnaire, je veux enregistrer un achat de carburant
- **Critères d'acceptation :**
  - Pouvoir créer un achat avec les informations du fournisseur
  - Pouvoir spécifier le type d'achat (carburant ou produits)
  - Pouvoir ajouter des détails d'achat (article, quantité, prix unitaire)
  - Pouvoir associer l'achat à une ou plusieurs stations
  - Le système doit calculer automatiquement les totaux
  - Le système doit permettre d'associer la livraison à une cuve spécifique

### US-ACH-002: En tant que gestionnaire, je veux enregistrer les mesures avant/après livraison
- **Critères d'acceptation :**
  - Pouvoir saisir la mesure avant livraison pour chaque cuve concernée
  - Pouvoir saisir la mesure après livraison
  - Le système doit calculer automatiquement l'écart de livraison
  - Le système doit permettre de commenter les écarts significatifs
  - Les mesures doivent être associées à un utilisateur responsable

### US-ACH-003: En tant que gestionnaire, je veux suivre les écarts de livraison
- **Critères d'acceptation :**
  - Pouvoir visualiser les écarts pour chaque livraison
  - Le système doit alerter les écarts supérieurs à un seuil défini
  - Pouvoir justifier les écarts dans le système
  - Pouvoir distinguer les écarts normaux des écarts anormaux
  - Les écarts doivent être historisés pour analyse

### US-ACH-004: En tant que gestionnaire, je veux contrôler la qualité du carburant reçu
- **Critères d'acceptation :**
  - Pouvoir enregistrer les contrôles de qualité du carburant
  - Pouvoir spécifier les paramètres contrôlés (densité, octane, etc.)
  - Pouvoir associer les résultats du contrôle à chaque livraison
  - Le système doit permettre de classer les livraisons comme conformes/non conformes
  - Les observations doivent être conservées dans l'historique

### US-ACH-005: En tant que gestionnaire, je veux suivre les coûts logistique
- **Critères d'acceptation :**
  - Pouvoir associer les coûts logistique à chaque achat
  - Pouvoir distinguer les différents types de coûts (transport, assurance, etc.)
  - Le système doit calculer le coût total de revient
  - Pouvoir analyser les coûts par fournisseur ou type de carburant
  - Les coûts doivent être intégrés dans l'évaluation du stock

### US-ACH-006: En tant que gestionnaire, je veux évaluer les fournisseurs
- **Critères d'acceptation :**
  - Pouvoir suivre les performances de chaque fournisseur
  - Pouvoir analyser les écarts de livraison par fournisseur
  - Pouvoir noter la qualité des livraisons
  - Pouvoir visualiser l'historique des livraisons
  - Le système doit produire des indicateurs de performance

### US-ACH-007: En tant que comptable, je veux que les achats génèrent des écritures comptables
- **Critères d'acceptation :**
  - Chaque achat valide génère automatiquement des écritures comptables
  - Les écritures respectent le plan comptable local (OHADA)
  - Les coûts logistique sont intégrés dans la valorisation du stock
  - Les écritures sont associées à des journaux spécifiques (achat, stock)
  - Les écritures sont numérotées automatiquement

### US-ACH-008: En tant que gestionnaire, je veux gérer les achats boutique
- **Critères d'acceptation :**
  - Pouvoir créer des achats pour les produits de boutique
  - Pouvoir affecter les achats aux familles de produits
  - Pouvoir gérer les produits de manière distincte des carburants
  - Les achats boutique doivent affecter les stocks de produits
  - Les écritures comptables doivent être générées comme pour les carburants

### US-ACH-009: En tant que gestionnaire, je veux créer et suivre les bons de commande
- **Critères d'acceptation :**
  - Pouvoir créer des bons de commande avant la livraison
  - Pouvoir associer des achats aux bons de commande
  - Pouvoir suivre le statut des bons (en cours, livré, facturé)
  - Le système doit permettre de lier les factures aux bons de commande
  - Pouvoir annuler ou modifier les bons dans certaines conditions

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: achats (existe déjà, extension requise)
```sql
-- La table existe déjà mais nécessite des extensions pour la qualité et les coûts logistique
-- Extension de la table achats existante
ALTER TABLE achats 
ADD COLUMN IF NOT EXISTS date_livraison_prevue DATE,
ADD COLUMN IF NOT EXISTS temperature_livraison NUMERIC(5,2),
ADD COLUMN IF NOT EXISTS qualite_moyenne_livraison NUMERIC(3,2),
ADD COLUMN IF NOT EXISTS cout_logistique_total NUMERIC(18,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS evaluation_fournisseur NUMERIC(3,2), -- Note sur 10
ADD COLUMN IF NOT EXISTS observation_generale TEXT;

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_achats_date_livraison ON achats(date_livraison_prevue);
CREATE INDEX IF NOT EXISTS idx_achats_fournisseur ON achats(fournisseur_id);
```

#### Table: achats_details (existe déjà, extension requise)
```sql
-- La table existe déjà mais nécessite des extensions pour la qualité
-- Extension de la table achats_details existante
ALTER TABLE achats_details 
ADD COLUMN IF NOT EXISTS temperature_livraison NUMERIC(5,3),
ADD COLUMN IF NOT EXISTS qualite_livraison NUMERIC(3,2), -- Note sur 10
ADD COLUMN IF NOT EXISTS observation_detaillee TEXT;
```

#### Table: mesures_livraison (existe déjà, extension requise)
```sql
-- La table existe déjà, extension pour une meilleure gestion
ALTER TABLE mesures_livraison
ADD COLUMN IF NOT EXISTS temperature_ambiante NUMERIC(5,2),
ADD COLUMN IF NOT EXISTS densite_carburant NUMERIC(5,3),
ADD COLUMN IF NOT EXISTS seuil_alerte_ecart NUMERIC(10,3) DEFAULT 100, -- seuil en litres
ADD COLUMN IF NOT EXISTS est_ecart_significatif BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS justificatif_ecart TEXT,
ADD COLUMN IF NOT EXISTS verification_fiscale BOOLEAN DEFAULT FALSE;

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_mesures_livraison_achat ON mesures_livraison(achat_id);
CREATE INDEX IF NOT EXISTS idx_mesures_livraison_cuve ON mesures_livraison(cuve_id);
```

#### Table: qualite_carburant (existe déjà, extension requise)
```sql
-- La table existe déjà, mise à jour pour relier aux achats
ALTER TABLE qualite_carburant
ADD COLUMN IF NOT EXISTS achat_id UUID REFERENCES achats(id);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_achat ON qualite_carburant(achat_id);
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_date ON qualite_carburant(date_controle);
```

#### Table: couts_logistique (existe déjà, extension requise)
```sql
-- La table existe déjà, extension pour inclure les détails
ALTER TABLE couts_logistique
ADD COLUMN IF NOT EXISTS achat_detail_id UUID REFERENCES achats_details(id),
ADD COLUMN IF NOT EXISTS pourcentage_vente NUMERIC(5,2), -- pourcentage du coût par rapport à la vente
ADD COLUMN IF NOT EXISTS cout_unitaire NUMERIC(18,4); -- coût par unité de mesure

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_couts_logistique_achat ON couts_logistique(achat_id);
CREATE INDEX IF NOT EXISTS idx_couts_logistique_fournisseur ON couts_logistique(fournisseur_id);
```

#### Table: evaluations_fournisseurs
```sql
CREATE TABLE IF NOT EXISTS evaluations_fournisseurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID NOT NULL REFERENCES fournisseurs(id),
    achat_id UUID REFERENCES achats(id),
    date_evaluation DATE NOT NULL,
    critere VARCHAR(50) NOT NULL, -- 'delai_livraison', 'qualite', 'prix', 'service', etc.
    note NUMERIC(3,2) NOT NULL CHECK (note >= 0 AND note <= 10), -- Note sur 10
    commentaire TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_evaluations_fournisseurs_fournisseur ON evaluations_fournisseurs(fournisseur_id);
CREATE INDEX idx_evaluations_fournisseurs_date ON evaluations_fournisseurs(date_evaluation);
CREATE INDEX idx_evaluations_fournisseurs_critere ON evaluations_fournisseurs(critere);
```

#### Table: historique_livraisons
```sql
CREATE TABLE IF NOT EXISTS historique_livraisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID NOT NULL REFERENCES achats(id),
    fournisseur_id UUID NOT NULL REFERENCES fournisseurs(id),
    date_livraison_reelle DATE NOT NULL,
    delai_realise INTEGER, -- en jours
    ecart_moyen_livraison NUMERIC(10,3), -- écart moyen en litres
    qualite_moyenne NUMERIC(3,2), -- sur 10
    evaluation_globale NUMERIC(3,2), -- sur 10
    observation_generale TEXT,
    utilisateur_livraison_id UUID REFERENCES utilisateurs(id),
    statut_livraison VARCHAR(20) DEFAULT 'Complete' CHECK (statut_livraison IN ('Complete', 'Partielle', 'Anomalie')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_livraisons_achat ON historique_livraisons(achat_id);
CREATE INDEX idx_historique_livraisons_fournisseur ON historique_livraisons(fournisseur_id);
CREATE INDEX idx_historique_livraisons_date ON historique_livraisons(date_livraison_reelle);
```

#### Table: rapports_achats
```sql
CREATE TABLE IF NOT EXISTS rapports_achats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id),
    type_rapport VARCHAR(50) NOT NULL, -- 'synthese', 'qualite', 'couts', 'fournisseur'
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    contenu JSONB,
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_rapports_achats_type ON rapports_achats(type_rapport);
CREATE INDEX idx_rapports_achats_periode ON rapports_achats(periode_debut, periode_fin);
```

## 4. API Backend

### 4.1 Achats de carburant

#### Endpoint: Créer un achat de carburant
- **Méthode:** POST
- **URL:** `/api/achats/carburant`
- **Payload (JSON):**
```json
{
  "fournisseur_id": "uuid-fournisseur",
  "date_achat": "2023-12-01",
  "date_livraison_prevue": "2023-12-05",
  "type_achat": "Carburants",
  "reference_facture": "FAC-2023-12-001",
  "observation": "Livraison à effectuer en journée",
  "details": [
    {
      "carburant_id": "uuid-carburant",
      "cuve_id": "uuid-cuve",
      "quantite": 10000.000,
      "prix_unitaire": 4500.0000,
      "temperature_livraison": 25.5,
      "qualite_livraison": 8.5
    }
  ],
  "stations": ["uuid-station1", "uuid-station2"],
  "cout_logistique": 150000.00
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-achat",
    "reference": "ACH-2023-12-001",
    "statut": "En attente de livraison",
    "total": 45000000.00,
    "fournisseur": {
      "id": "uuid-fournisseur",
      "nom": "Nom du fournisseur"
    }
  }
}
```
- **Codes d'erreur possibles:**
  - 400: Données invalides
  - 401: Non authentifié
  - 403: Accès refusé
  - 404: Fournisseur, carburant ou cuve non trouvé
  - 500: Erreur serveur

#### Endpoint: Valider une livraison
- **Méthode:** PUT
- **URL:** `/api/achats/{id}/valider-livraison`
- **Payload (JSON):**
```json
{
  "mesures_avant": [
    {
      "cuve_id": "uuid-cuve",
      "mesure": 2500.000
    }
  ],
  "mesures_apres": [
    {
      "cuve_id": "uuid-cuve",
      "mesure": 12450.000
    }
  ],
  "temperature_ambiante": 26.5,
  "densite_carburant": 0.750,
  "qualite_controle": [
    {
      "type_controle": "densite",
      "valeur_relevee": "0.750",
      "resultat": "Conforme"
    }
  ],
  "couts_logistique": [
    {
      "type_cout": "transport",
      "montant": 80000.00,
      "description": "Transport routier"
    }
  ]
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-achat",
    "statut": "Livré",
    "date_livraison": "2023-12-05",
    "ecarts": [
      {
        "cuve_id": "uuid-cuve",
        "ecart_livraison": -50.000,
        "est_ecart_significatif": true
      }
    ],
    "evaluation_fournisseur": 7.8
  }
}
```

#### Endpoint: Liste des achats avec filtres
- **Méthode:** GET
- **URL:** `/api/achats?statut=Livré&date_debut=2023-12-01&date_fin=2023-12-31&fournisseur_id=uuid-fournisseur`
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid-achat",
        "reference_facture": "FAC-2023-12-001",
        "fournisseur": "Nom du fournisseur",
        "date_achat": "2023-12-01",
        "date_livraison": "2023-12-05",
        "total": 45000000.00,
        "statut": "Livré",
        "evaluation_globale": 7.8,
        "ecart_moyen": -50.000
      }
    ],
    "total": 150,
    "page": 1,
    "pages": 8
  }
}
```

### 4.2 Gestion des fournisseurs

#### Endpoint: Évaluer un fournisseur
- **Méthode:** POST
- **URL:** `/api/fournisseurs/{id}/evaluer`
- **Payload (JSON):**
```json
{
  "achats_ids": ["uuid-achat1", "uuid-achat2"],
  "evaluations": [
    {
      "critere": "delai_livraison",
      "note": 8.5,
      "commentaire": "Livraison dans les délais"
    },
    {
      "critere": "qualite",
      "note": 7.0,
      "commentaire": "Légère variation de densité"
    }
  ]
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "fournisseur_id": "uuid-fournisseur",
    "note_globale": 7.8,
    "evaluations_enregistrees": 2
  }
}
```

### 4.3 Rapports et analyses

#### Endpoint: Générer un rapport d'achats
- **Méthode:** POST
- **URL:** `/api/rapports/achats`
- **Payload (JSON):**
```json
{
  "type_rapport": "synthese", // 'synthese', 'qualite', 'couts', 'fournisseur'
  "periode_debut": "2023-12-01",
  "periode_fin": "2023-12-31",
  "fournisseur_id": "uuid-fournisseur", // optionnel
  "station_id": "uuid-station" // optionnel
}
```
- **Réponse (JSON):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-rapport",
    "type": "synthese",
    "periode": {
      "debut": "2023-12-01",
      "fin": "2023-12-31"
    },
    "contenu": {
      "achats_total": 450000000.00,
      "nombre_achats": 25,
      "ecarts_moyens": -25.500,
      "qualite_moyenne": 8.2,
      "couts_logistique": 1250000.00
    },
    "fichier_telechargement": "/api/rapports/achats/uuid-rapport/download"
  }
}
```

## 5. Logique Métier

### 5.1 Règles de validation des achats

1. **Validation des données d'achat:**
   - Le fournisseur doit être actif
   - Les dates d'achat et de livraison doivent être valides
   - La date de livraison ne peut être antérieure à la date d'achat
   - Les quantités et prix doivent être positifs
   - Les articles/carburants doivent être actifs

2. **Contrôle des mesures de livraison:**
   - La mesure après livraison doit être supérieure ou égale à la mesure avant
   - Les écarts de plus de 1% du volume livré doivent être signalés
   - Les écarts doivent être justifiés dans le système
   - Les températures doivent être dans des plages normales

3. **Contrôle de qualité:**
   - Les résultats de contrôle doivent être enregistrés pour chaque livraison
   - Les livraisons non conformes doivent être signalées
   - La qualité moyenne des livraisons influence l'évaluation du fournisseur

4. **Calcul des coûts logistique:**
   - Les coûts doivent être répartis entre les articles/carburants concernés
   - Les coûts unitaires doivent être intégrés dans la valorisation du stock
   - Le coût total de revient doit être calculé correctement

5. **Mouvements de stock:**
   - Les mouvements de stock sont générés automatiquement après validation de livraison
   - Le calcul du CUMP (coût unitaire moyen pondéré) doit être effectué
   - Les stocks théoriques sont mis à jour immédiatement

### 5.2 Workflows

1. **Workflow d'achat de carburant:**
   - Création de l'achat
   - Validation de l'achat
   - Réception des mesures avant livraison
   - Réception des mesures après livraison
   - Calcul des écarts
   - Contrôle de qualité
   - Validation de la livraison
   - Génération des écritures comptables
   - Mise à jour des stocks
   - Évaluation du fournisseur

2. **Workflow d'achat de boutique:**
   - Création de l'achat
   - Validation de l'achat
   - Réception de la livraison
   - Contrôle de qualité
   - Validation de la livraison
   - Génération des écritures comptables
   - Mise à jour des stocks

### 5.3 Cas particuliers

1. **Livraison partielle:**
   - Le système permet de valider une livraison partielle
   - Un achat peut être marqué comme "partiellement livré"
   - Les écarts sont calculés sur la base de la quantité livrée

2. **Anomalie de livraison:**
   - Si un écart significatif est détecté, le système alerte
   - Une procédure de vérification est déclenchée
   - L'achat peut être mis en "attente d'analyse"

3. **Retour de marchandise:**
   - Le système permet de gérer les retours de marchandises
   - Les mouvements de stock sont inversés
   - Les écritures comptables sont rectifiées

### 5.4 Impacts sur d'autres modules

1. **Module de trésorerie:**
   - Création d'écritures de dette fournisseur
   - Mise à jour des soldes fournisseurs
   - Génération de paiements fournisseurs

2. **Module de comptabilité:**
   - Génération automatique des écritures d'achat
   - Valorisation des stocks
   - Mise à jour des comptes de charges et de stocks

3. **Module de stocks:**
   - Mise à jour des stocks après livraison
   - Calcul des coûts de revient
   - Génération des mouvements de stock

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)

```
achats (1) ----< (n) achats_details
achats (1) ----< (n) mesures_livraison
achats (1) ----< (n) qualite_carburant
achats (1) ----< (n) couts_logistique
achats (1) ----< (n) historique_livraisons

fournisseurs (1) ----< (n) achats
fournisseurs (1) ----< (n) evaluations_fournisseurs

carburants (1) ----< (n) achats_details
cuves (1) ----< (n) achats_details
cuves (1) ----< (n) mesures_livraison
cuves (1) ----< (n) qualite_carburant

stocks (1) ----< (n) stocks_mouvements
achats (1) ----< (n) stocks_mouvements
achats (1) ----< (n) achats_tresorerie
achats (1) ----< (n) dettes_fournisseurs
```

### 6.2 Diagramme de séquence (textuel)

```
Client          Backend         Stock/Compta     Trésorerie
  |                |                |                |
  |---Créer Achat--->|                |                |
  |                |---Valider------>|                |
  |                |<---OK-----------|                |
  |                |                |                |
  |---Valider Livr->|---Mesures----->|                |
  |                |<---Calcul Ecart-|                |
  |                |---Contrôle Ql--->|                |
  |                |<---OK-----------|                |
  |                |---Mouvement Stock|                |
  |                |<---OK-----------|                |
  |                |---Écriture Compta|                |
  |                |<---OK-----------|                |
  |                |---Dette Créée--->|                |
  |                |<---OK-----------|                |
  |---Réponse------|                |                |
  |<---------------|                |                |
```

## 7. Tests Requis

### 7.1 Tests unitaires

1. **Test de validation des achats:**
   - Tester la validation des données d'achat
   - Tester les contraintes de date
   - Tester la validation des quantités et prix

2. **Test du calcul des écarts:**
   - Tester le calcul des écarts de livraison
   - Tester la détection des écarts significatifs
   - Tester la génération des justificatifs

3. **Test de la qualité du carburant:**
   - Tester l'enregistrement des contrôles de qualité
   - Tester la classification conforme/non conforme
   - Tester les alertes de qualité

### 7.2 Tests d'intégration

1. **Test complet d'achat de carburant:**
   - Tester le workflow complet d'achat
   - Vérifier la génération des écritures comptables
   - Vérifier la mise à jour des stocks
   - Vérifier la création des dettes fournisseurs

2. **Test d'achat boutique:**
   - Tester le workflow d'achat de produits
   - Vérifier la mise à jour des stocks boutique
   - Vérifier la génération des écritures comptables

3. **Test de performance:**
   - Tester le traitement de plusieurs achats simultanément
   - Vérifier les temps de réponse
   - Tester la montée en charge

### 7.3 Tests de charge/performance

1. **Charge élevée:**
   - Simuler 1000 achats simultanés
   - Vérifier la stabilité du système
   - Mesurer les temps de réponse

2. **Accès concurrents:**
   - Tester plusieurs utilisateurs créant des achats
   - Vérifier la cohérence des données
   - Tester la gestion des conflits

### 7.4 Jeux de données de test

1. **Données de base:**
   - Fournisseurs de test
   - Carburants et articles de test
   - Stations et cuves de test
   - Plan comptable de test

2. **Scénarios de test:**
   - Achats avec écarts
   - Achats avec anomalies de qualité
   - Achats avec coûts logistique
   - Évaluations de fournisseurs

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées

1. **Implémentation des modèles de données:**
   - [ ] Créer les tables supplémentaires (évaluations_fournisseurs, historique_livraisons)
   - [ ] Mettre à jour les relations entre tables existantes
   - [ ] Créer les indexes pour améliorer les performances
   - [ ] Implémenter les contraintes d'intégrité

2. **Développement des API:**
   - [ ] Créer les endpoints pour la gestion des achats
   - [ ] Implémenter la validation des données d'entrée
   - [ ] Créer les endpoints pour la gestion des mesures de livraison
   - [ ] Développer les endpoints pour l'évaluation des fournisseurs
   - [ ] Créer les endpoints pour les rapports d'achats

3. **Logique métier:**
   - [ ] Implémenter le calcul des écarts de livraison
   - [ ] Développer la logique de contrôle de qualité
   - [ ] Implémenter le calcul des coûts logistique
   - [ ] Créer les workflows d'achat complétés
   - [ ] Gérer les cas particuliers (anomalies, retours)

4. **Intégration comptable:**
   - [ ] Générer automatiquement les écritures comptables
   - [ ] Associer les coûts logistique à la valorisation
   - [ ] Créer les écritures de dette fournisseur
   - [ ] Gérer la mise à jour des soldes fournisseurs

5. **Mouvements de stock:**
   - [ ] Créer les mouvements de stock après livraison
   - [ ] Calculer le CUMP pour les articles
   - [ ] Mettre à jour les stocks théoriques et réels
   - [ ] Générer les historiques de mouvements

6. **Sécurité et permissions:**
   - [ ] Implémenter les contrôles d'accès aux fonctionnalités
   - [ ] Créer les permissions spécifiques aux achats
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
4. Intégrer la gestion des mesures de livraison
5. Ajouter la gestion de la qualité
6. Intégrer la comptabilité et les mouvements de stock
7. Développer les rapports et analyses
8. Écrire et exécuter les tests
9. Finaliser la documentation

### 8.3 Livrables attendus

1. **Code source:**
   - Modèles de données complets
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
   - Risque de données incohérentes entre stocks, achats et comptabilité
   - Risque de duplication ou perte de données lors de la validation de livraison
   - Risque de calculs erronés des écarts ou des coûts logistique

2. **Performance:**
   - Risque de ralentissement avec un grand volume d'achats
   - Risque de lenteur dans la génération des rapports
   - Risque de contention sur les données de stock

3. **Sécurité:**
   - Risque de modification non autorisée des données d'achat
   - Risque de suppression accidentelle de données critiques
   - Risque d'accès non autorisé aux données sensibles

### 9.2 Risques techniques

1. **Complexité des calculs:**
   - Gestion du CUMP pour les articles avec différentes dates d'achat
   - Répartition correcte des coûts logistique
   - Gestion des corrections d'écarts et de leur impact comptable

2. **Synchronisation des données:**
   - Maintien de la cohérence entre stocks théoriques et réels
   - Synchronisation entre les modules d'achat, stock et comptabilité
   - Gestion des accès concurrents aux mêmes données

3. **Évolutivité:**
   - Capacité du système à gérer un grand volume de transactions
   - Adaptabilité du système aux changements de besoins
   - Scalabilité horizontale des fonctionnalités

### 9.3 Dette technique potentielle

1. **Refactoring futur:**
   - Nécessité de simplifier les workflows d'achat si des cas plus complexes émergent
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
