"""Excepciones de la capa de dominio (RA4).

No tienen conocimiento de códigos de estado HTTP ni transporte.
La capa de presentación (controladores / error handlers) se encarga de traducirlas
a códigos de estado y respuestas JSON uniformes (RF6).
"""


class ErrorDeDominio(Exception):
    """Error base para reglas incumplidas del dominio."""
    pass


# Alias para compatibilidad con código existente
ErrorDominio = ErrorDeDominio


class ParametroInvalido(ErrorDeDominio):
    """
    Se lanza cuando un parámetro requerido no es válido o está incompleto (RF6).
    """
    def __init__(self, campo: str, motivo: str):
        self.campo = campo
        self.motivo = motivo
        super().__init__(f"Parámetro inválido '{campo}': {motivo}")


class ValorFisicamenteImposible(ParametroInvalido):
    """
    Se lanza cuando una medición física excede los límites posibles terrestres (RF6).
    Hereda de ParametroInvalido para cumplir con la jerarquía de validaciones.
    """
    def __init__(self, campo: str, valor: float, motivo: str):
        self.valor = valor
        super().__init__(campo, motivo)


class EspecieNoSoportada(ErrorDeDominio):
    """
    Se lanza cuando se solicitan rangos de referencia para una especie
    que no se encuentra en el catálogo del repositorio (H-06 / RF6).
    """
    def __init__(self, especie: str):
        self.especie = especie
        super().__init__(f"La especie '{especie}' no está soportada en el sistema.")


# Alias en inglés para compatibilidad
UnknownPlantType = EspecieNoSoportada
PhysicallyImpossibleValue = ValorFisicamenteImposible
InvalidParameter = ParametroInvalido
