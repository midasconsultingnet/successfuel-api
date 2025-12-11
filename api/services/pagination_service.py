from typing import List, TypeVar, Type, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
from ..utils.pagination import PaginatedResponse
from ..utils.filters import BaseFilterParams

T = TypeVar('T')


def apply_filters_and_pagination(
    db: Session,
    model: Type[T],
    filter_params: BaseFilterParams,
    query_filters: Optional[List[Any]] = None
) -> PaginatedResponse[T]:
    """
    Applique les filtres, le tri et la pagination à une requête SQLAlchemy
    
    :param db: Session SQLAlchemy
    :param model: Modèle SQLAlchemy à requêter
    :param filter_params: Paramètres de filtre et de pagination
    :param query_filters: Filtres supplémentaires à appliquer à la requête
    :return: Réponse paginée
    """
    # Construction de la requête de base
    query = db.query(model)
    
    # Application des filtres supplémentaires
    if query_filters:
        query = query.filter(and_(*query_filters))
    
    # Application des filtres génériques (recherche textuelle)
    if filter_params.q:
        # Cette fonctionnalité nécessiterait une logique spécifique selon les champs
        # à rechercher dans chaque modèle
        search_filters = []
        # Ici, nous devrions construire dynamiquement une recherche sur les champs textuels
        # du modèle, ce qui dépend de chaque modèle spécifique
        # Pour l'instant, nous n'implémentons pas cette fonctionnalité
        pass
    
    # Application du tri
    if filter_params.sort_by:
        sort_field = getattr(model, filter_params.sort_by, None)
        if sort_field:
            if filter_params.sort_order == 'desc':
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())
    
    # Calcul du total avant pagination
    total = query.count()
    
    # Application de la pagination
    items = query.offset(filter_params.skip).limit(filter_params.limit).all()
    
    # Détermination s'il y a plus d'éléments
    has_more = (filter_params.skip + filter_params.limit) < total
    
    return PaginatedResponse(
        items=items,
        total=total,
        skip=filter_params.skip,
        limit=filter_params.limit,
        has_more=has_more
    )


def apply_specific_filters(
    query,
    filter_params: BaseFilterParams,
    model
):
    """
    Applique les filtres spécifiques d'un modèle à une requête SQLAlchemy
    
    :param query: Requête SQLAlchemy à modifier
    :param filter_params: Paramètres de filtre spécifique à un modèle
    :param model: Modèle SQLAlchemy
    :return: Requête SQLAlchemy modifiée
    """
    # Application des filtres spécifiques en fonction des attributs du filter_params
    for field, value in filter_params.dict(exclude={'skip', 'limit', 'sort_by', 'sort_order', 'q'}).items():
        if value is not None:
            model_attr = getattr(model, field, None)
            if model_attr is not None:
                query = query.filter(model_attr == value)
    
    return query