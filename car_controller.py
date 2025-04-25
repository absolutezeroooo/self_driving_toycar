import pygame
import time

pygame.init()
pygame.joystick.init() 


try: 
    joystick = pygame.joystick.Joystick(0) #only one joystick is used in our case
    joystick.init() #initialize joystick module
    print("joystick connection established")
except pygame.error: #else print a error msg
    print("Joystick not found, please try again")
    quit()
    
#hat_number = pygame.get_numhats()
# while True:
#     pygame.event.pump()
#     for i in range(joystick.get_numbuttons()):
#         print(f"Button {i}: {joystick.get_button(i)}", end="  ")
#     print()
#     time.sleep(0.1)

while True:
    pygame.event.pump()
    if(joystick.get_button(3)): pygame.quit
    x_axis = joystick.get_axis(2) #right stick left -- right
    y_axis = joystick.get_axis(3) #right stick up -- down
    print(f"X: {x_axis:.4f}, Y: {y_axis:.4f}")
    time.sleep(0.1)
    
pygame.quit()


