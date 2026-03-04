import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic

# Load the CSV files
im2gps_results = pd.read_csv('im2gps_results.csv')
im2gps3k_results = pd.read_csv('im2gps3k_results.csv')


# Ensure the Geodesic_distance_km column is calculated if not present
def calculate_geodesic_distance(df) :
    if 'Geodesic_distance_km' not in df.columns :
        df['Geodesic_distance_km'] = df.apply(lambda row : geodesic(
            (row['LAT'], row['LON']),
            (row['LAT'] - row['Latitude_diff'], row['LON'] - row['Longitude_diff'])
        ).km, axis=1)
    return df


im2gps_results = calculate_geodesic_distance(im2gps_results)
im2gps3k_results = calculate_geodesic_distance(im2gps3k_results)


# Function to plot the distribution of geodesic distances
def plot_geodesic_distance_distribution(df, title, filename) :
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Geodesic_distance_km'], bins=30, kde=True)
    plt.title(title)
    plt.xlabel('error_km')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(f'{filename}')
    plt.close()


# Function to calculate error metrics for the given dataset
def calculate_error_metrics(df) :
    metrics = {
        'Metric Name' : ['Street level (1 km)', 'City level (25 km)', 'Region level (200 km)', 'Country level (750 km)',
                         'Continent level (2500 km)', 'Median Error (km)'],
        'Metric Value' : [
            (df['Geodesic_distance_km'] <= 1).mean() * 100,
            (df['Geodesic_distance_km'] <= 25).mean() * 100,
            (df['Geodesic_distance_km'] <= 200).mean() * 100,
            (df['Geodesic_distance_km'] <= 750).mean() * 100,
            (df['Geodesic_distance_km'] <= 2500).mean() * 100,
            df['Geodesic_distance_km'].median()
        ]
    }
    return pd.DataFrame(metrics)


# Function to plot the error metrics
def plot_error_metrics(metrics_df, title, filename) :
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Metric Name', y='Metric Value', data=metrics_df)
    plt.title(title)
    plt.xlabel('Metric Name')
    plt.ylabel('Metric Value')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{filename}')
    plt.close()


# Plot the distribution of geodesic distances for both datasets
plot_geodesic_distance_distribution(im2gps_results, 'Error Distribution for im2gps_rgb_images',
                                    'im2gps_error_distribution.png')
plot_geodesic_distance_distribution(im2gps3k_results, 'Error Distribution for im2gps3k_rgb_images',
                                    'im2gps3k_error_distribution.png')

# Calculate error metrics for both datasets
im2gps_metrics = calculate_error_metrics(im2gps_results)
im2gps3k_metrics = calculate_error_metrics(im2gps3k_results)

# Plot error metrics for both datasets
plot_error_metrics(im2gps_metrics, 'Error Metrics for im2gps_rgb_images', 'im2gps_error_metrics.png')
plot_error_metrics(im2gps3k_metrics, 'Error Metrics for im2gps3k_rgb_images', 'im2gps3k_error_metrics.png')


# Function to sample and analyze images with the highest and lowest errors
def analyze_samples(df, n=5, dataset_name='dataset') :
    highest_errors = df.nlargest(n, 'Geodesic_distance_km')
    lowest_errors = df.nsmallest(n, 'Geodesic_distance_km')

    print(f"Highest errors for {dataset_name}:")
    print(highest_errors[['IMG_ID', 'LAT', 'LON', 'lat_predict', 'lon_predict', 'Latitude_diff', 'Longitude_diff', 'Geodesic_distance_km']])
    print(f"\nLowest errors for {dataset_name}:")
    print(lowest_errors[['IMG_ID', 'LAT', 'LON', 'lat_predict', 'lon_predict', 'Latitude_diff', 'Longitude_diff', 'Geodesic_distance_km']])

    return highest_errors, lowest_errors


# Analyze samples from both datasets
high_errors_im2gps, low_errors_im2gps = analyze_samples(im2gps_results, dataset_name='im2gps')
high_errors_im2gps3k, low_errors_im2gps3k = analyze_samples(im2gps3k_results, dataset_name='im2gps3k')

# Save results to CSV for each dataset
im2gps_results.to_csv('im2gps_analysis_results.csv', index=False)
im2gps3k_results.to_csv('im2gps3k_analysis_results.csv', index=False)

# Combine and save samples for visualization if needed
combined_samples = pd.concat([high_errors_im2gps, low_errors_im2gps, high_errors_im2gps3k, low_errors_im2gps3k],
                             keys=['high_im2gps', 'low_im2gps', 'high_im2gps3k', 'low_im2gps3k']).reset_index(
    level=0).rename(columns={'level_0' : 'SampleType'})

combined_samples.to_csv('combined_im2gps_analysis_results.csv', index=False)

# Save metrics to CSV
im2gps_metrics.to_csv('im2gps_metrics.csv', index=False)
im2gps3k_metrics.to_csv('im2gps3k_metrics.csv', index=False)

# Display the images from samples
for index, row in combined_samples.iterrows() :
    print(
        f"Sample Type: {row['SampleType']}, Image: {row['IMG_ID']}, Geodesic Distance: {row['Geodesic_distance_km']:.2f} km")

# Plot all four images in one figure
fig, axes = plt.subplots(2, 2, figsize=(20, 12))

# Error distribution plots
sns.histplot(im2gps_results['Geodesic_distance_km'], bins=30, kde=True, ax=axes[0, 0])
axes[0, 0].set_title('Error Distribution for im2gps_rgb_images')
axes[0, 0].set_xlabel('error_km')
axes[0, 0].set_ylabel('Count')

sns.histplot(im2gps3k_results['Geodesic_distance_km'], bins=30, kde=True, ax=axes[0, 1])
axes[0, 1].set_title('Error Distribution for im2gps3k_rgb_images')
axes[0, 1].set_xlabel('error_km')
axes[0, 1].set_ylabel('Count')

# Error metrics plots
sns.barplot(x='Metric Name', y='Metric Value', data=im2gps_metrics, ax=axes[1, 0])
axes[1, 0].set_title('Error Metrics for im2gps_rgb_images')
axes[1, 0].set_xlabel('Metric Name')
axes[1, 0].set_ylabel('Metric Value')
axes[1, 0].set_xticks(range(len(im2gps_metrics)))
axes[1, 0].set_xticklabels(im2gps_metrics['Metric Name'], rotation=45)

sns.barplot(x='Metric Name', y='Metric Value', data=im2gps3k_metrics, ax=axes[1, 1])
axes[1, 1].set_title('Error Metrics for im2gps3k_rgb_images')
axes[1, 1].set_xlabel('Metric Name')
axes[1, 1].set_ylabel('Metric Value')
axes[1, 1].set_xticks(range(len(im2gps3k_metrics)))
axes[1, 1].set_xticklabels(im2gps3k_metrics['Metric Name'], rotation=45)

plt.tight_layout()
plt.savefig('all_metrics.png')
plt.show()
