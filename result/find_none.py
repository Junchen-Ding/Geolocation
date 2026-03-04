import pandas as pd

# Load the CSV files
file1 = 'parsed_im2gps3k_rgb_images.csv'
file2 = 'parsed_im2gps_rgb_images.csv'

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# Define a function to check for missing coordinates
def missing_coordinates(df, dataset_name):
    missing_df = df[df['lat_predict'].isna() | df['lon_predict'].isna()][['IMG_ID']]
    missing_df['dataset'] = dataset_name
    return missing_df

# Find missing coordinates in both datasets
missing_df1 = missing_coordinates(df1, 'im2gps3k')
missing_df2 = missing_coordinates(df2, 'im2gps')

# Combine the missing data into one dataframe
combined_missing_df = pd.concat([missing_df1, missing_df2])

# Save the combined dataframe to a new CSV file
combined_missing_df.to_csv('combined_none_coordinate.csv', index=False)