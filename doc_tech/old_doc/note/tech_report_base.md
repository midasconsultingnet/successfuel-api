# Technical Specification - Module de Rapports

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de générer les rapports comptables et de gestion de la station-service SuccessFuel. L'objectif est de fournir aux gestionnaires et comptables un ensemble d'outils de reporting complets pour surveiller la performance financière et opérationnelle de leur station-service, conformément aux normes comptables locales (OHADA) et aux besoins de gestion opérationnelle.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module de reporting complet permettant :
- De générer les états financiers comptables (bilan, compte de résultat, grand livre, balance, journal)
- De produire des rapports de gestion opérationnelle
- De suivre les indicateurs clés de performance (KPIs)
- De faire des déclarations fiscales et de suivre la conformité
- D'analyser les tendances et de faire des prévisions

### Définition du périmètre
Le périmètre inclut :
- Génération des rapports comptables (bilan, grand livre, balance, journal)
- Génération des déclarations fiscales
- Suivi de la conformité
- Analyse de la consommation et du rendement des pompistes/caissiers
- Analyse des stocks, dettes/créances et rentabilité
- Calcul des indicateurs KPIs
- Prévisions et analyse des tendances
- Analyse comparative entre différentes périodes
- Export des rapports dans différents formats

## 2. User Stories & Critères d'acceptation

### US-REP-001: En tant que comptable, je veux générer un bilan
- **Critères d'acceptation :**
  - Pouvoir sélectionner une période de référence
  - Le bilan doit inclure les actifs, passifs et capitaux propres
  - Le bilan doit respecter la structure du plan comptable local
  - Pouvoir exporter le bilan au format PDF, Excel ou CSV
  - Les totaux doivent être correctement calculés et équilibrés

### US-REP-002: En tant que comptable, je veux générer un grand livre
- **Critères d'acceptation :**
  - Pouvoir sélectionner une période de référence
  - Le grand livre doit afficher tous les mouvements par compte
  - Le solde initial et final de chaque compte doit être calculé
  - Pouvoir filtrer par compte ou groupe de comptes
  - Pouvoir exporter les données au format PDF, Excel ou CSV

### US-REP-003: En tant que comptable, je veux générer une balance générale
- **Critères d'acceptation :**
  - Pouvoir sélectionner une période de référence
  - La balance doit afficher les soldes de tous les comptes
  - Pouvoir choisir le format (soldes période, soldes cumulés, soldes définitifs)
  - La balance doit être équilibrée (total débit = total crédit)
  - Pouvoir exporter la balance au format PDF, Excel ou CSV

### US-REP-004: En tant que comptable, je veux générer un journal
- **Critères d'acceptation :**
  - Pouvoir sélectionner une période de référence
  - Le journal doit afficher les écritures comptables ordonnées par date
  - Pouvoir filtrer par type d'opération ou journal spécifique
  - Les écritures doivent être validées et équilibrées
  - Pouvoir exporter le journal au format PDF, Excel ou CSV

### US-REP-005: En tant que gestionnaire, je veux générer des déclarations fiscales
- **Critères d'acceptation :**
  - Pouvoir générer les déclarations fiscales (TVA, etc.) selon les normes locales
  - Les montants doivent être calculés automatiquement
  - Pouvoir exporter les déclarations dans les formats requis
  - Pouvoir suivre les dates de dépôt et le statut des déclarations
  - Les déclarations doivent être conformes à la réglementation en vigueur

### US-REP-006: En tant que gestionnaire, je veux un suivi de conformité
- **Critères d'acceptation :**
  - Pouvoir suivre l'état de conformité aux différentes normes
  - Pouvoir planifier et suivre les contrôles de conformité
  - Afficher les non-conformités et les actions correctives
  - Pouvoir exporter les rapports de conformité

