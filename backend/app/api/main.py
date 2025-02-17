from fastapi import FastAPI, HTTPException
import uvicorn

from ..service import users as service
from ..models import User
from ..errors import Duplicate, Missing
from .routes import users, login


app = FastAPI()
app.include_router(users.router)
app.include_router(login.router)
#uvicorn backend.app.api.main:app --reload


if __name__ == "__main__":
    uvicorn.run(app, reload=True)