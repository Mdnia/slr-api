from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from database import database


from routers import auth, users

tags_metadata = [
    {
        "name": "switch",
        "description": "Endpoints used to control the SLR block state",
    },
    {
        "name": "users",
        "description": "Endpoints used to manage users",
    },
    {
        "name": "schedule",
        "description": "Endpoints used to manage the schedule",
    },
    {
        "name": "auth",
        "description": "Endpoints for authentication",
    },
]

app = FastAPI(
    version="0.1.0",
    title="SLR Switch Controller",
    description="Ny Ålesund Switch Controller",
    tags=tags_metadata,
    docs_url="/"
)

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/ping/", include_in_schema=False)
async def ping():
    return "pong"


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()