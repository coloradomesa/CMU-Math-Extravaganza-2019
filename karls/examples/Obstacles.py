# use "pip install pygame" to add pygame to python 
import pygame
import random
 
BLUE = (0, 0, 255)  # color of clear in the player
pygame.init()
screen = pygame.display.set_mode([800, 600]) 
pygame.display.set_caption('Click to Jump')
 
click_sound = pygame.mixer.Sound("weepweep.wav") # audio for jump
background_position = [0, 0]
background_image = pygame.image.load("back.bmp").convert() # background image
player_image = pygame.image.load("light1.bmp").convert() # the player image
mine_image = pygame.image.load("light2.bmp").convert()
player_image.set_colorkey(BLUE)
done = False
ax=0 # pixels per second per second
vx=50 # pixels per second
vy=0
x=400 # pixels
y=300
start=pygame.time.get_ticks()
dt=0  # ms of time

#Code for making mine locations randomly on the screen
mines=[]
for i in range(1, 30):
    #mines.append([400, 300])
    mx=random.randint(0, 800)
    my=random.randint(0, 600)
    mines.append([mx, my])

while not done:
    ay=20 
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

    #Draw Mines
    for mine in mines:
        #Check for collision
        if x>=mine[0]-10 and x<=mine[0]+10 and y>=mine[1]-10 and y<=mine[1]+10:
            vx=0
            vy=0
            ay=0
        else:
            screen.blit(mine_image, mine)

    screen.blit(player_image, [x, y])
    pygame.display.flip()
    pygame.time.wait(10) # let the processor breath
pygame.quit()
