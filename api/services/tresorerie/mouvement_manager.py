from sqlalchemy.orm import Session
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid
from ...models.tresorerie import MouvementTresorerie
from ...models.achat import Achat
from ...models.achat_carburant import AchatCarburant
from ...models.vente import Vente
from ...models.vente_carburant import VenteCarburant
from ...exceptions import InsufficientFundsException, InvalidTransactionException
from ..comptabilite import ComptabiliteManager, TypeOperationComptable


class TypeMouvement(str, Enum):
    ENTREE = "entrée"
    SORTIE = "sortie"


class MouvementTresorerieManager:
    """
    Classe centralisée pour la gestion des mouvements de trésorerie
    dans les modules d'achats et de ventes.
    """
    
    @staticmethod
    def creer_mouvement_achat(
        db: Session,
        achat_id: uuid.UUID,
        type_achat: str,  # 'boutique' ou 'carburant'
        utilisateur_id: uuid.UUID,
        commentaire: Optional[str] = None,
        montant: Optional[float] = None,
        tresorerie_station_id: Optional[uuid.UUID] = None
    ) -> MouvementTresorerie:
        """
        Crée un mouvement de trésorerie pour un achat (type 'sortie').
        """
        if type_achat == 'boutique':
            achat = db.query(Achat).filter(Achat.id == achat_id).first()
            if not achat:
                raise InvalidTransactionException(f"Achat boutique {achat_id} non trouvé")

            montant = montant or float(achat.montant_total)
            tresorerie_station_id = tresorerie_station_id or achat.tresorerie_station_id
            module_origine = "achats_boutique"
            reference_origine = f"AB-{achat_id}"

        elif type_achat == 'carburant':
            achat = db.query(AchatCarburant).filter(AchatCarburant.id == achat_id).first()
            if not achat:
                raise InvalidTransactionException(f"Achat carburant {achat_id} non trouvé")

            montant = montant or float(achat.montant_total)
            # If tresorerie_station_id is not provided, we'll need to handle it differently
            # since AchatCarburant doesn't have a direct tresorerie_station_id
            module_origine = "achats_carburant"
            reference_origine = f"AC-{achat_id}"
        else:
            raise InvalidTransactionException("Type d'achat non valide")

        # For carburant, we need to get the tresorerie_station_id from the payments
        if type_achat == 'carburant' and not tresorerie_station_id:
            # Get the first payment to determine the tresorerie_station_id
            from ...models.achat_carburant import PaiementAchatCarburant
            paiement = db.query(PaiementAchatCarburant).filter(
                PaiementAchatCarburant.achat_carburant_id == achat_id
            ).first()

            if not paiement:
                raise InvalidTransactionException(f"Aucun paiement trouvé pour l'achat carburant {achat_id}")

            tresorerie_station_id = paiement.tresorerie_station_id

        # Créer le mouvement de trésorerie
        mouvement = MouvementTresorerie(
            tresorerie_station_id=tresorerie_station_id,
            type_mouvement=TypeMouvement.SORTIE,
            montant=montant,
            date_mouvement=datetime.utcnow(),
            description=f"Paiement pour {module_origine} {achat_id}",
            module_origine=module_origine,
            reference_origine=reference_origine,
            utilisateur_id=utilisateur_id,
            commentaire=commentaire
        )

        db.add(mouvement)
        db.commit()
        db.refresh(mouvement)

        # Enregistrer l'écriture comptable
        try:
            if type_achat == 'boutique':
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=TypeOperationComptable.ACHAT_BOUTIQUE,
                    reference_origine=reference_origine,
                    montant=montant,
                    compte_debit="607",  # Achats de marchandises
                    compte_credit="512",  # Trésorerie
                    libelle=f"Achat boutique #{achat_id}",
                    utilisateur_id=utilisateur_id
                )
            elif type_achat == 'carburant':
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=TypeOperationComptable.ACHAT_CARBURANT,
                    reference_origine=reference_origine,
                    montant=montant,
                    compte_debit="607",  # Achats de carburant
                    compte_credit="512",  # Trésorerie
                    libelle=f"Achat carburant #{achat_id}",
                    utilisateur_id=utilisateur_id
                )
        except Exception as e:
            # En cas d'erreur, on continue sans l'écriture comptable
            print(f"Erreur lors de l'enregistrement de l'écriture comptable pour l'achat {achat_id}: {str(e)}")

        return mouvement
    
    @staticmethod
    def creer_mouvement_vente(
        db: Session,
        vente_id: uuid.UUID,
        type_vente: str,  # 'boutique' ou 'carburant'
        utilisateur_id: uuid.UUID,
        commentaire: Optional[str] = None
    ) -> MouvementTresorerie:
        """
        Crée un mouvement de trésorerie pour une vente (type 'entrée').
        """
        if type_vente == 'boutique':
            vente = db.query(Vente).filter(Vente.id == vente_id).first()
            if not vente:
                raise InvalidTransactionException(f"Vente boutique {vente_id} non trouvée")

            montant = float(vente.montant_total)
            module_origine = "ventes_boutique"
            reference_origine = f"VB-{vente_id}"

        elif type_vente == 'carburant':
            vente = db.query(VenteCarburant).filter(VenteCarburant.id == vente_id).first()
            if not vente:
                raise InvalidTransactionException(f"Vente carburant {vente_id} non trouvée")

            montant = float(vente.montant_total)
            module_origine = "ventes_carburant"
            reference_origine = f"VC-{vente_id}"
        else:
            raise InvalidTransactionException("Type de vente non valide")

        # Créer le mouvement de trésorerie
        mouvement = MouvementTresorerie(
            tresorerie_station_id=vente.tresorerie_station_id,
            type_mouvement=TypeMouvement.ENTREE,
            montant=montant,
            date_mouvement=datetime.utcnow(),
            description=f"Paiement reçu pour {module_origine} {vente_id}",
            module_origine=module_origine,
            reference_origine=reference_origine,
            utilisateur_id=utilisateur_id,
            commentaire=commentaire
        )

        db.add(mouvement)
        db.commit()
        db.refresh(mouvement)

        # Enregistrer l'écriture comptable
        try:
            if type_vente == 'boutique':
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=TypeOperationComptable.VENTE_BOUTIQUE,
                    reference_origine=reference_origine,
                    montant=montant,
                    compte_debit="512",  # Trésorerie
                    compte_credit="707",  # Ventes de marchandises
                    libelle=f"Vente boutique #{vente_id}",
                    utilisateur_id=utilisateur_id
                )
            elif type_vente == 'carburant':
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=TypeOperationComptable.VENTE_CARBURANT,
                    reference_origine=reference_origine,
                    montant=montant,
                    compte_debit="512",  # Trésorerie
                    compte_credit="707",  # Ventes de carburant
                    libelle=f"Vente carburant #{vente_id}",
                    utilisateur_id=utilisateur_id
                )
        except Exception as e:
            # En cas d'erreur, on continue sans l'écriture comptable
            print(f"Erreur lors de l'enregistrement de l'écriture comptable pour la vente {vente_id}: {str(e)}")

        return mouvement

    @staticmethod
    def creer_mouvement_paiement_achat_carburant(
        db: Session,
        paiement_achat_id: uuid.UUID,
        utilisateur_id: uuid.UUID,
        commentaire: Optional[str] = None
    ) -> MouvementTresorerie:
        """
        Crée un mouvement de trésorerie pour un paiement d'achat carburant (type 'sortie').
        """
        from ...models.achat_carburant import PaiementAchatCarburant
        paiement = db.query(PaiementAchatCarburant).filter(
            PaiementAchatCarburant.id == paiement_achat_id
        ).first()

        if not paiement:
            raise InvalidTransactionException(f"Paiement d'achat carburant {paiement_achat_id} non trouvé")

        # Créer le mouvement de trésorerie
        mouvement = MouvementTresorerie(
            tresorerie_station_id=paiement.tresorerie_station_id,
            type_mouvement=TypeMouvement.SORTIE,
            montant=float(paiement.montant),
            date_mouvement=datetime.utcnow(),
            description=f"Paiement pour achat carburant (ID: {paiement.achat_carburant_id})",
            module_origine="achats_carburant",
            reference_origine=f"PAC-{paiement.id}",
            utilisateur_id=utilisateur_id,
            commentaire=commentaire
        )

        db.add(mouvement)
        db.commit()
        db.refresh(mouvement)

        # Enregistrer l'écriture comptable
        try:
            ComptabiliteManager.enregistrer_ecriture_double(
                db=db,
                type_operation=TypeOperationComptable.ACHAT_CARBURANT,
                reference_origine=f"PAC-{paiement.id}",
                montant=float(paiement.montant),
                compte_debit="607",  # Achats de carburant
                compte_credit="512",  # Trésorerie
                libelle=f"Paiement pour achat carburant #{paiement.achat_carburant_id}",
                utilisateur_id=utilisateur_id
            )
        except Exception as e:
            # En cas d'erreur, on continue sans l'écriture comptable
            print(f"Erreur lors de l'enregistrement de l'écriture comptable pour le paiement d'achat {paiement_achat_id}: {str(e)}")

        return mouvement
    
    @staticmethod
    def annuler_mouvement(
        db: Session,
        mouvement_id: uuid.UUID,
        utilisateur_id: uuid.UUID,
        motif: str
    ) -> MouvementTresorerie:
        """
        Annule un mouvement de trésorerie en créant un mouvement inverse.
        """
        mouvement_original = db.query(MouvementTresorerie).filter(
            MouvementTresorerie.id == mouvement_id
        ).first()

        if not mouvement_original:
            raise InvalidTransactionException(f"Mouvement {mouvement_id} non trouvé")

        if mouvement_original.statut == "annulé":
            raise InvalidTransactionException("Le mouvement est déjà annulé")

        # Créer un mouvement inverse
        type_inverse = TypeMouvement.SORTIE if mouvement_original.type_mouvement == TypeMouvement.ENTREE else TypeMouvement.ENTREE

        mouvement_annulation = MouvementTresorerie(
            tresorerie_station_id=mouvement_original.tresorerie_station_id,
            type_mouvement=type_inverse,
            montant=mouvement_original.montant,
            date_mouvement=datetime.utcnow(),
            description=f"Annulation du mouvement {mouvement_id} - {motif}",
            module_origine=mouvement_original.module_origine,
            reference_origine=f"AN-{mouvement_original.reference_origine}",  # Ajouter un préfixe pour identifier l'annulation
            utilisateur_id=utilisateur_id,
            mouvement_origine_id=mouvement_original.id,
            est_annule=True
        )

        # Mettre à jour le statut du mouvement original
        mouvement_original.statut = "annulé"
        mouvement_original.est_annule = True

        db.add(mouvement_annulation)
        db.commit()
        db.refresh(mouvement_annulation)

        # Enregistrer l'écriture comptable d'annulation
        try:
            # Déterminer le type d'opération pour l'annulation
            type_operation = None
            if "achats_boutique" in mouvement_original.module_origine:
                type_operation = TypeOperationComptable.ACHAT_BOUTIQUE
            elif "achats_carburant" in mouvement_original.module_origine:
                type_operation = TypeOperationComptable.ACHAT_CARBURANT
            elif "ventes_boutique" in mouvement_original.module_origine:
                type_operation = TypeOperationComptable.VENTE_BOUTIQUE
            elif "ventes_carburant" in mouvement_original.module_origine:
                type_operation = TypeOperationComptable.VENTE_CARBURANT
            else:
                type_operation = TypeOperationComptable.MOUVEMENT_TRESORERIE

            # Créer une écriture inverse pour annuler l'écriture originale
            # Si l'original était une sortie (débit), l'annulation sera un crédit
            if mouvement_original.type_mouvement == TypeMouvement.SORTIE:
                # Annulation d'une sortie = écriture inverse (débit -> crédit)
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=type_operation,
                    reference_origine=f"AN-{mouvement_original.reference_origine}",
                    montant=float(mouvement_original.montant),
                    compte_debit="512",  # Trésorerie
                    compte_credit="607",  # Achats de carburant ou marchandises
                    libelle=f"Annulation - Achat #{mouvement_original.reference_origine} - {motif}",
                    utilisateur_id=utilisateur_id
                )
            else:
                # Annulation d'une entrée = écriture inverse (crédit -> débit)
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=type_operation,
                    reference_origine=f"AN-{mouvement_original.reference_origine}",
                    montant=float(mouvement_original.montant),
                    compte_debit="707",  # Ventes de carburant ou marchandises
                    compte_credit="512",  # Trésorerie
                    libelle=f"Annulation - Vente #{mouvement_original.reference_origine} - {motif}",
                    utilisateur_id=utilisateur_id
                )
        except Exception as e:
            # En cas d'erreur, on continue sans l'écriture comptable
            print(f"Erreur lors de l'enregistrement de l'écriture comptable d'annulation pour le mouvement {mouvement_id}: {str(e)}")

        return mouvement_annulation
    
    @staticmethod
    def creer_mouvement_general(
        db: Session,
        tresorerie_station_id: uuid.UUID,
        type_mouvement: str,  # 'entrée' ou 'sortie'
        montant: float,
        utilisateur_id: uuid.UUID,
        description: str,
        module_origine: str,
        reference_origine: str,
        commentaire: Optional[str] = None,
        statut: str = "validé"
    ) -> MouvementTresorerie:
        """
        Crée un mouvement de trésorerie générique.
        """
        # Valider le type de mouvement
        if type_mouvement not in ["entrée", "sortie"]:
            raise InvalidTransactionException("Type de mouvement non valide")

        # Valider le solde avant transaction si c'est une sortie
        if type_mouvement == "sortie":
            MouvementTresorerieManager.valider_solde_avant_transaction(
                db, tresorerie_station_id, montant, TypeMouvement.SORTIE
            )

        # Créer le mouvement de trésorerie
        mouvement = MouvementTresorerie(
            tresorerie_station_id=tresorerie_station_id,
            type_mouvement=type_mouvement,
            montant=montant,
            date_mouvement=datetime.utcnow(),
            description=description,
            module_origine=module_origine,
            reference_origine=reference_origine,
            utilisateur_id=utilisateur_id,
            commentaire=commentaire,
            statut=statut
        )

        db.add(mouvement)
        db.commit()
        db.refresh(mouvement)

        # Enregistrer l'écriture comptable
        try:
            # Déterminer le type d'opération comptable basé sur le module d'origine
            type_operation = None
            compte_debit = ""
            compte_credit = ""

            if "achats_boutique" in module_origine:
                type_operation = TypeOperationComptable.ACHAT_BOUTIQUE
                compte_debit = "607"  # Achats de marchandises
                compte_credit = "512"  # Trésorerie
            elif "achats_carburant" in module_origine:
                type_operation = TypeOperationComptable.ACHAT_CARBURANT
                compte_debit = "607"  # Achats de carburant
                compte_credit = "512"  # Trésorerie
            elif "ventes_boutique" in module_origine:
                type_operation = TypeOperationComptable.VENTE_BOUTIQUE
                compte_debit = "512"  # Trésorerie
                compte_credit = "707"  # Ventes de marchandises
            elif "ventes_carburant" in module_origine:
                type_operation = TypeOperationComptable.VENTE_CARBURANT
                compte_debit = "512"  # Trésorerie
                compte_credit = "707"  # Ventes de carburant
            else:
                type_operation = TypeOperationComptable.MOUVEMENT_TRESORERIE
                # Pour les mouvements génériques, on suppose que c'est un mouvement de trésorerie
                if type_mouvement == "entrée":
                    compte_debit = "512"  # Trésorerie
                    compte_credit = "74"   # Subventions ou autres produits
                else:  # sortie
                    compte_debit = "65"    # Charges diverses
                    compte_credit = "512"  # Trésorerie

            ComptabiliteManager.enregistrer_ecriture_double(
                db=db,
                type_operation=type_operation,
                reference_origine=reference_origine,
                montant=montant,
                compte_debit=compte_debit,
                compte_credit=compte_credit,
                libelle=description,
                utilisateur_id=utilisateur_id
            )
        except Exception as e:
            # En cas d'erreur, on continue sans l'écriture comptable
            print(f"Erreur lors de l'enregistrement de l'écriture comptable pour le mouvement général {reference_origine}: {str(e)}")

        return mouvement

    @staticmethod
    def valider_solde_avant_transaction(
        db: Session,
        tresorerie_station_id: uuid.UUID,
        montant: float,
        type_mouvement: TypeMouvement
    ) -> bool:
        """
        Valide qu'une trésorerie a suffisamment de fonds pour une transaction de sortie.
        """
        if type_mouvement == TypeMouvement.SORTIE:
            from ..tresoreries.tresorerie_service import get_solde_tresorerie_station
            solde_actuel = get_solde_tresorerie_station(db, tresorerie_station_id)

            if solde_actuel < montant:
                raise InsufficientFundsException(
                    f"Solde insuffisant. Solde actuel: {solde_actuel}, Montant requis: {montant}"
                )

        return True