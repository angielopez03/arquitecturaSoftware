"""Excepciones de la capa de dominio.
No tienen conocimiento de códigos de estado HTTP ni transporte (RA4).
La capa de presentación (controladores / error handlers) se encarga de traducirlas
a códigos de estado y respuestas JSON uniformes (RF6).
"""


class ErrorDominio(Exception):
    """Clase base para todos los errores de la capa de dominio."""
    pass


class EspecieNoSoportada(ErrorDominio):
    """
    Se lanza cuando se solicitan rangos de referencia para una especie
    que no se encuentra en el catálogo del repositorio (H-06 / RF6).
    """
    def __init__(self, especie: str):
        self.especie = especie
        super().__init__(f"La especie '{especie}' no está soportada en el sistema.")


class ValorFisicamenteImposible(ErrorDominio):
    """
    Se lanza cuando una medición física excede los límites posibles terrestres (RF6).
    """
    def __init__(self, campo: str, valor: float, motivo: str):
        self.campo = campo
        self.valor = valor
        self.motivo = motivo
        super().__init__(f"Valor físicamente imposible para '{campo}': {valor}. {motivo}")


class ParametroInvalido(ErrorDominio):
    """
    Se lanza cuando un parámetro requerido no es válido o está incompleto (RF6).
    """
    def __init__(self, campo: str, motivo: str):
        self.campo = campo
        self.motivo = motivo
        super().__init__(f"Parámetro inválido '{campo}': {motivo}")


# Alias en inglés para compatibilidad
UnknownPlantType = EspecieNoSoportada
PhysicallyImpossibleValue = ValorFisicamenteImposible
InvalidParameter = ParametroInvalido
