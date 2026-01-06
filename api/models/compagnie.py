from sqlalchemy import Column, String, Integer, Boolean, DateTime, func, ForeignKey, DECIMAL, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from .base_model import BaseModel


class NiveauValidation(PyEnum):
    NIVEAU_1 = 1
    NIVEAU_2 = 2
    NIVEAU_3 = 3
    NIVEAU_4 = 4
    NIVEAU_5 = 5

class Compagnie(BaseModel):
    __tablename__ = "compagnie"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"), nullable=False)  # Changed to pays_id UUID
    adresse = Column(String)
    telephone = Column(String(20))
    email = Column(String(255))
    devise = Column(String(10), default="XOF")  # Changed default to XOF
    infos_plus = Column(JSONB)  # Additional information in JSON format

    # Relationships
    stations = relationship("Station", back_populates="compagnie", lazy="select")
    regles_validation = relationship("RegleValidation", back_populates="compagnie", lazy="select")


class Station(BaseModel):
    __tablename__ = "station"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)
    nom = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False)  # Removed unique=True constraint to allow per company
    adresse = Column(String)
    coordonnees_gps = Column(JSONB)  # JSONB for coordinates GPS
    statut = Column(String(20), default="inactif")  # Default to inactif
    config = Column(String, default='{"completion": {"station": false, "carburants": false, "cuves": false, "pistolets": false, "jauge": false, "fournisseurs": false, "clients": false, "employes": false, "tresorerie": false, "immobilisations": false, "soldes": false}}')  # JSON string for configuration
    groupe_id = Column(UUID(as_uuid=True), ForeignKey("groupes_partenaire.id"), nullable=True)  # Link to groupes_partenaire
    infos_plus = Column(JSONB)  # Additional information in JSON format

    __table_args__ = (
        CheckConstraint("statut IN ('actif', 'inactif', 'supprimer')", name="check_station_status"),
    )

    # Relationships
    compagnie = relationship("Compagnie", back_populates="stations", lazy="select")
    groupe_partenaire = relationship("GroupePartenaire", back_populates="stations", lazy="select")
    cuves = relationship("Cuve", back_populates="station", lazy="select")
    stocks = relationship("StockProduit", back_populates="station", lazy="select")
    lots = relationship("Lot", back_populates="station", lazy="select")


