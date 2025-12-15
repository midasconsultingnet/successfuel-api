from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field
from fastapi import Query


T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Paramètres de base pour la pagination
    """
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer")
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum d'éléments à retourner")


class SortParams(BaseModel):
    """
    Paramètres pour le tri
    """
    sort_by: Optional[str] = Query(None, description="Champ sur lequel trier")
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Ordre de tri")


class BaseFilterParams(PaginationParams, SortParams):
    """
    Paramètres de base combinant pagination et tri
    """
    q: Optional[str] = Query(None, description="Recherche textuelle générique")


class FilterField(BaseModel):
    """
    Représente un champ de filtre avec son opérateur et sa valeur
    """
    field: str
    operator: str = "eq"  # eq, neq, gt, gte, lt, lte, like, in
    value: str


class AdvancedFilterParams(BaseFilterParams):
    """
    Paramètres de filtre avancés
    """
    filters: Optional[List[FilterField]] = Field(None, description="Filtres avancés")
    search_fields: Optional[List[str]] = Field(None, description="Champs sur lesquels effectuer la recherche textuelle")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Réponse paginée contenant une liste d'éléments avec des métadonnées de pagination
    """
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool = Field(description="Indique s'il y a plus d'éléments disponibles")

    model_config = {'from_attributes': True}