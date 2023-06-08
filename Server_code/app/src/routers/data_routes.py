import time
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from utils.authentication import manager
from utils.pydantic_models import UserLogin, DrivingData, TripStats
from utils.db_utils import select_all_driving_data, select_all_trip_stats, \
    insert_driving_data, insert_into_trip_stats, select_driving_data_range
from utils.driving_scorer import calcTripStats


router = APIRouter()
is_driving = {}



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
    driving_stats = select_all_trip_stats(user.user_id)
    response = [jsonable_encoder(data) for data in driving_stats]
    return JSONResponse(content=response)


@router.get("/calculate_score", response_class=JSONResponse)
def calculate_driving_score(request: Request, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    global is_driving
    timestamp = is_driving.pop(user.user_id)
    driving_data = select_driving_data_range(user.user_id, 1686200314, 1686200521)
    trip_stats = calcTripStats(driving_data)

    result = insert_into_trip_stats(trip_stats, user.user_id)
    if not result:
        return JSONResponse({"message": "Failed to calculate score"})
    return JSONResponse({"message": "Successfully calculated score"})


@router.post("/post_driving_data", response_class=JSONResponse)
def post_driving_data(request: Request, data: DrivingData, user: UserLogin=Depends(manager)) -> JSONResponse:
    if user is None:
        return JSONResponse({"message": "Invalid credentials"})
    global is_driving
    if user.user_id not in is_driving:
        is_driving[user.user_id] = time.time()

    result = insert_driving_data(data, user.user_id)
    if not result:
        return JSONResponse({"message": "Failed to insert data"})
    return JSONResponse({"message": "Successfully inserted data"})


    