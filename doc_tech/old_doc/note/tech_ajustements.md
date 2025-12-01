# Technical Specification - Module Ajustements

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer les ajustements de stock et les réinitialisations d'index dans le système SuccessFuel. L'objectif est de permettre aux gestionnaires de gérer les écarts de stock boutique (périmés, cassés) et de réinitialiser les index de pistolets de manière sécurisée avec validation hiérarchique.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas de fonctionnalités adéquates pour :
- Gérer les sorties de stock boutique pour les articles périmés ou cassés
- Analyser les causes de péremption
- Réinitialiser les index de pistolets de manière sécurisée
- Appliquer des validations hiérarchiques pour les opérations sensibles
- Conserver un historique des actions critiques

### Définition du périmètre
Le périmètre inclut :
- Gestion des ajustements de stock boutique (entrée/sortie pour périmés/cassés)
- Analyse des causes de péremption
- Réinitialisation sécurisée des index de pistolets
- Mise en place d'un système de validation hiérarchique
- Journalisation des actions critiques
- Génération des écritures comptables liées aux ajustements
- Intégration avec les modules de gestion des stocks et des pistolets

## 2. User Stories & Critères d'acceptation

### US-AJUST-001: En tant que gestionnaire, je veux gérer les sorties de stock boutique pour les articles périmés ou cassés
- **Critères d'acceptation :**
  - Pouvoir créer un ajustement de stock pour les articles périmés ou cassés
  - Pouvoir spécifier l'article, la quantité et le motif de l'ajustement
  - Pouvoir sélectionner le type d'ajustement (Perte, Casse, Péremption)
  - Le système doit mettre à jour le stock théorique
  - Le système doit enregistrer l'utilisateur responsable
  - Le système doit justifier l'ajustement

### US-AJUST-002: En tant que gestionnaire, je veux analyser les causes de péremption
- **Critères d'acceptation :**
  - Pouvoir visualiser les ajustements de stock par motif
  - Pouvoir filtrer par période, article ou station
  - Pouvoir exporter les données d'analyse
  - Le système doit proposer des indicateurs clés (quantité, valeur, fréquence)
  - Pouvoir identifier les articles les plus affectés par la péremption

### US-AJUST-003: En tant que gestionnaire, je veux réinitialiser les index de pistolets de manière sécurisée
- **Critères d'acceptation :**
  - Pouvoir demander une réinitialisation d'index pour un pistolet spécifique
  - Pouvoir spécifier l'ancien index et le nouvel index
  - Pouvoir justifier la réinitialisation
  - Le système ne doit pas permettre la modification directe des index existants
  - Le système doit enregistrer la demande de réinitialisation

### US-AJUST-004: En tant que gestionnaire, je veux appliquer des validations hiérarchiques pour les réinitialisations d'index
- **Critères d'acceptation :**
  - Les réinitialisations d'index doivent être validées par un utilisateur autorisé
  - Les validations hiérarchiques doivent être configurables par type d'opération
  - Le système doit notifier les validateurs appropriés
  - Le système doit bloquer les réinitialisations non validées
  - Le système doit conserver l'historique des validations

### US-AJUST-005: En tant que gestionnaire, je veux que les ajustements génèrent des écritures comptables
- **Critères d'acceptation :**
  - Chaque ajustement valide génère automatiquement des écritures comptables
  - Les écritures respectent le plan comptable local (OHADA)
  - Les ajustements de stock génèrent des écritures de type "Ajustement stock"
  - Les écritures sont associées à des journaux spécifiques
  - Les écritures sont numérotées automatiquement

### US-AJUST-006: En tant que gestionnaire, je veux accéder à un historique des ajustements
- **Critères d'acceptation :**
  - Pouvoir consulter l'historique complet des ajustements
  - Pouvoir filtrer par type d'ajustement, période, utilisateur
  - Pouvoir visualiser les détails de chaque ajustement
  - Le système doit conserver les données avant/après modification
  - Le système doit tracer les utilisateurs responsables

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: ajustements_stock (EXISTANTE - à compléter si nécessaire)
```sql
CREATE TABLE ajustements_stock (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE, -- Pour les carburants
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    type_ajustement VARCHAR(20) NOT NULL CHECK (type_ajustement IN ('Entree', 'Sortie', 'Perte', 'Casse', 'Peremption')),
    quantite NUMERIC(18,3) NOT NULL, -- Positive pour entrée, négative pour sortie
    motif TEXT NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    date_ajustement DATE NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_ajustements_stock_article ON ajustements_stock(article_id);
CREATE INDEX idx_ajustements_stock_cuve ON ajustements_stock(cuve_id);
CREATE INDEX idx_ajustements_stock_station ON ajustements_stock(station_id);
CREATE INDEX idx_ajustements_stock_compagnie ON ajustements_stock(compagnie_id);
CREATE INDEX idx_ajustements_stock_date ON ajustements_stock(date_ajustement);
CREATE INDEX idx_ajustements_stock_type ON ajustements_stock(type_ajustement);
```

