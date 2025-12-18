from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .journal_comptable_schemas import EcritureComptable, JournalComptableResponse
from fastapi import HTTPException


def get_journal_comptable(
    db: Session, 
    date_debut: str, 
    date_fin: str
) -> JournalComptableResponse:
    """
    Générer le journal comptable entre deux dates
    """
    try:
        date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide")
    
    items: List[EcritureComptable] = []
    total_debit = 0.0
    total_credit = 0.0
    
    # 1. Générer les écritures pour les ventes
    from ..models.vente import Vente
    ventes = db.query(Vente).filter(
        Vente.date >= date_debut_obj,
        Vente.date <= date_fin_obj
    ).all()

    for vente in ventes:
        montant = float(vente.montant_total or 0)

        # Écriture de débit : Banque/Client -> Produits vendus
        debit_item = EcritureComptable(
            id=vente.id,
            date_ecriture=vente.date,
            libelle=f"Vente #{vente.numero_piece_comptable or vente.id}",
            compte_debit="57 - Banque",  # Simplifié car le modèle Vente ne contient pas methode_paiement
            compte_credit="70 - Ventes de produits",
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(vente.id),
            module_origine="ventes",
            details={
                "numero_piece_comptable": vente.numero_piece_comptable,
                "client": vente.client.nom if vente.client else "N/A"
            }
        )
        items.append(debit_item)
        total_debit += montant

        # Écriture de crédit : Produits vendus <- Banque/Client
        credit_item = EcritureComptable(
            id=vente.id,
            date_ecriture=vente.date,
            libelle=f"Vente #{vente.numero_piece_comptable or vente.id}",
            compte_debit="70 - Ventes de produits",
            compte_credit="57 - Banque",  # Simplifié car le modèle Vente ne contient pas methode_paiement
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(vente.id),
            module_origine="ventes",
            details={
                "numero_piece_comptable": vente.numero_piece_comptable,
                "client": vente.client.nom if vente.client else "N/A"
            }
        )
        items.append(credit_item)
        total_credit += montant
    
    # 2. Générer les écritures pour les achats
    from ..models.achat import Achat
    achats = db.query(Achat).filter(
        Achat.date >= date_debut_obj,
        Achat.date <= date_fin_obj
    ).all()

    for achat in achats:
        montant = float(achat.montant_total or 0)

        # Écriture de débit : Stock/Fourniture -> Fournisseur/Banque
        debit_item = EcritureComptable(
            id=achat.id,
            date_ecriture=achat.date,
            libelle=f"Achat #{achat.numero_piece_comptable or achat.id}",
            compte_debit="37 - Stock" if achat.type == "carburant" else "60 - Achats de stock",
            compte_credit="40 - Fournisseurs",  # Simplifié car le modèle Achat ne contient pas methode_paiement
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(achat.id),
            module_origine="achats",
            details={
                "numero_piece_comptable": achat.numero_piece_comptable,
                "fournisseur": achat.fournisseur.nom if achat.fournisseur else "N/A"
            }
        )
        items.append(debit_item)
        total_debit += montant

        # Écriture de crédit : Fournisseur/Banque <- Stock/Fourniture
        credit_item = EcritureComptable(
            id=achat.id,
            date_ecriture=achat.date,
            libelle=f"Achat #{achat.numero_piece_comptable or achat.id}",
            compte_debit="40 - Fournisseurs",  # Simplifié car le modèle Achat ne contient pas methode_paiement
            compte_credit="37 - Stock" if achat.type == "carburant" else "60 - Achats de stock",
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(achat.id),
            module_origine="achats",
            details={
                "numero_piece_comptable": achat.numero_piece_comptable,
                "fournisseur": achat.fournisseur.nom if achat.fournisseur else "N/A"
            }
        )
        items.append(credit_item)
        total_credit += montant
    
    # 3. Générer les écritures pour les charges
    from ..models.charge import Charge
    charges = db.query(Charge).filter(
        Charge.date >= date_debut_obj,
        Charge.date <= date_fin_obj
    ).all()

    for charge in charges:
        montant = float(charge.montant or 0)

        # Écriture de débit : Charges -> Fournisseur/Banque
        debit_item = EcritureComptable(
            id=charge.id,
            date_ecriture=charge.date,
            libelle=f"Charge: {charge.description}",
            compte_debit=f"6{charge.categorie[:2]} - {charge.categorie}" if charge.categorie else "65 - Autres charges",
            compte_credit="40 - Fournisseurs" if charge.fournisseur else "57 - Banque",
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(charge.id),
            module_origine="charges",
            details={
                "categorie": charge.categorie,
                "fournisseur": charge.fournisseur if charge.fournisseur else "N/A"
            }
        )
        items.append(debit_item)
        total_debit += montant

        # Écriture de crédit : Fournisseur/Banque <- Charges
        credit_item = EcritureComptable(
            id=charge.id,
            date_ecriture=charge.date,
            libelle=f"Charge: {charge.description}",
            compte_debit="40 - Fournisseurs" if charge.fournisseur else "57 - Banque",
            compte_credit=f"6{charge.categorie[:2]} - {charge.categorie}" if charge.categorie else "65 - Autres charges",
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(charge.id),
            module_origine="charges",
            details={
                "categorie": charge.categorie,
                "fournisseur": charge.fournisseur if charge.fournisseur else "N/A"
            }
        )
        items.append(credit_item)
        total_credit += montant
    
    # 4. Générer les écritures pour les salaires
    from ..models.salaire import Salaire
    salaires = db.query(Salaire).filter(
        Salaire.date_paiement >= date_debut_obj,
        Salaire.date_paiement <= date_fin_obj
    ).all()

    for salaire in salaires:
        montant = float(salaire.montant_total or 0)

        # Écriture de débit : Charges de personnel -> Banque
        debit_item = EcritureComptable(
            id=salaire.id,
            date_ecriture=salaire.date_paiement,
            libelle=f"Salaire: {salaire.employe.nom if salaire.employe else 'N/A'}",
            compte_debit="62 - Charges de personnel",
            compte_credit="57 - Banque",
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(salaire.id),
            module_origine="salaires",
            details={
                "employe": salaire.employe.nom if salaire.employe else "N/A",
                "periode": salaire.periode
            }
        )
        items.append(debit_item)
        total_debit += montant

        # Écriture de crédit : Banque <- Charges de personnel
        credit_item = EcritureComptable(
            id=salaire.id,
            date_ecriture=salaire.date_paiement,
            libelle=f"Salaire: {salaire.employe.nom if salaire.employe else 'N/A'}",
            compte_debit="57 - Banque",
            compte_credit="62 - Charges de personnel",
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(salaire.id),
            module_origine="salaires",
            details={
                "employe": salaire.employe.nom if salaire.employe else "N/A",
                "periode": salaire.periode
            }
        )
        items.append(credit_item)
        total_credit += montant
    
    # 5. Générer les écritures pour les mouvements de trésorerie
    from ..models.tresorerie import MouvementTresorerie
    mouvements = db.query(MouvementTresorerie).filter(
        MouvementTresorerie.date_mouvement >= date_debut_obj,
        MouvementTresorerie.date_mouvement <= date_fin_obj
    ).all()

    for mouvement in mouvements:
        montant = float(mouvement.montant or 0)

        # Déterminer les comptes en fonction du type de mouvement
        if mouvement.type_mouvement == "entrée":
            compte_debit = "57 - Banque"  # ou le compte de trésorerie approprié
            compte_credit = "70 - Ventes" if "vente" in mouvement.module_origine else "74 - Subventions reçues"
        else:  # sortie
            compte_debit = "65 - Autres charges" if "charge" in mouvement.module_origine else "60 - Achats"
            compte_credit = "57 - Banque"  # ou le compte de trésorerie approprié

        # Écriture de débit
        debit_item = EcritureComptable(
            id=mouvement.id,
            date_ecriture=mouvement.date_mouvement,
            libelle=f"Mouvement trésorerie: {mouvement.description}",
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(mouvement.id),
            module_origine="trésorerie",
            details={
                "type_mouvement": mouvement.type_mouvement,
                "module_origine": mouvement.module_origine
            }
        )
        items.append(debit_item)
        total_debit += montant

        # Écriture de crédit
        credit_item = EcritureComptable(
            id=mouvement.id,
            date_ecriture=mouvement.date_mouvement,
            libelle=f"Mouvement trésorerie: {mouvement.description}",
            compte_debit=compte_credit,
            compte_credit=compte_debit,
            montant=montant,
            devise="XOF",  # Champ devise n'existe pas dans le modèle
            reference=str(mouvement.id),
            module_origine="trésorerie",
            details={
                "type_mouvement": mouvement.type_mouvement,
                "module_origine": mouvement.module_origine
            }
        )
        items.append(credit_item)
        total_credit += montant
    
    # Trier par date d'écriture
    items.sort(key=lambda x: x.date_ecriture)
    
    response = JournalComptableResponse(
        date_debut=date_debut_obj,
        date_fin=date_fin_obj,
        items=items,
        total_items=len(items),
        total_debit=total_debit,
        total_credit=total_credit
    )
    
    # Vérifier que le total des débits égale le total des crédits (équilibre comptable)
    if abs(total_debit - total_credit) > 0.01:  # Tolérer une petite différence due aux arrondis
        print(f"ATTENTION: Le journal comptable n'est pas équilibré. Débit: {total_debit}, Crédit: {total_credit}")
    
    return response