### US-REP-007: En tant que gestionnaire, je veux analyser la consommation
- **Critères d'acceptation :**
  - Pouvoir suivre la consommation de carburant par type
  - Pouvoir analyser les tendances de consommation
  - Afficher les données par période (jour, semaine, mois, année)
  - Pouvoir comparer avec les périodes précédentes

### US-REP-008: En tant que gestionnaire, je veux analyser le rendement des pompistes/caissiers
- **Critères d'acceptation :**
  - Pouvoir suivre le rendement de chaque employé
  - Calcul des indicateurs clés (ventes, volumes, etc.)
  - Pouvoir comparer les performances entre employés
  - Afficher les tendances de performance

### US-REP-009: En tant que gestionnaire, je veux analyser les stocks
- **Critères d'acceptation :**
  - Pouvoir consulter les niveaux de stock en temps réel
  - Afficher les mouvements de stock sur une période
  - Identifier les stocks en dessous du seuil minimal
  - Calculer la valeur des stocks

### US-REP-010: En tant que gestionnaire, je veux analyser les dettes/créances
- **Critères d'acceptation :**
  - Pouvoir suivre les dettes fournisseurs et créances clients
  - Afficher les échéances et le respect des délais
  - Identifier les retards de paiement
  - Calculer les soldes actuels et potentiels

### US-REP-011: En tant que gestionnaire, je veux analyser la rentabilité
- **Critères d'acceptation :**
  - Calculer les marges brutes et nettes
  - Afficher les indicateurs de rentabilité
  - Pouvoir analyser par produit ou service
  - Comparer la rentabilité entre différentes périodes

### US-REP-012: En tant que gestionnaire, je veux accéder aux indicateurs KPIs
- **Critères d'acceptation :**
  - Calculer les KPIs opérationnels clés
  - Afficher les KPIs sur une interface de tableau de bord
  - Pouvoir suivre l'évolution des KPIs dans le temps
  - Pouvoir configurer des alertes pour les seuils critiques

### US-REP-013: En tant que gestionnaire, je veux faire des prévisions
- **Critères d'acceptation :**
  - Pouvoir prévoir la demande en carburant
  - Calculer les prévisions de ventes
  - Afficher les tendances et les prévisions graphiquement
  - Pouvoir exporter les données de prévision

### US-REP-014: En tant que gestionnaire, je veux faire des analyses comparatives
- **Critères d'acceptation :**
  - Pouvoir comparer les données entre différentes périodes
  - Pouvoir comparer avec les objectifs fixés
  - Pouvoir comparer entre différentes stations
  - Afficher les écarts et les tendances

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: rapports_financiers
```sql
CREATE TABLE rapports_financiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_rapport VARCHAR(50) NOT NULL, -- 'bilan', 'compte_resultat', 'grand_livre', 'balance', 'journal', 'tva', 'etat_tva'
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    contenu JSONB, -- Contenu du rapport au format JSON
    format_sortie VARCHAR(20) DEFAULT 'PDF', -- PDF, Excel, CSV, etc.
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Termine', 'Erreur', 'Archive')),
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    station_id UUID REFERENCES stations(id),
    fichier_joint TEXT, -- Lien ou nom du fichier de rapport généré
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_rapports_financiers_type ON rapports_financiers(type_rapport);
CREATE INDEX idx_rapports_financiers_periode ON rapports_financiers(periode_debut, periode_fin);
CREATE INDEX idx_rapports_financiers_utilisateur ON rapports_financiers(utilisateur_generateur_id);
CREATE INDEX idx_rapports_financiers_compagnie ON rapports_financiers(compagnie_id);
CREATE INDEX idx_rapports_financiers_station ON rapports_financiers(station_id);
```

#### Table: declarations_fiscales
```sql
-- Déjà existante dans la base de données
-- Voir le fichier D:\succes_fuel\doc_tech\succes_fuel_bdd_reordered.sql
-- Pas besoin de la redéfinir ici
```

#### Table: kpi_operations
```sql
-- Déjà existante dans la base de données
-- Voir le fichier D:\succes_fuel\doc_tech\succes_fuel_bdd_reordered.sql
-- Pas besoin de la redéfinir ici
```

