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

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

try:
    while True:
        frame = Vilib.img
        if frame is None:
            print("Waiting for camera...")
            time.sleep(0.1)
            continue

        frame_resized = cv2.resize(frame, (96, 96))
        frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        input_data = frame_gray.astype(np.float32)
        scale, zero_point = input_details[0]['quantization']
        input_data = input_data / scale + zero_point
        if input_details[0]['dtype'] == np.uint8:
            input_data = np.clip(np.round(input_data), 0, 255).astype(np.uint8)
        else:  # assume int8
            input_data = np.clip(np.round(input_data), -128, 127).astype(np.int8)
        input_data = input_data.reshape((1, 96, 96, 1))


        # frame_resized = cv2.resize(frame, (96, 96))
        # frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        # input_data = frame_gray.astype(np.float32) / 255.0
        # input_data = input_data.reshape((1, 96, 96, 1))

        interpreter.set_tensor(input_details[0]['index'], input_data)
        
        interpreter.invoke()

        # Step 2: Get raw model output
        output_data = interpreter.get_tensor(output_details[0]['index'])  # ← comes from internal memory

        # Step 3: Dequantize if model is quantized
        out_scale, out_zero_point = output_details[0]['quantization']
        steering = (output_data.astype(np.float32) - out_zero_point) * out_scale
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
