import os
import csv
import time
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
        return exif_data
    except Exception as e:
        print(f"Error reading EXIF data from {image_path}: {e}")
        return {}


def get_gps_info(exif_data):
    gps_info = {}
    if 'GPSInfo' in exif_data:
        for tag, value in exif_data['GPSInfo'].items():
            gps_tag_name = GPSTAGS.get(tag, tag)
            gps_info[gps_tag_name] = value
    return gps_info


def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)


def parse_gps_info(gps_info):
    if gps_info:
        gps_latitude = gps_info.get('GPSLatitude')
        gps_latitude_ref = gps_info.get('GPSLatitudeRef')
        gps_longitude = gps_info.get('GPSLongitude')
        gps_longitude_ref = gps_info.get('GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != 'N':
                lat = -lat
            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != 'E':
                lon = -lon
            return lat, lon
    return None, None


def process_images_and_save_csv(resource_folder, csv_file):
    results = []
    for root, dirs, files in os.walk(resource_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(('jpg', 'jpeg', 'png')):
                exif_data = get_exif_data(file_path)
                gps_info = get_gps_info(exif_data)
                lat, lon = parse_gps_info(gps_info)
                if lat and lon:
                    results.append((file, lat, lon))
                    print(f"Processed image: {file}, Latitude: {lat}, Longitude: {lon}")  # Debug info
                else:
                    print(f"No GPS data found for image: {file}")

    if results:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Filename', 'Latitude', 'Longitude'])
            writer.writerows(results)
        print(f'Data written to {csv_file}')
    else:
        print("No GPS data found in any images.")


if __name__ == "__main__":
    resource_folder = 'resource'  # 资源文件夹路径
    if not os.path.exists(resource_folder):
        os.makedirs(resource_folder)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    csv_file_path = os.path.join(resource_folder, f'exif_data_{timestamp}.csv')

    process_images_and_save_csv(resource_folder, csv_file_path)