class Cuve(BaseModel):
    __tablename__ = "cuve"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    nom = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False)
    capacite_maximale = Column(DECIMAL(12, 2), nullable=False)  # in liters - changed to DECIMAL for precision
    niveau_actuel = Column(DECIMAL(12, 2), default=0)  # in liters - changed to DECIMAL for precision
    carburant_id = Column(UUID(as_uuid=True), ForeignKey("carburant.id"), nullable=False)  # References the carburant table
    statut = Column(String(20), default="actif")  # Changed to string with actif/inactif/maintenance
    barremage = Column(String)  # JSON string for the calibration data
    alert_stock = Column(DECIMAL(12, 2), default=0)  # Stock alert threshold - added DECIMAL for precision

    # Relationships
    station = relationship("Station", back_populates="cuves", lazy="select")
    pistolets = relationship("Pistolet", back_populates="cuve", lazy="select")
    carburant = relationship("Carburant", back_populates="cuves", lazy="select")
    etat_initial = relationship("EtatInitialCuve", back_populates="cuve", lazy="select", uselist=False)
    stock_carburant = relationship("StockCarburant", back_populates="cuve", lazy="select", uselist=False)

    def est_operable(self, db_session):
        """
        Vérifie si la cuve est opérationnelle
        Une cuve est opérationnelle si :
        1. Son statut est 'actif'
        2. Elle a un barremage défini
        3. Elle a un état initial défini
        """
        if self.statut != 'actif':
            return False

        if not self.barremage:
            return False

        # Vérifier si un état initial existe pour cette cuve
        count = db_session.query(EtatInitialCuve).filter(
            EtatInitialCuve.cuve_id == self.id
        ).count()
        return count > 0

    def calculer_volume(self, hauteur_cm):
        """
        Calcule le volume en litres à partir de la hauteur en cm
        en utilisant le barremage de la cuve
        """
        if not self.barremage:
            raise ValueError("Le barremage n'est pas défini pour cette cuve")

        import json
        # Gérer les deux cas : barremage peut être une chaîne JSON ou déjà un objet Python
        if isinstance(self.barremage, str):
            try:
                barremage = json.loads(self.barremage)
            except json.JSONDecodeError:
                raise ValueError("Le barremage est mal formaté")
        else:
            # Si self.barremage n'est pas une chaîne, on suppose que c'est déjà un objet Python
            barremage = self.barremage

        # Vérifier que le barremage est bien une liste
        if not isinstance(barremage, list):
            raise ValueError("Le barremage est mal formaté - ce n'est pas une liste d'objets")

        # Trier le barremage par hauteur pour assurer l'ordre
        # Supporte les deux formats (hauteur_cm/volume_litres et hauteur/volume)
        def get_hauteur(item):
            return item.get('hauteur_cm', item.get('hauteur', 0))

        barremage_trie = sorted(barremage, key=get_hauteur)

        # Trouver les deux points entre lesquels se trouve la hauteur
        point_inf = None
        point_sup = None

        for i, point in enumerate(barremage_trie):
            point_hauteur = get_hauteur(point)
            if point_hauteur <= hauteur_cm:
                point_inf = point
            if point_hauteur >= hauteur_cm and point_inf is not None:
                point_sup = point
                break

        # Si la hauteur est inférieure à la plus petite hauteur du barremage
        if point_inf is None:
            # Prendre le premier point
            first_point = barremage_trie[0] if barremage_trie else {}
            return first_point.get('volume_litres', first_point.get('volume', 0))

        # Si la hauteur est supérieure à la plus grande hauteur du barremage
        if point_sup is None:
            # Prendre le dernier point
            last_point = barremage_trie[-1] if barremage_trie else {}
            return last_point.get('volume_litres', last_point.get('volume', 0))

        # Si la hauteur correspond exactement à un point
        point_inf_hauteur = get_hauteur(point_inf)
        point_sup_hauteur = get_hauteur(point_sup)

        if point_inf_hauteur == hauteur_cm:
            return point_inf.get('volume_litres', point_inf.get('volume', 0))

        if point_sup_hauteur == hauteur_cm:
            return point_sup.get('volume_litres', point_sup.get('volume', 0))

        # Calculer le volume par interpolation linéaire
        hauteur_inf = get_hauteur(point_inf)
        hauteur_sup = get_hauteur(point_sup)

        hauteur_diff = hauteur_sup - hauteur_inf
        volume_inf = point_inf.get('volume_litres', point_inf.get('volume', 0))
        volume_sup = point_sup.get('volume_litres', point_sup.get('volume', 0))
        volume_diff = volume_sup - volume_inf

        # Calculer le facteur d'interpolation
        facteur = (hauteur_cm - hauteur_inf) / hauteur_diff if hauteur_diff != 0 else 0

        volume = volume_inf + (volume_diff * facteur)
        return round(volume, 2)  # Arrondir à 2 décimales

    def calculer_hauteur(self, volume_litres):
        """
        Calcule la hauteur en cm à partir du volume en litres
        en utilisant le barremage de la cuve
        """
        if not self.barremage:
            raise ValueError("Le barremage n'est pas défini pour cette cuve")

        import json
        # Gérer les deux cas : barremage peut être une chaîne JSON ou déjà un objet Python
        if isinstance(self.barremage, str):
            try:
                barremage = json.loads(self.barremage)
            except json.JSONDecodeError:
                raise ValueError("Le barremage est mal formaté")
        else:
            # Si self.barremage n'est pas une chaîne, on suppose que c'est déjà un objet Python
            barremage = self.barremage

        # Vérifier que le barremage est bien une liste
        if not isinstance(barremage, list):
            raise ValueError("Le barremage est mal formaté - ce n'est pas une liste d'objets")

        # Trier le barremage par volume pour assurer l'ordre
        # Supporte les deux formats (hauteur_cm/volume_litres et hauteur/volume)
        def get_volume(item):
            return item.get('volume_litres', item.get('volume', 0))

        barremage_trie = sorted(barremage, key=get_volume)

        # Trouver les deux points entre lesquels se trouve le volume
        point_inf = None
        point_sup = None

        for i, point in enumerate(barremage_trie):
            point_volume = get_volume(point)
            if point_volume <= volume_litres:
                point_inf = point
            if point_volume >= volume_litres and point_inf is not None:
                point_sup = point
                break

        # Si le volume est inférieur au plus petit volume du barremage
        if point_inf is None:
            # Prendre le premier point
            first_point = barremage_trie[0] if barremage_trie else {}
            return first_point.get('hauteur_cm', first_point.get('hauteur', 0))

        # Si le volume est supérieur au plus grand volume du barremage
        if point_sup is None:
            # Prendre le dernier point
            last_point = barremage_trie[-1] if barremage_trie else {}
            return last_point.get('hauteur_cm', last_point.get('hauteur', 0))

        # Si le volume correspond exactement à un point
        point_inf_volume = get_volume(point_inf)
        point_sup_volume = get_volume(point_sup)

        if point_inf_volume == volume_litres:
            return point_inf.get('hauteur_cm', point_inf.get('hauteur', 0))

        if point_sup_volume == volume_litres:
            return point_sup.get('hauteur_cm', point_sup.get('hauteur', 0))

        # Calculer la hauteur par interpolation linéaire
        volume_inf = get_volume(point_inf)
        volume_sup = get_volume(point_sup)

        volume_diff = volume_sup - volume_inf
        hauteur_inf = point_inf.get('hauteur_cm', point_inf.get('hauteur', 0))
        hauteur_sup = point_sup.get('hauteur_cm', point_sup.get('hauteur', 0))
        hauteur_diff = hauteur_sup - hauteur_inf

        # Calculer le facteur d'interpolation
        facteur = (volume_litres - volume_inf) / volume_diff if volume_diff != 0 else 0

        hauteur = hauteur_inf + (hauteur_diff * facteur)
        return round(hauteur, 2)  # Arrondir à 2 décimales


