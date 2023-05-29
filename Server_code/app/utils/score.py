def calculate_lane_change_count(gps_data, imu_lateral_acceleration):
    lane_change_count = 0
    previous_lateral_acceleration = 0
    is_lane_change = False
    threshold = 0

    for i in range(len(gps_data)):
        lateral_acceleration = imu_lateral_acceleration[i]

        # Adjust the threshold based on GPS accuracy
        threshold_adjusted = threshold + 2.5  # Adjust the threshold by adding the GPS accuracy range (2.5 meters)


        if abs(lateral_acceleration - previous_lateral_acceleration) > threshold:
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


