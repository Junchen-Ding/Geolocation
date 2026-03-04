import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Load the CSV files
im2gps_predict = pd.read_csv('parsed_im2gps_rgb_images.csv')
im2gps_truth = pd.read_csv('im2gps_places365.csv')
im2gps3k_predict = pd.read_csv('parsed_im2gps3k_rgb_images.csv')
im2gps3k_truth = pd.read_csv('im2gps3k_places365.csv')

# Rename columns in truth files to match predict files for merging
im2gps_truth_renamed = im2gps_truth.rename(columns={'IMG_ID': 'IMG_ID'})
im2gps3k_truth_renamed = im2gps3k_truth.rename(columns={'IMG_ID': 'IMG_ID'})

# Merge the prediction and truth data on the image name
im2gps_merged = pd.merge(im2gps_predict, im2gps_truth_renamed, on='IMG_ID', suffixes=('_pred', '_truth'))
im2gps3k_merged = pd.merge(im2gps3k_predict, im2gps3k_truth_renamed, on='IMG_ID', suffixes=('_pred', '_truth'))

# Filter out invalid latitude and longitude values
im2gps_merged = im2gps_merged[
    (im2gps_merged['LAT'].between(-90, 90)) &
    (im2gps_merged['LON'].between(-180, 180)) &
    (im2gps_merged['lat_predict'].between(-90, 90)) &
    (im2gps_merged['lon_predict'].between(-180, 180))
]

im2gps3k_merged = im2gps3k_merged[
    (im2gps3k_merged['LAT'].between(-90, 90)) &
    (im2gps3k_merged['LON'].between(-180, 180)) &
    (im2gps3k_merged['lat_predict'].between(-90, 90)) &
    (im2gps3k_merged['lon_predict'].between(-180, 180))
]

# Function to calculate differences and distances
def calculate_differences(df):
    df['Latitude_diff'] = df['LAT'] - df['lat_predict']
    df['Longitude_diff'] = df['LON'] - df['lon_predict']
    df['Geodesic_distance_km'] = df.apply(lambda row: geodesic(
        (row['LAT'], row['LON']),
        (row['lat_predict'], row['lon_predict'])
    ).km, axis=1)
    return df

im2gps_results = calculate_differences(im2gps_merged)
im2gps3k_results = calculate_differences(im2gps3k_merged)

# Select required columns
im2gps_results = im2gps_results[['IMG_ID', 'LAT', 'LON', 'lat_predict', 'lon_predict', 'Latitude_diff', 'Longitude_diff', 'Geodesic_distance_km']]
im2gps3k_results = im2gps3k_results[['IMG_ID', 'LAT', 'LON', 'lat_predict', 'lon_predict', 'Latitude_diff', 'Longitude_diff', 'Geodesic_distance_km']]

# Save the results to CSV
im2gps_results.to_csv('im2gps_results.csv', index=False)
im2gps3k_results.to_csv('im2gps3k_results.csv', index=False)


#import pandas as pd
# import numpy as np
# from geopy.distance import geodesic
# import re
#
# # Load the CSV files
# im2gps_predict = pd.read_csv('im2gps_rgb_images.csv')
# im2gps_truth = pd.read_csv('im2gps_places365.csv')
# im2gps3k_predict = pd.read_csv('im2gps3k_rgb_images.csv')
# im2gps3k_truth = pd.read_csv('im2gps3k_places365.csv')
#
# # Rename columns in truth files to match predict files for merging
# im2gps_truth_renamed = im2gps_truth.rename(columns={'IMG_ID': 'RelativePath'})
# im2gps3k_truth_renamed = im2gps3k_truth.rename(columns={'IMG_ID': 'RelativePath'})
#
# # Merge the prediction and truth data on the image name
# im2gps_merged = pd.merge(im2gps_predict, im2gps_truth_renamed, on='RelativePath', suffixes=('_pred', '_truth'))
# im2gps3k_merged = pd.merge(im2gps3k_predict, im2gps3k_truth_renamed, on='RelativePath', suffixes=('_pred', '_truth'))
#
# # Function to extract coordinates from 'Result' column
# def extract_coordinates(result):
#     match = re.search(r'Coordinates: ([\d\.\-]+), ([\d\.\-]+)', result)
#     if match:
#         return float(match.group(1)), float(match.group(2))
#     return None, None
#
# im2gps_merged['Latitude_pred'], im2gps_merged['Longitude_pred'] = zip(*im2gps_merged['Result'].apply(extract_coordinates))
# im2gps3k_merged['Latitude_pred'], im2gps3k_merged['Longitude_pred'] = zip(*im2gps3k_merged['Result'].apply(extract_coordinates))
#
# # Filter out rows where coordinates could not be extracted
# im2gps_merged = im2gps_merged.dropna(subset=['Latitude_pred', 'Longitude_pred'])
# im2gps3k_merged = im2gps3k_merged.dropna(subset=['Latitude_pred', 'Longitude_pred'])
#
# # Function to calculate differences and distances
# def calculate_differences(df):
#     df['Latitude_diff'] = df['LAT'] - df['Latitude_pred']
#     df['Longitude_diff'] = df['LON'] - df['Longitude_pred']
#     df['Geodesic_distance_km'] = df.apply(lambda row: geodesic(
#         (row['LAT'], row['LON']),
#         (row['Latitude_pred'], row['Longitude_pred'])
#     ).km, axis=1)
#     return df
# im2gps_results = calculate_differences(im2gps_merged)
# im2gps3k_results = calculate_differences(im2gps3k_merged)
#
# # Select required columns
# im2gps_results = im2gps_results[['RelativePath', 'LAT', 'LON', 'Latitude_diff', 'Longitude_diff', 'Geodesic_distance_km']]
# im2gps3k_results = im2gps3k_results[['RelativePath', 'LAT', 'LON', 'Latitude_diff', 'Longitude_diff', 'Geodesic_distance_km']]
#
# # Save the results to CSV
# im2gps_results.to_csv('im2gps_results.csv', index=False)
# im2gps3k_results.to_csv('im2gps3k_results.csv', index=False)