#### Table: reinitialisation_index_pistolets (EXISTANTE - à compléter si nécessaire)
```sql
CREATE TABLE reinitialisation_index_pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pistolet_id UUID REFERENCES pistolets(id),
    ancien_index NUMERIC(18,3) NOT NULL,
    nouvel_index NUMERIC(18,3) NOT NULL,
    utilisateur_demande_id UUID REFERENCES utilisateurs(id),
    utilisateur_autorise_id UUID REFERENCES utilisateurs(id),
    motif TEXT NOT NULL,
    date_demande TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_autorisation TIMESTAMPTZ,
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Approuve', 'Rejete', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_reinit_index_pistolets_pistolet ON reinitialisation_index_pistolets(pistolet_id);
CREATE INDEX idx_reinit_index_pistolets_demande ON reinitialisation_index_pistolets(utilisateur_demande_id);
CREATE INDEX idx_reinit_index_pistolets_autorise ON reinitialisation_index_pistolets(utilisateur_autorise_id);
CREATE INDEX idx_reinit_index_pistolets_statut ON reinitialisation_index_pistolets(statut);
CREATE INDEX idx_reinit_index_pistolets_date ON reinitialisation_index_pistolets(date_demande);
```

#### Table: validations_hierarchiques (EXISTANTE - à compléter si nécessaire)
```sql
CREATE TABLE validations_hierarchiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(50) NOT NULL, -- Ex: 'reinitialisation_index', 'ajustement_stock'
    seuil_montant NUMERIC(18,2), -- Montant à partir duquel validation est requise
    niveau_validation INTEGER DEFAULT 1, -- Niveau hiérarchique requis pour validation
    profil_autorise_id UUID REFERENCES profils(id), -- Profil autorisé à valider
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);

-- Index pour les performances
CREATE INDEX idx_validations_hierarchiques_operation_type ON validations_hierarchiques(operation_type);
CREATE INDEX idx_validations_hierarchiques_profil ON validations_hierarchiques(profil_autorise_id);
```

#### Table: causes_premption (NOUVELLE - pour analyser les causes de péremption)
```sql
CREATE TABLE causes_peremption (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_causes_peremption_compagnie ON causes_peremption(compagnie_id);
```

#### Table: ajustements_stock_causes (NOUVELLE - pour lier les ajustements aux causes de péremption)
```sql
CREATE TABLE ajustements_stock_causes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ajustement_stock_id UUID REFERENCES ajustements_stock(id) ON DELETE CASCADE,
    cause_peremption_id UUID REFERENCES causes_peremption(id),
    details TEXT, -- Détails spécifiques à chaque ajustement
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_ajustements_stock_causes_ajustement ON ajustements_stock_causes(ajustement_stock_id);
CREATE INDEX idx_ajustements_stock_causes_cause ON ajustements_stock_causes(cause_peremption_id);
```

### 3.2 Relations
- `ajustements_stock` → `articles` (many-to-one): chaque ajustement concerne un article
- `ajustements_stock` → `stations` (many-to-one): chaque ajustement est lié à une station
- `ajustements_stock` → `utilisateurs` (many-to-one): chaque ajustement est fait par un utilisateur
- `reinitialisation_index_pistolets` → `pistolets` (many-to-one): chaque réinitialisation concerne un pistolet
- `reinitialisation_index_pistolets` → `utilisateurs` (many-to-one): chaque réinitialisation est demandée/demandée par un utilisateur
- `validations_hierarchiques` → `profils` (many-to-one): chaque validation requiert un profil spécifique
- `ajustements_stock_causes` → `ajustements_stock` (many-to-one): chaque ajustement peut avoir une ou plusieurs causes
- `ajustements_stock_causes` → `causes_peremption` (many-to-one): chaque ajustement peut être lié à une cause de péremption

