import os
import imgInfo.main as im

file_path = '/Users/junchen/Desktop/script/resource/yfcc4k_rgb_images/25935894.jpg'

# Check if the file exists
if os.path.exists(file_path):
    result = im.info(file_path)
    print(getattr(result, 'meta_data')['comment'])
    print(type(result))
else:
    print(f"File not found: {file_path}")
