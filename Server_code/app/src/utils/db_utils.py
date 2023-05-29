import mysql.connector as mysql
import datetime
import time
import os

from utils.pydantic_models import UserInDB, UserLogin, UserRegistration, DrivingData, DrivingStats
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
    query = """INSERT INTO DrivingData (user_id, accelerometer_x, accelerometer_y, accelerometer_z, 
    gyroscope_x, gyroscope_y, gyroscope_z, throttle_position, vehicle_speed, engine_rpm, latitude, longitude)
    values (%s, %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s);"""
    cursor.execute(query, (user_id, data.accelerometer_x, data.accelerometer_y, 
                           data.accelerometer_z, data.gyroscope_x, data.gyroscope_y, 
                           data.gyroscope_z, data.throttle_position, data.vehicle_speed, 
                           data.engine_rpm, data.latitude, data.longitude))
    db.commit()
    result = cursor.rowcount
    db.close()
    return True if result == 1 else False


def insert_driving_stats(stats: DrivingStats, user_id: int) -> bool:
    db, cursor = open_connection()
    query = """INSERT INTO DrivingStats (user_id, driving_score, smoothness_score, eco_driving_score, 
    lane_changes, sharp_wide_turns, hard_brakes, hard_accels)
    values (%s, %s , %s , %s , %s , %s , %s , %s);"""
    cursor.execute(query, (user_id, stats.driving_score, stats.smoothness_score, 
                           stats.eco_driving_score, stats.lane_changes, stats.sharp_wide_turns, 
                           stats.hard_brakes, stats.hard_accels))
    db.commit()
    result = cursor.rowcount
    db.close()
    return True if result == 1 else False


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
        print(row[13])
        data.append(DrivingData(accelerometer_x=row[2], accelerometer_y=row[3], accelerometer_z=row[4], 
                                gyroscope_x=row[5], gyroscope_y=row[6], gyroscope_z=row[7], 
                                throttle_position=row[8], vehicle_speed=row[9], engine_rpm=row[10], 
                                latitude=row[11], longitude=row[12], timestamp=str(row[13])))
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
                                  lane_changes=row[5], sharp_wide_turns=row[6], 
                                  hard_brakes=row[7], hard_accels=row[8], timestamp_unix_ms=row[9]))
    return stats    


def select_all_driving_data_by_timestamp(user_id: int, start_timestamp: int, end_timestamp: int) -> list[DrivingData] | None:
    # Convert unix timestamp to datetime string
    start_datetime = datetime.fromtimestamp(start_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.fromtimestamp(end_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    db, cursor = open_connection()
    query = f"SELECT * FROM DrivingData WHERE user_id={user_id} AND timestamp BETWEEN '{start_datetime}' AND '{end_datetime}';"
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    if result is None:
        return None
    data = []
    for row in result:
        data.append(DrivingData(accelerometer_x=row[2], accelerometer_y=row[3], accelerometer_z=row[4], 
                                gyroscope_x=row[5], gyroscope_y=row[6], gyroscope_z=row[7], 
                                throttle_position=row[8], vehicle_speed=row[9], engine_rpm=row[10], 
                                latitude=row[11], longitude=row[12], timestamp_unix_ms=row[13]))
    return data


def select_all_driving_stats_by_timestamp(user_id: int, start_timestamp: int, end_timestamp: int) -> list[DrivingStats] | None:
    # Convert unix timestamp to datetime string
    start_datetime = datetime.fromtimestamp(start_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.fromtimestamp(end_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    db, cursor = open_connection()
    query = f"SELECT * FROM DrivingStats WHERE user_id={user_id} AND timestamp BETWEEN '{start_datetime}' AND '{end_datetime}';"
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    if result is None:
        return None
    stats = []
    for row in result:
        stats.append(DrivingStats(driving_score=row[2], 
                                  smoothness_score=row[3], eco_driving_score=row[4], 
                                  lane_changes=row[5], sharp_wide_turns=row[6], 
                                  hard_brakes=row[7], hard_accels=row[8], timestamp_unix_ms=row[9]))
    return stats


def open_connection() -> tuple[mysql.connection.MySQLConnection, mysql.connection.MySQLCursor]:
    db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
    cursor = db.cursor()
    return db, cursor

