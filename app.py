"""
Punto de entrada principal para Railway y ejecución local.
Mantiene compatibilidad con Procfile: web: gunicorn "app:create_app()"
"""
from backend.app import create_app
from backend.infrastructure.config import Config

cfg = Config.from_env()
app = create_app(cfg)

if __name__ == "__main__":
    app.run(host=cfg.host, port=cfg.port)
