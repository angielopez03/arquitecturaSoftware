from flask import Blueprint, render_template, request, current_app

from backend.domain.model.entities import Plant

plant_bp = Blueprint("plant_bp", __name__, template_folder="../templates")


@plant_bp.route("/", methods=["GET"])
def index():
    """Muestra el formulario (View)."""
    return render_template("index.html")


@plant_bp.route("/evaluar", methods=["POST"])
def evaluar():
    """
    Controller (MVC): recibe la request HTTP, delega en los
    servicios/repositorios inyectados, y renderiza la vista.
    No contiene logica de negocio.
    """
    input_provider = current_app.config["INPUT_PROVIDER"]
    diagnosis_service = current_app.config["DIAGNOSIS_SERVICE"]

    plant = Plant(
        name=request.form["plant_name"],
        plant_type=request.form["plant_type"],
    )
    measurement = input_provider.get_measurement(request.form)

    result = diagnosis_service.diagnose(plant, measurement)

    return render_template("result.html", result=result)