#### Table: suivi_conformite
```sql
-- Déjà existante dans la base de données
-- Voir le fichier D:\succes_fuel\doc_tech\succes_fuel_bdd_reordered.sql
-- Pas besoin de la redéfinir ici
```

#### Table: prevision_demande
```sql
-- Déjà existante dans la base de données
-- Voir le fichier D:\succes_fuel\doc_tech\succes_fuel_bdd_reordered.sql
-- Pas besoin de la redéfinir ici
```

#### Table: analyse_commerciale
```sql
-- Déjà existante dans la base de données
-- Voir le fichier D:\succes_fuel\doc_tech\succes_fuel_bdd_reordered.sql
-- Pas besoin de la redéfinir ici
```

#### Table: modeles_rapports
```sql
-- Déjà existante dans la base de données
-- Voir le fichier D:\succes_fuel\doc_tech\succes_fuel_bdd_reordered.sql
-- Pas besoin de la redéfinir ici
```

#### Nouvelle table: historique_rapports
```sql
CREATE TABLE historique_rapports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom_rapport VARCHAR(100) NOT NULL, -- Nom du rapport (ex: "Bilan mensuel")
    type_rapport VARCHAR(50) NOT NULL, -- Type de rapport
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    utilisateur_demandeur_id UUID REFERENCES utilisateurs(id),
    utilisateur_generation_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Demande' CHECK (statut IN ('Demande', 'En cours', 'Termine', 'Erreur', 'Archive')),
    parametres JSONB, -- Paramètres utilisés pour la génération
    resultat_generation TEXT, -- Résultat de la génération (succès/erreur)
    date_demande TIMESTAMPTZ DEFAULT now(),
    date_generation TIMESTAMPTZ,
    date_consultation TIMESTAMPTZ,
    est_a_jour BOOLEAN DEFAULT FALSE,
    compagnie_id UUID REFERENCES compagnies(id),
    station_id UUID REFERENCES stations(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_rapports_type ON historique_rapports(type_rapport);
CREATE INDEX idx_historique_rapports_periode ON historique_rapports(periode_debut, periode_fin);
CREATE INDEX idx_historique_rapports_demandeur ON historique_rapports(utilisateur_demandeur_id);
CREATE INDEX idx_historique_rapports_generation ON historique_rapports(utilisateur_generation_id);
```

### 3.2 Index recommandés
```sql
-- Index sur la table rapports_financiers
CREATE INDEX idx_rapports_financiers_date ON rapports_financiers(created_at);
CREATE INDEX idx_rapports_financiers_statut ON rapports_financiers(statut);

-- Index sur la table historique_rapports
CREATE INDEX idx_historique_rapports_date ON historique_rapports(created_at);
CREATE INDEX idx_historique_rapports_a_jour ON historique_rapports(est_a_jour);
```

### 3.3 Triggers / Règles d'intégrité
```sql
-- Trigger pour vérifier que la période de fin est postérieure à la période de début
CREATE OR REPLACE FUNCTION verifier_periode_rapport()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.periode_fin < NEW.periode_debut THEN
        RAISE EXCEPTION 'La période de fin (%s) doit être postérieure à la période de début (%s)', NEW.periode_fin, NEW.periode_debut;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du trigger
CREATE TRIGGER trigger_verifier_periode_rapport
    BEFORE INSERT OR UPDATE ON rapports_financiers
    FOR EACH ROW
    EXECUTE FUNCTION verifier_periode_rapport();

-- Trigger similaire pour la table historique_rapports
CREATE TRIGGER trigger_verifier_periode_historique
    BEFORE INSERT OR UPDATE ON historique_rapports
    FOR EACH ROW
    EXECUTE FUNCTION verifier_periode_rapport();
```

## 4. API Backend

### 4.1 Endpoints pour les rapports financiers

