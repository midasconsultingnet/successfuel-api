# Documentation de l'API Comptable - SuccessFuel

## Introduction

Cette documentation décrit les endpoints de l'API comptable du système SuccessFuel. Le module comptable permet la gestion du plan comptable, des écritures comptables, du bilan initial, et des rapports financiers conformément aux systèmes locaux (OHADA) et aux besoins de gestion opérationnelle des stations-service.

## Authentification

Tous les endpoints nécessitent une authentification JWT valide. Le token doit être inclus dans l'en-tête Authorization: `Bearer {token}`.

## Contrôle d'accès

Le système implémente un contrôle d'accès basé sur les rôles (RBAC) avec des permissions spécifiques :
- **Gérant de compagnie** : Accès complet à toutes les fonctionnalités comptables pour sa propre compagnie
- **Super Administrateur** : Accès complet aux opérations comptables dans tout le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Utilisateur de compagnie** : Accès limité selon ses permissions spécifiques

Toutes les requêtes sont filtrées selon la compagnie de l'utilisateur connecté.

---

## Plan Comptable

### Créer un compte comptable
`POST /api/v1/plan-comptable/`

**Permissions requises :** `gerer_plan_comptable`

**Body:**
```json
{
  "numero": "string (20)",
  "intitule": "string (255)",
  "classe": "string (5)",
  "type_compte": "string (100)",
  "sens_solde": "D|C",
  "description": "string",
  "compagnie_id": "UUID"
}
```

**Réponse:**
```json
{
  "id": "UUID",
  "numero": "string",
  "intitule": "string",
  "classe": "string",
  "type_compte": "string",
  "sens_solde": "string",
  "description": "string",
  "statut": "Actif|Inactif|Supprime",
  "est_compte_racine": "bool",
  "est_compte_de_resultat": "bool",
  "est_compte_actif": "bool",
  "pays_id": "UUID",
  "est_specifique_pays": "bool",
  "code_pays": "string",
  "compagnie_id": "UUID",
  "compte_parent_id": "UUID",
  "created_at": "string",
  "updated_at": "string"
}
```

### Obtenir un compte comptable
`GET /api/v1/plan-comptable/{plan_id}`

**Permissions requises :** `consulter_plan_comptable`

### Mettre à jour un compte comptable
`PUT /api/v1/plan-comptable/{plan_id}`

**Permissions requises :** `gerer_plan_comptable`

**Body:**
```json
{
  "intitule": "string",
  "description": "string",
  "statut": "string",
  "compte_parent_id": "UUID"
}
```

### Supprimer un compte comptable
`DELETE /api/v1/plan-comptable/{plan_id}`

**Permissions requises :** `gerer_plan_comptable`

### Lister les comptes comptables
`GET /api/v1/plan-comptable/`

**Permissions requises :** `consulter_plan_comptable`

**Paramètres de requête :**
- `compagnie_id`: Filtre par compagnie
- `statut`: Filtre par statut (Actif, Inactif, Supprime)
- `classe`: Filtre par classe comptable
- `type_compte`: Filtre par type de compte

### Créer un journal
`POST /api/v1/plan-comptable/journaux/`

**Permissions requises :** `gerer_journaux`

**Body:**
```json
{
  "code": "string (20)",
  "libelle": "string (100)",
  "description": "string",
  "type_journal": "achats|ventes|tresorerie|banque|caisse|opex|stock|autre",
  "pays_id": "UUID",
  "compagnie_id": "UUID"
}
```

---

## Écritures Comptables

### Créer une écriture comptable
`POST /api/v1/ecritures/ecritures-comptables/`

**Permissions requises :** `gerer_ecritures_comptables`

**Body:**
```json
{
  "journal_id": "UUID",
  "date_ecriture": "YYYY-MM-DD",
  "libelle": "string",
  "tiers_id": "UUID",
  "operation_id": "UUID",
  "operation_type": "string",
  "reference_externe": "string",
  "compagnie_id": "UUID",
  "lignes": [
    {
      "compte_id": "UUID",
      "montant_debit": "float",
      "montant_credit": "float",
      "libelle": "string",
      "tiers_id": "UUID",
      "projet_id": "UUID"
    }
  ]
}
```

