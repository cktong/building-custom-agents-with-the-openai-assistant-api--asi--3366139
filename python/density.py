def estimate_unique_users(density_data, average_duration):
    """
    Function to estimate the number of unique users attending the event.
    Args:
density_data: List of density values captured every minute.
average_duration: Average duration of stay for event attendees (in minutes).
    Returns:
Estimated number of unique users attending the event.
    """
    # Initialize variables
    flow_counts = []  # List to store flow counts for each minute
    total_flow = 0    # Total flow of individuals entering and exiting the event site
    velocity_matrix = []
    # Estimate flow counts
    for i in range(1, len(density_data)):
        # For simplicity, assume higher density indicates people entering, lower density indicates people exiting
        # flow_count = velocity * density_data[i]
        flow_count = max(0, density_data[i] - density_data[i-1])
        flow_counts.append(flow_count)
        try: 
            density_data[i+average_duration] = density_data[i+average_duration] + density_data[i]
        # print("flow counts:")
            print(flow_counts)
        except IndexError:
            print("index error:", i)
    
    # Aggregate flow counts over the duration of the event
    total_flow = sum(flow_counts)
    print(total_flow)
    # Estimate the total number of unique users
    estimated_users = total_flow
    return estimated_users
# Example usage
if __name__ == "__main__":
    # Example density data (replace with actual data), every 15 minutes
    density_data = [0, 10, 30, 50, 60, 100, 120, 150, 180, 200, 180, 160, 140, 120, 100, 80, 60, 50]
    # Average duration of stay (replace with actual value)
    average_duration = 4  # 15 minute intervals, 2 hours
    # Estimate unique users
    estimated_users = estimate_unique_users(density_data, average_duration)
    print("Estimated number of unique users:", estimated_users)