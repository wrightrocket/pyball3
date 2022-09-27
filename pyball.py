#!/usr/bin/python
# Created by Keith Wright
# 
import os
import sys
import time
import random
import pygame
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

def load_high_score():
    filename = 'highscore.txt'
    try:
        handle = open(filename)
        highscore = int(handle.read())
    except IOError:
        print 'Failed to open "highscore.txt" for reading'
        highscore = 0
    except ValueError:
        highscore = 0
    else:
        handle.close()
    return highscore

def save_high_score(highscore):
    filename = 'highscore.txt'
    try:
        handle = open(filename,'w')
        handle.write(str(highscore))
    except IOError:
        print 'Failed to open "highscore.txt" for writing'
    else:
        handle.close()

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): 
            print 'no sound pass'
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

class Ball(pygame.sprite.Sprite):
    '''pyball created with pygame.draw'''
    def __init__(self, color, num):
        pygame.sprite.Sprite.__init__(self) 
        self.image = self.ballImage(color, num)
        self.rect = self.image.get_rect()
        self.num = num
        BORDERLR = 50
        hpos = random.randint(BORDERLR, width - BORDERLR)
        BORDERTB = 150
        self.height = random.randint(BORDERTB, height - BORDERTB)
	VSPEED = [-2,-3,-4,-5,2,3,4,5]
        self.vspeed = random.choice(VSPEED)
	HSPEED = [-3,-2,2,3]
        self.hspeed = random.choice(HSPEED)
        self.min = height - self.height + self.rect.bottom
        self.max = height - self.rect.bottom
        vpos = random.randint(self.min, self.max)
        self.rect.topleft = hpos, vpos

    def ballImage(self, color, num):
        s = pygame.Surface((50,50))
        s.fill(mycolor['white'])
        s.set_colorkey(mycolor['white'])
        s.convert_alpha()
        pygame.draw.circle(s, color, (25,25), 25, 0)
        font = pygame.font.Font(None, 36)
        text = font.render(str(num), 1, (10, 10, 10))
        textpos = text.get_rect(centerx=s.get_width()/2,
            centery=s.get_height()/2)
        s.blit(text, textpos)
        return s

    def update(self):
        "move the ball across the screen, and turn at the ends"
        if self.rect.left < 0 or self.rect.right > width:
            self.hspeed = -self.hspeed
            bounce_sound.play()
        if self.rect.top  < self.min or self.rect.bottom > height:
            self.vspeed = -self.vspeed
            if self.rect.bottom > height:
                bounce_sound.play()
        ball = self.rect.move((self.hspeed,self.vspeed))
        self.rect = ball

def next_level(numballs,score):
    '''Provide a transition screen between levels'''    
#    global score, highscore,numballs
    level = numballs - 1
    if pygame.font:
        background.fill((0,0,250))
        screen.fill((0,0,250))
        font = pygame.font.Font(None, 36)
        text = font.render('Your Score: %s' % score, 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2,centery=50)
        background.blit(text, textpos)
        text = font.render('Level %s' % level, 1, (10,10,10))
        textpos = text.get_rect(centerx=background.get_width()/2,
            centery=background.get_height()/2)
        background.blit(text, textpos)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        time.sleep(3)
        pygame.event.clear()

def newBalls(numballs):
    global balls 
    global highest
    balls = []
    ballsh = []
    for ball in range(1, numballs + 1):
        newball = Ball((mycolort[ball]),ball)
        balls.append(newball)
        ballsh.append(newball.height)
    for ball in balls:
        if ball.height ==  max(ballsh):
            highest = ball.num
        
def draw_score(score,points,final=False):
    '''Update the score text'''
    if pygame.font:
        background.fill((250,250,250))
        font = pygame.font.Font(None, 36)
        text = font.render("Score: %s  Highest ball?  Points %s" 
            % (score,points), 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text, textpos)
    if final:
        screen.blit(background, (0, 0))
        pygame.display.flip()
        time.sleep(5)        

def greeting(score,final=True):
    global highscore
    if pygame.font:
        background.fill((250,0,0))
        screen.fill((250,0,0))
        font = pygame.font.Font(None, 36)
        if final:
            text = font.render("Your Score: %s  High Score %s" 
                % (score,highscore), 1, (10, 10, 10))
        else:
            text = font.render("pyball by Keith Wright",
                1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2, 
            centery = 50) # BORDERTOP
        background.blit(text, textpos)
        text = font.render('Play (y/n)', 1, (10,10,10))
        textpos = text.get_rect(centerx=background.get_width()/2,
            centery=background.get_height()/2)
        background.blit(text, textpos)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        if score > highscore:
            save_high_score(score)
            highscore = score
        pygame.event.clear()
        while True:
            #for event in pygame.event.poll():
            event = pygame.event.wait()
            if event:
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_n:
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_y:
                    numballs = 2
                    return numballs

def main():
    score = 0
    counter = 0
    points = 100
    numballs = greeting(score, False)
    newBalls(numballs)
    allsprites = pygame.sprite.RenderPlain((balls))
    while 1:
        timer = clock.tick(60)
        counter += timer
        if counter > 100:
            points -= 1
            if points < 0:
                points = 0
            counter = 0
        for event in pygame.event.get():
            correct = None
            if event.type == QUIT:
                numballs = greeting(score)
                score = 0
                numballs = greeting(score)
                points = 100
                newBalls(numballs)
                allsprites = pygame.sprite.RenderPlain((balls))
    	        next_level(numballs,score)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                score = 0
                numballs = greeting(score)
                points = 100
                newBalls(numballs)
                allsprites = pygame.sprite.RenderPlain((balls))
    	        next_level(numballs,score)
            elif event.type == KEYDOWN and event.key > 48 and event.key < 59:
                keypress = event.key - 48 # K_1 == 49...K_9 == 58
                if keypress > 0 and keypress < 10:
                    if keypress == highest:
                        correct = True
                    else:
                        correct = False
                    if correct == True:
                        score += points
                        numballs += 1
                        hit_sound.play()
                        time.sleep(1)
                    elif correct == False:
                        numballs += 1
                        miss_sound.play()
                        time.sleep(1)
                    if numballs == 10:
                        draw_score(score,points,final=True)
                        numballs = greeting(score)
                	score = 0
                    if correct == True or correct == False:
                        points = 100
                        newBalls(numballs)
                        allsprites = pygame.sprite.RenderPlain((balls))
    		        next_level(numballs,score)
        draw_score(score,points)
        allsprites.update()
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__': 
    mycolort = [(250,250,250),(250,0,0),(0,250,0),(0,0,250),
        (250,0,250),(0,250,250),(250,250,0),(125,125,125),(175,0,25),(175,225,0)]
    mycolorn = ['white', 'red','green','blue','purple','cyan','yellow']
    mycolor = dict(zip(mycolorn,mycolort))
    pygame.init()
    screen = pygame.display.set_mode()
    width, height = screen.get_size()
    #size = width, height = 640, 480
    BOTTOMBORDER = 90 
    height -= BOTTOMBORDER
    screen = pygame.display.set_mode((width,height))
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(mycolor['white'])
    screen.blit(background, (0, 0))
    pygame.display.set_caption('pyball')
    pygame.mouse.set_visible(0)
    miss_sound = load_sound('miss.wav')
    hit_sound = load_sound('hit.wav')
    bounce_sound = load_sound('bounce.wav')
    highscore = load_high_score()
    clock = pygame.time.Clock()
    pygame.display.flip()
    main()
