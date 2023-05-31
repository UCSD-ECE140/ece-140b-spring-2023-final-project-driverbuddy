from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from utils.authentication import manager
from utils.pydantic_models import UserLogin, DrivingData, DrivingStats
from utils.db_utils import select_all_driving_data, select_all_driving_stats, \
    select_all_driving_data_by_timestamp, select_all_driving_stats_by_timestamp, \
    insert_driving_data, insert_driving_stats
from fastapi.encoders import jsonable_encoder

router = APIRouter()


@router.get("/get_driving_data", response_class=JSONResponse)
def get_all_driving_data(request: Request, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_data = select_all_driving_data(user.user_id)
    response = {}
    for i, data in enumerate(driving_data):
        response[i] = jsonable_encoder(data)
    return JSONResponse(content=response)


@router.get("/get_driving_stats", response_class=JSONResponse)
def get_all_driving_stats(request: Request, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_stats = select_all_driving_stats(user.user_id)
    response = {}
    for data in driving_stats:
        response[data.timestamp_unix_ms] = jsonable_encoder(data)
    return JSONResponse(content=response)


@router.get("/get_driving_data/{start}/{end}", response_class=JSONResponse)
def get_all_driving_data_by_timestamp(request: Request, start: int, end: int, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_data = select_all_driving_data_by_timestamp(user.user_id, start, end)
    response = {}
    for data in driving_data:
        response[data.timestamp_unix_ms] = jsonable_encoder(data)
    return JSONResponse(content=response)


@router.get("/get_driving_stats/{start}/{end}", response_class=JSONResponse)
def get_all_driving_stats_by_timestamp(request: Request, start: int, end: int, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    driving_stats = select_all_driving_stats_by_timestamp(user.user_id, start, end)
    response = {}
    for data in driving_stats:
        response[data.timestamp_unix_ms] = jsonable_encoder(data)
    return JSONResponse(content=response)


@router.post("/post_driving_data", response_class=JSONResponse)
def post_driving_data(request: Request, data: DrivingData, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    result = insert_driving_data(data, user.user_id)
    if not result:
        return JSONResponse({"message": "Failed to insert data"})
    return JSONResponse({"message": "Successfully inserted data"})


@router.post("/post_driving_stats", response_class=JSONResponse)
def post_driving_stats(request: Request, data: DrivingStats, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    result = insert_driving_stats(data, user.user_id)
    if not result:
        return JSONResponse({"message": "Failed to insert data"})
    return JSONResponse({"message": "Successfully inserted data"})
    