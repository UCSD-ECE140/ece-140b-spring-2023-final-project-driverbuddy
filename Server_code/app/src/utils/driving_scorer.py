'''
This file contains how all the data will be processed into stats and scores before getting saved in database.
Created by Andy Fong
'''

import math
import requests
import statistics
from datetime import datetime
from geopy.distance import geodesic
from utils.pydantic_models import DrivingData, TripStats

def calcTripStats(driving_data: list[DrivingData]):
    tripSeconds = calculate_time_difference(driving_data[0].timestamp, driving_data[-1].timestamp)
    data = format_data(driving_data)
    tripSpeeds = calculate_speeds(data['accel_y'])
    total_milage = calculate_distance(tripSpeeds)
    hard_accels = detect_hard_accelerations(data['vehicle_speed'])
    hard_brakes = calculate_hard_braking_count(data['accel_x'])
    sharp_wide_turns = calculate_harsh_cornering(data['accel_y'])
    driving_score = calculate_driving_score(hard_brakes, hard_accels, sharp_wide_turns, 
                                                    total_milage, tripSeconds)
    smoothness_score = calculate_stability_score(data['pitch'], data['roll'], data['yaw'], data['accel_y'], data['accel_x'])
    route_score = calculate_route_efficiency_score(data['latitude'], data['longitude'])

    currTrip = TripStats(driving_score=driving_score, smoothness_score=smoothness_score, route_score=route_score, sharp_wide_turns=sharp_wide_turns,
                            hard_accels=hard_accels, hard_brakes=hard_brakes, total_milage=total_milage, timestamp=driving_data[0].timestamp)
    return currTrip


def format_data(driving_data: list[DrivingData]) -> dict:
    data = {}
    data['accel_x'] = []
    data['accel_y'] = []
    data['accel_z'] = []
    data['yaw'] = []
    data['pitch'] = []
    data['roll'] = []
    data['throttle_position'] = []
    data['vehicle_speed'] = []
    data['engine_rpm'] = []
    data['latitude'] = []
    data['longitude'] = []
    data['timestamp'] = []
    for sample in driving_data:
        data['accel_x'].append(sample.accel_x)
        data['accel_y'].append(sample.accel_y)
        data['accel_z'].append(sample.accel_z)
        data['yaw'].append(sample.yaw)
        data['pitch'].append(sample.pitch)
        data['roll'].append(sample.roll)
        data['throttle_position'].append(sample.throttle_position)
        data['vehicle_speed'].append(sample.vehicle_speed)
        data['engine_rpm'].append(sample.engine_rpm)
        data['latitude'].append(sample.latitude)
        data['longitude'].append(sample.longitude)
        data['timestamp'].append(sample.timestamp)
    return data

# def updateCurrTrip(drivingData: DrivingData, currTrip: TripStats):
#     # change to += if drivingData is not the entirety of the trip, but snippets
#     currTrip.trip_hard_accels = detect_hard_accelerations(drivingData.vehicle_speed)
#     currTrip.trip_hard_brakes = calculate_hard_braking_count(drivingData.accel_x)
#     currTrip.trip_sharp_wide_turns = calculate_harsh_cornering(drivingData.accel_y)
#     # change timestamp function
#     currTrip.trip_time = calculate_timestamp_difference(drivingData.timestamp[0],drivingData.timestamp[-1])
#     currTrip.trip_milage = calculate_distance(drivingData.latitude[0], drivingData.longitude[0], drivingData.latitude[-1], drivingData.longitude[-1])

#     return currTripy

# def updateDrivingStats(drivingData: DrivingData, drivingStats: DrivingStats):
#     # drivingStats.speeding_inst = 
    
