import pygame
import time
import os
import csv
import cv2
from picarx import Picarx
from vilib import Vilib
import numpy as np


class data_collector:
    def __init__(self, data_folder, fps):
        self.data_folder = data_folder
        self.fps = fps
        self.image_folder = os.path.join(self.data_folder, "saved_images") #path to the image folder
        self.csv_path = os.path.join(self.data_folder, "controller_data.csv") #path to the csv file
        
        os.makedirs(self.data_folder, exist_ok=True) #make a data folder if does not exist one
        
        self.controller_data_csv = open(self.csv_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.controller_data_csv)
        self.csv_writer.writerow(["file_name", "class_name"])
    
        self.image_number = 0
        self.start_time = time.time()
        
        #initializing camera ... 
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=False,web=True)
        

    def record_data(self, controller_data):
        image_name = f"{self.image_number:05d}.jpg"
        image_path = self.image_folder
        full_image_path = os.path.join(image_path, image_name)

        # Wait until the camera image is ready
        attempts = 0
        while (Vilib.img is None or not hasattr(Vilib.img, "shape")) and attempts < 50:
            time.sleep(0.05)
            attempts += 1

        if Vilib.img is None or not hasattr(Vilib.img, "shape"):
            print("Error: Camera image not ready after waiting")
            return

        # Save the photo using Vilib
        photo_saved = Vilib.take_photo(f"{self.image_number:05d}", path=image_path)

        if not photo_saved:
            print("Warning: Failed to save photo.")
            return

        # Load, convert to grayscale, resize to 96x96, and overwrite
        try:
            img = cv2.imread(full_image_path)
            resized = cv2.resize(img, (96, 96))
            # norm_resized = resized.astype(np.float32) / 255.0
            cv2.imwrite(full_image_path, resized)  # Overwrite the original image
        except Exception as e:
            print(f"Error processing image: {e}")
            return

        # Save joystick control data
        self.csv_writer.writerow([image_name, f"{controller_data:.6f}"])
        print(f"Saved {image_name} with controller value {controller_data}")
        self.image_number += 1
        
        
    def driving_and_collect(self) -> None:
        while(True):
            pygame.event.pump()
            if(joystick.get_button(1)):
                print("stop button pressed, stop recording...")
                break
            elif(joystick.get_button(3)):
                car_control(0, 0)
                print("X button presssed, pausing...")
                
                while(True):
                    pygame.event.pump()
                    if(joystick.get_button(0)):
                        print("A pressed, resuming...")
                        time.sleep(1)
                        break
            else:
                current_time = time.time()
                x_axis = joystick.get_axis(2) #right stick left -- right
                y_axis = joystick.get_axis(1) #controls moving forward or backward
                car_control(y_axis, x_axis)
                if(current_time - self.start_time < 1/self.fps):
                    continue
                else:    
                    self.record_data(x_axis)
                    self.start_time = current_time
 
        print("Closing csv file...")
        self.controller_data_csv.close()
        print("closing camera...")
        Vilib.camera_close()
    
def car_control(move: float, direction: float):
    angle = int(direction * 30)
    px.set_dir_servo_angle(angle)
    #print(f"angle: {angle}")
    
    if(move > 0.2): px.backward(20)
    elif(move >= 0): 
        px.forward(0)
    else:
        px.forward(20)




if __name__ == "__main__":
    pygame.init()
    pygame.joystick.init() 
    try: 
        joystick = pygame.joystick.Joystick(0) #only one joystick is used in our case
        joystick.init() #initialize joystick module
        print("joystick connection established")
    except pygame.error: #else print a error msg
        print("Joystick not found, please try again")
        quit()
        
    px = Picarx()
    
    while True:
        pygame.event.pump()
        if(joystick.get_button(3)): #Press X for exit
            print("exit button pressed, quit...")
            break
        elif(joystick.get_button(0)): #Press A for recording
            print("Recording button pressed, start recording...")
            time.sleep(1)
            collector = data_collector(data_folder="/home/1/driving_car_data", fps=12)
            collector.driving_and_collect()
            
        x_axis = joystick.get_axis(2) #right stick left -- right
        #y_axis = joystick.get_axis(3) #right stick up -- down
        y_axis = joystick.get_axis(1)
        #print(f"X: {x_axis:.4f}, Y: {y_axis:.4f}")
        car_control(y_axis, x_axis)
        time.sleep(0.1)
   
    px.stop()  
    print("exiting pygame...")
    pygame.quit()
    exit(0)
    
