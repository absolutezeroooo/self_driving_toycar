import edge_impulse_linux.image as ei
import cv2
import os
import numpy as np
import csv

import json


# ====== Load the Edge Impulse Model ======
model_path = os.path.join(os.path.dirname(__file__), "model1.eim")
print(model_path)
model = ei.ImpulseRunner(model_path)
model_info =model.init()
print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
print("Model loaded successfully.")

# ====== Paths ======
image_folder = "/home/1/driving_car_data/saved_images"
csv_folder = "/home/1/driving_car_data"
csv_path = os.path.join(csv_folder, "controller_data.csv")
threshold = 0.2

# ====== Load Ground Truth Data ======
steering_labels = {}
with open(csv_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        filename = row['file_name'].strip()
        try:
            steering = float(row['class_name'])
            steering_labels[filename] = steering
        except ValueError:
            print(f"Invalid steering value in row: {row}")

# ====== Evaluation Storage ======
y_true = []
y_pred = []

# ====== Run Inference ======
try:
    for filename in sorted(os.listdir(image_folder)):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        if filename not in steering_labels:
            print(f"No label for {filename}, skipping.")
            continue

        image_path = os.path.join(image_folder, filename)
        frame = cv2.imread(image_path)

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # img_float = frame_gray.astype(np.float32) / 255.0
        img_list = frame_gray.flatten().tolist()

        # if(filename == "00000.jpg"):
        #     print(img_list)
            
        result = model.classify(img_list)
        prediction = result['result']['classification']['value']
        
        # print(json.dumps(result, indent=2))
        
        actual = steering_labels[filename]
        print(f"{filename}: Predicted = {prediction:.4f}, Actual = {actual:.4f}")

        y_true.append(actual)
        y_pred.append(prediction)

    # ====== Calculate Metrics ======
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mse = np.mean((y_true - y_pred) ** 2)
    accuracy = np.mean(np.abs(y_true - y_pred) <= threshold) * 100

    print("\n=== Evaluation Summary ===")
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Accuracy (|error| <= {threshold}): {accuracy:.2f}%")

except KeyboardInterrupt:
    print("Interrupted.")
finally:
    model.stop()