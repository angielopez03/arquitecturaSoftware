"""Capa de Dominio (RA3, RA4)."""
from backend.domain.errors import (
    ErrorDominio,
    EspecieNoSoportada,
    UnknownPlantType,
    ValorFisicamenteImposible,
    PhysicallyImpossibleValue,
    ParametroInvalido,
    InvalidParameter,
)

__all__ = [
    "ErrorDominio",
    "EspecieNoSoportada",
    "UnknownPlantType",
    "ValorFisicamenteImposible",
    "PhysicallyImpossibleValue",
    "ParametroInvalido",
    "InvalidParameter",
]