#     # Effectively the same as the function above after this point
#     drivingStats.hard_accels += detect_hard_accelerations(drivingData.vehicle_speed)
#     drivingStats.hard_brakes += calculate_hard_braking_count(drivingData.accel_x)
#     drivingStats.sharp_wide_turns += calculate_harsh_cornering(drivingData.accel_y)
#     # change timestamp function
#     drivingStats.timestamp = calculate_timestamp_difference(drivingData.timestamp[0],drivingData.timestamp[-1])
#     trip_dist = calculate_distance(drivingData.latitude[0], drivingData.longitude[0], drivingData.latitude[-1], drivingData.longitude[-1])
#     trip_time = calculate_timestamp_difference(drivingData.timestamp[0],drivingData.timestamp[-1])
#     drivingStats.driving_score = calculate_driving_score(drivingStats.hard_brakes, drivingStats.hard_accels, drivingStats.sharp_wide_turns, trip_dist, trip_time)
#     drivingStats.smoothness_score = calculate_stability_score(drivingData.pitch, drivingData.roll, drivingData.yaw, drivingData.accel_y, drivingData.accel_x)
#     drivingStats.eco_driving_score = calculate_eco_driving_score(drivingData.vehicle_speed, drivingData.engine_rpm, drivingData.accel_y, drivingData.gps_speed, drivingData.throttle_position)
#     return drivingStats


# Use this to calculate vehicle speed data from accel_y
def calculate_speeds(accelerations):
    speeds = [0]  # Initial speed is 0
    for acceleration in accelerations:
        speed = speeds[-1] + acceleration
        speeds.append(speed)
    return speeds

def calculate_distance(speeds):
    # Assuming m/s for input, outputs mph
    distance = 0
    for speed in speeds:
        distance += speed
    distance_miles = distance / 1609.34
    return distance_miles

def calculate_time_difference(start_timestamp, end_timestamp):
    start_datetime = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")
    time_difference = end_datetime - start_datetime
    seconds = time_difference.seconds % 60
    return seconds

def detect_hard_accelerations(obd2_speed_data, time_data, threshold):
    acceleration = []
    acceleration_change = []

    # Calculate acceleration from speed data
    for i in range(len(obd2_speed_data)-1):
        speed_change = obd2_speed_data[i+1] - obd2_speed_data[i]
        time_change = time_data[i+1] - time_data[i]
        acceleration.append(speed_change / time_change)

    # Calculate rate of change of acceleration
    for i in range(len(acceleration)-1):
        acceleration_rate_change = acceleration[i+1] - acceleration[i]
        time_change = time_data[i+1] - time_data[i] # need to ask for timestamp format to calculate actual time difference.
        acceleration_change.append(acceleration_rate_change / time_change)

    # Detect instances of aggressive acceleration
    aggressive_acceleration_indices = []
    for i in range(len(acceleration_change)):
        if acceleration_change[i] > threshold:
            aggressive_acceleration_indices.append(i)

    # Return count of instances of aggressive acceleration
    return len(aggressive_acceleration_indices)

def calculate_hard_braking_count(longitudinal_acceleration_data): # x axis
    # Initialize variables
    hard_braking_count = 0
    is_hard_braking = False
    deceleration_threshold = 5 # change later

    # Iterate over the acceleration data
    for i in range(1, len(longitudinal_acceleration_data)):
        current_acc = longitudinal_acceleration_data[i]
        previous_acc = longitudinal_acceleration_data[i - 1]

        deceleration = current_acc - previous_acc

        if deceleration < deceleration_threshold:
            if not is_hard_braking:
                is_hard_braking = True
                hard_braking_count += 1
        else:
            is_hard_braking = False

    return hard_braking_count

# for sharp and wide turns
def calculate_harsh_cornering(imu_lateral_acceleration): # accelerometer y
    harsh_cornering_count = 0
    threshold = 5

    # Check for rapid changes in lateral acceleration
    for i in range(len(imu_lateral_acceleration) - 1):
        acceleration_change = abs(imu_lateral_acceleration[i+1] - imu_lateral_acceleration[i])
        
        if acceleration_change > threshold:
            harsh_cornering_count += 1

    return harsh_cornering_count

def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Earth radius in meters
    earth_radius = 6371000

    # Haversine formula to calculate distance
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    return distance

# def get_speed_limit(latitude, longitude):
#     url = f"https://api.openstreetmap.org/api/0.6/way?format=json&lat={latitude}&lon={longitude}"
#     print(url)
#     response = requests.get(url)
#     print(response)
#     if response.status_code == 200:
#         data = response.json()
    
#         for tag in data["osm"]["way"]["tag"]:
#             if tag["@k"] == "maxspeed":
#                 return tag["@v"]

#     return None

