import math
import requests
import statistics
from pydantic_models import DrivingData, DrivingStats, TripStats

GOOGLE_MAPS_API_KEY = 'AIzaSyAwdv9efqNsmsBe7Yn2o9gKNvzako36QPM'

def updateCurrTrip(drivingData: DrivingData, currTrip: TripStats):
    # change to += if drivingData is not the entirety of the trip, but snippets
    currTrip.trip_hard_accels = detect_hard_accelerations(drivingData.vehicle_speed)
    currTrip.trip_hard_brakes = calculate_hard_braking_count(drivingData.accelerometer_x)
    currTrip.trip_sharp_wide_turns = calculate_harsh_cornering(drivingData.accelerometer_y)
    # change timestamp function
    currTrip.trip_time = calculate_timestamp_difference(drivingData.timestamp[0],drivingData.timestamp[-1])
    currTrip.trip_milage = calculate_distance(drivingData.latitude[0], drivingData.longitude[0], drivingData.latitude[-1], drivingData.longitude[-1])

    return currTrip

def updateDrivingStats(drivingData: DrivingData, drivingStats: DrivingStats):
    # drivingStats.speeding_inst = 
    
    # Effectively the same as the function above after this point
    drivingStats.hard_accels += detect_hard_accelerations(drivingData.vehicle_speed)
    drivingStats.hard_brakes += calculate_hard_braking_count(drivingData.accelerometer_x)
    drivingStats.sharp_wide_turns += calculate_harsh_cornering(drivingData.accelerometer_y)
    # change timestamp function
    drivingStats.timestamp = calculate_timestamp_difference(drivingData.timestamp[0],drivingData.timestamp[-1])
    trip_dist = calculate_distance(drivingData.latitude[0], drivingData.longitude[0], drivingData.latitude[-1], drivingData.longitude[-1])
    trip_time = calculate_timestamp_difference(drivingData.timestamp[0],drivingData.timestamp[-1])
    drivingStats.driving_score = calculate_driving_score(drivingStats.speeding_inst, drivingStats.hard_brakes, drivingStats.hard_accels,
                                                         drivingStats.sharp_wide_turns, trip_dist, trip_time)
    drivingStats.smoothness_score = calculate_stability_score(drivingData.gyroscope_y, drivingData.gyroscope_x, drivingData.gyroscope_z, drivingData.accelerometer_y, drivingData.accelerometer_x, drivingData.throttle_position)
    drivingStats.eco_driving_score = calculate_eco_driving_score(drivingData.vehicle_speed, drivingData.engine_rpm, drivingData.accelerometer_y, drivingData.gps_speed, drivingData.throttle_position)
    return drivingStats

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

def calculate_timestamp_difference(begin, end):
    # selects two timestamps and parses through the both of them to calculate the time that passed
    beginTime = int(begin.split(' ')[3]) # change
    endTime = int(end.split(' ')[3])
    difference = 234
    return difference

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

def get_speed_limit(latitude, longitude):
    url = f"https://api.openstreetmap.org/api/0.6/way?format=json&lat={latitude}&lon={longitude}"
    print(url)
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        data = response.json()
    
        for tag in data["osm"]["way"]["tag"]:
            if tag["@k"] == "maxspeed":
                return tag["@v"]

    return None

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

def detect_speeding_instances(speed_data, lat, lng):
    # Assuming that the indexes of speed data correspond to the gps data
    speeding_instances = 0
    threshold = 5 # mph over speed limit threshold
    lat_lng_data = [(lat[i], lng[i]) for i in range(0, len(lat))]
    # Iterate over the speed data and latitude/longitude data
    for speed, (lat, lng) in zip(speed_data, lat_lng_data):
        speed_limit = get_speed_limit(lat, lng)
        if speed_limit is not None and speed > (speed_limit + threshold):
            speeding_instances += 1

    return speeding_instances

