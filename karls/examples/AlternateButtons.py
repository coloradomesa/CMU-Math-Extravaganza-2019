# use "pip install pygame" to add pygame to python 
import pygame
 
BLUE = (0, 0, 255)  # color of clear in the player
pygame.init()
screen = pygame.display.set_mode([800, 600]) 
pygame.display.set_caption('Click to Jump')
 
click_sound = pygame.mixer.Sound("weepweep.wav") # audio for jump
background_position = [0, 0]
background_image = pygame.image.load("back.bmp").convert() # background image
player_image = pygame.image.load("light2.bmp").convert() # the player image
player_image.set_colorkey(BLUE)
done = False
ax=0 # pixels per second per second
ay=20 
vx=50 # pixels per second
vy=0
x=400 # pixels
y=300
start=pygame.time.get_ticks()
dt=0  # ms of time
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        #elif event.type == pygame.MOUSEBUTTONDOWN:
            #vy=vy-50  # jump up
            #click_sound.play()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                vy=vy-50
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                vy=vy+50
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                vx=vx+50
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                vx=vx-50

    end=pygame.time.get_ticks();
    dt=(end-start)/1000.0 # slice of time in seconds
    start=end
    vx=vx+ax*dt  # update velocities with accelerations for dt seconds
    vy=vy+ay*dt
    x=x+vx*dt  # update positions with velocities for dt seconds
    y=y+vy*dt
    if x < 0:
        x=800+x
    if x > 800:
        x=x-800
    if y < 0:
        y=600+y
    if y > 600:
        y=y-600
    screen.blit(background_image, background_position)
    screen.blit(player_image, [x, y])
    pygame.display.flip()
    pygame.time.wait(10) # let the processor breath
pygame.quit()
