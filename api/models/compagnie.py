from sqlalchemy import Column, String, Integer, Boolean, DateTime, func, ForeignKey, DECIMAL, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Compagnie(Base):
    __tablename__ = "compagnie"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"), nullable=False)  # Changed to pays_id UUID
    adresse = Column(String)
    telephone = Column(String(20))
    email = Column(String(255))
    devise = Column(String(10), default="XOF")  # Changed default to XOF
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    stations = relationship("Station", back_populates="compagnie")


class Station(Base):
    __tablename__ = "station"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)
    nom = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False)  # Removed unique=True constraint to allow per company
    adresse = Column(String)
    coordonnees_gps = Column(String)  # JSON string
    statut = Column(String(20), default="inactif")  # Default to inactif
    config = Column(String, default='{"completion": {"station": false, "carburants": false, "cuves": false, "pistolets": false, "jauge": false, "fournisseurs": false, "clients": false, "employes": false, "tresorerie": false, "immobilisations": false, "soldes": false}}')  # JSON string for configuration
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("statut IN ('actif', 'inactif', 'supprimer')", name="check_station_status"),
    )

    # Relationships
    compagnie = relationship("Compagnie", back_populates="stations")
    cuves = relationship("Cuve", back_populates="station")


class Cuve(Base):
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
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    station = relationship("Station", back_populates="cuves")
    pistolets = relationship("Pistolet", back_populates="cuve")
    carburant = relationship("Carburant", back_populates="cuves")

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
        try:
            barremage = json.loads(self.barremage)
        except json.JSONDecodeError:
            raise ValueError("Le barremage est mal formaté")

        # Trier le barremage par hauteur pour assurer l'ordre
        barremage_trie = sorted(barremage, key=lambda x: x['hauteur_cm'])

        # Trouver les deux points entre lesquels se trouve la hauteur
        point_inf = None
        point_sup = None

        for i, point in enumerate(barremage_trie):
            if point['hauteur_cm'] <= hauteur_cm:
                point_inf = point
            if point['hauteur_cm'] >= hauteur_cm and point_inf is not None:
                point_sup = point
                break

        # Si la hauteur est inférieure à la plus petite hauteur du barremage
        if point_inf is None:
            # Prendre le premier point
            return barremage_trie[0]['volume_litres'] if barremage_trie else 0

        # Si la hauteur est supérieure à la plus grande hauteur du barremage
        if point_sup is None:
            # Prendre le dernier point
            return barremage_trie[-1]['volume_litres'] if barremage_trie else 0

        # Si la hauteur correspond exactement à un point
        if point_inf['hauteur_cm'] == hauteur_cm:
            return point_inf['volume_litres']

        if point_sup['hauteur_cm'] == hauteur_cm:
            return point_sup['volume_litres']

        # Calculer le volume par interpolation linéaire
        hauteur_diff = point_sup['hauteur_cm'] - point_inf['hauteur_cm']
        volume_diff = point_sup['volume_litres'] - point_inf['volume_litres']

        # Calculer le facteur d'interpolation
        facteur = (hauteur_cm - point_inf['hauteur_cm']) / hauteur_diff if hauteur_diff != 0 else 0

        volume = point_inf['volume_litres'] + (volume_diff * facteur)
        return round(volume, 2)  # Arrondir à 2 décimales

    def calculer_hauteur(self, volume_litres):
        """
        Calcule la hauteur en cm à partir du volume en litres
        en utilisant le barremage de la cuve
        """
        if not self.barremage:
            raise ValueError("Le barremage n'est pas défini pour cette cuve")

        import json
        try:
            barremage = json.loads(self.barremage)
        except json.JSONDecodeError:
            raise ValueError("Le barremage est mal formaté")

        # Trier le barremage par volume pour assurer l'ordre
        barremage_trie = sorted(barremage, key=lambda x: x['volume_litres'])

        # Trouver les deux points entre lesquels se trouve le volume
        point_inf = None
        point_sup = None

        for i, point in enumerate(barremage_trie):
            if point['volume_litres'] <= volume_litres:
                point_inf = point
            if point['volume_litres'] >= volume_litres and point_inf is not None:
                point_sup = point
                break

        # Si le volume est inférieur au plus petit volume du barremage
        if point_inf is None:
            # Prendre le premier point
            return barremage_trie[0]['hauteur_cm'] if barremage_trie else 0

        # Si le volume est supérieur au plus grand volume du barremage
        if point_sup is None:
            # Prendre le dernier point
            return barremage_trie[-1]['hauteur_cm'] if barremage_trie else 0

        # Si le volume correspond exactement à un point
        if point_inf['volume_litres'] == volume_litres:
            return point_inf['hauteur_cm']

        if point_sup['volume_litres'] == volume_litres:
            return point_sup['hauteur_cm']

        # Calculer la hauteur par interpolation linéaire
        volume_diff = point_sup['volume_litres'] - point_inf['volume_litres']
        hauteur_diff = point_sup['hauteur_cm'] - point_inf['hauteur_cm']

        # Calculer le facteur d'interpolation
        facteur = (volume_litres - point_inf['volume_litres']) / volume_diff if volume_diff != 0 else 0

        hauteur = point_inf['hauteur_cm'] + (hauteur_diff * facteur)
        return round(hauteur, 2)  # Arrondir à 2 décimales


class Pistolet(Base):
    __tablename__ = "pistolet"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    numero = Column(String(50), nullable=False)  # Changed from nom to numero
    statut = Column(String(20), default="actif")  # Changed to string with actif/inactif/maintenance
    index_initial = Column(Integer, default=0)
    index_final = Column(Integer)
    date_derniere_utilisation = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    cuve = relationship("Cuve", back_populates="pistolets")


class EtatInitialCuve(Base):
    __tablename__ = "etat_initial_cuve"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    hauteur_jauge_initiale = Column(DECIMAL(12, 2), nullable=False)  # in cm
    volume_initial_calcule = Column(DECIMAL(12, 2), nullable=False)  # in liters
    date_initialisation = Column(DateTime, nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    verrouille = Column(Boolean, default=False)  # To prevent modifications after movements
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MouvementStockCuve(Base):
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
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())