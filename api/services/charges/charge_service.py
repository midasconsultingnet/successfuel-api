from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional
from ...models.charge import Charge, PaiementCharge
from ...charges.schemas import (
    ChargeCreate,
    ChargeUpdate,
    PaiementChargeCreate,
    PaiementChargeUpdate
)


class ChargeService:
    @staticmethod
    def get_charge_by_id(db: Session, charge_id: str, compagnie_id: str) -> Optional[Charge]:
        return db.query(Charge).filter(
            Charge.id == charge_id,
            Charge.compagnie_id == compagnie_id
        ).first()

    @staticmethod
    def get_charges_by_company(
        db: Session, 
        compagnie_id: str, 
        skip: int = 0, 
        limit: int = 100,
        statut: Optional[str] = None
    ) -> List[Charge]:
        query = db.query(Charge).filter(Charge.compagnie_id == compagnie_id)
        
        if statut:
            query = query.filter(Charge.statut == statut)
            
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_charge(db: Session, charge_data: ChargeCreate, utilisateur_id: str) -> Charge:
        # Calcul du solde dû initial
        solde_du = charge_data.montant
        
        # Si un paiement est inclus avec la création
        if hasattr(charge_data, 'paiement_initial') and charge_data.paiement_initial:
            solde_du -= charge_data.paiement_initial.montant_paye
            
        charge = Charge(
            station_id=charge_data.station_id,
            categorie=charge_data.categorie,
            fournisseur_id=charge_data.fournisseur_id,
            date=charge_data.date,
            montant=charge_data.montant,
            description=charge_data.description,
            date_echeance=charge_data.date_echeance,
            statut="paye" if solde_du <= 0 else "en_cours_paiement" if solde_du < charge_data.montant else "prevu",
            methode_paiement=charge_data.methode_paiement,
            numero_piece_comptable=charge_data.numero_piece_comptable,
            utilisateur_id=utilisateur_id,
            solde_du=solde_du,
            compagnie_id=charge_data.compagnie_id,
            est_recurrente=charge_data.est_recurrente,
            frequence_recurrence=charge_data.frequence_recurrence,
            date_prochaine_occurrence=charge_data.date_prochaine_occurrence,
            seuil_alerte=charge_data.seuil_alerte,
            arret_compte=charge_data.arret_compte
        )
        db.add(charge)
        db.commit()
        db.refresh(charge)
        return charge

    @staticmethod
    def update_charge(db: Session, charge_id: str, charge_data: ChargeUpdate, compagnie_id: str) -> Optional[Charge]:
        charge = db.query(Charge).filter(
            Charge.id == charge_id,
            Charge.compagnie_id == compagnie_id
        ).first()
        
        if not charge:
            return None
            
        # Mettre à jour les champs avec les nouvelles valeurs
        for field, value in charge_data.dict(exclude_unset=True).items():
            setattr(charge, field, value)
            
        # Recalculer le statut en fonction du solde dû
        if charge.solde_du <= 0:
            charge.statut = "paye"
        elif charge.solde_du < charge.montant:
            charge.statut = "en_cours_paiement"
        elif charge.date_echeance and charge.date_echeance < datetime.now():
            charge.statut = "echu"
        else:
            charge.statut = "prevu"
            
        db.commit()
        db.refresh(charge)
        return charge

    @staticmethod
    def delete_charge(db: Session, charge_id: str, compagnie_id: str) -> bool:
        charge = db.query(Charge).filter(
            Charge.id == charge_id,
            Charge.compagnie_id == compagnie_id
        ).first()
        
        if not charge:
            return False
            
        db.delete(charge)
        db.commit()
        return True

    @staticmethod
    def create_paiement_charge(
        db: Session, 
        paiement_data: PaiementChargeCreate, 
        utilisateur_id: str
    ) -> PaiementCharge:
        paiement = PaiementCharge(
            charge_id=paiement_data.charge_id,
            date_paiement=paiement_data.date_paiement or datetime.now(),
            montant_paye=paiement_data.montant_paye,
            methode_paiement=paiement_data.methode_paiement,
            reference_paiement=paiement_data.reference_paiement,
            utilisateur_id=utilisateur_id,
            commentaire=paiement_data.commentaire,
            compagnie_id=paiement_data.compagnie_id
        )
        db.add(paiement)
        
        # Mettre à jour le solde de la charge associée
        charge = db.query(Charge).filter(Charge.id == paiement_data.charge_id).first()
        if charge:
            charge.solde_du -= paiement_data.montant_paye
            
            # Mettre à jour le statut de la charge en fonction du solde
            if charge.solde_du <= 0:
                charge.statut = "paye"
            elif charge.solde_du < charge.montant:
                charge.statut = "en_cours_paiement"
                
            db.add(charge)
        
        db.commit()
        db.refresh(paiement)
        return paiement

    @staticmethod
    def get_paiements_for_charge(
        db: Session, 
        charge_id: str, 
        compagnie_id: str
    ) -> List[PaiementCharge]:
        return db.query(PaiementCharge).filter(
            PaiementCharge.charge_id == charge_id,
            PaiementCharge.compagnie_id == compagnie_id
        ).all()
    
    @staticmethod
    def gerer_charges_recurrentes(db: Session, compagnie_id: str):
        """Génère les charges récurrentes en fonction de leur fréquence"""
        today = date.today()
        
        # Trouver toutes les charges récurrentes dont la date de prochaine occurrence est aujourd'hui ou antérieure
        charges_a_actualiser = db.query(Charge).filter(
            Charge.compagnie_id == compagnie_id,
            Charge.est_recurrente == True,
            Charge.date_prochaine_occurrence <= today
        ).all()
        
        for charge in charges_a_actualiser:
            # Créer une nouvelle occurrence de la charge
            nouvelle_charge = Charge(
                station_id=charge.station_id,
                categorie=charge.categorie,
                fournisseur_id=charge.fournisseur_id,
                date=datetime.now(),
                montant=charge.montant,
                description=charge.description,
                date_echeance=charge.date_echeance,
                statut="prevu",
                methode_paiement=charge.methode_paiement,
                numero_piece_comptable=charge.numero_piece_comptable,
                utilisateur_id=charge.utilisateur_id,
                solde_du=charge.montant,
                compagnie_id=charge.compagnie_id,
                est_recurrente=charge.est_recurrente,
                frequence_recurrence=charge.frequence_recurrence,
                seuil_alerte=charge.seuil_alerte,
                arret_compte=charge.arret_compte
            )
            db.add(nouvelle_charge)
            
            # Mettre à jour la date de prochaine occurrence en fonction de la fréquence
            if charge.frequence_recurrence == "quotidienne":
                charge.date_prochaine_occurrence = today + timedelta(days=1)
            elif charge.frequence_recurrence == "hebdomadaire":
                charge.date_prochaine_occurrence = today + timedelta(weeks=1)
            elif charge.frequence_recurrence == "mensuelle":
                # Calculer le même jour du mois suivant
                try:
                    charge.date_prochaine_occurrence = today.replace(month=today.month + 1)
                except ValueError:
                    # Gérer le cas où le mois suivant n'a pas le même jour (ex: 31 janvier -> février)
                    charge.date_prochaine_occurrence = (today.replace(day=28) + timedelta(days=4)).replace(day=today.day)
            elif charge.frequence_recurrence == "annuelle":
                charge.date_prochaine_occurrence = today.replace(year=today.year + 1)
            
            db.add(charge)
        
        db.commit()


