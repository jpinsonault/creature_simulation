import os
import pygame
import sys
import random
from pygame import draw
from pygame.locals import *
from collections import deque
from CreatureSim import CreatureSim
from GameObjects import Background
from GameObjects import Creature
from GameObjects import Food
from Window import Window

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

camera_dir = [0, 0]
rect_dir = [0, 0]
zoom_dir = 0

RECT_SIZE = 40
MOVEMENT_SPEED = 2
ZOOM_SPEED = 0.01

clock = pygame.time.Clock()

size = width, height = 1000, 800

screen = pygame.display.set_mode(size)
scene = None
window = None


def main():
    game_loop()


def game_loop():
    running = True
    global rectangle
    global window
    global scene
    window = Window(width,height, x=-(width / 2), y=-(height / 2))
    scene = Background()
    creatures = []

    for x in range(0, 1000, 10):
        for y in range(0, 1000, 40):
            new_creature = Creature(x=x, y=y, color=WHITE)
            creatures.append(new_creature)
            new_creature.reparent_to(scene)

    print("Num Creatures: {}".format(len(creatures)))

    while running:
        dt = clock.tick(70)
        pygame.display.set_caption("Press Esc to quit. FPS: %.2f" % (clock.get_fps()))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            update_camera_dir(event)
            
        window.move(*camera_dir)
        window.set_zoom(zoom_dir)

        render_frame()


def update_camera_dir(event):
    global camera_dir
    global rect_dir
    global zoom_dir

    if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            raise SystemExit()

        if event.key == K_w:
            camera_dir[1] += MOVEMENT_SPEED
        if event.key == K_s:
            camera_dir[1] += -MOVEMENT_SPEED
        if event.key == K_a:
            camera_dir[0] += MOVEMENT_SPEED
        if event.key == K_d:
            camera_dir[0] += -MOVEMENT_SPEED

        if event.key == K_e:
            zoom_dir += ZOOM_SPEED
        if event.key == K_q:
            zoom_dir += -ZOOM_SPEED


    if event.type == KEYUP:
        if event.key == K_w:
            camera_dir[1] = 0
        if event.key == K_s:
            camera_dir[1] = 0
        if event.key == K_a:
            camera_dir[0] = 0
        if event.key == K_d:
            camera_dir[0] = 0

        if event.key == K_e:
            zoom_dir = 0
        if event.key == K_q:
            zoom_dir = 0

    return camera_dir


def render_frame():
    screen.fill(BLACK)

    scene.draw(screen, window)
    
    pygame.display.flip()


def menu():
    pass


if __name__ == '__main__':
    # main()
    game = CreatureSim()
    game.run()