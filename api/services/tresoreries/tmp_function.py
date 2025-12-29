def annuler_transfert_tresorerie(db: Session, current_user, transfert_id: uuid.UUID):
    """Annule un transfert de trésorerie en créant des mouvements inverses"""
    from sqlalchemy import text
    from ..tresorerie.mouvement_manager import MouvementTresorerieManager

    # Récupérer le transfert à annuler
    transfert = db.query(TransfertTresorerieModel).join(
        TresorerieModel,
        TransfertTresorerieModel.tresorerie_source_id == TresorerieModel.id
    ).filter(
        TransfertTresorerieModel.id == transfert_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not transfert:
        raise HTTPException(status_code=404, detail="Transfert trésorerie not found")

    # Vérifier si le transfert est déjà annulé
    if transfert.statut == "annulé":
        raise HTTPException(status_code=400, detail="Le transfert est déjà annulé")

    # Récupérer les détails du transfert pour créer les mouvements inverses
    transfert_source = transfert.tresorerie_source_id
    transfert_destination = transfert.tresorerie_destination_id
    montant = transfert.montant

    # Vérifier si les trésoreries sont des trésoreries station ou globales
    tresorerie_source_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == transfert_source,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    tresorerie_destination_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == transfert_destination,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    # Déterminer les paramètres pour les mouvements inverses en fonction du type de trésorerie
    if tresorerie_source_station:
        source_params = {"tresorerie_station_id": transfert_source}
    else:
        # Vérifier si c'est une trésorerie globale
        tresorerie_source_globale = db.query(TresorerieModel).filter(
            TresorerieModel.id == transfert_source,
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).first()
        if tresorerie_source_globale:
            source_params = {"tresorerie_globale_id": transfert_source}
        else:
            raise HTTPException(status_code=404, detail="Trésorerie source non trouvée")

    if tresorerie_destination_station:
        destination_params = {"tresorerie_station_id": transfert_destination}
    else:
        # Vérifier si c'est une trésorerie globale
        tresorerie_destination_globale = db.query(TresorerieModel).filter(
            TresorerieModel.id == transfert_destination,
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).first()
        if tresorerie_destination_globale:
            destination_params = {"tresorerie_globale_id": transfert_destination}
        else:
            raise HTTPException(status_code=404, detail="Trésorerie destination non trouvée")

    # Créer les mouvements inverses pour annuler le transfert
    # 1. Mouvement de sortie de la destination (annulation de l'entrée)
    mouvement_sortie_destination = MouvementTresorerieManager.creer_mouvement_general(
        db,
        type_mouvement="sortie",
        montant=montant,
        utilisateur_id=current_user.id,
        description=f"Annulation du transfert - sortie de la trésorerie destination (TRANSFERT-{transfert_id})",
        module_origine="tresorerie",
        reference_origine=f"ANNUL-TRANSFERT-{transfert_id}-SORTIE",
        statut="validé",
        **destination_params
    )

    # 2. Mouvement d'entrée dans la source (annulation de la sortie)
    mouvement_entree_source = MouvementTresorerieManager.creer_mouvement_general(
        db,
        type_mouvement="entrée",
        montant=montant,
        utilisateur_id=current_user.id,
        description=f"Annulation du transfert - entrée dans la trésorerie source (TRANSFERT-{transfert_id})",
        module_origine="tresorerie",
        reference_origine=f"ANNUL-TRANSFERT-{transfert_id}-ENTREE",
        statut="validé",
        **source_params
    )

    # Mettre à jour le statut du transfert original à "annulé"
    transfert.statut = "annulé"
    db.commit()
    db.refresh(transfert)

    return {
        "message": "Transfert trésorerie annulé avec succès",
        "transfert_id": transfert.id,
        "mouvement_sortie_destination_id": mouvement_sortie_destination.id if mouvement_sortie_destination else None,
        "mouvement_entree_source_id": mouvement_entree_source.id if mouvement_entree_source else None
    }