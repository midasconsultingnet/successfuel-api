# Modèle de données - Module Ventes Carburant

## Entités principales

### Vente_Carburant
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - carburant_id (UUID, référence à Carburant)
  - cuve_id (UUID, référence à Cuve)
  - pistolet_id (UUID, référence à Pistolet)
  - quantite_vendue (decimal, obligatoire)
  - prix_unitaire (decimal, obligatoire)
  - montant_total (decimal, calculé)
  - date_vente (datetime, obligatoire)
  - index_initial (decimal, obligatoire)
  - index_final (decimal, obligatoire)
  - pompiste (string, nom du pompiste, obligatoire)
  - qualite_marshalle_id (UUID, référence à Utilisateur, optionnel)
  - montant_paye (decimal)
  - mode_paiement (string: "espèce", "chèque", "carte crédit", "note de crédit", "crédit client", etc.)
  - statut (string: "enregistrée", "validée", "annulée", default "enregistrée")
  - utilisateur_id (UUID, référence à Utilisateur)
  - numero_piece_comptable (string)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Carburant
  - N..1 avec Cuve
  - N..1 avec Pistolet
  - N..1 avec Utilisateur (qualite_marshalle_id)
  - N..1 avec Utilisateur (utilisateur_id)
  - 1..* avec Mouvement_Stock_Cuve
  - 1..* avec Mouvement_Tresorerie (pour les paiements)
  - 1..* avec Creance_Employe (si montant payé < montant dû)

### Mouvement_Stock_Cuve
- **Champs**:
  - id (UUID)
  - livraison_carburant_id (UUID, référence à Livraison_Carburant, optionnel)
  - vente_carburant_id (UUID, référence à Vente_Carburant, optionnel)
  - inventaire_carburant_id (UUID, référence à Inventaire_Carburant, optionnel)
  - cuve_id (UUID, référence à Cuve)
  - type_mouvement (string: "entrée", "sortie", "ajustement", obligatoire)
  - quantite (decimal, obligatoire)
  - date_mouvement (datetime, obligatoire)
  - stock_avant (decimal)
  - stock_apres (decimal)
  - utilisateur_id (UUID, référence à Utilisateur)
  - reference_origine (string, obligatoire)
  - module_origine (string, obligatoire)
  - statut (string: "validé", "annulé", default "validé")

- **Contraintes**:
  - Une seule référence possible : (livraison_carburant_id NOT NULL AND vente_carburant_id IS NULL AND inventaire_carburant_id IS NULL)
    OR (livraison_carburant_id IS NULL AND vente_carburant_id NOT NULL AND inventaire_carburant_id IS NULL)
    OR (livraison_carburant_id IS NULL AND vente_carburant_id IS NULL AND inventaire_carburant_id NOT NULL)

- **Relations**:
  - N..1 avec Livraison_Carburant (optionnel)
  - N..1 avec Vente_Carburant (optionnel)
  - N..1 avec Inventaire_Carburant (optionnel)
  - N..1 avec Cuve
  - N..1 avec Utilisateur

### Creance_Employe
- **Champs**:
  - id (UUID)
  - vente_carburant_id (UUID, référence à Vente_Carburant)
  - pompiste (string, nom du pompiste, obligatoire)
  - montant_du (decimal, obligatoire)
  - montant_paye (decimal, obligatoire)
  - solde_creance (decimal, calculé)
  - date_creation (datetime, obligatoire)
  - date_echeance (date)
  - statut (string: "en_cours", "payé", "partiellement_payé", default "en_cours")
  - utilisateur_gestion_id (UUID, référence à Utilisateur)

- **Relations**:
  - N..1 avec Vente_Carburant
  - N..1 avec Utilisateur (utilisateur_gestion_id)

### Historique_Vente
- **Champs**:
  - id (UUID)
  - vente_carburant_id (UUID, référence à Vente_Carburant)
  - utilisateur_id (UUID, référence à Utilisateur)
  - type_historique (string: "création", "modification", "validation", "annulation", obligatoire)
  - donnees_avant (jsonb)
  - donnees_apres (jsonb)
  - date_historique (datetime, obligatoire)
  - motif_annulation (text, optionnel)

- **Relations**:
  - N..1 avec Vente_Carburant
  - N..1 avec Utilisateur

## Relations avec d'autres modules
- **Module Structure de la Compagnie**: Les ventes affectent les cuves et pistolets
- **Module Produits et Stocks**: Les ventes concernent des produits de type carburant
- **Module Tiers**: Les pompistes sont des tiers de type employé
- **Module Mouvements Financiers**: Les créances employés sont gérées via ce module
- **Module Trésoreries**: Les paiements affectent les trésoreries
- **Module Utilisateurs**: Les utilisateurs effectuent les ventes et sont QM
- **Module États, Bilans et Comptabilité**: Pour les rapports de ventes
- **Module Salaires**: Les créances employés sont liées aux salaires
- **Module Livraisons Carburant**: Les ajustements de stock sont liés aux mouvements de stock de ventes et livraisons

## Contraintes d'intégrité
- Une vente est liée à une seule cuve et un seul pistolet
- La quantité vendue est calculée à partir de la différence entre index final et initial
- Si le montant payé par le pompiste est inférieur au montant dû, une créance employé est créée
- Le stock après vente ne peut pas être négatif
- L'historique des modifications est conservé pour chaque vente
- Un mouvement de stock de type "sortie" est créé automatiquement lors de la validation de la vente

## Vues de reporting

### vue_ventes_carburant
- **Description**: Vue consolidée des ventes de carburant avec détails des stations, carburants, cuves et utilisateurs
- **Jointures**:
  - vente_carburant JOIN station ON (vente_carburant.station_id = station.id)
  - vente_carburant JOIN carburant ON (vente_carburant.carburant_id = carburant.id)
  - vente_carburant JOIN cuve ON (vente_carburant.cuve_id = cuve.id)
  - vente_carburant JOIN utilisateur ON (vente_carburant.utilisateur_id = utilisateur.id)
- **Champs**:
  - vc.id
  - vc.station_id
  - s.nom AS station_nom
  - vc.carburant_id
  - c.nom AS carburant_libelle
  - vc.cuve_id
  - cu.nom AS cuve_nom
  - vc.pistolet_id
  - pt.nom AS pistolet_nom
  - vc.quantite_vendue
  - vc.prix_unitaire
  - vc.montant_total
  - vc.date_vente
  - vc.index_initial
  - vc.index_final
  - vc.pompiste
  - vc.utilisateur_id
  - u.nom AS utilisateur_nom
  - u.prenom AS utilisateur_prenom
  - vc.mode_paiement
  - vc.statut