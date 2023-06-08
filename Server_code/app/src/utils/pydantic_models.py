from pydantic import BaseModel
from pydantic import EmailStr


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
    accel_x: float
    accel_y: float
    accel_z: float
    yaw: float
    pitch: float
    roll: float
    throttle_position: float
    vehicle_speed: float
    engine_rpm: float
    latitude: float
    longitude: float
    timestamp: int

class TripStats(BaseModel):
    driving_score: float
    smoothness_score: float
    eco_driving_score: float    
    sharp_wide_turns: int
    hard_brakes: int
    hard_accels: int
    total_mileage: float
    timestamp: int
