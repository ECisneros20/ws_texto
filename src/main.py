import logging
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import Constantes, setup_logging

# Configura el logging
setup_logging()
# Obtiene un logger para este módulo
logger = logging.getLogger(__name__)
logger.setLevel("INFO")
# Cargar .env
load_dotenv()

if __name__ == "__main__":
    print(Constantes.encoding.value)
    print(os.getenv("token_hf"))
    logger.info("Prueba info")
    logger.error("Prueba error")
    try:
        donuts_per_guest = 5 / 0
    except ZeroDivisionError:
        logger.exception("Prueba excepción")
