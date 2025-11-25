# Technical Specification - Dépôt de garantie

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer les dépôts de garantie des clients dans le système SuccessFuel. L'objectif est de permettre aux gestionnaires de suivre les dépôts de garantie effectués par les clients, leurs utilisations éventuelles, et les remboursements associés. Le système doit également permettre de suivre les contrats de fidélité liés à ces dépôts.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas de fonctionnalités adéquates pour :
- Enregistrer les dépôts de garantie des clients
- Suivre l'utilisation des dépôts (paiement de dette/vente/écart)
- Gérer les remboursements de dépôts
- Afficher l'historique complet des transactions
- Afficher le solde visible client en temps réel
- Suivre les contrats de fidélité liés aux dépôts

### Définition du périmètre
Le périmètre inclut :
- Gestion des dépôts de garantie (enregistrement, utilisation, remboursement)
- Historique complet des transactions liées aux dépôts
- Affichage du solde visible client
- Suivi des contrats de fidélité
- Génération des écritures comptables liées aux dépôts
- Intégration avec les modules clients et trésorerie
- Génération de rapports liés aux dépôts de garantie

## 2. User Stories & Critères d'acceptation

### US-DG-001: En tant que gestionnaire, je veux enregistrer un dépôt de garantie d'un client
- **Critères d'acceptation :**
  - Pouvoir sélectionner le client concerné
  - Pouvoir spécifier le montant du dépôt
  - Pouvoir enregistrer le mode de paiement utilisé
  - Pouvoir enregistrer la référence du paiement
  - Le système doit créer une écriture comptable au passif
  - Le système doit enregistrer la date d'enregistrement
  - Le système doit permettre d'ajouter un commentaire optionnel
  - Le dépôt doit être affecté à la bonne compagnie

