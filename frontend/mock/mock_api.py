"""
MOCK TEMPORAL - BORRAR ANTES DE LA ENTREGA FINAL.

Sirve para desarrollar el front sin esperar a que las ramas de dominio e
infraestructura esten integradas. No importa nada del proyecto: devuelve
JSON fijo con la forma exacta del contrato acordado en el commit 0.

Uso:  python3 frontend/mock/mock_api.py
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

TABLA = {
    "sansevieria": {"humedad": (40, 70, "%"), "luz": (200, 1500, "lux"), "temperatura": (18, 29, "C")},
    "helecho": {"humedad": (60, 85, "%"), "luz": (150, 800, "lux"), "temperatura": (16, 26, "C")},
    "suculenta": {"humedad": (10, 30, "%"), "luz": (800, 2500, "lux"), "temperatura": (15, 32, "C")},
}
LIMITES = {"humedad": (0, 100), "luz": (0, 200000), "temperatura": (-50, 80)}


def error(codigo, mensaje, detalle=None):
    return jsonify({"error": codigo, "mensaje": mensaje, "detalle": detalle or {}})


@app.after_request
def cors(res):
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Headers"] = "Content-Type"
    res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return res


@app.get("/api/v1/especies")
def especies():
    return jsonify([
        {"nombre": n, "rangos": {p: {"min": v[0], "max": v[1], "unidad": v[2]} for p, v in r.items()}}
        for n, r in TABLA.items()
    ])


@app.route("/api/v1/diagnosticos", methods=["POST", "OPTIONS"])
def diagnosticos():
    if request.method == "OPTIONS":
        return ("", 204)

    cuerpo = request.get_json(silent=True)
    if not isinstance(cuerpo, dict):
        return error("PARAMETRO_INVALIDO", "Se esperaba un cuerpo JSON valido.", {"campo": "cuerpo"}), 400

    especie = (cuerpo.get("especie") or "").strip().lower()
    if not especie:
        return error("PARAMETRO_INVALIDO", "El parametro 'especie' es invalido: ausente.", {"campo": "especie"}), 400
    if especie not in TABLA:
        return error("ESPECIE_NO_SOPORTADA", f"La especie '{especie}' no esta en la tabla.", {"especie": especie}), 404

    valores = {}
    for campo in ("humedad", "luz", "temperatura"):
        bruto = cuerpo.get(campo)
        if bruto is None or bruto == "":
            return error("PARAMETRO_INVALIDO", f"El parametro '{campo}' es invalido: ausente.", {"campo": campo}), 400
        try:
            v = float(str(bruto).replace(",", "."))
        except ValueError:
            return error("PARAMETRO_INVALIDO", f"El parametro '{campo}' es invalido: valor no numerico.", {"campo": campo}), 400
        mn, mx = LIMITES[campo]
        if not (mn <= v <= mx):
            return error("PARAMETRO_INVALIDO", f"El parametro '{campo}' es invalido: fuera del rango fisico.", {"campo": campo}), 400
        valores[campo] = v

    parametros, recomendaciones = [], []
    for campo, (mn, mx, unidad) in TABLA[especie].items():
        v = valores[campo]
        nivel = "OPTIMO" if mn <= v <= mx else ("BAJO" if v < mn else "ALTO")
        parametros.append({"nombre": campo, "valor": v, "unidad": unidad,
                           "rangoOptimo": [mn, mx], "estado": nivel})
        if nivel != "OPTIMO":
            recomendaciones.append(f"[mock] {campo} en nivel {nivel}.")

    fuera = len(recomendaciones)
    estado = "SALUDABLE" if fuera == 0 else ("EN_RIESGO" if fuera == 1 else "CRITICO")
    return jsonify({"especie": especie, "estado": estado,
                    "parametros": parametros, "recomendaciones": recomendaciones})


@app.errorhandler(404)
def no_encontrada(e):
    return error("RUTA_NO_ENCONTRADA", "La ruta solicitada no existe en esta API."), 404


if __name__ == "__main__":
    print("MOCK escuchando en http://localhost:5000  (borrar este archivo antes de entregar)")
    app.run(port=5000, debug=True)