#### POST /api/rapports/financiers
- **Description:** Générer un nouveau rapport financier
- **Payload:**
```json
{
  "type_rapport": "bilan",
  "periode_debut": "2023-01-01",
  "periode_fin": "2023-01-31",
  "format_sortie": "PDF",
  "parametres": {
    "inclure_details": true,
    "format_compte": "complet",  // ou "resume"
    "devise_affichage": "MGA",
    "groupement": "classe"  // pour le grand livre
  }
}
```
- **Réponse:**
```json
{
  "id": "uuid-v4",
  "type_rapport": "bilan",
  "periode_debut": "2023-01-01",
  "periode_fin": "2023-01-31",
  "statut": "En cours",
  "format_sortie": "PDF",
  "fichier_joint": null,
  "date_generation": null,
  "compagnie_id": "uuid-v4",
  "station_id": "uuid-v4"
}
```
- **Codes d'erreur:**
  - 400: Données invalides (période incorrecte, type de rapport non valide)
  - 401: Non autorisé
  - 403: Accès refusé (permissions insuffisantes)
  - 422: Paramètres manquants ou invalides

#### GET /api/rapports/financiers/{id}
- **Description:** Récupérer un rapport financier spécifique
- **Réponse:**
```json
{
  "id": "uuid-v4",
  "type_rapport": "bilan",
  "periode_debut": "2023-01-01",
  "periode_fin": "2023-01-31",
  "contenu": {
    "actifs": {
      "immobilisations": 50000000,
      "stocks": 20000000,
      "creances": 15000000,
      "disponibilites": 5000000
    },
    "passifs": {
      "capitaux_propres": 60000000,
      "dettes": 30000000
    },
    "total_general": 90000000
  },
  "format_sortie": "PDF",
  "statut": "Termine",
  "fichier_joint": "rapports/2023-01-01_2023-01-31_bilan.pdf",
  "date_generation": "2023-02-01T10:30:00Z",
  "compagnie_id": "uuid-v4",
  "station_id": "uuid-v4"
}
```

#### GET /api/rapports/financiers
- **Description:** Lister les rapports financiers avec filtres
- **Paramètres d'URL:**
  - `type_rapport`: (optionnel) filtre par type de rapport
  - `periode_debut`: (optionnel) filtre par période
  - `periode_fin`: (optionnel) filtre par période
  - `statut`: (optionnel) filtre par statut
  - `compagnie_id`: (optionnel) filtre par compagnie
  - `station_id`: (optionnel) filtre par station
  - `page`: (optionnel) pagination
  - `limit`: (optionnel) pagination
- **Réponse:**
```json
{
  "rapports": [
    {
      "id": "uuid-v4",
      "type_rapport": "bilan",
      "periode_debut": "2023-01-01",
      "periode_fin": "2023-01-31",
      "statut": "Termine",
      "date_generation": "2023-02-01T10:30:00Z",
      "fichier_joint": "rapports/2023-01-01_2023-01-31_bilan.pdf"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "pages": 10
  }
}
```

#### GET /api/rapports/financiers/{id}/telecharger
- **Description:** Télécharger le fichier du rapport
- **Réponse:** Fichier binaire selon le format demandé

### 4.2 Endpoints pour les KPIs

#### GET /api/kpis
- **Description:** Récupérer les KPIs opérationnels
- **Paramètres d'URL:**
  - `station_id`: (optionnel) filtre par station
  - `periode_debut`: (optionnel) période de référence
  - `periode_fin`: (optionnel) période de référence
  - `type_carburant`: (optionnel) filtre par type de carburant
- **Réponse:**
```json
{
  "kpis": {
    "litres_vendus": 50000,
    "marge_brute": 25000000,
    "nombre_clients_servis": 1500,
    "volume_moyen_transaction": 20000,
    "productivite_horaires": 4000
  },
  "periode_reference": {
    "debut": "2023-01-01",
    "fin": "2023-01-31"
  }
}
```