### US-DG-002: En tant que gestionnaire, je veux utiliser un dépôt de garantie pour payer une dette/vente/écart
- **Critères d'acceptation :**
  - Pouvoir sélectionner un dépôt de garantie actif d'un client
  - Pouvoir spécifier le type d'utilisation (Dette, Vente, Ecart)
  - Pouvoir saisir le montant à utiliser (jusqu'au montant total du dépôt)
  - Pouvoir référencer l'opération d'origine (facture, vente, écart)
  - Le système doit mettre à jour le solde restant du dépôt
  - Le système doit enregistrer l'utilisateur qui a effectué l'utilisation
  - Le système doit enregistrer la date d'utilisation
  - Le système doit créer une écriture comptable pour l'utilisation

### US-DG-003: En tant que gestionnaire, je veux rembourser un dépôt de garantie
- **Critères d'acceptation :**
  - Pouvoir sélectionner un dépôt de garantie éligible au remboursement
  - Pouvoir modifier le statut du dépôt à "Rembourse"
  - Le système doit empêcher l'utilisation du dépôt après remboursement
  - Le système doit permettre d'ajouter des détails sur le remboursement
  - Le système doit enregistrer l'utilisateur qui a effectué le remboursement

### US-DG-004: En tant que gestionnaire, je veux consulter l'historique complet des transactions
- **Critères d'acceptation :**
  - Pouvoir visualiser l'historique complet d'un dépôt de garantie
  - Pouvoir voir les utilisations effectuées sur un dépôt
  - Pouvoir filtrer par client, période ou type d'opération
  - Pouvoir exporter l'historique
  - Le système doit afficher les détails de chaque transaction

### US-DG-005: En tant que gestionnaire, je veux visualiser le solde visible client
- **Critères d'acceptation :**
  - Pouvoir consulter le solde actuel des dépôts de garantie pour un client
  - Pouvoir voir le montant total déposé
  - Pouvoir voir le montant restant disponible
  - Pouvoir voir le montant déjà utilisé
  - Le solde doit être mis à jour en temps réel

### US-DG-006: En tant que gestionnaire, je veux suivre les contrats de fidélité liés aux dépôts
- **Critères d'acceptation :**
  - Pouvoir associer un dépôt de garantie à un contrat de fidélité
  - Pouvoir visualiser les dépôts liés à un programme de fidélité
  - Pouvoir suivre l'évolution des dépôts dans le cadre des programmes de fidélité
  - Pouvoir identifier les clients fidèles basés sur leurs dépôts

### US-DG-007: En tant que comptable, je veux que les dépôts génèrent des écritures comptables
- **Critères d'acceptation :**
  - Chaque dépôt valide génère automatiquement des écritures comptables
  - Les écritures respectent le plan comptable local (OHADA)
  - Les dépôts de garantie sont enregistrés dans un compte passif approprié
  - Les utilisations de dépôts génèrent les écritures de contrepartie
  - Les écritures sont associées à des journaux spécifiques (passif)
  - Les écritures sont numérotées automatiquement

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: depot_garantie (EXISTANTE - à documenter)
```sql
CREATE TABLE depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    montant NUMERIC(18,2) NOT NULL,
    date_enregistrement DATE NOT NULL,
    mode_paiement VARCHAR(50),
    reference_paiement VARCHAR(100),
    utilisateur_enregistre_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Utilise', 'Rembourse', 'Transfere')) NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_depot_garantie_client ON depot_garantie(client_id);
CREATE INDEX idx_depot_garantie_compagnie ON depot_garantie(compagnie_id);
CREATE INDEX idx_depot_garantie_date ON depot_garantie(date_enregistrement);
CREATE INDEX idx_depot_garantie_statut ON depot_garantie(statut);
CREATE INDEX idx_depot_garantie_utilisateur ON depot_garantie(utilisateur_enregistre_id);
```

#### Table: utilisation_depot_garantie (EXISTANTE - à documenter)
```sql
CREATE TABLE utilisation_depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    depot_garantie_id UUID REFERENCES depot_garantie(id),
    type_utilisation VARCHAR(20) NOT NULL CHECK (type_utilisation IN ('Dette', 'Vente', 'Ecart', 'Autre')),
    montant_utilise NUMERIC(18,2) NOT NULL,
    reference_operation VARCHAR(100), -- Référence à la facture, vente, etc.
    utilisateur_utilise_id UUID REFERENCES utilisateurs(id),
    date_utilisation DATE NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_utilisation_depot_garantie_depot ON utilisation_depot_garantie(depot_garantie_id);
CREATE INDEX idx_utilisation_depot_garantie_compagnie ON utilisation_depot_garantie(compagnie_id);
CREATE INDEX idx_utilisation_depot_garantie_type ON utilisation_depot_garantie(type_utilisation);
CREATE INDEX idx_utilisation_depot_garantie_date ON utilisation_depot_garantie(date_utilisation);
CREATE INDEX idx_utilisation_depot_garantie_utilisateur ON utilisation_depot_garantie(utilisateur_utilise_id);
```

### 3.2 Relations
- `depot_garantie` → `clients` (many-to-one): chaque dépôt est lié à un client
- `depot_garantie` → `utilisateurs` (many-to-one): chaque dépôt est enregistré par un utilisateur
- `depot_garantie` → `compagnies` (many-to-one): chaque dépôt appartient à une compagnie
- `utilisation_depot_garantie` → `depot_garantie` (many-to-one): chaque utilisation est liée à un dépôt
- `utilisation_depot_garantie` → `utilisateurs` (many-to-one): chaque utilisation est faite par un utilisateur
- `utilisation_depot_garantie` → `compagnies` (many-to-one): chaque utilisation appartient à une compagnie

### 3.3 Triggers / Règles d'intégrité
- Trigger pour s'assurer que le montant utilisé ne dépasse pas le montant total du dépôt
- Contrainte pour s'assurer que la date d'utilisation est postérieure ou égale à la date d'enregistrement du dépôt
- Trigger pour mettre à jour automatiquement le statut d'un dépôt lorsqu'il est complètement utilisé ou remboursé
- Contrainte pour s'assurer que seuls les dépôts "Actif" peuvent être utilisés

### 3.4 Contraintes supplémentaires
- Le montant du dépôt doit être strictement positif
- Le statut d'un dépôt ne peut pas revenir à "Actif" une fois qu'il a été "Rembourse", "Utilise" ou "Transfere"
- Le montant utilisé dans une opération ne peut pas être supérieur au solde restant du dépôt
- Pour un dépôt donné, la somme des montants utilisés ne peut pas dépasser le montant total du dépôt

## 4. API Backend

### 4.1 Gestion des dépôts de garantie
- **POST** `/api/depots-garantie` - Créer un dépôt de garantie
  - Payload: `{client_id, montant, mode_paiement, reference_paiement, commentaire}`
  - Réponse: `{id, client_id, montant, montant_restant, date_enregistrement, mode_paiement, statut, commentaire, created_at}`
  - Codes d'erreur: `400` (erreur validation), `401` (non authentifié), `403` (accès refusé), `404` (client non trouvé), `500` (erreur serveur)

- **GET** `/api/depots-garantie` - Lister les dépôts de garantie
  - Paramètres: `?client_id&statut&date_debut&date_fin&compagnie_id&page&limit`
  - Réponse: `[{id, client_id, client_code, client_nom, montant, montant_restant, date_enregistrement, mode_paiement, statut, reference_paiement, commentaire}, ...]`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `500` (erreur serveur)

- **GET** `/api/depots-garantie/{id}` - Consulter un dépôt spécifique
  - Réponse: `{id, client_id, client_code, client_nom, montant, montant_restant, date_enregistrement, mode_paiement, reference_paiement, utilisateur_enregistre_id, utilisateur_enregistre_nom, statut, commentaire, historique_utilisations: [...]}`  
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `404` (dépôt non trouvé), `500` (erreur serveur)

- **PUT** `/api/depots-garantie/{id}/rembourser` - Rembourser un dépôt de garantie
  - Payload: `{commentaire: "optionnel"}`
  - Réponse: `{id, statut, commentaire, updated_at}`
  - Codes d'erreur: `400` (erreur validation), `401` (non authentifié), `403` (accès refusé), `404` (dépôt non trouvé), `409` (dépôt non éligible au remboursement), `500` (erreur serveur)

### 4.2 Gestion des utilisations de dépôts
- **POST** `/api/utilisations-depot` - Créer une utilisation de dépôt
  - Payload: `{depot_garantie_id, type_utilisation, montant_utilise, reference_operation, commentaire}`
  - Réponse: `{id, depot_garantie_id, type_utilisation, montant_utilise, montant_restant_depot, reference_operation, utilisateur_utilise_id, date_utilisation, commentaire}`
  - Codes d'erreur: `400` (erreur validation), `401` (non authentifié), `403` (accès refusé), `404` (dépôt non trouvé), `409` (montant insuffisant), `500` (erreur serveur)

- **GET** `/api/utilisations-depot` - Lister les utilisations de dépôts
  - Paramètres: `?depot_garantie_id&type_utilisation&date_debut&date_fin&compagnie_id&page&limit`
  - Réponse: `[{id, depot_garantie_id, depot_client_id, depot_client_code, type_utilisation, montant_utilise, reference_operation, utilisateur_utilise_id, utilisateur_utilise_nom, date_utilisation, commentaire}, ...]`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `500` (erreur serveur)

### 4.3 Consultation des soldes
- **GET** `/api/depots-garantie/solde-client/{client_id}` - Obtenir le solde des dépôts d'un client
  - Réponse: `{client_id, client_code, client_nom, montant_total_deposes, montant_total_utilises, montant_restant_global}`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `404` (client non trouvé), `500` (erreur serveur)

- **GET** `/api/depots-garantie/historique/{depot_id}` - Obtenir l'historique d'un dépôt
  - Réponse: `{depot_id, depot_montant_initial, historique: [{type, montant, date, reference, utilisateur}, ...], solde_actuel}`
  - Codes d'erreur: `401` (non authentifié), `403` (accès refusé), `404` (dépôt non trouvé), `500` (erreur serveur)

## 5. Logique Métier

### 5.1 Règles de validation des dépôts de garantie
- Le montant du dépôt doit être strictement positif
- Le client doit être en statut "Actif"
- La date d'enregistrement ne peut pas être dans le futur
- Le mode de paiement doit être valide par rapport aux modes de paiement configurés dans le système
- Les dépôts ne peuvent être enregistrés que dans la compagnie de l'utilisateur connecté

### 5.2 Règles de validation des utilisations
- Le dépôt de garantie doit avoir un statut "Actif"
- Le montant à utiliser ne doit pas dépasser le solde restant du dépôt
- Le type d'utilisation doit être parmi les valeurs prédéfinies (Dette, Vente, Ecart, Autre)
- La date d'utilisation ne peut pas être antérieure à la date d'enregistrement du dépôt
- Une fois un dépôt complètement utilisé, son statut passe automatiquement à "Utilise"

### 5.3 Règles de remboursement
- Seuls les dépôts avec le statut "Actif" et non partiellement utilisés peuvent être remboursés
- Le remboursement d'un dépôt partiellement utilisé est possible mais nécessite une justification
- Après remboursement, le dépôt n'est plus utilisable
- Le remboursement doit être enregistré dans les mouvements de trésorerie appropriés

### 5.4 Impacts sur d'autres modules
- Les dépôts de garantie affectent les soldes de trésorerie
- Les dépôts de garantie génèrent des écritures comptables dans le module de comptabilité
- Les dépôts de garantie sont visibles dans les fiches clients
- Les dépôts peuvent être utilisés pour compenser des dettes clients
- Les dépôts peuvent être liés aux programmes de fidélité

### 5.5 Workflows
#### Workflow d'enregistrement d'un dépôt :
1. L'utilisateur sélectionne un client actif
2. L'utilisateur saisit le montant du dépôt et les détails du paiement
3. Le système crée un enregistrement dans la table depot_garantie
4. Le système génère automatiquement une écriture comptable (au passif)
5. Le système enregistre l'utilisateur et la date d'enregistrement
6. Le système met à jour le solde du client

#### Workflow d'utilisation d'un dépôt :
1. L'utilisateur sélectionne un dépôt de garantie actif appartenant au client
2. L'utilisateur spécifie le montant à utiliser (≤ au solde restant)
3. L'utilisateur sélectionne le type d'utilisation (Dette/Vente/Ecart)
4. L'utilisateur fournit la référence de l'opération d'origine si applicable
5. Le système met à jour le solde restant du dépôt
6. Le système crée un enregistrement dans la table utilisation_depot_garantie
7. Le système met à jour le statut du dépôt si complètement utilisé
8. Le système génère les écritures comptables appropriées

#### Workflow de remboursement :
1. L'utilisateur sélectionne un dépôt éligible au remboursement
2. Le système vérifie que le dépôt est éligible (statut Actif, non partiellement utilisé ou avec justification)
3. Le système change le statut du dépôt à "Rembourse"
4. Le système enregistre le remboursement dans les mouvements de trésorerie
5. Le système met à jour le solde du client
6. Le système empêche toute utilisation future du dépôt

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
compagnies ||--o{ depot_garantie : appartient
compagnies ||--o{ utilisation_depot_garantie : appartient
clients ||--o{ depot_garantie : possède
utilisateurs ||--o{ depot_garantie : enregistre
utilisateurs ||--o{ utilisation_depot_garantie : utilise
depot_garantie ||--o{ utilisation_depot_garantie : a des utilisations
```

### 6.2 Diagramme de séquence (textuel) - Utilisation d'un dépôt de garantie
```
Utilisateur -> API: POST /api/utilisations-depot
API -> Validation: Vérifier dépôt actif
Validation -> API: Dépôt valide
API -> Validation: Vérifier montant <= solde restant
Validation -> API: Montant valide
API -> DB: Créer utilisation_depot_garantie
DB -> API: Utilisation créée
API -> DB: Mettre à jour montant_restant dans depot_garantie
DB -> API: Montant mis à jour
API -> Journalisation: Créer écriture comptable
Journalisation -> API: Écriture comptable créée
API -> Notifications: Avertir parties prenantes
Notifications -> API: Notification envoyée
API -> Utilisateur: Confirmation d'utilisation
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test de validation des montants de dépôt (positif)
- Test de validation des types d'utilisation
- Test de la logique de calcul du solde restant
- Test des contraintes de statut de dépôt
- Test de la génération d'écritures comptables
- Test de la validation de remboursement

### 7.2 Tests d'intégration
- Test complet du workflow d'enregistrement d'un dépôt
- Test complet du workflow d'utilisation d'un dépôt
- Test complet du workflow de remboursement
- Test de la génération automatique des écritures comptables
- Test de la propagation des mouvements de trésorerie
- Test de la mise à jour des soldes clients
- Test de la journalisation des actions critiques

### 7.3 Tests de charge/performance
- Test de performance lors de la création massive de dépôts
- Test de performance lors de l'affichage des historiques
- Test de performance lors de l'accès aux soldes clients
- Test de performance lors de la recherche de dépôts

### 7.4 Jeux de données de test
- Jeu de données clients pour test des dépôts
- Jeu de données de dépôts de garantie avec différents statuts
- Jeu de données d'utilisateurs avec différents profils
- Jeu de données d'opérations pour test des utilisations
- Jeu de données de programmes de fidélité pour test des associations

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Créer les modèles de données (depot_garantie, utilisation_depot_garantie)
- [ ] Implémenter les endpoints API pour la gestion des dépôts
- [ ] Implémenter les endpoints API pour les utilisations
- [ ] Mettre en place la logique de calcul des soldes
- [ ] Implémenter la génération automatique des écritures comptables
- [ ] Créer les interfaces utilisateur pour la gestion des dépôts
- [ ] Créer les interfaces pour la consultation des soldes
- [ ] Implémenter l'intégration avec les modules clients
- [ ] Mettre en place la journalisation des actions critiques
- [ ] Intégrer les validations de sécurité et d'accès
- [ ] Créer les vues d'analyse et de reporting
- [ ] Créer des vues pour le suivi des contrats de fidélité

### 8.2 Ordre recommandé
1. Déploiement des modèles de base (depot_garantie, utilisation_depot_garantie) si nécessaire
2. Développement des endpoints d'API pour les dépôts de garantie
3. Développement des endpoints d'API pour les utilisations
4. Mise en place des validations métier
5. Intégration avec les modules existants (clients, comptabilité, trésorerie)
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
- La gestion des soldes de dépôt doit être cohérente pour éviter les erreurs
- Les remboursements doivent être soigneusement contrôlés pour éviter les abus
- La génération des écritures comptables doit être rigoureuse pour la conformité
- La traçabilité des opérations est essentielle pour la sécurité financière
- Les accès aux fonctionnalités doivent être strictement contrôlés

### 9.2 Risques techniques
- Risque de performances si les requêtes sur les dépôts et leurs utilisations ne sont pas correctement indexées
- Risque de données incohérentes si les validations ne sont pas suffisamment strictes
- Risque de sécurité si les contrôles d'accès ne sont pas correctement implémentés
- Risque de perte d'historique si la journalisation n'est pas fiable

### 9.3 Dette technique potentielle
- Gestion des dépôts partiellement utilisés: solution à améliorer avec des contrôles plus fins
- Suivi des contrats de fidélité: possibilité d'ajouter des algorithmes d'analyse prédictive
- Sécurité: renforcement de la validation des droits d'accès à chaque opération critique
- Calcul des soldes: optimisation potentielle avec mise en cache si performance devient un problème