from typing import List, Union

from database import (db_delete_user, query_roles, query_all_users,
                      query_user, update_existing_user, write_new_user)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User
from passlib.hash import pbkdf2_sha256

from .auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/users", tags=["users"])

