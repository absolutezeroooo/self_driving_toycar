import pandas as pd
import json
import os
import shutil

# Load CSV
csv_file = r'D:\ELEN6908\driving_car_data\controller_data.csv'
image_folder = r'D:\ELEN6908\driving_car_data\saved_images'
output_folder = r'D:\ELEN6908\edge_impulse_upload'

df = pd.read_csv(csv_file)

# Create output folder
os.makedirs(output_folder, exist_ok=True)

# Initialize labels dictionary (outside the loop!)
labels = {}

# Copy images and prepare labels
for idx, row in df.iterrows():
    img_file = int(row['image_name'])  # Convert to int
    image_file = f"{img_file:05}.jpg"  # Format to 00000.jpg
    label = float(row['controller_data']) # Read label
    
    src_path = os.path.join(image_folder, image_file)
    dst_path = os.path.join(output_folder, image_file)

    if os.path.exists(src_path):
        shutil.copy(src_path, dst_path)
        labels[image_file] = label
    else:
        print(f"Warning: {src_path} not found!")

# After copying all images, save labels.json
with open(os.path.join(output_folder, 'labels.json'), 'w') as f:
    json.dump(labels, f)

print("Finished preparing files")