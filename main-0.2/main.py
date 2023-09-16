import pygame
import random
import numpy as np
from sys import exit

pygame.init()

## setting the game configurations 
WIDTH = 1500
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("nn dino")
mainClock = pygame.time.Clock()
FPS = 60

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# constants
x_ground = HEIGHT - 75
n_copies = 100
lr = 0.1

# variables

mask = False
time_multiplayer = 1

game_speed = 5
obstacle_timer = 0
obstacle_cooldown = 2000
generation = 1
dino_distance = 1700

key_c = 0

dino_best = ()
best_nn = []

## classes and functions

def create_dino(n=n_copies):
    dino.clear()
    #creating dino
    for i in range(n):
        dino.append(Dino(x_ground))
        dino_group.add(dino[i])
    dino_group.add(dino_best)
    
def game_over():
    global game_speed
    game_speed = 5
    obstacle_group.empty()
    create_dino()

def nn(nn_array, i_1, i_2, i_3): 

    ##
    ## w = weights, b = bias, i = input, h_1 = hidden 1, h_2 = hidden 2, o = output
    ## e.g. w_i_h_1 = weights from input layer to hidden 1 layer
    ##
    i = np.array([[i_1*0.001,i_2*0.08,i_3*0.0015]])
    w_i_h_1 = nn_array[0]
    w_h_1_2 = nn_array[1]
    w_h_2_o = nn_array[2]
    b_i_h_1 = nn_array[3]
    b_h_1_2 = nn_array[4]
    b_h_2_o = nn_array[5]

    h_pre = b_i_h_1 + (w_i_h_1 @ i.T)
    h_1 = 1 / (1 + np.exp(-h_pre))

    h_pre= b_h_1_2 + (w_h_1_2 @ h_1)*1.03
    h_2 = 1 / (1 + np.exp(-h_pre))

    h_pre = b_h_2_o + (w_h_2_o @ h_2)
    o = 1 / (1 + np.exp(-h_pre))

    if (o[0]-o[1]) > 0.15:   return 2
    elif (o[1]-o[0]) > 0.15: return 2
    else: return np.argmax(o)

def display_text(text, x, y):
    font = pygame.font.SysFont("Arial", 21)
    f_text = font.render(text, True, WHITE)
    screen.blit(f_text, (x, y))
    
class Dino(pygame.sprite.Sprite):
    
    def __init__(self, x, x_a=0):
        super().__init__()
        self.x = x
        self.x_a = x_a
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.nn = []
        self.output = 2
        self.gravity = 5
        self.a = random.randint(5, 20)
        self.b = random.randint(5, 20)

        self.rect = pygame.draw.rect(screen, self.color, (25, self.x, 50, 50))

        if best_nn == []:
            self.nn = [
                np.random.uniform(-50, 50, (self.a,3)),
                np.random.uniform(-0.5, 0.5, (self.b,self.a)),
                np.random.uniform(-0.5, 0.5, (3,self.b)),
                np.zeros((self.a, 1)),
                np.zeros((self.b, 1)),
                np.zeros((3,1))]
        else:

            self.pre_nn = [
                np.random.uniform(-50*lr, 50*lr, (self.a,3)),
                np.random.uniform(-0.5*lr, 0.5*lr, (self.b,self.a)),
                np.random.uniform(-0.5*lr, 0.5*lr, (3,self.b)),
                np.random.uniform(-50*lr, 50*lr, (self.a,1)),
                np.random.uniform(-0.5*lr, 0.5*lr, (self.b,1)),
                np.random.uniform(-0.5*lr, 0.5*lr, (3,1))]

            self.nn = [best + r for best, r in zip(best_nn, self.pre_nn)]


    def down(self):
        self.x = x_ground
        self.x_a = 0

    def jump(self):
        if self.x == x_ground:
            self.x_a = 35

    def update(self):
        global best_nn, dino_best, dino_distance

        #applying gravity
        if self.x < x_ground:
            self.x += self.gravity
        
        if self.x_a > 0:
            self.x -=3*self.gravity
            self.x_a -=1

        #obstacle_group != None == calculate distance

        for obstacle in obstacle_group:
            if self.rect.colliderect(obstacle.rect):
                best_nn = self.nn
                dino_best = dino_group.sprites()
                dino_group.remove(self)

        ##NN CONTROL 
                
        self.output = nn(self.nn, dino_distance, game_speed, self.x)

        if self.output == 0:
            self.jump()
        elif self.output == 1:
            self.down()           

        ##Draw rect
        self.rect = pygame.draw.rect(screen, self.color, (25, self.x, 50, 50))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, TYPE, y=(WIDTH + 200)):
        super().__init__()
        self.TYPE = TYPE
        self.y = y

        if self.TYPE == 0: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground, 50, 50))
        if self.TYPE == 1: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground - 50, 50, 100))
        if self.TYPE == 2: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground, 150, 50))
        if self.TYPE == 3: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground - 50, 100, 100))

    def update(self):
        self.y -= game_speed

        if self.y < -150:
            obstacle_group.remove(self)
            
        #drawing obstacle
        if self.TYPE == 0: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground, 50, 50))
        if self.TYPE == 1: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground - 50, 50, 100))
        if self.TYPE == 2: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground, 150, 50))
        if self.TYPE == 3: self.rect = pygame.draw.rect(screen, WHITE, (self.y, x_ground - 50, 100, 100))

