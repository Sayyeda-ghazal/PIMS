from fastapi import FastAPI
import Users_auth, PIMS_auth
from database import Base, engine

app = FastAPI()

app.include_router(Users_auth.router)  
app.include_router(PIMS_auth.router)

Base.metadata.create_all(engine)