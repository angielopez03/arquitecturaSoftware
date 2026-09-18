import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """
    Configuración centralizada de la aplicación (Capa de Infraestructura).
    Permite desacoplar rutas de archivos, puertos y orígenes CORS del código fuente.
    Soporta inyección dinámica desde variables de entorno (RA7, Railway).
    """
    csv_path: str
    port: int
    host: str
    cors_origins: str

    @classmethod
    def from_env(cls) -> "Config":
        # Directorio raíz del proyecto (dos niveles arriba de backend/infrastructure/)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        default_csv = os.path.join(base_dir, "data", "plant_ranges.csv")

        return cls(
            csv_path=os.environ.get("CSV_PATH", default_csv),
            port=int(os.environ.get("PORT", "5000")),
            host=os.environ.get("HOST", "0.0.0.0"),
            cors_origins=os.environ.get("CORS_ORIGINS", "*"),
        )
