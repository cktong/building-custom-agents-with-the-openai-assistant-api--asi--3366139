import pandas as pd
from math import sqrt

# Load the data
file_path = 'Untitled Folder/Ranger valley.csv'
df = pd.read_csv(file_path)

# Convert the 'time' column to datetime format
df['time'] = pd.to_datetime(df['time'])

# Extract year and month for grouping
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month

# Function to calculate the heat index ("feels like" temperature)
def calculate_heat_index(temp, rh):
    # Simplified Heat Index formula (in °C)
    hi = 0.5 * (temp + 61.0 + ((temp - 68.0) * 1.2) + (rh * 0.094))
    return hi

# Apply the Heat Index calculation to the DataFrame
df['feels_like_temp'] = df.apply(lambda row: calculate_heat_index(row['temp'], row['rh']), axis=1)

# Group by year and month
grouped = df.groupby(['year', 'month'])

# Initialize lists to store results
results = []

# Loop through each group
for (year, month), group in grouped:
    # Step 1: Calculate total observations
    total_observations = len(group)
    
    # Step 2: Calculate the number of observations where temperature is below 30°C
    above_40_observations = len(group[group['temp'] > 39.9])
    
    # Step 3: Calculate p-hat (proportion)
    p_hat = above_40_observations / total_observations
    
    # Step 4: Calculate the standard error (SE)
    standard_error = sqrt(p_hat * (1 - p_hat) / total_observations)
    
    # Step 5: Set the Z-score for the desired confidence level (1.96 for 95% confidence)
    z_score = 1.96
    
    # Step 6: Calculate the confidence interval
    ci_lower = p_hat - z_score * standard_error
    ci_upper = p_hat + z_score * standard_error
    
    # Calculate the average "feels like" temperature
    avg_feels_like_temp = group['feels_like_temp'].mean()
    
    # Store results
    results.append({
        'Year': year,
        'Month': month,
        'Proportion Above 40°C': p_hat,
        '95% CI Lower': ci_lower,
        '95% CI Upper': ci_upper,
        'Average Feels Like Temperature': avg_feels_like_temp
    })

# Convert the results into a DataFrame for easy viewing
results_df = pd.DataFrame(results)

# Display the results
# import ace_tools as tools; tools.display_dataframe_to_user(name="Temperature Analysis by Month and Year", dataframe=results_df)