import pandas as pd
import re
import os


# Define a function to split the 'result' column into multiple columns
def split_result_column_optimized(df) :
    # Replace the '\n' in 'Result' column with ';' to make splitting easier
    df['Result'] = df['Result'].str.replace('\n', ';')

    # Split the 'Result' column
    result_split = df['Result'].str.split(';', expand=True)

    # Prepare empty columns for the expected parts
    df['country'] = None
    df['state'] = None
    df['city'] = None
    df['lat_predict'] = None
    df['lon_predict'] = None

    # Define keywords for each part
    keywords = {
        'Country: ' : 'country',
        'State: ' : 'state',
        'City: ' : 'city'
    }

    # Populate the columns based on the keywords
    for col in result_split.columns :
        for key, val in keywords.items() :
            if val == 'country' :
                df[val] = df[val].combine_first(
                    result_split[col].where(result_split[col].str.contains(key)).str.replace(key, '').str.split().str[
                        0])
            else :
                df[val] = df[val].combine_first(
                    result_split[col].where(result_split[col].str.contains(key)).str.replace(key, ''))

    # Extract coordinates
    def extract_coordinates(text) :
        if pd.isnull(text) :
            return None, None
        # Matching various formats of latitude and longitude including decimal degrees and degree-minute-second formats
        match = re.findall(r'(-?\d+(\.\d+)?°?\s*\d*′?\s*\d*″?\s*[NnSsEeWw]?|-?\d+(\.\d+)?°?[NnSsEeWw]?)', text)
        if match and len(match) >= 2 :
            lat, lon = match[-2][0], match[-1][0]
            return lat, lon
        return None, None

    df[['lat_predict', 'lon_predict']] = df.apply(lambda row : pd.Series(extract_coordinates(row['Result'])), axis=1)

    # Drop the original 'Result' and 'FullPath' columns
    df.drop(columns=['Result', 'FullPath'], inplace=True)

    # Rename 'RelativePath' to 'IMG_ID'
    df.rename(columns={'RelativePath' : 'IMG_ID'}, inplace=True)

    return df


# Load the CSV files
im2gps_rgb_images_filename = 'im2gps_rgb_images.csv'
im2gps3k_rgb_images_filename = 'im2gps3k_rgb_images.csv'

im2gps_rgb_images = pd.read_csv(im2gps_rgb_images_filename)
im2gps3k_rgb_images = pd.read_csv(im2gps3k_rgb_images_filename)

# Process both dataframes
im2gps_rgb_images_processed_optimized = split_result_column_optimized(im2gps_rgb_images)
im2gps3k_rgb_images_processed_optimized = split_result_column_optimized(im2gps3k_rgb_images)

# Save the processed dataframes to new CSV files in the root directory
parsed_im2gps_rgb_images_filename = f'parsed_{os.path.basename(im2gps_rgb_images_filename)}'
parsed_im2gps3k_rgb_images_filename = f'parsed_{os.path.basename(im2gps3k_rgb_images_filename)}'

im2gps_rgb_images_processed_optimized.to_csv(parsed_im2gps_rgb_images_filename, index=False)
im2gps3k_rgb_images_processed_optimized.to_csv(parsed_im2gps3k_rgb_images_filename, index=False)
