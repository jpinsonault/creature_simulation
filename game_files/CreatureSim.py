import os
import pygame
import sys
import random
from pygame import draw
from pygame.locals import *
from collections import deque
from GameObjects import Background
from GameObjects import Creature
from GameObjects import Food
from Window import Window

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

class PyGameBase(object):
    """docstring for PyGameBase"""
    default_key_map = {
        K_w: "w",
        K_s: "s",
        K_a: "a",
        K_d: "d",
        K_e: "e",
        K_q: "q"
    }

    def __init__(self):
        super(PyGameBase, self).__init__()

    def set_key(self, key, value):
        self.key_map[key] = value

    def register_keys(self, key_map):
        self.key_map = key_map

        self.key_presses = dict((value, False) for value in self.key_map.values())


class CreatureSim(PyGameBase):
    """Runs the creature sim game"""

    CAMERA_MOVE_SPEED = .5
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        super(CreatureSim, self).__init__()
        self.running = True
        self.camera = Window(self.WIDTH, self.HEIGHT, x=-(self.WIDTH / 2), y=-(self.HEIGHT / 2))
        self.scene = Background()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.clock = pygame.time.Clock()



    def run(self):
        self.load()

        self.setup_keys()

        self.game_loop()

    def game_loop(self):
        while self.running:
            self.dt = self.clock.tick(60)

            self.handle_events()
            self.move_camera()
            self.render_frame()

    def move_camera(self):
        if self.key_presses["zoom-in"]:
            self.camera.zoom_in(self.dt)
        if self.key_presses["zoom-out"]:
            self.camera.zoom_out(self.dt)

        if self.key_presses["cam-up"]:
            self.camera.move(y_change=-self.dt * self.CAMERA_MOVE_SPEED)
        if self.key_presses["cam-down"]:
            self.camera.move(y_change=self.dt * self.CAMERA_MOVE_SPEED)
        if self.key_presses["cam-left"]:
            self.camera.move(x_change=self.dt * self.CAMERA_MOVE_SPEED)
        if self.key_presses["cam-right"]:
            self.camera.move(x_change=-self.dt * self.CAMERA_MOVE_SPEED)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            self.handle_key_press(event)

    def handle_key_press(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                raise SystemExit()
            try:
                self.key_presses[self.key_map[event.key]] = True
            except KeyError:
                pass
        if event.type == KEYUP:
            try:
                self.key_presses[self.key_map[event.key]] = False
            except KeyError:
                pass

    def load(self):
        self.creatures = []

        for x in range(0, 1000, 20):
            for y in range(0, 1000, 40):
                new_creature = Creature(x=x, y=y, color=WHITE)
                self.creatures.append(new_creature)
                new_creature.reparent_to(self.scene)

        print("Num Creatures: {}".format(len(self.creatures)))

    def update_positions(self):
        pass

    def render_frame(self):
        pygame.display.set_caption(str(self.clock.get_fps()))

        self.screen.fill(BLACK)

        self.scene.draw(self.screen, self.camera)
        
        pygame.display.flip()

    def detect_collisions(self):
        pass

    def setup_keys(self):
        """Sets up key presses"""
        key_map = {
            K_w: "cam-up",
            K_s: "cam-down",
            K_a: "cam-left",
            K_d: "cam-right",
            K_e: "zoom-out",
            K_q: "zoom-in"
        }

        self.register_keys(key_map)
