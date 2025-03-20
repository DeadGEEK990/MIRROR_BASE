from fastapi.templating import Jinja2Templates
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


TEMPLATES = Jinja2Templates(directory="frontend/templates")
SECRET_KEY = "kek-and-kuk"
ALGORITHM = "HS256"