def calculate_driving_score(speeding_count, hard_braking_count, aggressive_acceleration_count, harsh_cornering_count, total_distance, total_duration):
    # Weightage for each driving parameter
    speeding_weight = 0.2
    hard_braking_weight = 0.2
    aggressive_acceleration_weight = 0.2
    harsh_cornering_weight = 0.2
    distance_weight = 0.1
    duration_weight = 0.1

    # Normalize the distance and duration values
    normalized_distance = total_distance / 1000  # Assuming total_distance is in meters
    normalized_duration = total_duration / 3600  # Assuming total_duration is in seconds

    # Score calculation
    speeding_score = max(1 - speeding_count / (normalized_distance + 1), 0)
    hard_braking_score = max(1 - hard_braking_count / (normalized_distance + 1), 0)
    aggressive_acceleration_score = max(1 - aggressive_acceleration_count / (normalized_distance + 1), 0)
    harsh_cornering_score = max(1 - harsh_cornering_count / (normalized_distance + 1), 0)
    distance_score = max(1 - normalized_distance / 100, 0)  # Normalize distance to a maximum of 100 km
    duration_score = max(1 - normalized_duration / 2, 0)  # Normalize duration to a maximum of 2 hours

    driving_score = (speeding_score * speeding_weight +
                     hard_braking_score * hard_braking_weight +
                     aggressive_acceleration_score * aggressive_acceleration_weight +
                     harsh_cornering_score * harsh_cornering_weight +
                     distance_score * distance_weight +
                     duration_score * duration_weight)

    return driving_score

