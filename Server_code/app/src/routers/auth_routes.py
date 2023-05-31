from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

from utils.authentication import manager, get_password_hash, verify_password
from utils.pydantic_models import User, UserInDB, UserLogin, UserRegistration
from utils.db_utils import create_user, select_user_by_username, delete_user


router = APIRouter()

@router.post("/token", response_class=JSONResponse)
def login(data: OAuth2PasswordRequestForm = Depends()) -> JSONResponse:
    username = data.username
    password = data.password

    user = select_user_by_username(username)
    if user is None:
        raise InvalidCredentialsException
    elif not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(data={"sub": username})
    response = JSONResponse({"message": "Success"})
    manager.set_cookie(response, access_token)
    return response


@router.post("/register", response_class=JSONResponse)
def register(user: UserRegistration) -> JSONResponse:

    db_result = create_user(user)
    if not db_result:
        return JSONResponse({"message": "Failed to create user"}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse({"message": "Success"})


@router.get("/logout", response_class=JSONResponse)
def logout() -> JSONResponse:
    response = JSONResponse({"message": "Success"})
    manager.set_cookie(response, "")
    return response


@router.post("/login", response_class=JSONResponse)
def login(user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"}, status_code=status.HTTP_401_UNAUTHORIZED)
    return JSONResponse({"message": "Success"})


@router.delete("/delete_user", response_class=JSONResponse)
def delete_account(user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"}, status_code=status.HTTP_401_UNAUTHORIZED)
    db_result = delete_user(user.username)
    if not db_result:
        return JSONResponse({"message": "Failed to delete user"}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse({"message": "Success"})