# def get_speed_limit(latitude: list, longitude: list):   # Assuming list as inputs, not just one value
#     # Fetch the expected speed limit from the Google Maps API
#     length = min(len(latitude), len(longitude))
#     url = f'https://roads.googleapis.com/v1/speedLimits?path={latitude[0]},{longitude[0]}'
#     i = 1
#     for i in range(length):
#         url += f'|{latitude[i]},{longitude[i]}'
#     url += f'&units=MPH&key={GOOGLE_MAPS_API_KEY}'
#     print(url)
#     response = requests.get(url)
#     print(response)
#     if response.status_code == 200:
#         try:
#             result = response.json()
#             print(result)
#             speed_limit = result['speedLimits']
#             return speed_limit
#         except (KeyError, IndexError):
#             pass
#     # If unable to fetch the speed limit, return None
#     return None

# def detect_speeding_instances(speed_data, lat, lng):
#     # Assuming that the indexes of speed data correspond to the gps data
#     speeding_instances = 0
#     threshold = 5 # mph over speed limit threshold
#     lat_lng_data = [(lat[i], lng[i]) for i in range(0, len(lat))]
#     # Iterate over the speed data and latitude/longitude data
#     for speed, (lat, lng) in zip(speed_data, lat_lng_data):
#         speed_limit = get_speed_limit(lat, lng)
#         if speed_limit is not None and speed > (speed_limit + threshold):
#             speeding_instances += 1

#     return speeding_instances

def calculate_driving_score(hard_braking_count, aggressive_acceleration_count, harsh_cornering_count, total_distance, total_duration):
    # Weightage for each driving parameter
    # speeding_weight = 0.2
    hard_braking_weight = 0.23
    aggressive_acceleration_weight = 0.23
    harsh_cornering_weight = 0.23
    distance_weight = 0.11
    duration_weight = 0.1

    # Normalize the distance and duration values
    normalized_distance = total_distance / 1000  # Assuming total_distance is in meters
    normalized_duration = total_duration / 3600  # Assuming total_duration is in seconds

    # Score calculation
    # speeding_score = max(1 - speeding_count / (normalized_distance + 1), 0)
    hard_braking_score = max(1 - hard_braking_count / (normalized_distance + 1), 0)
    aggressive_acceleration_score = max(1 - aggressive_acceleration_count / (normalized_distance + 1), 0)
    harsh_cornering_score = max(1 - harsh_cornering_count / (normalized_distance + 1), 0)
    distance_score = max(1 - normalized_distance / 100, 0)  # Normalize distance to a maximum of 100 km
    duration_score = max(1 - normalized_duration / 2, 0)  # Normalize duration to a maximum of 2 hours

    driving_score = (hard_braking_score * hard_braking_weight +
                     aggressive_acceleration_score * aggressive_acceleration_weight +
                     harsh_cornering_score * harsh_cornering_weight +
                     distance_score * distance_weight +
                     duration_score * duration_weight)

    return driving_score

def calculate_stability_score(pitch_data, roll_data, yaw_rate_data, lateral_acceleration_data, longitudinal_acceleration_data):
    # Define scoring weights for different factors
    pitch_stability_weight = 0.2
    roll_stability_weight = 0.2
    yaw_stability_weight = 0.1
    smooth_turns_weight = 0.1
    smooth_acceleration_weight = 0.15
    smooth_braking_weight = 0.15

    # Calculate scores for each factor
    pitch_stability_score = pitch_stability_weight * calculate_pitch_stability_score(pitch_data)
    roll_stability_score = roll_stability_weight * calculate_roll_stability_score(roll_data)
    yaw_stability_score = yaw_stability_weight * calculate_yaw_stability_score(yaw_rate_data)
    smooth_turns_score = smooth_turns_weight * calculate_smooth_turns_score(lateral_acceleration_data)
    smooth_acceleration_score = smooth_acceleration_weight * calculate_smooth_acceleration_score(longitudinal_acceleration_data)
    smooth_braking_score = smooth_braking_weight * calculate_smooth_braking_score(longitudinal_acceleration_data)

    # Calculate the total stability score
    stability_score = (
        pitch_stability_score +
        roll_stability_score +
        yaw_stability_score +
        smooth_turns_score +
        smooth_acceleration_score +
        smooth_braking_score
    )

    return stability_score

    # Smoothness / Stability Score
