from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from utils.authentication import manager
from utils.pydantic_models import UserLogin
from utils.db_utils import select_all_driving_data, select_all_driving_stats, select_all_driving_data_by_timestamp, select_all_driving_stats_by_timestamp
from fastapi.encoders import jsonable_encoder

router = APIRouter()


@router.get("/driving_data", response_class=JSONResponse)
def get_all_driving_data(request: Request, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_data = select_all_driving_data(user.user_id)
    response = {}
    for data in driving_data:
        response[data.timestamp_unix_ms] = jsonable_encoder(data)
    return JSONResponse(content=response)


@router.get("/driving_stats", response_class=JSONResponse)
def get_all_driving_stats(request: Request, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_stats = select_all_driving_stats(user.user_id)
    response = {}
    for data in driving_stats:
        response[data.timestamp_unix_ms] = jsonable_encoder(data)
    return JSONResponse(content=response)


@router.get("/driving_data/{start}/{end}", response_class=JSONResponse)
def get_all_driving_data_by_timestamp(request: Request, start: int, end: int, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_data = select_all_driving_data_by_timestamp(user.user_id, start, end)
    response = {}
    for data in driving_data:
        response[data.timestamp_unix_ms] = jsonable_encoder(data)
    return JSONResponse(content=response)


@router.get("/driving_stats/{start}/{end}", response_class=JSONResponse)
def get_all_driving_stats_by_timestamp(request: Request, start: int, end: int, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_stats = select_all_driving_stats_by_timestamp(user.user_id, start, end)
    response = {}
    for data in driving_stats:
        response[data.timestamp_unix_ms] = jsonable_encoder(data)
    return JSONResponse(content=response)
