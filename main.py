from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

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