class SeuilAlerteService:
    @staticmethod
    def verifier_seuils_alerte(db: Session, compagnie_id: str):
        """Vérifie si des charges dépassent les seuils d'alerte configurables"""
        charges = db.query(Charge).filter(
            Charge.compagnie_id == compagnie_id
        ).all()
        
        alertes = []
        for charge in charges:
            if charge.seuil_alerte and charge.montant > charge.seuil_alerte:
                alertes.append({
                    "charge_id": charge.id,
                    "categorie": charge.categorie,
                    "montant": charge.montant,
                    "seuil": charge.seuil_alerte,
                    "message": f"La charge {charge.categorie} dépasse le seuil d'alerte de {charge.seuil_alerte}"
                })
        
        return alertes


class GestionEcheancesService:
    @staticmethod
    def verifier_echeances(db: Session, compagnie_id: str, jours_avant_rappel: int = 7):
        """Vérifie les charges en échéance et génère les rappels"""
        date_limite = date.today() + timedelta(days=jours_avant_rappel)
        
        charges_en_echeance = db.query(Charge).filter(
            Charge.compagnie_id == compagnie_id,
            Charge.date_echeance.isnot(None),
            Charge.date_echeance <= date_limite,
            Charge.statut != "paye"
        ).all()
        
        rappels = []
        for charge in charges_en_echeance:
            jours_restants = (charge.date_echeance.date() - date.today()).days
            rappels.append({
                "charge_id": charge.id,
                "categorie": charge.categorie,
                "date_echeance": charge.date_echeance,
                "jours_restants": jours_restants,
                "message": f"Rappel: La charge {charge.categorie} arrive à échéance dans {jours_restants} jours"
            })
        
        return rappels


class SystemeArretCompteService:
    @staticmethod
    def mettre_a_jour_arrets_compte(db: Session, compagnie_id: str):
        """Met à jour les arrêts de compte en fonction des charges impayées"""
        # Trouver les tiers avec des charges en retard de paiement
        date_limite = date.today() - timedelta(days=30)  # Par exemple, 30 jours de retard
        
        charges_impayees = db.query(Charge).filter(
            Charge.compagnie_id == compagnie_id,
            Charge.date_echeance < date_limite,
            Charge.statut.in_(["echu", "en_cours_paiement"]),
            Charge.solde_du > 0
        ).all()
        
        # Marquer les fournisseurs concernés avec un arrêt de compte
        fournisseurs_a_arreter = set()
        for charge in charges_impayees:
            if charge.fournisseur_id:
                fournisseurs_a_arreter.add(charge.fournisseur_id)
        
        return list(fournisseurs_a_arreter)