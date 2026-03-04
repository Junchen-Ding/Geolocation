import pandas as pd
import re

# Load the CSV files
file1 = 'parsed_im2gps3k_rgb_images.csv'
file2 = 'parsed_im2gps_rgb_images.csv'

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)


# Define a function to convert various DMS formats to decimal degrees
def dms_to_decimal(dms) :
    if pd.isna(dms) :
        return None
    dms = str(dms)
    pattern = re.compile(r'(-?\d+(\.\d+)?°?\s*\d*′?\s*\d*″?\s*[NnSsEeWw]?|-?\d+(\.\d+)?°?[NnSsEeWw]?)')
    match = pattern.match(dms.strip())

    if not match :
        raise ValueError(f"Invalid DMS format: {dms}")

    dms = match.group(0)
    direction = re.findall(r'[NnSsEeWw]', dms)
    direction = direction[0].upper() if direction else None

    dms = re.sub(r'[NnSsEeWw]', '', dms).strip()

    parts = re.split(r'[°′″\s]+', dms)
    degrees = float(parts[0])
    minutes = float(parts[1]) if len(parts) > 1 and parts[1] else 0
    seconds = float(parts[2]) if len(parts) > 2 and parts[2] else 0

    decimal = degrees + minutes / 60 + seconds / 3600

    if direction in ['S', 'W'] :
        decimal = -decimal

    return decimal


# Apply the conversion function to the relevant columns
if 'lat_predict' in df1.columns and 'lon_predict' in df1.columns :
    df1['lat_predict'] = df1['lat_predict'].apply(dms_to_decimal)
    df1['lon_predict'] = df1['lon_predict'].apply(dms_to_decimal)

if 'lat_predict' in df2.columns and 'lon_predict' in df2.columns :
    df2['lat_predict'] = df2['lat_predict'].apply(dms_to_decimal)
    df2['lon_predict'] = df2['lon_predict'].apply(dms_to_decimal)

# Save the modified dataframes back to CSV files
df1.to_csv(file1, index=False)
df2.to_csv(file2, index=False)
