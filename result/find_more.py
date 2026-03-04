import pandas as pd

# Load the uploaded CSV files
im2gps_rgb_images = pd.read_csv('im2gps_rgb_images.csv')
im2gps3k_rgb_images = pd.read_csv('im2gps3k_rgb_images.csv')
combined_none_coordinate = pd.read_csv('combined_none_coordinate.csv')

# Concatenate the first two tables to have a single lookup table
all_images = pd.concat([im2gps_rgb_images, im2gps3k_rgb_images])

# Function to extract the explanation part from the result string or return the whole result if no explanation is found
def extract_explanation_or_result(result):
    explanation = None
    for part in result.split('\n'):
        if part.startswith('Explanation:'):
            explanation = part.split('Explanation: ')[-1]
    return explanation if explanation else result

# Apply the updated extraction function to the Result column
all_images['Explanation'] = all_images['Result'].apply(extract_explanation_or_result)

# Merge the combined_none_coordinate with all_images on the relative paths
merged_df = combined_none_coordinate.merge(all_images[['RelativePath', 'Explanation']], left_on='IMG_ID', right_on='RelativePath', how='left')

# Drop the redundant 'RelativePath' column from the merged dataframe
merged_df = merged_df.drop(columns=['RelativePath'])

# Save the final dataframe to a new CSV file
merged_df.to_csv('combined_none_coordinate.csv', index=False)

