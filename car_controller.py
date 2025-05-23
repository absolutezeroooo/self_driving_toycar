import pygame
import time
from picarx import Picarx



    
def car_control(move: float, direction: float):
    angle = int(direction * 30)
    px.set_dir_servo_angle(angle)
    print(f"angle: {angle}")
    
    if(move > 0.2): px.backward(40)
    elif(move >= 0): 
        px.forward(0)
    else:
        px.forward(40)




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
        if(joystick.get_button(3)): 
            break
        x_axis = joystick.get_axis(2) #right stick left -- right
        #y_axis = joystick.get_axis(3) #right stick up -- down
        y_axis = joystick.get_axis(1)
        #print(f"X: {x_axis:.4f}, Y: {y_axis:.4f}")
        car_control(y_axis, x_axis)
        time.sleep(0.1)
   
    px.stop()  
    pygame.quit()
    