## Objects

#Dino group
dino = []
dino_group = pygame.sprite.Group()

#obstacle group
obstacle_group = pygame.sprite.Group()
obstacle = Obstacle(0)

create_dino()

while True:
    screen.fill("black")

    
    ## update

    dino_group.update()
    
    # game over check

    if dino_group.sprites() == []:
        generation += 1
        game_over()
        lr -= 0.05*(1/generation)

    if mask: 
        screen.fill("black")
        dino_group.sprites()[-1].update()

    obstacle_group.update()

    game_speed += 0.005

    ## calculate distance between dino-obstacle
    if obstacle_group.sprites() != []:
        last_obstacle = obstacle_group.sprites()[0]
        dino_distance = last_obstacle.rect.x - dino[0].x
    else: dino_distance = 1700

    ## obstacle code
    if pygame.time.get_ticks() - obstacle_timer >= obstacle_cooldown:
        obstacle = Obstacle(random.randint(0,3))
        obstacle_group.add(obstacle)
        obstacle_timer = pygame.time.get_ticks()
        obstacle_cooldown = random.randint(int(2000 - 30*game_speed),int(3000 - 30*game_speed))

    ## Display default text
    display_text(f'Game speed: {round(game_speed,1)}', 1300, 15)
    display_text(f'Generation: {generation}', 1300, 40)
    display_text(f'number of copies: {len(dino_group.sprites())}', 1300, 65)
    display_text(f'Time multiplayer (v): {time_multiplayer}', 1300, 90)
    display_text(f'Mask on (m): {mask}', 1300, 115)

    ## key controls
    if key_c > 0: key_c -= 1
    else: 
        key = pygame.key.get_pressed()

        if key [pygame.K_v]:
            if time_multiplayer == 1 and key_c == 0: 
                time_multiplayer = 2
                key_c = 15
            if time_multiplayer == 2 and key_c == 0: 
                time_multiplayer = 4
                key_c = 30 
            if time_multiplayer == 4 and key_c == 0: 
                time_multiplayer = 0.5
                key_c = 60
            if time_multiplayer == 0.5 and key_c == 0: 
                time_multiplayer = 1
                key_c = 120

        elif key [pygame.K_m]:
            if mask and key_c == 0: 
                mask = False
                key_c = 60 
            elif mask == False and key_c == 0: 
                mask = True
                key_c = 60 

    ## pygame essential 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    mainClock.tick(FPS*time_multiplayer)
    pygame.display.update()