### 3.3 Triggers / Règles d'intégrité
- Trigger pour vérifier la cohérence des index lors de la réinitialisation (nouvel index > ancien index pour certaines opérations)
- Trigger pour empêcher la modification directe des index de pistolets (doit passer par la table de réinitialisation)
- Contrainte pour s'assurer que la quantité d'ajustement est positive
- Contrainte pour s'assurer que les ajustements de type "Perte", "Casse", "Peremption" ont une quantité négative

## 4. API Backend

### 4.1 Gestion des ajustements de stock
- **POST** `/api/ajustements-stock` - Créer un ajustement de stock
  - Payload: `{article_id, station_id, type_ajustement, quantite, motif, commentaire}`
  - Réponse: `{id, article_id, station_id, type_ajustement, quantite, motif, utilisateur_id, date_ajustement}`
  - Codes d'erreur: `400` (erreur validation), `401` (non authentifié), `403` (accès refusé), `404` (article/station non trouvé), `500` (erreur serveur)

- **GET** `/api/ajustements-stock` - Lister les ajustements de stock
  - Paramètres: `?station_id&date_debut&date_fin&type_ajustement&motif&compagnie_id&page&limit`
  - Réponse: `[{id, article_id, article_code, article_libelle, type_ajustement, quantite, motif, utilisateur_id, utilisateur_nom, date_ajustement, commentaire}, ...]`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `500` (erreur serveur)

- **GET** `/api/ajustements-stock/{id}` - Consulter un ajustement spécifique
  - Réponse: `{id, article_id, article_code, article_libelle, station_id, station_code, station_nom, type_ajustement, quantite, motif, utilisateur_id, utilisateur_nom, date_ajustement, commentaire, created_at}`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `404` (ajustement non trouvé), `500` (erreur serveur)

### 4.2 Gestion des réinitialisations d'index de pistolets
- **POST** `/api/reinitialisations-index` - Créer une demande de réinitialisation d'index
  - Payload: `{pistolet_id, ancien_index, nouvel_index, motif}`
  - Réponse: `{id, pistolet_id, ancien_index, nouvel_index, utilisateur_demande_id, motif, statut, date_demande}`
  - Codes d'erreur: `400` (erreur validation), `401` (non authentifié), `403` (accès refusé), `404` (pistolet non trouvé), `500` (erreur serveur)

- **PUT** `/api/reinitialisations-index/{id}/valider` - Valider une demande de réinitialisation
  - Payload: `{statut: "Approuve"|"Rejete", commentaire: "optionnel"}`
  - Réponse: `{id, statut, date_autorisation, utilisateur_autorise_id}`
  - Codes d'erreur: `400` (erreur validation), `401` (non authentifié), `403` (accès refusé), `404` (demande non trouvée), `500` (erreur serveur)

- **GET** `/api/reinitialisations-index` - Lister les réinitialisations
  - Paramètres: `?pistolet_id&statut&date_debut&date_fin&compagnie_id&page&limit`
  - Réponse: `[{id, pistolet_id, pistolet_code, ancien_index, nouvel_index, utilisateur_demande_id, utilisateur_demande_nom, utilisateur_autorise_id, utilisateur_autorise_nom, motif, statut, date_demande}, ...]`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `500` (erreur serveur)

### 4.3 Gestion des causes de péremption
- **POST** `/api/causes-peremption` - Créer une cause de péremption
  - Payload: `{libelle, description}`
  - Réponse: `{id, libelle, description, statut}`
  - Codes d'erreur: `400` (erreur validation), `401` (non authentifié), `403` (accès refusé), `500` (erreur serveur)

- **GET** `/api/causes-peremption` - Lister les causes de péremption
  - Paramètres: `?statut&compagnie_id`
  - Réponse: `[{id, libelle, description, statut}, ...]`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `500` (erreur serveur)

### 4.4 Analyse des ajustements
- **GET** `/api/rapports/ajustements-analyse` - Obtenir l'analyse des ajustements
  - Paramètres: `?station_id&date_debut&date_fin&type_ajustement&compagnie_id`
  - Réponse: `{total_quantite, total_valeur, ajustements_par_motif: [{motif, quantite, valeur}], articles_plus_affectes: [{article_id, libelle, quantite_pertee}]}`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `500` (erreur serveur)