# Effectively just takes the standard deviation of every list and see if the value would
# exceed a certain threshold.

def calculate_pitch_stability_score(pitch_data):
    # Calculate the standard deviation of pitch data
    pitch_std = statistics.pstdev(pitch_data)

    # Define thresholds for pitch stability
    pitch_stability_threshold = 2.0

    # Assign score based on the magnitude of pitch standard deviation
    if pitch_std <= pitch_stability_threshold:
        pitch_stability_score = 10.0
    else:
        pitch_stability_score = max(0.0, 10.0 - (pitch_std - pitch_stability_threshold))

    return pitch_stability_score

def calculate_roll_stability_score(roll_data):
    # Calculate the standard deviation of roll data
    roll_std = statistics.pstdev(roll_data)

    # Define thresholds for roll stability
    roll_stability_threshold = 2.0

    # Assign score based on the magnitude of roll standard deviation
    if roll_std <= roll_stability_threshold:
        roll_stability_score = 10.0
    else:
        roll_stability_score = max(0.0, 10.0 - (roll_std - roll_stability_threshold))

    return roll_stability_score

def calculate_yaw_stability_score(yaw_rate_data):
    # Calculate the standard deviation of yaw rate data
    yaw_rate_std = statistics.pstdev(yaw_rate_data)

    # Define thresholds for yaw stability
    yaw_stability_threshold = 1.0

    # Assign score based on the magnitude of yaw rate standard deviation
    if yaw_rate_std <= yaw_stability_threshold:
        yaw_stability_score = 10.0
    else:
        yaw_stability_score = max(0.0, 10.0 - (yaw_rate_std - yaw_stability_threshold))

    return yaw_stability_score

def calculate_smooth_turns_score(lateral_acceleration_data):
    # Calculate the standard deviation of lateral acceleration data
    lateral_acceleration_std = statistics.pstdev(lateral_acceleration_data)

    # Define thresholds for smooth turns
    smooth_turns_threshold = 1.0

    # Assign score based on the magnitude of lateral acceleration standard deviation
    if lateral_acceleration_std <= smooth_turns_threshold:
        smooth_turns_score = 10.0
    else:
        smooth_turns_score = max(0.0, 10.0 - (lateral_acceleration_std - smooth_turns_threshold))

    return smooth_turns_score

def calculate_smooth_acceleration_score(longitudinal_acceleration_data):
    # Calculate the standard deviation of longitudinal acceleration data
    longitudinal_acceleration_std = statistics.pstdev(longitudinal_acceleration_data)

    # Define thresholds for smooth acceleration
    smooth_acceleration_threshold = 1.0

    # Assign score based on the magnitude of longitudinal acceleration standard deviation
    if longitudinal_acceleration_std <= smooth_acceleration_threshold:
        smooth_acceleration_score = 10.0
    else:
        smooth_acceleration_score = max(0.0, 10.0 - (longitudinal_acceleration_std - smooth_acceleration_threshold))

    return smooth_acceleration_score

def calculate_smooth_braking_score(longitudinal_acceleration_data):
    # Calculate the standard deviation of longitudinal acceleration data
    longitudinal_acceleration_std = statistics.pstdev(longitudinal_acceleration_data)

    # Define thresholds for smooth braking
    smooth_braking_threshold = 1.0

    # Assign score based on the magnitude of longitudinal acceleration standard deviation
    if longitudinal_acceleration_std <= smooth_braking_threshold:
        smooth_braking_score = 10.0
    else:
        smooth_braking_score = max(0.0, 10.0 - (longitudinal_acceleration_std - smooth_braking_threshold))

    return smooth_braking_score

def calculate_steering_stability_score(steering_angle_data):
    # Calculate the standard deviation of steering angle data
    steering_angle_std = statistics.pstdev(steering_angle_data)

    # Define thresholds for steering stability
    steering_stability_threshold = 5.0

    # Assign score based on the magnitude of steering angle standard deviation
    if steering_angle_std <= steering_stability_threshold:
        steering_stability_score = 10.0
    else:
        steering_stability_score = max(0.0, 10.0 - (steering_angle_std - steering_stability_threshold))

    return steering_stability_score

