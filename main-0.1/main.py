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
FPS = 120

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# constants
x_ground = HEIGHT - 75
n_copies = 200
lr = 0.1

# variables

game_speed = 5
obstacle_timer = 0
obstacle_cooldown = 2000
generation = 1

dino_best = ()
best_nn = []

## classes and functions
def create_dino():
    dino.clear()
    #creating dino
    for i in range(n_copies):
        dino.append(Dino(x_ground))
        dino_group.add(dino[i])
    dino_group.add(dino_best)
    

def game_over():
    global game_speed
    game_speed = 5
    obstacle_group.empty()

def nn(nn_array, i_1, i_2, i_3): 

    ##
    ## w = weights, b = bias, i = input, h_1 = hidden 1, h_2 = hidden 2, o = output
    ## e.g. w_i_h_1 = weights from input layer to hidden 1 layer
    ##
    i = np.array([[i_1*0.01,i_2,i_3*0.05]])
    w_i_h_1 = nn_array[0]
    w_h_1_2 = nn_array[1]
    w_h_2_o = nn_array[2]
    b_i_h_1 = nn_array[3]
    b_h_1_2 = nn_array[4]
    b_h_2_o = nn_array[5]

    h_pre = b_i_h_1 + (w_i_h_1 @ i.T)*0.001
    h_1 = 1 / (1 + np.exp(-h_pre))

    h_pre= b_h_1_2 + (w_h_1_2 @ h_1)
    h_2 = 1 / (1 + np.exp(-h_pre))

    h_pre = b_h_2_o + (w_h_2_o @ h_2)
    o = 1 / (1 + np.exp(-h_pre))

    if (o[0]-o[1]) > 0.2:
        return 2
    elif (o[0]-o[2]) > 0.2:
        return 2
    elif (o[1]-o[0]) > 0.2:
        return 2
    elif (o[1]-o[2]) > 0.2:
        return 2
    elif (o[2]-o[0]) > 0.2:
        return 2
    elif (o[2]-o[1]) > 0.2:
        return 2
    else: return np.argmax(o)



class Dino(pygame.sprite.Sprite):
    
    def __init__(self, x, x_a=0):
        super().__init__()
        self.x = x
        self.x_a = x_a
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.nn = []
        self.output = 0
        self.gravity = 5

        self.rect = pygame.draw.rect(screen, self.color, (25, self.x, 50, 50))
       
        

        if best_nn == []:
            self.nn = [
                np.random.uniform(-100, 100, (8,3)),
                np.random.uniform(-0.5, 0.5, (20,8)),
                np.random.uniform(-0.5, 0.5, (3,20)),
                np.zeros((8, 1)),
                np.zeros((20, 1)),
                np.zeros((3,1))]
        else:

            self.r_nn = [
                np.random.uniform(-100*lr, 100*lr, (8,3)),
                np.random.uniform(-0.5*lr, 0.5*lr, (20,8)),
                np.random.uniform(-0.5*lr, 0.5*lr, (3,20)),
                np.random.uniform(-0.5*lr, 0.5*lr, (8,1)),
                np.random.uniform(-0.5*lr, 0.5*lr, (20,1)),
                np.random.uniform(-0.5*lr, 0.5*lr, (3,1))]

            self.nn = [best + r for best, r in zip(best_nn, self.r_nn)]


    def down(self):
        self.x = x_ground

    def jump(self):
        self.x_a = 35

    def update(self):
        global best_nn, dino_best

        #applying gravity
        if self.x < x_ground:
            self.x += self.gravity
        
        if self.x_a > 0:
            self.x -=3*self.gravity
            self.x_a -=1

        #obstacle_group != None == calculate distance
        if obstacle_group.sprites() != []:
            last_obstacle = obstacle_group.sprites()[0]
            self.distance = last_obstacle.rect.x - self.rect.x
        else: self.distance = 1700

        for obstacle in obstacle_group:
            if self.rect.colliderect(obstacle.rect):
                best_nn = self.nn
                dino_best = dino_group.sprites()
                dino_group.remove(self)



        ##NN CONTROL 
                
        self.output = nn(self.nn, self.distance, game_speed, self.x)

        if self.output == 0:
            if self.x == x_ground:
                self.jump()
        elif self.output == 1:
            self.down()           
            self.x_a = 0

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
    dino_group.update()
    obstacle_group.update()

    game_speed += 0.005

    if dino_group.sprites() == []:
        generation += 1
        game_over()
        create_dino()
        lr -= 0.01*(1/generation)

    #obstacle code
    if pygame.time.get_ticks() - obstacle_timer >= obstacle_cooldown:
        obstacle = Obstacle(random.randint(0,3))
        obstacle_group.add(obstacle)
        obstacle_timer = pygame.time.get_ticks()
        obstacle_cooldown = random.randint(int(2000 - 30*game_speed),int(3000 - 30*game_speed))


    ## pygame essential 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    mainClock.tick(FPS)
    pygame.display.update()