def calculate_stability_score(pitch_data, roll_data, yaw_rate_data, lateral_acceleration_data, longitudinal_acceleration_data, steering_angle_data):
    # Define scoring weights for different factors
    pitch_stability_weight = 0.2
    roll_stability_weight = 0.2
    yaw_stability_weight = 0.1
    smooth_turns_weight = 0.1
    smooth_acceleration_weight = 0.1
    smooth_braking_weight = 0.1
    steering_stability_weight = 0.2

    # Calculate scores for each factor
    pitch_stability_score = pitch_stability_weight * calculate_pitch_stability_score(pitch_data)
    roll_stability_score = roll_stability_weight * calculate_roll_stability_score(roll_data)
    yaw_stability_score = yaw_stability_weight * calculate_yaw_stability_score(yaw_rate_data)
    smooth_turns_score = smooth_turns_weight * calculate_smooth_turns_score(lateral_acceleration_data)
    smooth_acceleration_score = smooth_acceleration_weight * calculate_smooth_acceleration_score(longitudinal_acceleration_data)
    smooth_braking_score = smooth_braking_weight * calculate_smooth_braking_score(longitudinal_acceleration_data)
    steering_stability_score = steering_stability_weight * calculate_steering_stability_score(steering_angle_data)

    # Calculate the total stability score
    stability_score = (
        pitch_stability_score +
        roll_stability_score +
        yaw_stability_score +
        smooth_turns_score +
        smooth_acceleration_score +
        smooth_braking_score +
        steering_stability_score
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

def calculate_eco_driving_score(obd2_speed_data, obd2_rpm_data, imu_acceleration_data, gps_speed_data, throttle_position_data):
    score = 0

    # Factor 1: Smooth acceleration and braking
    smooth_acceleration = detect_smooth_acceleration(obd2_speed_data, obd2_rpm_data)
    smooth_braking = detect_smooth_braking(obd2_speed_data, obd2_rpm_data)
    score += (smooth_acceleration + smooth_braking) / 2

    # Factor 2: Efficient speed maintenance
    speed_efficiency = detect_efficient_speed_maintenance(obd2_speed_data, gps_speed_data)
    score += speed_efficiency

    # Factor 3: Minimizing harsh cornering
    harsh_cornering = calculate_harsh_cornering(imu_acceleration_data)
    score += harsh_cornering

    # Factor 4: Fuel efficiency
    fuel_efficiency = calculate_fuel_efficiency(obd2_speed_data, obd2_rpm_data, throttle_position_data)
    score += fuel_efficiency

    # Factor 5: Eco-friendly driving behavior (e.g., minimizing idling time, using eco-mode)
    eco_friendly_behavior = detect_eco_friendly_behavior(obd2_speed_data)
    score += eco_friendly_behavior

    # Normalize the score between 0 and 100
    score = min(max(score, 0), 100)

    return score

def detect_smooth_acceleration(obd2_speed_data, obd2_rpm_data):
    acceleration = calculate_acceleration(obd2_speed_data)
    rpm_change = calculate_rpm_change(obd2_rpm_data)

    # Calculate the standard deviation of acceleration and RPM change
    acceleration_std = statistics.stdev(acceleration)
    rpm_change_std = statistics.stdev(rpm_change)

    # Determine the smoothness score based on the deviation thresholds
    smoothness_score = 100 - (acceleration_std * 10) - (rpm_change_std / 5)

    # Limit the score to a range of 0 to 100
    smoothness_score = max(0, min(100, smoothness_score))

    return smoothness_score

def detect_smooth_braking(obd2_speed_data, obd2_rpm_data):
    deceleration = calculate_deceleration(obd2_speed_data)
    rpm_change = calculate_rpm_change(obd2_rpm_data)

    # Calculate the standard deviation of deceleration and RPM change
    deceleration_std = statistics.stdev(deceleration)
    rpm_change_std = statistics.stdev(rpm_change)

    # Determine the smoothness score based on the deviation thresholds
    smoothness_score = 100 - (deceleration_std * 10) - (rpm_change_std / 5)

    # Limit the score to a range of 0 to 100
    smoothness_score = max(0, min(100, smoothness_score))

    return smoothness_score

def calculate_acceleration(speed_data):
    # Calculate acceleration as the derivative of speed with respect to time
    acceleration = []
    for i in range(1, len(speed_data)):
        speed_change = speed_data[i] - speed_data[i-1]
        time_change = 1  # Assuming the time interval is 1 second
        acceleration.append(speed_change / time_change)

    return acceleration

def calculate_deceleration(speed_data):
    # Calculate deceleration as the negative derivative of speed with respect to time
    deceleration = []
    for i in range(1, len(speed_data)):
        speed_change = speed_data[i] - speed_data[i-1]
        time_change = 1  # Assuming the time interval is 1 second
        deceleration.append(-speed_change / time_change)

    return deceleration

def calculate_rpm_change(rpm_data):
    # Calculate RPM change as the difference between consecutive RPM values
    rpm_change = []
    for i in range(1, len(rpm_data)):
        rpm_change.append(rpm_data[i] - rpm_data[i-1])

    return rpm_change

def detect_efficient_speed_maintenance(obd2_speed_data, gps_speed_data):
    inefficient_speed_changes = 0

    for obd2_speed, gps_speed in zip(obd2_speed_data, gps_speed_data):
        if abs(obd2_speed - gps_speed) > 5:  # Threshold for inefficient speed change
            inefficient_speed_changes += 1

    efficiency_score = 1 - (inefficient_speed_changes / len(obd2_speed_data))
    return efficiency_score * 100

def calculate_fuel_efficiency(obd2_speed_data, obd2_rpm_data, throttle_position_data):
    total_fuel_consumption = 0
    total_distance_traveled = 0

    for speed, rpm, throttle_position in zip(obd2_speed_data, obd2_rpm_data, throttle_position_data):
        fuel_consumption = calculate_fuel_consumption(speed, rpm, throttle_position)
        total_fuel_consumption += fuel_consumption
        total_distance_traveled += calculate_distance_traveled(speed)

    if total_distance_traveled > 0:
        fuel_efficiency = total_distance_traveled / total_fuel_consumption
    else:
        fuel_efficiency = 0

    return fuel_efficiency

def calculate_fuel_consumption(speed, rpm, throttle_position):
    # Placeholder function to calculate fuel consumption based on speed, RPM, and throttle position
    fuel_consumption = 0.05 * speed + 0.1 * rpm - 0.02 * throttle_position  # Sample calculation
    return fuel_consumption

def calculate_distance_traveled(speed):
    # Placeholder function to calculate distance traveled based on speed
    # change number depending on time btwn samples
    distance_traveled = speed / 3600  # Assuming speed is given in miles per hour
    return distance_traveled

def detect_eco_friendly_behavior(obd2_speed_data):
    idling_time = calculate_idling_time(obd2_speed_data)
    eco_mode_usage = detect_eco_mode_usage(obd2_speed_data)

    # Calculate the score based on idling time and eco mode usage
    eco_friendly_score = 100

    if idling_time > 10:  # If idling time exceeds 10 seconds
        eco_friendly_score -= 10

    if not eco_mode_usage:
        eco_friendly_score -= 20

    return eco_friendly_score

def calculate_idling_time(speed_data):
    idling_time = 0
    idle_threshold = 5  # Speed threshold below which the vehicle is considered idling

    for speed in speed_data:
        if speed < idle_threshold:
            idling_time += 1  # Increase idling time by 1 second

    return idling_time

def detect_eco_mode_usage(speed_data):
    eco_mode_threshold = 60  # Speed threshold (in km/h) above which eco mode is expected to be enabled

    for speed in speed_data:
        if speed > eco_mode_threshold:
            return False

    return True

lat = 32.863974
long = -117.202272
speed_limit_test = get_speed_limit(lat, long) # Nobel Drive
print(speed_limit_test)