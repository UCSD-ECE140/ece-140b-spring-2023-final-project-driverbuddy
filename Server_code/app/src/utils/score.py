import statistics
import math
import requests
import googlemaps

def get_speed_limit(latitude, longitude):
    # Fetch the expected speed limit from the Google Maps API
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={GOOGLE_MAPS_API_KEY}'
    response = requests.get(url)

    if response.status_code == 200:
        try:
            result = response.json()
            speed_limit = result['results'][0]['speed_limit']
            return speed_limit
        except (KeyError, IndexError):
            pass

    # If unable to fetch the speed limit, return a default value
    return None

def detect_speeding_instances(speed_data, lat, lng):
    speeding_instances = 0
    threshold = 5 # mph over speed limit threshold
    lat_lng_data = [(lat[i], lng[i]) for i in range(0, len(lat))]
    # Iterate over the speed data and latitude/longitude data
    for speed, (lat, lng) in zip(speed_data, lat_lng_data):
        speed_limit = get_speed_limit(lat, lng)
        if speed_limit is not None and speed > (speed_limit + threshold):
            speeding_instances += 1

    return speeding_instances

def calculate_lane_change_count(gps_data, imu_lateral_acceleration):
    lane_change_count = 0
    previous_lateral_acceleration = 0
    is_lane_change = False
    threshold = 0

    for i in range(len(gps_data)):
        lateral_acceleration = imu_lateral_acceleration[i]

        # Adjust the threshold based on GPS accuracy
        # Remove/edit adjustment post testing
        threshold_adjusted = threshold + 2.5  # Adjust the threshold by adding the GPS accuracy range (2.5 meters)

        if abs(lateral_acceleration - previous_lateral_acceleration) > threshold_adjusted:
            # Significant change in lateral acceleration, potential lane change
            if not is_lane_change:
                # Start of a new lane change event
                lane_change_count += 1
                is_lane_change = True
        else:
            # No significant change in lateral acceleration, no lane change
            is_lane_change = False

        previous_lateral_acceleration = lateral_acceleration

    return lane_change_count

def calculate_hard_braking_count(longitudinal_acceleration_data, deceleration_threshold):
    # Initialize variables
    hard_braking_count = 0
    is_hard_braking = False

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

def detect_aggressive_acceleration(obd2_speed_data, time_data, threshold):
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
        time_change = time_data[i+1] - time_data[i]
        acceleration_change.append(acceleration_rate_change / time_change)

    # Detect instances of aggressive acceleration
    aggressive_acceleration_indices = []
    for i in range(len(acceleration_change)):
        if acceleration_change[i] > threshold:
            aggressive_acceleration_indices.append(i)

    # Return count of instances of aggressive acceleration
    return len(aggressive_acceleration_indices)

def calculate_driving_score(speeding_count, hard_braking_count, aggressive_acceleration_count, lane_departure_count, total_distance, total_duration):
    # Weightage for each driving parameter
    speeding_weight = 0.2
    hard_braking_weight = 0.2
    aggressive_acceleration_weight = 0.2
    lane_departure_weight = 0.2
    distance_weight = 0.1
    duration_weight = 0.1

    # Normalize the distance and duration values
    normalized_distance = total_distance / 1000  # Assuming total_distance is in meters
    normalized_duration = total_duration / 3600  # Assuming total_duration is in seconds

    # Score calculation
    speeding_score = max(1 - speeding_count / (normalized_distance + 1), 0)
    hard_braking_score = max(1 - hard_braking_count / (normalized_distance + 1), 0)
    aggressive_acceleration_score = max(1 - aggressive_acceleration_count / (normalized_distance + 1), 0)
    lane_departure_score = max(1 - lane_departure_count / (normalized_distance + 1), 0)
    distance_score = max(1 - normalized_distance / 100, 0)  # Normalize distance to a maximum of 100 km
    duration_score = max(1 - normalized_duration / 2, 0)  # Normalize duration to a maximum of 2 hours

    overall_score = (speeding_score * speeding_weight +
                     hard_braking_score * hard_braking_weight +
                     aggressive_acceleration_score * aggressive_acceleration_weight +
                     lane_departure_score * lane_departure_weight +
                     distance_score * distance_weight +
                     duration_score * duration_weight)

    return overall_score

