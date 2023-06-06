import mysql.connector as mysql
import os
from dotenv import load_dotenv

load_dotenv("credentials.env")

db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']


def init_db():
    db = mysql.connect(user=db_user, password=db_pass, host=db_host)
    cursor = db.cursor()

    try:
        cursor.execute("CREATE DATABASE DriverBuddy")
    except Exception as e:
        print(f"Failed creating database: {e}")

    cursor.execute("USE DriverBuddy")

    try:
        cursor.execute("""
        CREATE TABLE Users (
            id                      INTEGER AUTO_INCREMENT PRIMARY KEY,
            first_name              VARCHAR(30) NOT NULL,
            last_name               VARCHAR(30) NOT NULL,
            email                   VARCHAR(100) NOT NULL UNIQUE,
            username                VARCHAR(30) NOT NULL UNIQUE,
            hashed_password         VARCHAR(100) NOT NULL,
            car_make                VARCHAR(30) NOT NULL,
            car_model               VARCHAR(30) NOT NULL,
            car_year                INTEGER NOT NULL
        );
        """)
    except Exception as e:
        print(f"Failed creating Users table: {e}")

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS DrivingData (
            id                      INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id                 INTEGER NOT NULL,
            accelerometer_x         FLOAT NOT NULL,
            accelerometer_y         FLOAT NOT NULL,
            accelerometer_z         FLOAT NOT NULL,
            gyroscope_x             FLOAT NOT NULL,
            gyroscope_y             FLOAT NOT NULL,
            gyroscope_z             FLOAT NOT NULL,
            throttle_position       FLOAT NOT NULL,
            vehicle_speed           FLOAT NOT NULL,
            engine_rpm              FLOAT NOT NULL,
            latitude                FLOAT NOT NULL,
            longitude               FLOAT NOT NULL,
            timestamp               TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
            FOREIGN KEY (user_id)   REFERENCES Users(id)
        );
        """)
    except Exception as e:
        print(f"Failed creating DrivingData table: {e}")

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS DrivingStats (
            id                      INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id                 INTEGER NOT NULL,
            driving_score           FLOAT NOT NULL,
            smoothness_score        FLOAT NOT NULL,
            eco_driving_score       FLOAT NOT NULL,
            sharp_wide_turns        INTEGER NOT NULL,
            hard_brakes             INTEGER NOT NULL,
            hard_accels             INTEGER NOT NULL,
            timestamp               TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
            FOREIGN KEY (user_id)   REFERENCES Users(id)
        );
        """)
    except Exception as e:
        print(f"Failed creating DrivingStats table: {e}")

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS TripStats (
            id                      INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id                 INTEGER NOT NULL,
            trip_sharp_wide_turns   INTEGER NOT NULL,
            trip_hard_brakes        INTEGER NOT NULL,
            trip_hard_accels        INTEGER NOT NULL,
            trip_time               FLOAT NOT NULL,
            trip_milage             FLOAT NOT NULL,
            timestamp               TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
            FOREIGN KEY (user_id)   REFERENCES Users(id)
        );
        """)
    except Exception as e:
        print(f"Failed creating DrivingStats table: {e}")

    db.close()
    
if __name__ == '__main__':
    init_db()