from fastapi.templating import Jinja2Templates


TEMPLATES = Jinja2Templates(directory="frontend/templates")
SECRET_KEY = "kek-and-kuk"
ALGORITHM = "HS256"