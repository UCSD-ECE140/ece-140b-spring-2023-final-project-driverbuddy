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
            accel_x                 FLOAT NOT NULL,
            accel_y                 FLOAT NOT NULL,
            accel_z                 FLOAT NOT NULL,
            yaw                     FLOAT NOT NULL,
            pitch                   FLOAT NOT NULL,
            roll                    FLOAT NOT NULL,
            throttle_position       FLOAT NOT NULL,
            vehicle_speed           FLOAT NOT NULL,
            engine_rpm              FLOAT NOT NULL,
            latitude                FLOAT NOT NULL,
            longitude               FLOAT NOT NULL,
            timestamp               INTEGER NOT NULL,
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
            timestamp               INTEGER NOT NULL,
            FOREIGN KEY (user_id)   REFERENCES Users(id)
        );
        """)
    except Exception as e:
        print(f"Failed creating DrivingStats table: {e}")

    db.close()
    
if __name__ == '__main__':
    init_db()