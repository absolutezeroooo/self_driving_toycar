import edge_impulse_linux.image as ei
import cv2
from PIL import Image
import time
from vilib import Vilib 
from picarx import Picarx
import os


def car_control(move: float, direction: float):
    angle = int(direction * 30)
    px.set_dir_servo_angle(angle)
    #print(f"angle: {angle}")
    
    if(move > 0.2): px.backward(40)
    elif(move >= 0): 
        px.forward(0)
    else:
        px.forward(40)

# ====== Initialize Camera ======
Vilib.camera_start()  # Start the Vilib camera
Vilib.display(local=False, web=True)  

px = Picarx()

# ====== Load the Edge Impulse Model ======

# Path to your model
model_path = os.path.join(os.path.dirname(__file__), "model1.eim")
model = ei.ImpulseRunner(model_path)
model.init()

print("Model loaded successfully.")

# ====== Inference Loop ======
try:
    while True:
        # 1. Capture frame from Vilib
        frame = Vilib.img  # Vilib.img is your current camera frame
        
        if frame is None:
            print("Waiting for camera...")
            time.sleep(0.1)
            continue


        # 2. Resize frame to model input size (usually 96x96)
        frame_resized = cv2.resize(frame, (96, 96))


        # 3. Run inference
        result = model.classify(frame_resized)

        # 4. Get the steering value
        steering_value = result['regression']['value']

        # 6. Print out
        print(f"Predicted steering: {steering_value:.3f}")

        # 7. Drive car
        car_control(40, steering_value)
        time.sleep(0.05)  # 20 fps approx

except KeyboardInterrupt:
    print("Exiting...")

finally:
    Vilib.camera_close()
    px.stop()  
