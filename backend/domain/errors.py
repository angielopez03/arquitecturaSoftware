class ErrorDeDominio(Exception):
    """Error base para reglas incumplidas del dominio."""


class ParametroInvalido(ErrorDeDominio):
    def __init__(self, campo: str, motivo: str):
        self.campo = campo
        self.motivo = motivo
        super().__init__(f"{campo}: {motivo}")


class ValorFisicamenteImposible(ParametroInvalido):
    def __init__(self, campo: str, valor, motivo: str):
        self.valor = valor
        super().__init__(campo, motivo)


class EspecieNoSoportada(ErrorDeDominio):
    def __init__(self, especie: str):
        self.especie = especie
        super().__init__(f"especie no soportada: {especie}")