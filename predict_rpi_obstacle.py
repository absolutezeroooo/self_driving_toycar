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
interpreter = tflite.Interpreter(model_path="model_fp32.tflite")
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
        distance = round(px.ultrasonic.read(), 2)
        
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





from picarx import Picarx
import time

POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around,
                    # < 20 backward

def main():
    try:
        px = Picarx()
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo

        while True:
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ",distance)
            if distance >= SafeDistance:
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            elif distance >= DangerDistance:
                px.set_dir_servo_angle(30)
                px.forward(POWER)
                time.sleep(0.1)
            else:
                px.set_dir_servo_angle(-30)
                px.backward(POWER)
                time.sleep(0.5)

    finally:
        px.forward(0)


if __name__ == "__main__":
    main()