**Contraintes :**
- L'écriture doit être équilibrée (débit = crédit)
- Chaque ligne ne peut avoir que du débit ou du crédit, pas les deux

### Obtenir une écriture comptable
`GET /api/v1/ecritures/ecritures-comptables/{ecriture_id}`

**Permissions requises :** `consulter_ecritures_comptables`

### Mettre à jour une écriture comptable
`PUT /api/v1/ecritures/ecritures-comptables/{ecriture_id}`

**Permissions requises :** `gerer_ecritures_comptables`

**Body:**
```json
{
  "libelle": "string",
  "tiers_id": "UUID",
  "operation_id": "UUID",
  "operation_type": "string",
  "est_validee": "bool",
  "reference_externe": "string"
}
```

### Supprimer une écriture comptable
`DELETE /api/v1/ecritures/ecritures-comptables/{ecriture_id}`

**Permissions requises :** `gerer_ecritures_comptables`

*Remarque : Seules les écritures non validées peuvent être supprimées*

### Lister les écritures comptables
`GET /api/v1/ecritures/ecritures-comptables/`

**Permissions requises :** `consulter_ecritures_comptables`

**Paramètres de requête :**
- `compagnie_id`: Filtre par compagnie
- `journal_id`: Filtre par journal
- `date_debut`: Filtre par date de début
- `date_fin`: Filtre par date de fin
- `est_validee`: Filtre par statut de validation
- `tiers_id`: Filtre par tiers
- `operation_type`: Filtre par type d'opération

---

## Bilan Initial

### Créer un bilan initial
`POST /api/v1/bilan-initial/bilan-initial/`

**Permissions requises :** `gerer_bilan_initial`

**Body:**
```json
{
  "compagnie_id": "UUID",
  "date_bilan_initial": "YYYY-MM-DD",
  "commentaire": "string",
  "utilisateur_id": "UUID",
  "description": "string",
  "lignes": [
    {
      "compte_numero": "string (20)",
      "compte_id": "UUID",
      "montant_initial": "float",
      "type_solde": "debit|credit",
      "poste_bilan": "actif|passif|capitaux_propres",
      "categorie_detaillee": "string (50)",
      "commentaire": "string"
    }
  ],
  "immobilisations": [
    {
      "code": "string (50)",
      "libelle": "string",
      "categorie": "string (100)",
      "date_achat": "YYYY-MM-DD",
      "valeur_acquisition": "float",
      "valeur_nette_comptable": "float",
      "amortissement_cumule": "float",
      "duree_amortissement": "integer",
      "date_fin_amortissement": "YYYY-MM-DD",
      "fournisseur_id": "UUID",
      "utilisateur_achat_id": "UUID",
      "observation": "string",
      "statut": "Actif|Cede|Hors service|Vendu"
    }
  ],
  "stocks": [
    {
      "type_stock": "carburant|produit_boutique",
      "article_id": "UUID",
      "carburant_id": "UUID",
      "cuve_id": "UUID",
      "quantite": "float",
      "prix_unitaire": "float",
      "commentaire": "string"
    }
  ],
  "creances_dettes": [
    {
      "type_tiers": "client|fournisseur",
      "tiers_id": "UUID",
      "montant_initial": "float",
      "devise": "string",
      "date_echeance": "YYYY-MM-DD",
      "reference_piece": "string (100)",
      "commentaire": "string"
    }
  ]
}
```

**Contraintes :**
- Le bilan doit être équilibré (actif = passif + capitaux propres)

### Obtenir un bilan initial
`GET /api/v1/bilan-initial/bilan-initial/{bilan_id}`

**Permissions requises :** `consulter_bilan_initial`

### Mettre à jour un bilan initial
`PUT /api/v1/bilan-initial/bilan-initial/{bilan_id}`

**Permissions requises :** `gerer_bilan_initial`

