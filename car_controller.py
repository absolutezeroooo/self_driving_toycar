import pygame


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

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            x_axis = joystick.get_axis(3) #right stick left -- right
            y_axis = joystick.get_axis(4) #right stick up -- down
            print(f"X: {x_axis:.4f}, Y: {y_axis:.4f}")

pygame.quit()

# while True:
#     pygame.event.pump()
#     x_axis = joystick.get_axis(0)  # Left stick horizontal
#     y_axis = joystick.get_axis(1)  # Left stick vertical
#     print(f"X: {x_axis:.2f}, Y: {y_axis:.2f}")