class Pistolet(BaseModel):
    __tablename__ = "pistolet"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    numero = Column(String(50), nullable=False)  # Changed from nom to numero
    statut = Column(String(20), default="actif")  # Changed to string with actif/inactif/maintenance
    index_initial = Column(Integer, default=0)
    index_final = Column(Integer)
    date_derniere_utilisation = Column(DateTime)

    # Relationships
    cuve = relationship("Cuve", back_populates="pistolets", lazy="select")


class EtatInitialCuve(BaseModel):
    __tablename__ = "etat_initial_cuve"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    hauteur_jauge_initiale = Column(DECIMAL(12, 2), nullable=False)  # in cm
    volume_initial_calcule = Column(DECIMAL(12, 2), nullable=False)  # in liters
    date_initialisation = Column(DateTime, nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    verrouille = Column(Boolean, default=False)  # To prevent modifications after movements

    # Relationships
    cuve = relationship("Cuve", back_populates="etat_initial", lazy="select")


class MouvementStockCuve(BaseModel):
    __tablename__ = "mouvement_stock_cuve"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    livraison_carburant_id = Column(UUID(as_uuid=True), ForeignKey("livraisons.id"))
    vente_carburant_id = Column(UUID(as_uuid=True), ForeignKey("vente_carburant.id"))
    inventaire_carburant_id = Column(UUID(as_uuid=True), ForeignKey("inventaires.id"))
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    type_mouvement = Column(String(10), nullable=False)  # 'entrée', 'sortie', 'ajustement'
    quantite = Column(DECIMAL(12, 2), nullable=False)
    date_mouvement = Column(DateTime, nullable=False)
    stock_avant = Column(DECIMAL(12, 2))  # Stock avant le mouvement
    stock_apres = Column(DECIMAL(12, 2))  # Stock après le mouvement
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    reference_origine = Column(String(100), nullable=False)
    module_origine = Column(String(100), nullable=False)
    statut = Column(String(20), default="validé")  # 'validé', 'annulé'