# Example usage
score = calculate_driving_score(speeding_count=2, hard_braking_count=1, aggressive_acceleration_count=3, lane_departure_count=0, total_distance=8500, total_duration=7200)
print(f"Driving Score: {score}")

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
    harsh_cornering = detect_harsh_cornering(imu_acceleration_data)
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

    # Determine if the acceleration and RPM change are within a desired threshold
    if acceleration_std < 2.0 and rpm_change_std < 500:
        smooth_acceleration_score = 100
    else:
        smooth_acceleration_score = 0

    return smooth_acceleration_score

def detect_smooth_braking(obd2_speed_data, obd2_rpm_data):
    deceleration = calculate_deceleration(obd2_speed_data)
    rpm_change = calculate_rpm_change(obd2_rpm_data)

    # Calculate the standard deviation of deceleration and RPM change
    deceleration_std = statistics.stdev(deceleration)
    rpm_change_std = statistics.stdev(rpm_change)

    # Determine if the deceleration and RPM change are within a desired threshold
    if deceleration_std < 2.0 and rpm_change_std < 500:
        smooth_braking_score = 100
    else:
        smooth_braking_score = 0

    return smooth_braking_score

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
    distance_traveled = speed / 3600  # Assuming speed is given in meters per hour
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
    idle_threshold = 5  # Speed threshold (in km/h) below which the vehicle is considered idling

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

    return stability_score * 100

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

def calculate_speed_control_score(speed_data):
    # Define thresholds for speed control
    max_speed_threshold = 120.0 

    # Calculate the maximum speed in the data
    max_speed = max(speed_data)

    # Assign score based on the maximum speed compared to the threshold
    if max_speed <= max_speed_threshold:
        speed_control_score = 10.0
    else:
        speed_control_score = max(0.0, 10.0 - (max_speed - max_speed_threshold))

    return speed_control_score

def calculate_safety_score(longitudinal_acceleration_data, lateral_acceleration_data, steering_angle_data, speed_data):
    # Define scoring weights for different factors
    smooth_acceleration_weight = 0.2
    smooth_braking_weight = 0.2
    smooth_turns_weight = 0.2
    steering_control_weight = 0.3
    speed_control_weight = 0.1

    # Calculate scores for each factor
    smooth_acceleration_score = smooth_acceleration_weight * calculate_smooth_acceleration_score(longitudinal_acceleration_data)
    smooth_braking_score = smooth_braking_weight * calculate_smooth_braking_score(longitudinal_acceleration_data)
    smooth_turns_score = smooth_turns_weight * calculate_smooth_turns_score(lateral_acceleration_data)
    steering_control_score = steering_control_weight * calculate_steering_stability_score(steering_angle_data)
    speed_control_score = speed_control_weight * calculate_speed_control_score(speed_data)

    # Calculate the total safety score
    safety_score = (
        smooth_acceleration_score +
        smooth_braking_score +
        smooth_turns_score +
        steering_control_score +
        speed_control_score
    )

    return safety_score

# for sharp and wide turns
def detect_harsh_cornering(imu_yaw_data, gps_lat_data, gps_lon_data):
    harsh_cornering_count = 0
    threshold = 10 # replace with actual threshold
    # Iterate over the data points
    for i in range(1, len(imu_yaw_data)):
        current_yaw = imu_yaw_data[i]
        previous_yaw = imu_yaw_data[i - 1]

        # Calculate change in yaw angle
        yaw_change = current_yaw - previous_yaw

        # Calculate distance between GPS points
        lat1 = gps_lat_data[i - 1]
        lon1 = gps_lon_data[i - 1]
        lat2 = gps_lat_data[i]
        lon2 = gps_lon_data[i]
        distance = calculate_distance(lat1, lon1, lat2, lon2)

        # Calculate lateral acceleration
        lateral_acceleration = calculate_lateral_acceleration(yaw_change, distance)

        # Check if lateral acceleration exceeds a threshold
        if lateral_acceleration > threshold:
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

def calculate_lateral_acceleration(yaw_change, distance):
    # Convert yaw change to radians
    yaw_change_rad = math.radians(yaw_change)

    # Calculate lateral acceleration
    lateral_acceleration = math.pow(yaw_change_rad, 2) * distance

    return lateral_acceleration