### 4.3 Endpoints pour les déclarations fiscales

#### POST /api/declarations-fiscales
- **Description:** Créer une déclaration fiscale
- **Payload:**
```json
{
  "type_declaration": "TVA",
  "periode_debut": "2023-01-01",
  "periode_fin": "2023-01-31",
  "montant_declare": 3240000
}
```

#### GET /api/declarations-fiscales
- **Description:** Lister les déclarations fiscales
- **Réponse:**
```json
{
  "declarations": [
    {
      "id": "uuid-v4",
      "type_declaration": "TVA",
      "periode_debut": "2023-01-01",
      "periode_fin": "2023-01-31",
      "montant_total": 3000000,
      "montant_declare": 3240000,
      "ecart": 240000,
      "statut": "Soumis",
      "date_depot": "2023-02-15",
      "fichier_joint": "declarations/tva_2023-01.pdf"
    }
  ]
}
```

### 4.4 Endpoints pour les prévisions

#### GET /api/prevision-demande
- **Description:** Récupérer les prévisions de demande
- **Paramètres d'URL:**
  - `carburant_id`: (optionnel) filtre par type de carburant
  - `station_id`: (optionnel) filtre par station
  - `date_prevision`: (optionnel) date de prévision
- **Réponse:**
```json
{
  "prevision": {
    "quantite_prevue": 15000,
    "methode_prevision": "historique",
    "confiance_prevision": 85.5,
    "commentaire": "Prévision basée sur l'historique des 3 derniers mois",
    "date_prevision": "2023-02-01"
  }
}
```

### 4.5 Endpoints pour les analyses commerciales

#### GET /api/analyses-commerciales
- **Description:** Récupérer les analyses commerciales
- **Paramètres d'URL:**
  - `type_analyse`: (optionnel) filtre par type d'analyse
  - `periode_debut`: (optionnel) période de référence
  - `periode_fin`: (optionnel) période de référence
  - `station_id`: (optionnel) filtre par station
- **Réponse:**
```json
{
  "analyses": [
    {
      "id": "uuid-v4",
      "type_analyse": "tendance_vente",
      "periode_debut": "2023-01-01",
      "periode_fin": "2023-01-31",
      "resultat": {
        "croissance_vente": 12.5,
        "evolution_volume": 8.2,
        "types_plus_vendus": ["Super", "Gasoil"]
      },
      "commentaire": "Croissance constante sur le mois",
      "utilisateur_analyse_id": "uuid-v4"
    }
  ]
}
```

## 5. Logique Métier

### 5.1 Règles de génération des rapports financiers
1. Les soldes des comptes doivent être calculés en fonction des écritures comptables validées dans la période
2. Le bilan doit respecter l'équation fondamentale: Actifs = Passifs + Capitaux Propres
3. Le grand livre doit afficher toutes les écritures ordonnées par date
4. La balance doit être équilibrée (total débit = total crédit)
5. Les déclarations fiscales doivent respecter les règles de calcul spécifiques aux normes locales (OHADA)

### 5.2 Workflows
1. **Génération d'un rapport financier:**
   - L'utilisateur sélectionne le type de rapport et la période
   - Le système valide les paramètres (période correcte, permissions)
   - Le système récupère les données comptables pour la période
   - Le système applique les règles de calcul spécifiques au type de rapport
   - Le système génère le rapport dans le format demandé
   - Le système enregistre le rapport généré dans la base de données

2. **Génération d'une déclaration fiscale:**
   - Le système récupère les montants applicables selon les règles fiscales
   - Le système calcule les montants dus
   - Le système génère un document de déclaration selon les normes requises
   - Le système met à jour le statut de la déclaration

3. **Calcul des KPIs opérationnels:**
   - Le système récupère les données de ventes, stocks et personnel
   - Le système applique les formules de calcul pour chaque KPI
   - Le système stocke les valeurs calculées pour une référence future
   - Le système met à jour les tendances et indicateurs

