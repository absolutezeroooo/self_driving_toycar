# predict_rpi.py

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from vilib import Vilib
from picarx import Picarx
import time

def car_control(move: float, direction: float):
    angle = int(direction * 30)
    px.set_dir_servo_angle(angle)
    if move > 0.2: 
        px.backward(1)
    elif move >= 0:
        px.forward(0)
    else:
        px.forward(1)

# Initialize Camera
Vilib.camera_start()
Vilib.display(local=False, web=True)

# Initialize Car
px = Picarx()

# Load TFLite Model
interpreter = tflite.Interpreter(model_path="model_int8.tflite")
interpreter.allocate_tensors()

# Get input and output tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Extract input/output quantization parameters
scale_in, zero_point_in = input_details[0]['quantization']
scale_out, zero_point_out = output_details[0]['quantization']

try:
    while True:
        frame = Vilib.img
        if frame is None:
            print("Waiting for camera...")
            time.sleep(0.1)
            continue
        # Step 1: Preprocess the image => Resize and convert to grayscale
        frame_resized = cv2.resize(frame, (96, 96))
        frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        # Flatten image
        input_data = frame_gray.astype(np.float32)
        input_data = input_data.reshape((1, 96, 96, 1))
        # Quantize input data
        input_quant = np.clip(np.round(input_data / scale_in + zero_point_in), 0, 255).astype(np.uint8)


        # ====== Run inference ======
        interpreter.set_tensor(input_details[0]['index'], input_data)        
        interpreter.invoke()

        # Step 2: Get raw model output
        output_data = interpreter.get_tensor(output_details[0]['index'])  

        # Step 3: Dequantize output data
        steering =  (output_data.astype(np.float32) - zero_point_out) * scale_out/255
        steering = steering[0][0]
        
        # steering = interpreter.get_tensor(output_details[0]['index'])[0][0]
        print(f"Predicted steering: {steering:.6f}")

        car_control(-1, steering)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping inference...")

finally:
    Vilib.camera_close()
    px.stop()