def calculate_route_efficiency_score(latitude, longitude):
    # Calculate the distance of the driven route compared to the optimal route
    driven_route_distance = sum(
        geodesic((latitude[i], longitude[i]), (latitude[i+1], longitude[i+1])).miles
        for i in range(len(latitude) - 1)
    )

    # Determine the start and end locations
    start_location = f"{latitude[0]},{longitude[0]}"
    end_location = f"{latitude[-1]},{longitude[-1]}"

    # Send a request to the Google Maps Directions API
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_location}&destination={end_location}&key=AIzaSyAwdv9efqNsmsBe7Yn2o9gKNvzako36QPM"
    response = requests.get(url)
    data = response.json()

    # Extract the coordinates of the optimal route
    optimal_route = []
    if data['status'] == 'OK':
        route = data['routes'][0]  # Assuming the first route is the optimal one
        for step in route['legs'][0]['steps']:
            optimal_route.append((step['start_location']['lat'], step['start_location']['lng']))
        optimal_route.append((route['legs'][0]['end_location']['lat'], route['legs'][0]['end_location']['lng']))
        optimal_route_distance = route['legs'][0]['distance']['value'] / 1609.34  # Convert meters to miles

    # Calculate the route efficiency score
    route_efficiency_score = 1 - (driven_route_distance / optimal_route_distance)

    return route_efficiency_score

# # Sample latitude and longitude lists
# latitude = [37.7749, 37.7758, 37.7762, 37.7765, 37.7771, 37.7773, 37.7779, 37.7783, 37.7789]
# longitude = [-122.4194, -122.4182, -122.4177, -122.4175, -122.4156, -122.4151, -122.4138, -122.4128, -122.4117]
# efficiency_score = calculate_route_efficiency_score(latitude, longitude)
# print(efficiency_score)

# def calculate_eco_driving_score( imu_acceleration_data, gps_speed_data):
#     score = 0

#     # Factor 1: Smooth acceleration and braking
#     smooth_acceleration = detect_smooth_acceleration(obd2_speed_data, obd2_rpm_data)
#     smooth_braking = detect_smooth_braking(obd2_speed_data, obd2_rpm_data)
#     score += (smooth_acceleration + smooth_braking) / 2

#     # Factor 2: Efficient speed maintenance
#     speed_efficiency = detect_efficient_speed_maintenance(obd2_speed_data, gps_speed_data)
#     score += speed_efficiency

#     # Factor 3: Minimizing harsh cornering
#     harsh_cornering = calculate_harsh_cornering(imu_acceleration_data)
#     score += harsh_cornering

#     # Factor 4: Fuel efficiency
#     fuel_efficiency = calculate_fuel_efficiency(obd2_speed_data, obd2_rpm_data, throttle_position_data)
#     score += fuel_efficiency

#     # Factor 5: Eco-friendly driving behavior (e.g., minimizing idling time, using eco-mode)
#     eco_friendly_behavior = detect_eco_friendly_behavior(obd2_speed_data)
#     score += eco_friendly_behavior

#     # Normalize the score between 0 and 100
#     score = min(max(score, 0), 100)

#     return score

# def detect_smooth_acceleration(obd2_speed_data, obd2_rpm_data):
#     acceleration = calculate_acceleration(obd2_speed_data)
#     rpm_change = calculate_rpm_change(obd2_rpm_data)

#     # Calculate the standard deviation of acceleration and RPM change
#     acceleration_std = statistics.stdev(acceleration)
#     rpm_change_std = statistics.stdev(rpm_change)

#     # Determine the smoothness score based on the deviation thresholds
#     smoothness_score = 100 - (acceleration_std * 10) - (rpm_change_std / 5)

#     # Limit the score to a range of 0 to 100
#     smoothness_score = max(0, min(100, smoothness_score))

#     return smoothness_score

# def detect_smooth_braking(obd2_speed_data, obd2_rpm_data):
#     deceleration = calculate_deceleration(obd2_speed_data)
#     rpm_change = calculate_rpm_change(obd2_rpm_data)

#     # Calculate the standard deviation of deceleration and RPM change
#     deceleration_std = statistics.stdev(deceleration)
#     rpm_change_std = statistics.stdev(rpm_change)

