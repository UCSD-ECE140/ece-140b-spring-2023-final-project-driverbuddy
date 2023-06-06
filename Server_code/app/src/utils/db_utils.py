import mysql.connector as mysql
import datetime
import time
import os

from utils.pydantic_models import UserInDB, UserLogin, UserRegistration, DrivingData, DrivingStats, TripStats
from utils.authentication import get_password_hash, verify_password, manager

db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']

@manager.user_loader()
def load_user(username: str) -> UserLogin:
    db, cursor = open_connection()
    query = f"SELECT username, id FROM Users WHERE username='{username}';"
    cursor.execute(query)
    result = cursor.fetchone()
    db.close()
    if result is None:
        return None
    return UserLogin(username=result[0], user_id=result[1])


def create_user(user: UserRegistration) -> bool:
    db, cursor = open_connection()
    if user.password != user.confirm_password:
        return False
    hashed_password = get_password_hash(user.password)
    query = """INSERT INTO Users (username, email, first_name, last_name, car_make, car_model, car_year, hashed_password)
    values (%s, %s , %s , %s , %s , %s , %s , %s);"""
    cursor.execute(query, (user.username, user.email, user.first_name, user.last_name, user.car_make, user.car_model, user.car_year, hashed_password))
    db.commit()
    result = cursor.rowcount
    db.close()
    return True if result == 1 else False


def select_user_by_username(username: str) -> UserInDB | None:
    db, cursor = open_connection()
    query = f"SELECT * FROM Users WHERE username='{username}';"
    cursor.execute(query)
    result = cursor.fetchone()
    db.close()
    if result is None:
        return None
    return UserInDB(id=result[0], username=result[4], email=result[3], first_name=result[1], last_name=result[2], car_make=result[6], car_model=result[7], car_year=result[8], hashed_password=result[5])


def update_user_by_field(username: str, field: str, value: str) -> bool:
    db, cursor = open_connection()
    query = f"UPDATE Users SET {field}='{value}' WHERE username='{username}';"
    cursor.execute(query)
    db.commit()
    result = cursor.rowcount
    db.close()
    if result == 0:
        return False
    return True


def delete_user(username: str) -> bool:
    db, cursor = open_connection()
    query = f"DELETE FROM Users WHERE username='{username}';"
    cursor.execute(query)
    db.commit()
    result = cursor.rowcount
    db.close()
    return True if result == 1 else False


def insert_driving_data(data: DrivingData, user_id: int) -> bool:
    db, cursor = open_connection()
    query = """INSERT INTO DrivingData (user_id, accel_x, accel_y, accel_y, yaw, pitch, roll, 
    throttle_position, vehicle_speed, engine_rpm, latitude, longitude, timestamp)
    values (%s, %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s);"""
    cursor.execute(query, (user_id, data.accel_x, data.accel_y, 
                           data.accel_z, data.yaw, data.pitch, 
                           data.roll, data.throttle_position, data.vehicle_speed, 
                           data.engine_rpm, data.latitude, data.longitude, time.time()))
    db.commit()
    result = cursor.rowcount
    db.close()
    return True if result == 1 else False


def insert_driving_stats(stats: DrivingStats, user_id: int) -> bool:
    db, cursor = open_connection()
    query = """INSERT INTO DrivingStats (user_id, driving_score, smoothness_score, eco_driving_score, 
    sharp_wide_turns, hard_brakes, hard_accels, timestamp)
    values (%s, %s , %s , %s , %s , %s , %s , %s);"""
    cursor.execute(query, (user_id, stats.driving_score, stats.smoothness_score, 
                           stats.eco_driving_score, stats.sharp_wide_turns, 
                           stats.hard_brakes, stats.hard_accels, time.time()))
    db.commit()
    result = cursor.rowcount
    db.close()
    return True if result == 1 else False


def insert_trip_stats(stats: TripStats):
    db, cursor = open_connection()
    



def select_all_driving_data(user_id: int) -> list[DrivingData] | None:
    db, cursor = open_connection()
    query = f"SELECT * FROM DrivingData WHERE user_id={user_id};"
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    if result is None:
        return None
    data = []
    for row in result:
        data.append(DrivingData(accel_x=row[2], accel_y=row[3], accel_z=row[4], 
                                yaw=row[5], pitch=row[6], roll=row[7], 
                                throttle_position=row[8], vehicle_speed=row[9], engine_rpm=row[10], 
                                latitude=row[11], longitude=row[12], timestamp=row[13]))
    return data


def select_all_driving_stats(user_id: int) -> list[DrivingStats] | None:
    db, cursor = open_connection()
    query = f"SELECT * FROM DrivingStats WHERE user_id={user_id};"
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    if result is None:
        return None
    stats = []
    for row in result:
        stats.append(DrivingStats(driving_score=row[2], 
                                  smoothness_score=row[3], eco_driving_score=row[4], 
                                  sharp_wide_turns=row[5], 
                                  hard_brakes=row[6], hard_accels=row[7], timestamp=row[8]))
    return stats    


def select_all_driving_data_by_timestamp(user_id: int, start_timestamp: int, end_timestamp: int) -> list[DrivingData] | None:
    db, cursor = open_connection()
    query = f"SELECT * FROM DrivingData WHERE user_id={user_id} AND timestamp BETWEEN '{start_timestamp}' AND '{end_timestamp}';"
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    if result is None:
        return None
    data = []
    for row in result:
        data.append(DrivingData(accel_x=row[2], accel_y=row[3], accel_z=row[4], 
                                yaw=row[5], pitch=row[6], roll=row[7], 
                                throttle_position=row[8], vehicle_speed=row[9], engine_rpm=row[10], 
                                latitude=row[11], longitude=row[12], timestamp=row[13]))
    return data


def select_all_driving_stats_by_timestamp(user_id: int, start_timestamp: int, end_timestamp: int) -> list[DrivingStats] | None:
    db, cursor = open_connection()
    query = f"SELECT * FROM DrivingStats WHERE user_id={user_id} AND timestamp BETWEEN '{start_timestamp}' AND '{end_timestamp}';"
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    if result is None:
        return None
    stats = []
    for row in result:
        stats.append(DrivingStats(driving_score=row[2], 
                                  smoothness_score=row[3], eco_driving_score=row[4], 
                                  sharp_wide_turns=row[5], 
                                  hard_brakes=row[6], hard_accels=row[7], timestamp=row[8]))
    return stats


def open_connection() -> tuple[mysql.connection.MySQLConnection, mysql.connection.MySQLCursor]:
    db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
    cursor = db.cursor()
    return db, cursor