### 5.3 Cas particuliers
1. Pour les rapports avec des dates futures, le système doit afficher un message d'erreur
2. Si une période est invalide (fin avant début), le système doit rejeter la requête
3. Si la base de données n'a pas suffisamment de données pour une période donnée, le système doit générer un rapport vide ou avec un message d'information
4. Pour les rapports en cascade (ex: consolidation de plusieurs stations), des règles spécifiques de regroupement doivent s'appliquer

### 5.4 Restrictions
1. Seuls les utilisateurs avec les permissions appropriées peuvent générer certains rapports (ex: bilan complet)
2. Les rapports doivent être générés seulement avec des données validées et approuvées
3. Les données sensibles doivent être masquées dans les rapports selon les permissions de l'utilisateur
4. Les rapports ne peuvent pas être générés pour des périodes futures

### 5.5 Impacts sur d'autres modules
1. Le module de reporting dépend fortement du module de comptabilité pour les écritures comptables
2. Le module de stock fournit des données pour les rapports d'inventaire et d'analyse
3. Le module de trésorerie fournit des données pour les rapports de flux de trésorerie
4. Le module des ventes fournit des données pour les analyses commerciales

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
rapports_financiers (1) -- (N) utilisateurs
rapports_financiers (1) -- (N) compagnies
rapports_financiers (1) -- (N) stations

declarations_fiscales -- utilisateurs (N) -- (1)
declarations_fiscales -- compagnies (N) -- (1)

kpi_operations -- stations (N) -- (1)
kpi_operations -- carburants (N) -- (0 ou 1)
kpi_operations -- utilisateurs (N) -- (1)

prevision_demande -- carburants (N) -- (1)
prevision_demande -- stations (N) -- (1)
prevision_demande -- utilisateurs (N) -- (1)

analyse_commerciale -- stations (N) -- (1)
analyse_commerciale -- utilisateurs (N) -- (1)

historique_rapports -- utilisateurs (N) -- (1)
historique_rapports -- compagnies (N) -- (1)
historique_rapports -- stations (N) -- (1)
```

### 6.2 Diagramme de séquence (textuel)
```
Utilisateur -> API: Demande de rapport (bilan, période, format)
API -> Validation: Vérification des droits et paramètres
Validation -> API: Autorisation validée
API -> Service: Récupération des écritures comptables
Service -> DB: Requête des écritures pour la période
DB -> Service: Retour des écritures
Service -> Calcul: Calcul des soldes par compte
Calcul -> Service: Soldes calculés
Service -> Formatage: Formatage selon le type de rapport
Formatage -> Service: Données formatées
Service -> API: Données du rapport
API -> Génération: Génération du fichier (PDF/Excel)
Génération -> API: Fichier généré
API -> DB: Enregistrement du rapport
DB -> API: Confirmation
API -> Utilisateur: Lien de téléchargement
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test de génération d'un rapport bilan avec des données valides
- Test de génération d'un rapport grand livre avec différentes options
- Test de génération d'une déclaration fiscale
- Test de calcul des KPIs avec différentes données
- Test de la validation des paramètres d'entrée

### 7.2 Tests d'intégration
- Test du workflow complet de génération d'un rapport financier
- Test de l'export des rapports dans différents formats
- Test de l'intégration avec le module de comptabilité
- Test de la sécurité d'accès aux rapports
- Test de la cohérence des données entre les différents rapports

### 7.3 Tests de charge/performance
- Test de la génération de rapports avec de grands volumes de données
- Test de la performance de génération pour des périodes longues
- Test de la concurrence (plusieurs utilisateurs générant des rapports simultanément)
- Test de la performance de téléchargement des rapports

