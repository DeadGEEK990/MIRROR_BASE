from fastapi.templating import Jinja2Templates
import logging
from dotenv import load_dotenv
import os


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


TEMPLATES = Jinja2Templates(directory="frontend/templates")
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

