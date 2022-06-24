import logging
import os
import uuid
from datetime import datetime, timedelta

import jwt
from database import query_user
# from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import JWT, User
from passlib.hash import pbkdf2_sha256

log = logging.getLogger("SwitchController")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=['authentication'])

# load_dotenv()
# JWT_SECRET = str(os.getenv("JWT_SECRET"))
# JWT_SECRET = "8a108929-0b56-4132-94d9-4c413135c04b"
JWT_SECRET = str(uuid.uuid4())
JWT_ALGORITHM = str(os.getenv("JWT_ALGORITHM"))
JWT_EXP_DELTA_SECONDS = int(os.getenv("JWT_EXP_DELTA_SECONDS"))

JWT_TOKEN_BAN_LIST = []


# Support functions
async def decode_token(token) -> dict:
    """Decode and verify jwt token
    an invalid token will throw an exception"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials {err}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def create_access_token(user: User) -> str:
    """Create JWT token"""
    payload = {
        'sub': user.user_name,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


async def create_refresh_token(user: User) -> str:
    """Create JWT token"""
    payload = {
        'sub': user.user_name,
        'typ': 'refresh',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


@ router.post("/login", response_model=JWT)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """## Login \n
    To log in, submit the user name and password as a form via POST.
    The endpoint will return a JWT access token and a refresh token for the
    user. And for each request, the access token should be passed in the
    authentication header. \n
    You can check the access token expiration by decoding the JWT and reading
    the payload. When or before the access token expires, request a new one by
    submitting the refresh token to the refresh endpoint.
    """
    # TODO: protect from timing attacks with secrets.compare_digest()
    user_dict = await query_user(form_data.username)
    user = User(**user_dict)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not pbkdf2_sha256.verify(form_data.password,
                                user_dict["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)

    response = JWT(access_token=access_token, refresh_token=refresh_token)

    log.info(f"User {user.user_name} logged in")

    return response


@router.post("/refresh", response_model=JWT)
async def refresh_user_token(token: str = Depends(oauth2_scheme)):
    """## Refresh JWT \n
    Use the refresh token to get a new access token and a new refresh token.
    A refresh token is only valid one time. \n
    If you submit a valid refresh token and get a 401 Unauthorized, make sure
    to log the exception! The server could have gone down, or someone may have
    stolen your refresh token!"""

    # Decode token will throw an exception if token is invalid i.e. expired
    payload = await decode_token(token)
    if payload['typ'] != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token in JWT_TOKEN_BAN_LIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    JWT_TOKEN_BAN_LIST.append(token)

    user_dict = await query_user(payload['sub'])
    user = User(**user_dict)
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)

    response = JWT(access_token=access_token, refresh_token=refresh_token)

    return response
