from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from datetime import datetime, timezone
from uuid import UUID
from ...models import Vente as VenteModel, VenteDetail as VenteDetailModel, Station
from ...models import VenteCarburant as VenteCarburantModel, CreanceEmploye as CreanceEmployeModel, PrixCarburant
from ...models.tresorerie import TresorerieStation as TresorerieStationModel, MouvementTresorerie as MouvementTresorerieModel
from ...models.compagnie import MouvementStockCuve
from ...models.mouvement_financier import Avoir as AvoirModel
from ...ventes import schemas
from ...utils.pagination import PaginatedResponse


def get_ventes(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les ventes appartenant aux stations de l'utilisateur"""
    # Calculer le total pour les métadonnées de pagination
    total_query = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    )
    total = total_query.count()

    # Récupérer les ventes avec pagination
    ventes = total_query.offset(skip).limit(limit).all()

    # Déterminer s'il y a plus d'éléments
    has_more = (skip + limit) < total

    # Retourner une réponse paginée structurée
    return PaginatedResponse(
        items=ventes,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )


def create_vente(db: Session, current_user, vente: schemas.VenteCreate):
    """Crée une nouvelle vente avec ses détails"""
    with db.begin():  # Using SQLAlchemy's built-in transaction management
        # Vérifier que la trésorerie station appartient à l'utilisateur
        trésorerie_station = db.query(TresorerieStationModel).join(
            Station,
            TresorerieStationModel.station_id == Station.id
        ).filter(
            TresorerieStationModel.id == vente.trésorerie_station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not trésorerie_station:
            raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

        # Calculate total amount from details
        total_amount = sum(detail.montant for detail in vente.details)

        # Create the main vente record
        db_vente = VenteModel(
            client_id=vente.client_id,
            date=vente.date,
            montant_total=total_amount,
            statut=vente.statut,
            type_vente=vente.type_vente,
            trésorerie_station_id=vente.trésorerie_station_id,
            numero_piece_comptable=vente.numero_piece_comptable,
            compagnie_id=current_user.compagnie_id
        )

        db.add(db_vente)
        db.flush()  # To get the ID before committing

        # Create the details
        for detail in vente.details:
            db_detail = VenteDetailModel(
                vente_id=db_vente.id,  # Utilisation directe de l'ID objet SQLAlchemy
                produit_id=detail.produit_id,
                quantite=detail.quantite,
                prix_unitaire=detail.prix_unitaire,
                montant=detail.montant,
                remise=detail.remise
            )
            db.add(db_detail)

        # Créer un mouvement de trésorerie pour enregistrer l'entrée d'argent
        mouvement_entree = MouvementTresorerieModel(
            trésorerie_station_id=vente.trésorerie_station_id,
            type_mouvement="entrée",
            montant=total_amount,
            date_mouvement=datetime.now(timezone.utc),
            description=f"Vente enregistrée (ID: {db_vente.id})",
            module_origine="ventes",
            reference_origine=f"VTE-{db_vente.id}",
            utilisateur_id=current_user.id
        )
        db.add(mouvement_entree)

        # Mettre à jour le solde de la trésorerie
        from ...services.tresoreries import mettre_a_jour_solde_tresorerie
        mettre_a_jour_solde_tresorerie(db, vente.trésorerie_station_id)

        db.commit()
        db.refresh(db_vente)

        return db_vente


def get_vente_by_id(db: Session, current_user, vente_id: UUID):
    """Récupère une vente spécifique par son ID"""
    vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")
    return vente


def update_vente(db: Session, current_user, vente_id: UUID, vente: schemas.VenteUpdate):
    """Met à jour une vente existante"""
    db_vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    update_data = vente.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vente, field, value)

    db.commit()
    db.refresh(db_vente)
    return db_vente


def delete_vente(db: Session, current_user, vente_id: UUID):
    """Supprime une vente existante"""
    vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    # Delete related details first
    db.query(VenteDetailModel).filter(VenteDetailModel.vente_id == vente_id).delete()

    db.delete(vente)
    db.commit()
    return {"message": "Vente deleted successfully"}


