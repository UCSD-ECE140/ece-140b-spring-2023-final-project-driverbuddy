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

class UserRegistration(BaseModel):
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
    timestamp_unix_ms: int

class DrivingStats(BaseModel):
    driving_score: float
    smoothness_score: float
    eco_driving_score: float
    lane_changes: int
    sharp_wide_turns: int
    hard_brakes: int
    hard_accels: int
    timestamp_unix_ms: int
