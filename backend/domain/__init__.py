"""Capa de Dominio (RA3, RA4)."""
from backend.domain.errors import (
    ErrorDeDominio,
    ErrorDominio,
    EspecieNoSoportada,
    UnknownPlantType,
    ValorFisicamenteImposible,
    PhysicallyImpossibleValue,
    ParametroInvalido,
    InvalidParameter,
)

__all__ = [
    "ErrorDeDominio",
    "ErrorDominio",
    "EspecieNoSoportada",
    "UnknownPlantType",
    "ValorFisicamenteImposible",
    "PhysicallyImpossibleValue",
    "ParametroInvalido",
    "InvalidParameter",
]
