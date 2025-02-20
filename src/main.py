import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI

import texto

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import setup_logging

# Configura el logging
setup_logging()
# Obtiene un logger para este módulo
logger = logging.getLogger(__name__)
logger.setLevel("INFO")
# Cargar .env
load_dotenv()

app = FastAPI()
app.include_router(texto.router)