**Body:**
```json
{
  "commentaire": "string",
  "est_valide": "bool",
  "est_verifie": "bool"
}
```

### Supprimer un bilan initial
`DELETE /api/v1/bilan-initial/bilan-initial/{bilan_id}`

**Permissions requises :** `gerer_bilan_initial`

*Remarque : Seuls les bilans non validés peuvent être supprimés*

### Lister les bilans initiaux
`GET /api/v1/bilan-initial/bilan-initial/`

**Permissions requises :** `consulter_bilan_initial`

**Paramètres de requête :**
- `compagnie_id`: Filtre par compagnie
- `date_bilan`: Filtre par date
- `est_valide`: Filtre par statut de validation
- `est_verifie`: Filtre par statut de vérification

---

## Rapports

### Créer un rapport financier
`POST /api/v1/rapports/rapports/financiers/`

**Permissions requises :** `generer_rapports`

**Body:**
```json
{
  "type_rapport": "bilan|compte_resultat|grand_livre|balance|journal|tva|etat_tva",
  "periode_debut": "YYYY-MM-DD",
  "periode_fin": "YYYY-MM-DD",
  "format_sortie": "PDF|Excel|CSV",
  "utilisateur_generateur_id": "UUID",
  "compagnie_id": "UUID",
  "station_id": "UUID",
  "commentaire": "string"
}
```

### Obtenir un rapport financier
`GET /api/v1/rapports/rapports/financiers/{rapport_id}`

**Permissions requises :** `consulter_rapports`

### Mettre à jour un rapport financier
`PUT /api/v1/rapports/rapports/financiers/{rapport_id}`

**Permissions requises :** `gerer_rapports`

### Supprimer un rapport financier
`DELETE /api/v1/rapports/rapports/financiers/{rapport_id}`

**Permissions requises :** `gerer_rapports`

### Lister les rapports financiers
`GET /api/v1/rapports/rapports/financiers/`

**Permissions requises :** `consulter_rapports`

**Paramètres de requête :**
- `compagnie_id`: Filtre par compagnie
- `type_rapport`: Filtre par type de rapport
- `periode_debut`: Filtre par date de début
- `periode_fin`: Filtre par date de fin
- `statut`: Filtre par statut

### Lister l'historique des rapports
`GET /api/v1/rapports/rapports/historique/`

**Permissions requises :** `consulter_historique_rapports`

**Paramètres de requête :**
- `compagnie_id`: Filtre par compagnie
- `type_rapport`: Filtre par type de rapport
- `nom_rapport`: Filtre par nom de rapport
- `periode_debut`: Filtre par date de début
- `periode_fin`: Filtre par date de fin
- `statut`: Filtre par statut
- `est_a_jour`: Filtre par statut de mise à jour

---

## Validation et Calcul des Soldes

### Vérifier l'équilibre d'une écriture
`POST /api/v1/validation/validation/verifier-ecriture-equilibree/`

**Permissions requises :** `valider_ecritures_comptables`

### Calculer le solde d'un compte
`GET /api/v1/soldes/soldes/compte/{compte_id}`

**Permissions requises :** `consulter_soldes`

**Paramètres de requête :**
- `date_solde`: Date pour le calcul du solde (facultatif, par défaut aujourd'hui)

---

## Erreurs

Toutes les erreurs renvoient un objet JSON avec le format suivant :
```json
{
  "status": "error",
  "message": "Description de l'erreur"
}
```

Codes d'erreur HTTP courants :
- 400: Requête incorrecte (validation échouée)
- 401: Non authentifié
- 403: Accès refusé
- 404: Ressource non trouvée
- 422: Entité non traitable
- 500: Erreur interne du serveur

## Considérations de Sécurité

1. Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
2. Les gérants de compagnie n'accèdent qu'aux données de leur propre compagnie
3. Les super administrateurs ont un accès global à toutes les données
4. Les permissions sont vérifiées à chaque requête
5. Les données sensibles sont protégées par des contrôles d'accès appropriés