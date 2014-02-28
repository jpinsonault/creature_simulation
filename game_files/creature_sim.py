import os
import pygame
import sys
import random
from pygame import draw
from pygame.locals import *
from collections import deque

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

rectangle = [0,0]
camera_dir = [0, 0]
rect_dir = [0, 0]
zoom_dir = 0

RECT_SIZE = 40
MOVEMENT_SPEED = 2
ZOOM_SPEED = 0.01

clock = pygame.time.Clock()

size = width, height = 1000, 800

screen = pygame.display.set_mode(size)
window = None


def main():
    game_loop()


def game_loop():
    running = True
    global rectangle
    global window
    window = Window(width,height)

    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            update_camera_dir(event)
            
        
        rectangle[0] += rect_dir[0]
        rectangle[1] += rect_dir[1]
        window.x_position += camera_dir[0]
        window.y_position += camera_dir[1]
        window.set_zoom(zoom_dir)

        render_frame(rectangle)


def update_camera_dir(event):
    global camera_dir
    global rect_dir
    global zoom_dir

    if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            raise SystemExit()

        if event.key == K_w:
            camera_dir[1] += -MOVEMENT_SPEED
        if event.key == K_s:
            camera_dir[1] += MOVEMENT_SPEED
        if event.key == K_a:
            camera_dir[0] += -MOVEMENT_SPEED
        if event.key == K_d:
            camera_dir[0] += MOVEMENT_SPEED

        if event.key == K_UP:
            rect_dir[1] += -MOVEMENT_SPEED
        if event.key == K_DOWN:
            rect_dir[1] += MOVEMENT_SPEED
        if event.key == K_LEFT:
            rect_dir[0] += -MOVEMENT_SPEED
        if event.key == K_RIGHT:
            rect_dir[0] += MOVEMENT_SPEED

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

        if event.key == K_UP:
            rect_dir[1] = 0
        if event.key == K_DOWN:
            rect_dir[1] = 0
        if event.key == K_LEFT:
            rect_dir[0] = 0
        if event.key == K_RIGHT:
            rect_dir[0] = 0

        if event.key == K_e:
            zoom_dir = 0
        if event.key == K_q:
            zoom_dir = 0

    return camera_dir


def render_frame(r):
    screen.fill(BLACK)
    top_left = window.scale(r)
    top_right = window.scale([r[0] + RECT_SIZE, r[1]])
    bottom_left = window.scale([r[0], r[1] + RECT_SIZE])
    bottom_right = window.scale([r[0] + RECT_SIZE, r[1] + RECT_SIZE])

    draw.aalines(screen, WHITE, True, [top_left, top_right, bottom_right, bottom_left], True)
    pygame.display.flip()


def menu():
    pass


class Window:
    """Hold properties and methods for dealing with zooming and moving the screen"""
    MIN_ZOOM = 0.01
    MAX_ZOOM = 4.0

    def __init__(self, width, height, zoom = 1.0):
        self.width = width
        self.height = height
        # Zoom is a factor, 1.0 being no zoom, 2.0 being twice as many pixels on each axis
        self.zoom = float(zoom)
        # x and y position of the top left of the screen in the virtual world
        self.x_position = 0
        self.y_position = 0

    def set_zoom(self, zoom):
        self.zoom += zoom
        self.zoom = max(self.zoom, self.MIN_ZOOM)
        self.zoom = min(self.zoom, self.MAX_ZOOM)

    def scale(self, coord):
        """Scales a coordinate from the virtual world to the screen"""
        x = int((coord[0] + self.x_position) / self.zoom + self.width/2)
        y = int((coord[1] + self.y_position) / self.zoom + self.height/2)
        return [x, y]


if __name__ == '__main__':
    main()