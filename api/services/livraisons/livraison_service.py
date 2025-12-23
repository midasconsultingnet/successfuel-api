"""
Service for managing fuel deliveries according to the new specifications.
This service handles creating, updating, and managing fuel deliveries,
including association with fuel purchases and stock updates.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ...models.livraison import Livraison
from ...models.compagnie import Cuve
from ...models.carburant import Carburant
from ...models.achat_carburant import AchatCarburant
from ...models.compagnie import Compagnie, MouvementStockCuve, Station
from ...models.user import User
from ...livraisons.schemas import LivraisonCreate, LivraisonUpdate
from ...exceptions import (
    EntityNotFoundException,
    ValidationErrorException,
    DatabaseIntegrityException
)

def get_livraison_by_id(db: Session, livraison_id: str) -> Livraison:
    """
    Retrieve a delivery by its ID
    
    Args:
        db: Database session
        livraison_id: UUID of the delivery to retrieve
        
    Returns:
        Livraison: The delivery object
        
    Raises:
        EntityNotFoundException: If the delivery is not found
    """
    livraison = db.query(Livraison).filter(Livraison.id == livraison_id).first()
    if not livraison:
        raise EntityNotFoundException(f"Livraison with id {livraison_id} not found")
    return livraison


def get_livraisons(db: Session, skip: int = 0, limit: int = 100) -> list[Livraison]:
    """
    Retrieve a list of deliveries with pagination
    
    Args:
        db: Database session
        skip: Number of deliveries to skip for pagination
        limit: Maximum number of deliveries to return
        
    Returns:
        List[Livraison]: List of delivery objects
    """
    return db.query(Livraison).offset(skip).limit(limit).all()


def get_livraisons_by_cuve(db: Session, cuve_id: str, skip: int = 0, limit: int = 100) -> list[Livraison]:
    """
    Retrieve delivery history for a specific tank
    
    Args:
        db: Database session
        cuve_id: UUID of the tank
        skip: Number of deliveries to skip for pagination
        limit: Maximum number of deliveries to return
        
    Returns:
        List[Livraison]: List of delivery objects for the tank
    """
    return db.query(Livraison).filter(Livraison.cuve_id == cuve_id).offset(skip).limit(limit).all()


def create_livraison(db: Session, livraison_data: LivraisonCreate) -> Livraison:
    """
    Create a new fuel delivery according to the new specifications
    
    Args:
        db: Database session
        livraison_data: Delivery data to create
        
    Returns:
        Livraison: The created delivery object
        
    Raises:
        ValidationErrorException: If validation checks fail
        DatabaseIntegrityException: If database constraints are violated
    """
    # Validate the associated entities exist
    validate_associated_entities(db, livraison_data)
    
    # Check if the tank accepts the fuel type
    validate_tank_fuel_compatibility(db, livraison_data.cuve_id, livraison_data.carburant_id)
    
    # Calculate montant_total if prix_unitaire is provided
    montant_total = None
    if livraison_data.prix_unitaire is not None and livraison_data.quantite_livree is not None:
        montant_total = livraison_data.prix_unitaire * livraison_data.quantite_livree
    
    # Create the delivery record
    db_livraison = Livraison(
        achat_carburant_id=livraison_data.achat_carburant_id,
        station_id=livraison_data.station_id,
        cuve_id=livraison_data.cuve_id,
        carburant_id=livraison_data.carburant_id,
        quantite_livree=livraison_data.quantite_livree,
        quantite_commandee=livraison_data.quantite_commandee,
        date_livraison=livraison_data.date_livraison,
        prix_unitaire=livraison_data.prix_unitaire,
        montant_total=montant_total,
        jauge_avant_livraison=livraison_data.jauge_avant_livraison,
        jauge_apres_livraison=livraison_data.jauge_apres_livraison,
        utilisateur_id=livraison_data.utilisateur_id,
        information=livraison_data.information,
        numero_facture=livraison_data.numero_facture,
        compagnie_id=livraison_data.compagnie_id,
        statut_livraison=livraison_data.statut_livraison
    )

    try:
        db.add(db_livraison)
        db.commit()
        db.refresh(db_livraison)
        
        # Update stock levels after creating the delivery
        update_stock_after_delivery(db, db_livraison)
        
        return db_livraison
    except Exception as e:
        db.rollback()
        raise DatabaseIntegrityException(f"Failed to create delivery: {str(e)}")


def update_livraison(db: Session, livraison_id: str, livraison_data: LivraisonUpdate) -> Livraison:
    """
    Update an existing fuel delivery
    
    Args:
        db: Database session
        livraison_id: UUID of the delivery to update
        livraison_data: Updated delivery data
        
    Returns:
        Livraison: The updated delivery object
        
    Raises:
        EntityNotFoundException: If the delivery is not found
        ValidationErrorException: If validation checks fail
        DatabaseIntegrityException: If database constraints are violated
    """
    db_livraison = get_livraison_by_id(db, livraison_id)
    
    # Apply updates
    update_data = livraison_data.dict(exclude_unset=True)
    
    # Recalculate montant_total if prix_unitaire is updated
    if 'prix_unitaire' in update_data and update_data['prix_unitaire'] is not None and db_livraison.quantite_livree is not None:
        update_data['montant_total'] = update_data['prix_unitaire'] * float(db_livraison.quantite_livree)
    elif 'quantite_livree' in update_data and update_data['quantite_livree'] is not None and db_livraison.prix_unitaire is not None:
        update_data['montant_total'] = float(db_livraison.prix_unitaire) * update_data['quantite_livree']
    
    for field, value in update_data.items():
        setattr(db_livraison, field, value)

    try:
        db.commit()
        db.refresh(db_livraison)
        
        # Update stock levels after updating the delivery
        update_stock_after_delivery(db, db_livraison)
        
        return db_livraison
    except Exception as e:
        db.rollback()
        raise DatabaseIntegrityException(f"Failed to update delivery: {str(e)}")


def delete_livraison(db: Session, livraison_id: str) -> bool:
    """
    Delete a delivery
    
    Args:
        db: Database session
        livraison_id: UUID of the delivery to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        EntityNotFoundException: If the delivery is not found
    """
    db_livraison = get_livraison_by_id(db, livraison_id)
    
    try:
        db.delete(db_livraison)
        db.commit()
        
        # Update stock levels after deleting the delivery
        update_stock_after_delivery(db, db_livraison)
        
        return True
    except Exception as e:
        db.rollback()
        raise DatabaseIntegrityException(f"Failed to delete delivery: {str(e)}")


def validate_associated_entities(db: Session, livraison_data: LivraisonCreate) -> bool:
    """
    Validate that all associated entities exist
    
    Args:
        db: Database session
        livraison_data: Delivery data to validate
        
    Returns:
        bool: True if all entities exist
        
    Raises:
        ValidationErrorException: If any associated entity doesn't exist
    """
    # Validate station exists
    station = db.query(Station).filter(Station.id == livraison_data.station_id).first()
    if not station:
        raise ValidationErrorException(f"Station with id {livraison_data.station_id} not found")
        
    # Validate tank exists
    cuve = db.query(Cuve).filter(Cuve.id == livraison_data.cuve_id).first()
    if not cuve:
        raise ValidationErrorException(f"Tank (Cuve) with id {livraison_data.cuve_id} not found")
    
    # Validate fuel type exists
    carburant = db.query(Carburant).filter(Carburant.id == livraison_data.carburant_id).first()
    if not carburant:
        raise ValidationErrorException(f"Fuel type (Carburant) with id {livraison_data.carburant_id} not found")
    
    # Validate user exists
    utilisateur = db.query(User).filter(User.id == livraison_data.utilisateur_id).first()
    if not utilisateur:
        raise ValidationErrorException(f"User with id {livraison_data.utilisateur_id} not found")
    
    # Validate company exists
    compagnie = db.query(Compagnie).filter(Compagnie.id == livraison_data.compagnie_id).first()
    if not compagnie:
        raise ValidationErrorException(f"Company with id {livraison_data.compagnie_id} not found")
    
    # If a fuel purchase is specified, validate it exists
    if livraison_data.achat_carburant_id:
        achat = db.query(AchatCarburant).filter(AchatCarburant.id == livraison_data.achat_carburant_id).first()
        if not achat:
            raise ValidationErrorException(f"Fuel purchase with id {livraison_data.achat_carburant_id} not found")
    
    return True


def validate_tank_fuel_compatibility(db: Session, cuve_id: str, carburant_id: str) -> bool:
    """
    Validate that the tank accepts the fuel type
    
    Args:
        db: Database session
        cuve_id: UUID of the tank
        carburant_id: UUID of the fuel type
        
    Returns:
        bool: True if the tank accepts the fuel type
        
    Raises:
        ValidationErrorException: If the fuel type is not compatible with the tank
    """
    cuve = db.query(Cuve).filter(Cuve.id == cuve_id).first()
    if not cuve:
        raise ValidationErrorException(f"Tank with id {cuve_id} not found")
    
    # In a real implementation, this would validate that the tank is compatible with the fuel type
    # For now, we'll assume all tanks can accept all fuel types (this is where the Structure module would come in)
    # Based on the specifications, the Structure module would handle this validation
    
    return True


def update_stock_after_delivery(db: Session, livraison: Livraison) -> bool:
    """
    Update stock levels after a delivery is created, updated, or deleted.
    This creates or updates stock movement records in the Mouvement_Stock_Cuve table.

    Args:
        db: Database session
        livraison: The delivery object that triggered the stock update

    Returns:
        bool: True if the update was successful
    """
    try:
        # Find any existing stock movement for this delivery and delete it (for updates/deletes)
        existing_mouvement = db.query(MouvementStockCuve).filter(
            MouvementStockCuve.livraison_carburant_id == livraison.id
        ).first()

        if existing_mouvement:
            db.delete(existing_mouvement)
            db.commit()

        # Only create a new movement if the delivery is active and has a positive quantity
        if livraison.est_actif and livraison.quantite_livree and float(livraison.quantite_livree) > 0:
            # Calculate stock before and after
            # In a real implementation, we would fetch the current stock from the tank before this delivery
            # For now, we'll set both to None and let the system calculate it later
            stock_avant = None  # Would be calculated from previous movements
            stock_apres = None  # Would be calculated as stock_avant + livraison.quantite_livree

            # Create a new stock movement record
            mouvement_stock = MouvementStockCuve(
                livraison_carburant_id=livraison.id,
                cuve_id=livraison.cuve_id,
                type_mouvement="entrée",  # Delivery increases stock
                quantite=livraison.quantite_livree,
                date_mouvement=livraison.date_livraison,
                stock_avant=stock_avant,
                stock_apres=stock_apres,
                utilisateur_id=livraison.utilisateur_id,
                reference_origine=f"LIV-{str(livraison.id)[:8]}",  # Reference for the delivery
                module_origine="livraisons",
                statut="validé"  # Default to validated
            )

            db.add(mouvement_stock)
            db.commit()

        return True
    except Exception as e:
        raise ValidationErrorException(f"Failed to update stock after delivery: {str(e)}")