### 7.4 Jeux de données de test
```sql
-- Données de test pour la génération de rapports
BEGIN;

-- Création d'une période comptable
INSERT INTO periodes_comptables (id, annee, mois, date_debut, date_fin, est_cloture, compagnie_id)
VALUES ('periode-uuid', 2023, 1, '2023-01-01', '2023-01-31', FALSE, 'compagnie-uuid');

-- Création de soldes comptables pour la période
INSERT INTO soldes_comptables (id, compte_numero, date_solde, solde_debit, solde_credit, compagnie_id, periode_id)
VALUES 
  ('solde-uuid-1', '100000', '2023-01-31', 0, 10000000, 'compagnie-uuid', 'periode-uuid'),  -- Capital
  ('solde-uuid-2', '411000', '2023-01-31', 5000000, 0, 'compagnie-uuid', 'periode-uuid'),   -- Clients
  ('solde-uuid-3', '530000', '2023-01-31', 2000000, 0, 'compagnie-uuid', 'periode-uuid'),   -- Banque
  ('solde-uuid-4', '370000', '2023-01-31', 8000000, 0, 'compagnie-uuid', 'periode-uuid');  -- Stocks

-- Création d'opérations pour tester les KPIs
INSERT INTO ventes (id, date_vente, total_ht, total_ttc, type_vente, compagnie_id, station_id)
VALUES 
  ('vente-uuid-1', '2023-01-15', 2000000, 2400000, 'Carburant', 'compagnie-uuid', 'station-uuid'),
  ('vente-uuid-2', '2023-01-20', 3000000, 3600000, 'Boutique', 'compagnie-uuid', 'station-uuid');

COMMIT;
```

## 8. Checklist Développeur

### 8.1 Tâches techniques
- [ ] Créer les modèles de données pour les rapports
- [ ] Implémenter les endpoints API REST pour les rapports
- [ ] Créer les services de calcul pour les indicateurs (bilan, grand livre, etc.)
- [ ] Implémenter les services de génération de rapports
- [ ] Créer les services de calcul des KPIs
- [ ] Implémenter les exports dans différents formats (PDF, Excel, CSV)
- [ ] Créer les interfaces utilisateur pour la génération et la consultation des rapports
- [ ] Implémenter les filtres et tris pour les rapports
- [ ] Créer les tests unitaires et d'intégration
- [ ] Implémenter la gestion de la sécurité et des permissions
- [ ] Créer les vues de tableau de bord pour les indicateurs clés
- [ ] Documenter les endpoints API

### 8.2 Ordre recommandé
1. Créer les modèles de données
2. Implémenter les services de base (calculs, export)
3. Créer les endpoints API
4. Implémenter la logique de génération des rapports
5. Créer les interfaces utilisateur
6. Intégrer les graphiques et visualisations
7. Créer les tests
8. Documenter le module
9. Optimiser les performances

### 8.3 Livrables attendus
- [ ] Fichiers de migration de la base de données
- [ ] Modèles de données
- [ ] Services de calcul des rapports
- [ ] Endpoints API
- [ ] Interface utilisateur pour les rapports
- [ ] Système d'export des rapports
- [ ] Tests unitaires et d'intégration
- [ ] Documentation technique
- [ ] Documentation utilisateur

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La performance de génération des rapports avec de grands volumes de données
- La complexité des calculs comptables selon les normes locales (OHADA)
- La sécurité des données dans les rapports selon les permissions des utilisateurs
- La précision des calculs fiscaux qui doivent être conformes à la réglementation

### 9.2 Risques techniques
- Risque de performance si les requêtes de données ne sont pas optimisées
- Risque de calculs incorrects si les règles comptables ne sont pas bien implémentées
- Risque de sécurité si les contrôles d'accès ne sont pas correctement mis en place
- Risque de perte de données si les rapports ne sont pas correctement sauvegardés

### 9.3 Dette technique potentielle
- La complexité des règles de calcul des rapports pourrait devenir difficile à maintenir
- L'ajout de nouveaux types de rapports pourrait complexifier l'architecture
- La gestion des différents formats d'export pourrait nécessiter des ajustements fréquents
- La mise à jour des normes fiscales et comptables pourrait nécessiter des modifications régulières