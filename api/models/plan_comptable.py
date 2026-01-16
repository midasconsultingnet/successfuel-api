from sqlalchemy import Column, String, Integer, UUID, ForeignKey
from sqlalchemy.orm import relationship
from .base_model import BaseModel
import uuid

class PlanComptableModel(BaseModel):
    __tablename__ = "plan_comptable"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_compte = Column(String(50), nullable=True)  # Numéro unique du compte (rendu nullable)
    libelle_compte = Column(String(255), nullable=False)  # Libellé du compte
    categorie = Column(String(100), nullable=False)  # Catégorie du compte (Actif, Passif, Produit, Charge)
    type_compte = Column(String(50), nullable=False)  # Type (Bilan, Resultat, etc.)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('plan_comptable.id'), nullable=True)  # Hiérarchie
    compagnie_id = Column(UUID(as_uuid=True), nullable=True)  # Identifiant de la compagnie (pour les sous-comptes)

    # Relations
    parent = relationship("PlanComptableModel", remote_side=[id], back_populates="children")
    children = relationship("PlanComptableModel", back_populates="parent")

    # Relations avec les écritures comptables
    ecritures_debit = relationship("EcritureComptableModel", foreign_keys="EcritureComptableModel.compte_debit", back_populates="compte_debit_rel")
    ecritures_credit = relationship("EcritureComptableModel", foreign_keys="EcritureComptableModel.compte_credit", back_populates="compte_credit_rel")

    # Relations inverses avec d'autres tables (si nécessaire)
    # Exemple : tiers, tresorerie, produit, methode_paiement, categories_charges
    # tiers = relationship("TiersModel", back_populates="compte_associe")
    # tresorerie = relationship("TresorerieModel", back_populates="compte_associe")
    # produit = relationship("ProduitModel", back_populates="compte_associe")
    # methode_paiement = relationship("MethodePaiementModel", back_populates="compte_associe")
    # categories_charges = relationship("CategoriesChargesModel", back_populates="compte_associe")