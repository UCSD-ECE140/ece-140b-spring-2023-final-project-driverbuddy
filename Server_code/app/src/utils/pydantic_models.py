from pydantic import BaseModel
from pydantic import EmailStr
import datetime


class User(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    car_make: str
    car_model: str
    car_year: int

class UserInDB(User):
    hashed_password: str

class UserLogin(BaseModel):
    username: str
    user_id: int

class UserRegistration(User):
    password: str
    confirm_password: str

class DrivingData(BaseModel):
    accelerometer_x: float
    accelerometer_y: float
    accelerometer_z: float
    gyroscope_x: float
    gyroscope_y: float
    gyroscope_z: float
    throttle_position: float
    vehicle_speed: float
    engine_rpm: float
    latitude: float
    longitude: float
    timestamp: str

class TripStats(BaseModel):
    trip_hard_brakes: int
    trip_hard_accels: int
    trip_sharp_wide_turns: int
    trip_time: float
    trip_milage: float


class DrivingStats(BaseModel):
    driving_score: float
    smoothness_score: float
    eco_driving_score: float
    sharp_wide_turns: int
    hard_brakes: int
    hard_accels: int
    speeding_inst: int
    timestamp: str