def get_vente_details(db: Session, current_user, vente_id: UUID, skip: int = 0, limit: int = 100):
    """Récupère les détails d'une vente spécifique"""
    # Vérifier que la vente appartient à l'utilisateur
    vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    details = db.query(VenteDetailModel).filter(VenteDetailModel.vente_id == vente_id).offset(skip).limit(limit).all()
    return details


def get_ventes_carburant(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les ventes de carburant appartenant aux stations de l'utilisateur"""
    # Calculer le total pour les métadonnées de pagination
    total_query = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    )
    total = total_query.count()

    # Récupérer les ventes de carburant avec pagination
    ventes_carburant = total_query.offset(skip).limit(limit).all()

    # Déterminer s'il y a plus d'éléments
    has_more = (skip + limit) < total

    # Retourner une réponse paginée structurée
    return PaginatedResponse(
        items=ventes_carburant,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )


def create_vente_carburant(db: Session, current_user, vente_carburant: schemas.VenteCarburantCreate):
    """Crée une nouvelle vente de carburant"""
    with db.begin():  # Using SQLAlchemy's built-in transaction management
        # Vérifier que la station appartient à l'utilisateur
        station = db.query(Station).filter(
            Station.id == vente_carburant.station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not station:
            raise HTTPException(status_code=403, detail="Station does not belong to your company")

        # Vérifier que la trésorerie station appartient à l'utilisateur si elle est spécifiée
        trésorerie_station = None
        if vente_carburant.trésorerie_station_id:
            trésorerie_station = db.query(TresorerieStationModel).join(
                Station,
                TresorerieStationModel.station_id == Station.id
            ).filter(
                TresorerieStationModel.id == vente_carburant.trésorerie_station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()

            if not trésorerie_station:
                raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

        # Récupérer les informations de la cuve pour déterminer le carburant_id
        from sqlalchemy import text
        result = db.execute(text("""
            SELECT c.carburant_id, s.id as station_id
            FROM cuve c
            JOIN station s ON c.station_id = s.id
            WHERE c.id = :cuve_id
        """), {"cuve_id": vente_carburant.cuve_id})

        cuve_data = result.fetchone()

        if not cuve_data or not cuve_data.carburant_id:
            raise HTTPException(status_code=404, detail="Carburant de la cuve non trouvé")

        # Vérifier que l'index initial est inférieur ou égal à l'index final
        if vente_carburant.index_initial > vente_carburant.index_final:
            raise HTTPException(status_code=400, detail="L'index initial ne peut pas être supérieur à l'index final")

        # Calculer la quantité mesurée par le pistolet
        quantite_mesuree = vente_carburant.index_final - vente_carburant.index_initial

        # Calculer l'écart entre la quantité vendue et la quantité mesurée
        ecart_quantite = abs(vente_carburant.quantite_vendue - quantite_mesuree)

        # Déterminer si une compensation est nécessaire (par exemple, si l'écart est supérieur à 1 litre)
        # Ce seuil pourrait être configurable selon les besoins
        seuil_ecart = 1.0  # en litres
        besoin_compensation = ecart_quantite > seuil_ecart

        # Déterminer le carburant_id à utiliser
        carburant_id = vente_carburant.carburant_id or cuve_data.carburant_id

        # Récupérer le prix de vente depuis la table prix_carburant
        prix_carburant = db.query(PrixCarburant).filter(
            PrixCarburant.carburant_id == carburant_id,
            PrixCarburant.station_id == vente_carburant.station_id
        ).first()

        if not prix_carburant or not prix_carburant.prix_vente:
            raise HTTPException(status_code=404, detail="Prix de vente non trouvé pour ce carburant et cette station")

        prix_unitaire = prix_carburant.prix_vente

        # Calculer le montant total
        montant_total = vente_carburant.quantite_vendue * prix_unitaire

        # Créer l'enregistrement de vente de carburant
        db_vente_carburant = VenteCarburantModel(
            station_id=vente_carburant.station_id,
            cuve_id=vente_carburant.cuve_id,
            pistolet_id=vente_carburant.pistolet_id,
            trésorerie_station_id=vente_carburant.trésorerie_station_id,  # Ajout de la référence à la trésorerie
            quantite_vendue=vente_carburant.quantite_vendue,
            prix_unitaire=prix_unitaire,
            montant_total=montant_total,
            date_vente=vente_carburant.date_vente,
            index_initial=vente_carburant.index_initial,
            index_final=vente_carburant.index_final,
            quantite_mesuree=quantite_mesuree,
            ecart_quantite=ecart_quantite,
            besoin_compensation=besoin_compensation,
            compensation_id=vente_carburant.compensation_id,
            pompiste=vente_carburant.pompiste,
            qualite_marshalle_id=vente_carburant.qualite_marshalle_id,
            montant_paye=vente_carburant.montant_paye,
            mode_paiement=vente_carburant.mode_paiement,
            utilisateur_id=vente_carburant.utilisateur_id
        )

        # Si le montant payé est inférieur au montant dû, créer une créance employé ou compensation
        if vente_carburant.montant_paye < montant_total:
            montant_creance = montant_total - vente_carburant.montant_paye

            creance_employe = CreanceEmployeModel(
                vente_carburant_id=db_vente_carburant.id,
                pompiste=vente_carburant.pompiste,
                montant_du=montant_creance,
                montant_paye=vente_carburant.montant_paye,
                solde_creance=montant_creance,
                created_at=vente_carburant.date_vente,
                utilisateur_gestion_id=vente_carburant.utilisateur_id
            )

            db.add(creance_employe)
            db_vente_carburant.creance_employe_id = creance_employe.id

        # Si une compensation pour écart de quantité est nécessaire
        if besoin_compensation:
            # Créer un avoir pour compenser l'écart de quantité
            # Récupérer la configuration de la compagnie pour déterminer le seuil d'écarts
            from ...models import Compagnie
            compagnie = db.query(Compagnie).filter(Compagnie.id == current_user.compagnie_id).first()

            # Déterminer le motif de l'avoir basé sur l'écart de quantité
            motif_avoir = f"Compensation pour écart de quantité sur la vente de carburant ID: {db_vente_carburant.id}"

            # Calculer le montant de compensation basé sur l'écart de quantité et le prix unitaire
            montant_compensation = ecart_quantite * prix_unitaire

            # Créer un nouvel avoir pour la compensation
            nouvel_avoir = AvoirModel(
                tiers_id=vente_carburant.utilisateur_id,  # L'utilisateur qui a effectué la vente
                montant_initial=montant_compensation,
                montant_utilise=0,  # Pas encore utilisé
                montant_restant=montant_compensation,
                date_emission=datetime.now(timezone.utc),
                date_utilisation=None,
                date_expiration=None,  # Date d'expiration configurable
                motif=motif_avoir,
                statut="emis",  # Statut initial
                utilisateur_emission_id=vente_carburant.utilisateur_id,
                utilisateur_utilisation_id=None,
                reference_origine=f"VTE-CB-{db_vente_carburant.id}",
                module_origine="ventes_carburant",
                compagnie_id=str(current_user.compagnie_id),
                station_id=str(vente_carburant.station_id)
            )

            db.add(nouvel_avoir)
            db.flush()  # Pour obtenir l'ID de l'avoir avant la validation

            # Lier l'avoir à la vente de carburant
            db_vente_carburant.compensation_id = nouvel_avoir.id
            db_vente_carburant.besoin_compensation = True  # Confirmer besoin de compensation

        # Si le client a payé plus que le montant dû (cas d'écart de paiement), créer un avoir
        if vente_carburant.montant_paye > montant_total:
            ecart_paiement = vente_carburant.montant_paye - montant_total

            motif_avoir = f"Avoir pour écart de paiement sur la vente de carburant ID: {db_vente_carburant.id}"

            # Créer un nouvel avoir pour le client
            nouvel_avoir_paiement = AvoirModel(
                tiers_id=vente_carburant.utilisateur_id,  # L'utilisateur qui a effectué la vente
                montant_initial=ecart_paiement,
                montant_utilise=0,  # Pas encore utilisé
                montant_restant=ecart_paiement,
                date_emission=datetime.now(timezone.utc),
                date_utilisation=None,
                date_expiration=None,  # Date d'expiration configurable
                motif=motif_avoir,
                statut="emis",  # Statut initial
                utilisateur_emission_id=vente_carburant.utilisateur_id,
                utilisateur_utilisation_id=None,
                reference_origine=f"VTE-CB-{db_vente_carburant.id}",
                module_origine="ventes_carburant",
                compagnie_id=str(current_user.compagnie_id),
                station_id=str(vente_carburant.station_id)
            )

            db.add(nouvel_avoir_paiement)
            db.flush()  # Pour obtenir l'ID de l'avoir avant la validation

            # Lier l'avoir à la vente de carburant si ce n'est pas déjà fait
            if not db_vente_carburant.compensation_id:
                db_vente_carburant.compensation_id = nouvel_avoir_paiement.id
            else:
                # Si une compensation pour écart de quantité existe déjà, on conserve la référence
                # et on considère que les deux compensations sont gérées via le système de gestion des avoirs
                pass

        db.add(db_vente_carburant)
        db.flush()  # Pour obtenir l'ID de la vente avant de créer les mouvements associés

        # Créer un mouvement de stock pour la sortie de carburant
        mouvement_stock = MouvementStockCuve(
            livraison_carburant_id=None,  # Pas de livraison associée pour une vente
            vente_carburant_id=db_vente_carburant.id,  # Lier au modèle de vente
            inventaire_carburant_id=None,  # Pas d'inventaire associé
            cuve_id=vente_carburant.cuve_id,
            type_mouvement="sortie",  # Carburant sort de la cuve
            quantite=vente_carburant.quantite_vendue,
            date_mouvement=vente_carburant.date_vente,
            stock_avant=None,  # Pourrait être calculé si nécessaire
            stock_apres=None,  # Pourrait être calculé si nécessaire
            utilisateur_id=vente_carburant.utilisateur_id,
            reference_origine=f"VTE-CB-{db_vente_carburant.id}",
            module_origine="ventes_carburant",
            statut="validé"
        )
        db.add(mouvement_stock)

        # Si la vente est effectuée en espèces et qu'une trésorerie est spécifiée, enregistrer le mouvement
        if (vente_carburant.mode_paiement == "espèce" or vente_carburant.mode_paiement == "chèque") and vente_carburant.trésorerie_station_id:
            # Créer un mouvement de trésorerie pour enregistrer l'entrée d'argent
            mouvement_entree = MouvementTresorerieModel(
                trésorerie_station_id=vente_carburant.trésorerie_station_id,
                type_mouvement="entrée",
                montant=vente_carburant.montant_paye,
                date_mouvement=datetime.now(timezone.utc),
                description=f"Vente carburant enregistrée (ID: {db_vente_carburant.id})",
                module_origine="ventes_carburant",
                reference_origine=f"VTE-CB-{db_vente_carburant.id}",
                utilisateur_id=current_user.id
            )
            db.add(mouvement_entree)

            # Mettre à jour le solde de la trésorerie
            from ...services.tresoreries import mettre_a_jour_solde_tresorerie
            mettre_a_jour_solde_tresorerie(db, vente_carburant.trésorerie_station_id)

        db.commit()  # Final commit after all operations are complete
        db.refresh(db_vente_carburant)

        return db_vente_carburant


def get_vente_carburant_by_id(db: Session, current_user, vente_carburant_id: UUID):
    """Récupère une vente de carburant spécifique par son ID"""
    vente_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        VenteCarburantModel.id == vente_carburant_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")
    return vente_carburant


def update_vente_carburant(db: Session, current_user, vente_carburant_id: UUID, vente_carburant: schemas.VenteCarburantUpdate):
    """Met à jour une vente de carburant existante"""
    db_vente_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        VenteCarburantModel.id == vente_carburant_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")

    update_data = vente_carburant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vente_carburant, field, value)

    db.commit()
    db.refresh(db_vente_carburant)
    return db_vente_carburant


def delete_vente_carburant(db: Session, current_user, vente_carburant_id: UUID):
    """Supprime une vente de carburant existante"""
    vente_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        VenteCarburantModel.id == vente_carburant_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")

    db.delete(vente_carburant)
    db.commit()
    return {"message": "Vente carburant deleted successfully"}


def get_creances_employes(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les créances employés appartenant aux stations de l'utilisateur"""
    from ...models import VenteCarburant
    # Calculer le total pour les métadonnées de pagination
    total_query = db.query(CreanceEmployeModel).join(
        VenteCarburant,
        CreanceEmployeModel.vente_carburant_id == VenteCarburant.id
    ).join(
        Station,
        VenteCarburant.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    )
    total = total_query.count()

    # Récupérer les créances employés avec pagination
    creances = total_query.offset(skip).limit(limit).all()

    # Déterminer s'il y a plus d'éléments
    has_more = (skip + limit) < total

    # Retourner une réponse paginée structurée
    return PaginatedResponse(
        items=creances,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )


def get_creance_employe_by_id(db: Session, current_user, creance_id: UUID):
    """Récupère une créance employé spécifique par son ID"""
    from ...models import VenteCarburant
    creance = db.query(CreanceEmployeModel).join(
        VenteCarburantModel,
        CreanceEmployeModel.vente_carburant_id == VenteCarburantModel.id
    ).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        CreanceEmployeModel.id == creance_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not creance:
        raise HTTPException(status_code=404, detail="Creance employé not found")
    return creance


def utiliser_avoir_pour_vente_carburant(db: Session, current_user, vente_carburant_id: UUID, avoir_id: UUID, montant_utilise: float):
    """Utilise un avoir pour compenser une vente de carburant"""
    # Récupérer la vente carburant
    vente_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        VenteCarburantModel.id == vente_carburant_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")

    # Récupérer l'avoir
    avoir = db.query(AvoirModel).filter(
        AvoirModel.id == avoir_id,
        AvoirModel.compagnie_id == str(current_user.compagnie_id)
    ).filter(AvoirModel.montant_restant >= montant_utilise).first()

    if not avoir:
        raise HTTPException(status_code=404, detail="Avoir not found or insufficient balance")

    # Mettre à jour l'avoir
    avoir.montant_utilise += montant_utilise
    avoir.montant_restant -= montant_utilise

    # Mettre à jour le statut de l'avoir
    if avoir.montant_restant <= 0:
        avoir.statut = "utilise"
    else:
        avoir.statut = "partiellement_utilise"

    # Enregistrer la date d'utilisation et l'utilisateur
    if avoir.montant_utilise > 0 and avoir.date_utilisation is None:
        avoir.date_utilisation = datetime.now(timezone.utc)
    avoir.utilisateur_utilisation_id = current_user.id

    # Mettre à jour l'enregistrement de la vente carburant
    vente_carburant.montant_paye += montant_utilise
    if vente_carburant.montant_paye >= vente_carburant.montant_total:
        vente_carburant.statut = "validée"

    # Mettre à jour l'éventuelle créance employé si elle existe
    if vente_carburant.creance_employe_id:
        creance = db.query(CreanceEmployeModel).filter(CreanceEmployeModel.id == vente_carburant.creance_employe_id).first()
        if creance:
            creance.montant_paye += montant_utilise
            creance.solde_creance -= montant_utilise
            if creance.solde_creance <= 0:
                creance.statut = "payé"
            elif creance.solde_creance < creance.montant_du:
                creance.statut = "partiellement_payé"

    db.commit()
    db.refresh(vente_carburant)
    db.refresh(avoir)

    return {"vente_carburant": vente_carburant, "avoir": avoir}