#     # Determine the smoothness score based on the deviation thresholds
#     smoothness_score = 100 - (deceleration_std * 10) - (rpm_change_std / 5)

#     # Limit the score to a range of 0 to 100
#     smoothness_score = max(0, min(100, smoothness_score))

#     return smoothness_score

# def calculate_acceleration(speed_data):
#     # Calculate acceleration as the derivative of speed with respect to time
#     acceleration = []
#     for i in range(1, len(speed_data)):
#         speed_change = speed_data[i] - speed_data[i-1]
#         time_change = 1  # Assuming the time interval is 1 second
#         acceleration.append(speed_change / time_change)

#     return acceleration

# def calculate_deceleration(speed_data):
#     # Calculate deceleration as the negative derivative of speed with respect to time
#     deceleration = []
#     for i in range(1, len(speed_data)):
#         speed_change = speed_data[i] - speed_data[i-1]
#         time_change = 1  # Assuming the time interval is 1 second
#         deceleration.append(-speed_change / time_change)

#     return deceleration

# def calculate_rpm_change(rpm_data):
#     # Calculate RPM change as the difference between consecutive RPM values
#     rpm_change = []
#     for i in range(1, len(rpm_data)):
#         rpm_change.append(rpm_data[i] - rpm_data[i-1])

#     return rpm_change

# def detect_efficient_speed_maintenance(obd2_speed_data, gps_speed_data):
#     inefficient_speed_changes = 0

#     for obd2_speed, gps_speed in zip(obd2_speed_data, gps_speed_data):
#         if abs(obd2_speed - gps_speed) > 5:  # Threshold for inefficient speed change
#             inefficient_speed_changes += 1

#     efficiency_score = 1 - (inefficient_speed_changes / len(obd2_speed_data))
#     return efficiency_score * 100

# def calculate_fuel_efficiency(obd2_speed_data, obd2_rpm_data, throttle_position_data):
#     total_fuel_consumption = 0
#     total_distance_traveled = 0

#     for speed, rpm, throttle_position in zip(obd2_speed_data, obd2_rpm_data, throttle_position_data):
#         fuel_consumption = calculate_fuel_consumption(speed, rpm, throttle_position)
#         total_fuel_consumption += fuel_consumption
#         total_distance_traveled += calculate_distance_traveled(speed)

#     if total_distance_traveled > 0:
#         fuel_efficiency = total_distance_traveled / total_fuel_consumption
#     else:
#         fuel_efficiency = 0

#     return fuel_efficiency

# def calculate_fuel_consumption(speed, rpm, throttle_position):
#     # Placeholder function to calculate fuel consumption based on speed, RPM, and throttle position
#     fuel_consumption = 0.05 * speed + 0.1 * rpm - 0.02 * throttle_position  # Sample calculation
#     return fuel_consumption

# def calculate_distance_traveled(speed):
#     # Placeholder function to calculate distance traveled based on speed
#     # change number depending on time btwn samples
#     distance_traveled = speed / 3600  # Assuming speed is given in miles per hour
#     return distance_traveled

# def detect_eco_friendly_behavior(obd2_speed_data):
#     idling_time = calculate_idling_time(obd2_speed_data)
#     eco_mode_usage = detect_eco_mode_usage(obd2_speed_data)

#     # Calculate the score based on idling time and eco mode usage
#     eco_friendly_score = 100

#     if idling_time > 10:  # If idling time exceeds 10 seconds
#         eco_friendly_score -= 10

#     if not eco_mode_usage:
#         eco_friendly_score -= 20

#     return eco_friendly_score

# def calculate_idling_time(speed_data):
#     idling_time = 0
#     idle_threshold = 5  # Speed threshold below which the vehicle is considered idling

#     for speed in speed_data:
#         if speed < idle_threshold:
#             idling_time += 1  # Increase idling time by 1 second

#     return idling_time

# def detect_eco_mode_usage(speed_data):
#     eco_mode_threshold = 60  # Speed threshold (in km/h) above which eco mode is expected to be enabled

#     for speed in speed_data:
#         if speed > eco_mode_threshold:
#             return False

#     return True

# # lat = 32.863974
# # long = -117.202272
# # speed_limit_test = get_speed_limit(lat, long) # Nobel Drive
# # print(speed_limit_test)