## 5. Logique Métier

### 5.1 Règles de validation des ajustements de stock
- Un ajustement de type "Perte", "Casse" ou "Peremption" doit avoir une quantité strictement négative
- Un ajustement de type "Entree" doit avoir une quantité strictement positive
- L'article concerné ne doit pas être en statut "Inactif" ou "Supprime"
- La station concernée ne doit pas être en statut "Inactif" ou "Supprime"
- Un motif détaillé est requis pour tout ajustement de stock
- Les ajustements de grande valeur (dépassant un seuil configurable) nécessitent une validation hiérarchique

### 5.2 Règles de validation des réinitialisations d'index
- La réinitialisation ne peut pas être demandée par un utilisateur n'ayant pas les droits appropriés
- Le nouvel index ne peut pas être inférieur à l'ancien index sans justification appropriée
- Chaque demande de réinitialisation nécessite une validation hiérarchique avant application
- Une demande de réinitialisation ne peut être validée que par un utilisateur d'un profil autorisé
- La modification directe des index de pistolets est interdite, seule la procédure de réinitialisation est autorisée

### 5.3 Règles de validation hiérarchique
- Les validations sont requises pour les opérations sensibles (réinitialisation d'index, ajustements de stock importants)
- Le niveau de validation requis est déterminé par le seuil montant ou le type d'opération
- Les utilisateurs doivent appartenir à un profil autorisé pour valider une opération spécifique
- Les validations peuvent être configurées par type d'opération via la table `validations_hierarchiques`

### 5.4 Impacts sur d'autres modules
- Les ajustements de stock affectent les mouvements de stock via la table `stocks_mouvements`
- Les ajustements de stock génèrent des écritures comptables dans le module de comptabilité
- Les réinitialisations d'index affectent les calculs de ventes de carburant (quantités vendues)
- Les réinitialisations d'index peuvent affecter les analyses de performance des pompistes

### 5.5 Workflows
#### Workflow d'ajustement de stock :
1. L'utilisateur crée un ajustement de stock avec les détails appropriés
2. Le système vérifie la validité des données (quantités, types, existence de l'article)
3. Si l'ajustement dépasse un seuil configuré, le système crée une demande de validation
4. Le système met à jour le stock théorique
5. Le système crée un mouvement de stock dans la table `stocks_mouvements`
6. Le système génère automatiquement une ou plusieurs écritures comptables

#### Workflow de réinitialisation d'index :
1. L'utilisateur crée une demande de réinitialisation d'index
2. Le système sauvegarde l'ancienne valeur de l'index
3. Le système crée une demande en attente de validation
4. Un utilisateur autorisé examine la demande et la valide/rejette
5. Si validée, le système met à jour l'index du pistolet
6. Le système enregistre le mouvement dans l'historique des index

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
compagnies ||--o{ stations : gère
compagnies ||--o{ utilisateurs : appartient
compagnies ||--o{ ajustements_stock : appartient
compagnies ||--o{ causes_peremption : appartient

stations ||--o{ ajustements_stock : localisé
stations ||--o{ cuve_stocks : localisé

articles ||--o{ ajustements_stock : affecte
articles ||--o{ stocks : gère

ajustements_stock ||--o{ ajustements_stock_causes : a des causes
ajustements_stock ||--o{ stocks_mouvements : crée

causes_peremption ||--o{ ajustements_stock_causes : cause
utilisateurs ||--o{ ajustements_stock : effectue
utilisateurs ||--o{ reinitialisation_index_pistolets : demande
utilisateurs ||--o{ reinitialisation_index_pistolets : autorise

pistolets ||--o{ reinitialisation_index_pistolets : concerne
pistolets ||--o{ historique_index_pistolets : a un historique

profils ||--o{ validations_hierarchiques : peut_valider
validations_hierarchiques ||--o{ reinitialisation_index_pistolets : requiert
```

### 6.2 Diagramme de séquence (textuel) - Réinitialisation d'index
```
Utilisateur -> API: POST /api/reinitialisations-index
API -> Validation: Vérification des droits
Validation -> API: Autorisation confirmée
API -> DB: Création demande réinitialisation (statut: En attente)
DB -> API: Demande créée
API -> Notifications: Avertir validateurs
Notifications -> API: Notification envoyée
API -> Utilisateur: Demande soumise avec succès

Validateurs -> API: GET /api/reinitialisations-index (statut: En attente)
API -> DB: Récupération demandes
DB -> API: Liste demandes
API -> Validateurs: Affichage demandes

Validateurs -> API: PUT /api/reinitialisations-index/{id}/valider
API -> DB: Mise à jour statut (Approuve/Rejete)
DB -> API: Statut mis à jour
API -> Pistolets: Mise à jour index si approuvé
Pistolets -> API: Index mis à jour
API -> Validateurs: Confirmation mise à jour
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test de validation des quantités d'ajustement de stock
- Test des contraintes de type d'ajustement (entrée/sortie)
- Test des seuils de validation hiérarchique
- Test de la génération d'écritures comptables
- Test des validations de réinitialisation d'index
- Test de la cohérence des dates et des index

### 7.2 Tests d'intégration
- Test complet du workflow d'ajustement de stock
- Test complet du workflow de réinitialisation d'index
- Test de la génération automatique des écritures comptables
- Test de la propagation des mouvements de stock
- Test des validations hiérarchiques
- Test de la journalisation des actions critiques

### 7.3 Tests de charge/performance
- Test de performance lors de la création massive d'ajustements
- Test de performance lors de l'affichage des analyses
- Test de performance lors de l'accès aux historiques
- Test de performance lors de la modification d'index de pistolets

### 7.4 Jeux de données de test
- Jeu de données d'articles pour test des ajustements de stock
- Jeu de données de pistolets pour test des réinitialisations
- Jeu de données d'utilisateurs avec différents profils
- Jeu de données d'opérations pour test des validations hiérarchiques
- Jeu de données de causes de péremption pour test des analyses

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Créer les modèles de données (ajustements_stock, reinitialisation_index_pistolets, validations_hierarchiques)
- [ ] Implémenter les endpoints API pour la gestion des ajustements
- [ ] Implémenter les endpoints API pour la gestion des réinitialisations
- [ ] Mettre en place la logique de validation hiérarchique
- [ ] Implémenter la génération automatique des écritures comptables
- [ ] Créer les interfaces utilisateur pour la gestion des ajustements
- [ ] Créer les interfaces utilisateur pour la gestion des réinitialisations
- [ ] Implémenter l'analyse des causes de péremption
- [ ] Mettre en place la journalisation des actions critiques
- [ ] Intégrer les validations de sécurité et d'accès
- [ ] Créer les vues d'analyse et de reporting

### 8.2 Ordre recommandé
1. Déploiement des modèles de base (ajustements_stock, reinitialisation_index_pistolets)
2. Développement des endpoints d'API pour les ajustements de stock
3. Développement des endpoints d'API pour les réinitialisations d'index
4. Mise en place des validations hiérarchiques
5. Intégration avec les modules existants (stocks, comptabilité)
6. Développement des interfaces utilisateur
7. Mise en place de la journalisation
8. Création des vues d'analyse
9. Tests unitaires et d'intégration
10. Documentation et déploiement

### 8.3 Livrables attendus
- [ ] Code source des nouvelles fonctionnalités
- [ ] Documentation technique des endpoints API
- [ ] Documentation utilisateur des nouvelles fonctionnalités
- [ ] Scripts de migration de base de données si nécessaire
- [ ] Jeux de tests unitaires et d'intégration
- [ ] Documentation des procédures d'exploitation

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La modification des index de pistolets peut affecter les calculs de ventes et les analyses de performance
- Les ajustements de stock importants peuvent impacter la rentabilité calculée
- Les validations hiérarchiques peuvent ralentir certaines opérations critiques
- La journalisation des actions critiques est essentielle pour la traçabilité

### 9.2 Risques techniques
- Risque de performances si les requêtes sur les ajustements de stock ne sont pas correctement indexées
- Risque de données incohérentes si les validations ne sont pas suffisamment strictes
- Risque de sécurité si les validations hiérarchiques ne sont pas correctement implémentées
- Risque de perte d'historique si la journalisation n'est pas fiable

### 9.3 Dette technique potentielle
- Gestion des index de pistolets : solution à améliorer avec des contrôles plus fins
- Validation hiérarchique : implémentation progressive des différents niveaux
- Analyse des causes : possibilité d'ajouter des algorithmes d'analyse prédictive
- Sécurité: renforcement de la validation des droits d'accès à chaque opération critique