import os
import pygame
import sys
sys.path.insert(0, '../')
import random
from random import randrange
from random import uniform
from pygame import draw
from pygame.locals import *
from collections import deque
from GameObjects import Background
from GameObjects import Creature
from GameObjects import Food
from Camera import Camera
from QuadTree import QuadTree

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
    CAM_WIDTH = 800
    CAM_HEIGHT = 800
    WORLD_WIDTH = 100000
    WORLD_HEIGHT = 100000

    def __init__(self):
        super(CreatureSim, self).__init__()
        self.running = True
        # self.camera = Camera(self.CAM_WIDTH, self.CAM_HEIGHT, x=-(self.CAM_WIDTH / 2), y=-(self.CAM_HEIGHT / 2))
        self.camera = Camera(self.CAM_WIDTH, self.CAM_HEIGHT, x=0, y=0, zoom=5.0)
        self.scene = Background()
        self.screen = pygame.display.set_mode((self.CAM_WIDTH, self.CAM_HEIGHT))
        # QuadTree for collision detection
        self.quadtree = QuadTree(bounds=(-self.WORLD_WIDTH/2, -self.WORLD_HEIGHT/2, self.WORLD_WIDTH, self.WORLD_HEIGHT), depth=9)

        self.clock = pygame.time.Clock()
        self.dt = 0

        # Will draw the quadtree overlay if true
        self.draw_quadtree = False

    def run(self):
        self.load()

        self.setup_keys()

        self.game_loop()

    def game_loop(self):
        while self.running:
            self.dt = self.clock.tick()

            self.handle_events()
            self.update_positions()
            self.handle_key_presses()
            self.render_frame()

    def handle_key_presses(self):
        # Camera Zoom
        if self.key_presses["zoom-in"]:
            self.camera.zoom_in(self.dt)
        if self.key_presses["zoom-out"]:
            self.camera.zoom_out(self.dt)

        # Camera movement
        if self.key_presses["cam-up"]:
            self.camera.move(y_change=-self.dt * self.CAMERA_MOVE_SPEED)
        if self.key_presses["cam-down"]:
            self.camera.move(y_change=self.dt * self.CAMERA_MOVE_SPEED)
        if self.key_presses["cam-left"]:
            self.camera.move(x_change=-self.dt * self.CAMERA_MOVE_SPEED)
        if self.key_presses["cam-right"]:
            self.camera.move(x_change=self.dt * self.CAMERA_MOVE_SPEED)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            self.register_key_presses(event)

    def register_key_presses(self, event):
        # Key Down
        ########################
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                raise SystemExit()
            try:
                self.key_presses[self.key_map[event.key]] = True
            except KeyError:
                pass

            if event.key == K_t:
                self.draw_quadtree = not self.draw_quadtree

        # Key Up
        ########################
        if event.type == KEYUP:
            try:
                self.key_presses[self.key_map[event.key]] = False
            except KeyError:
                pass

    def load(self):
        self.creatures = []

        for x in range(400):
            new_creature = Creature(x=randrange(-1500, 1500), y=randrange(-1500, 1500), color=WHITE)
            self.creatures.append(new_creature)
            new_creature.reparent_to(self.scene)
            new_creature.calc_absolute_position()
            
        self.quadtree.insert_objects(self.creatures)

        print("Num Creatures: {}".format(len(self.creatures)))

    def render_frame(self):
        pygame.display.set_caption(str(self.clock.get_fps()))

        self.screen.fill(BLACK)

        self.scene.draw(self.screen, self.camera)
        if self.draw_quadtree:
            self.quadtree.draw_tree(self.screen, self.camera)
        
        pygame.display.flip()

    def update_positions(self):
        for creature in self.creatures:
            network = creature.nn
            network.compute_network()
            outputs = network.get_outputs()
            creature.rotate(self.dt * outputs[0] / 50.0)
            creature.move_forward(self.dt * outputs[1])

        # self.scene.rotate(self.dt * .0005)
        self.quadtree.update_objects(self.creatures)

    def setup_keys(self):
        """Sets up key presses"""
        key_map = {
            K_w: "cam-up",
            K_s: "cam-down",
            K_a: "cam-left",
            K_d: "cam-right",
            K_e: "zoom-out",
            K_q: "zoom-in",
        }

        self.register_keys(key_map)
