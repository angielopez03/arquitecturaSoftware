from flask import Blueprint, current_app, render_template, request

from backend.domain.model.entities import Measurement, Plant

plant_bp = Blueprint("plant_bp", __name__, template_folder="../../templates")


@plant_bp.route("/", methods=["GET"])
def index():
    """Muestra el formulario (View)."""
    return render_template("index.html")


@plant_bp.route("/evaluar", methods=["POST"])
def evaluar():
    """
    Controller: recibe la request HTTP, construye los objetos de dominio en el borde (RA6)
    y delega en el caso de uso DiagnosisService.
    """
    diagnosis_service = current_app.config["DIAGNOSIS_SERVICE"]

    plant = Plant(
        name=request.form["plant_name"],
        plant_type=request.form["plant_type"],
    )
    measurement = Measurement(
        humidity=float(request.form["humidity"]),
        light=float(request.form["light"]),
        temperature=float(request.form["temperature"]),
    )

    result = diagnosis_service.diagnose(plant, measurement)

    return render_template("result.html", result=result)
