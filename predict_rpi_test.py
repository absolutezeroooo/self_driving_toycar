# evaluate_tflite_model.py

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import os
import csv

# ====== Paths ======
model_path = "model_fp32.tflite"
image_folder = "/home/1/driving_car_data/saved_images"
csv_path = "/home/1/driving_car_data/controller_data.csv"
threshold = 0.2

# ====== Load Ground Truth Labels ======
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

# ====== Load TFLite Model ======
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# ====== Inference and Evaluation ======
y_true = []
y_pred = []

for filename in sorted(os.listdir(image_folder)):
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue
    if filename not in steering_labels:
        print(f"Skipping {filename} (no label)")
        continue

    image_path = os.path.join(image_folder, filename)
    frame = cv2.imread(image_path)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    input_data = frame_gray.astype(np.float32) / 255.0
    input_data = input_data.reshape((1, 96, 96, 1))

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]

    actual = steering_labels[filename]
    print(f"{filename}: Predicted = {prediction:.4f}, Actual = {actual:.4f}")

    y_true.append(actual)
    y_pred.append(prediction)

# ====== Metrics ======
y_true = np.array(y_true)
y_pred = np.array(y_pred)
mse = np.mean((y_true - y_pred) ** 2)
accuracy = np.mean(np.abs(y_true - y_pred) <= threshold) * 100

print("\n=== Evaluation Summary ===")
print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"Accuracy (|error| <= {threshold}): {accuracy:.2f}%")