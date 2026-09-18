"""
DTO de salida (capa de presentacion).

Traduce objetos del dominio al contrato JSON del Anexo A. El dominio no
sabe que existe JSON: si manana el contrato cambia, solo cambia este archivo.
"""

UNIDADES = {"humedad": "%", "luz": "lux", "temperatura": "C"}


def diagnostico_a_json(diagnostico) -> dict:
    return {
        "especie": diagnostico.especie,
        "estado": diagnostico.estado.value,
        "parametros": [
            {
                "nombre": p.nombre,
                "valor": p.valor,
                "unidad": UNIDADES.get(p.nombre, ""),
                "rangoOptimo": [p.rango.minimo, p.rango.maximo],
                "estado": p.nivel.value,
            }
            for p in diagnostico.parametros
        ],
        "recomendaciones": list(diagnostico.recomendaciones),
    }


def especies_a_json(especies) -> list:
    return [
        {
            "nombre": e.nombre,
            "rangos": {
                nombre: {
                    "min": rango.minimo,
                    "max": rango.maximo,
                    "unidad": UNIDADES.get(nombre, ""),
                }
                for nombre, rango in e.rangos.items()
            },
        }
        for e in especies
    ]
