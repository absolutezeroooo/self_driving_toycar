import edge_impulse_linux.image as ei
import cv2
from PIL import Image
import time
from vilib import Vilib 
from picarx import Picarx
import os
import numpy as np

def car_control(move: float, direction: float):
    angle = int(direction * 30)
    px.set_dir_servo_angle(angle)
    #print(f"angle: {angle}")
    
    if(move > 0.2): px.backward(1)
    elif(move >= 0): 
        px.forward(0)
    else:
        px.forward(1)
    
    #make the car moveforward for 0.5s, then stop
    time.sleep(0.1)
    px.forward(0)
    time.sleep(0.1)

# ====== Initialize Camera ======
Vilib.camera_start()  # Start the Vilib camera
Vilib.display(local=False, web=True)  

px = Picarx()

# ====== Load the Edge Impulse Model ======

# Path to model
model_path = os.path.join(os.path.dirname(__file__), "model1.eim")
model = ei.ImpulseRunner(model_path)
model.init()
print("Model loaded successfully.")

# ====== Inference Loop ======
try:
    while True:
        frame = Vilib.img
            
        if frame is None:
            print("Waiting for camera...")
            time.sleep(0.1)
            continue

        frame_resized = cv2.resize(frame, (96, 96))
        frame_GRAY = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        
        img_flat = frame_GRAY.astype(np.float32)  / 255.0
        img_list = frame_GRAY.flatten().tolist()
        
        # img_flat = frame_GRAY.flatten() / 255.0
        # img_list = img_flat.tolist()

        result = model.classify(img_list)

        # Corrected way to get regression output
        steering_value = result['result']['classification']['value']

        print(f"Predicted steering: {steering_value:.8f}")

        # (Assuming you have a car_control() function)
        car_control(-1, steering_value)

        time.sleep(0.05)  # 20 fps approx

except KeyboardInterrupt:
    print("Exiting...")

finally:
    Vilib.camera_close()
    px.stop()  
