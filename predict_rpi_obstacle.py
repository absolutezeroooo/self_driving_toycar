# predict_rpi.py

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from vilib import Vilib
from picarx import Picarx
import time

forward_speed = 10
backward_speed = 10

def car_control(move: float, direction: float):
    angle = int(direction * 30)
    px.set_dir_servo_angle(angle)
    if move > 0.2: 
        px.backward(backward_speed)
    elif move >= 0:
        px.forward(0)
    else:
        px.forward(forward_speed)

def obstacle_avoidence(distance: int):
    if(distance <= 15):  
        px.set_dir_servo_angle(0)
        px.backward(backward_speed)
        time.sleep(1)
        
    elif(distance <= 25):
        px.set_dir_servo_angle(25)
        px.forward(forward_speed)
        time.sleep(1)
        
        px.set_dir_servo_angle(0)
        px.forward(forward_speed)
        time.sleep(0.3)
        
        px.set_dir_servo_angle(-25)
        px.forward(forward_speed)
        time.sleep(1.2)
        
    return

# Initialize Camera
Vilib.camera_start()
Vilib.display(local=False, web=True)

# Initialize Car
px = Picarx()

# Load TFLite Model
interpreter = tflite.Interpreter(model_path="model_fp32.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


try:
    while True:
        distance = round(px.ultrasonic.read(), 2) #first check if there are obstacle on the track
        obstacle_avoidence(distance)
            
        frame = Vilib.img
        if frame is None:
            print("Waiting for camera...")
            time.sleep(0.1)
            continue
            
        frame_resized = cv2.resize(frame, (96, 96))
        frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        input_data = frame_gray.astype(np.float32) / 255.0
        input_data = input_data.reshape((1, 96, 96, 1))

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        steering = interpreter.get_tensor(output_details[0]['index'])[0][0]
        print(f"Predicted steering: {steering:.6f}")

        car_control(-1, steering)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping inference...")

finally:
    Vilib.camera_close()
    px.stop()