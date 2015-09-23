import pygame
import sys
import pickle
from random import randrange
from pygame.locals import *
from collections import namedtuple

# User made libraries
from GameObjects import Background
from GameObjects import Creature
from GameObjects import Food
from Camera import Camera
from QuadTree import QuadTree
from Breeder import Breeder
from UserInterface import UserInterface
from UserInterface import TextBox
from UserInterface import MultilineTextBox
from StatsTracker import StatsTracker
from SceneGraph import SceneGraph
from SceneGraph import OldStyleTransformer

from Colors import *

CreatureStats = namedtuple('CreatureStats', 'max, average, top_10_percent')


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
        super().__init__()
        self.clock = pygame.time.Clock()

        pygame.init()

    def set_key(self, key, value):
        self.key_map[key] = value

    def register_keys(self, key_map):
        self.key_map = key_map

        self.key_presses = dict((value, False) for value in self.key_map.values())


class CreatureSim(PyGameBase):
    """Runs the creature sim game"""
    CAMERA_MOVE_SPEED = .5

    GAME_SPEED_INCREMENT = .1
    MAX_GAME_SPEED = 2
    MIN_GAME_SPEED = .1
    WORLD_WIDTH = 100000
    WORLD_HEIGHT = 100000
    SELECTED_COLOR = GREEN

    def __init__(self):
        super().__init__()
        self.infoObject = pygame.display.Info()
        self.CAM_HEIGHT = self.infoObject.current_h - 80
        self.CAM_WIDTH = int(self.infoObject.current_w/2-100)
        self.num_of_creatures = 180
        self.num_of_food = 100
        self.game_bounds = (-5000, 5000)

        self.running = True
        # self.camera = Camera(self.CAM_WIDTH, self.CAM_HEIGHT, x=-(self.CAM_WIDTH / 2), y=-(self.CAM_HEIGHT / 2))
        self.camera = Camera(self.CAM_WIDTH, self.CAM_HEIGHT, x=0, y=0, zoom=1.0)
        self.scene = Background()
        self.screen = pygame.display.set_mode((self.CAM_WIDTH, self.CAM_HEIGHT))

        self.fullscreen = False

        # QuadTree for collision detection
        self.quadtree = QuadTree(
            bounds=(
                -self.WORLD_WIDTH/2,
                -self.WORLD_HEIGHT/2,
                self.WORLD_WIDTH,
                self.WORLD_HEIGHT),
            depth=9)
 
        self.ui = UserInterface(self.screen)

        self.dt = 0

        # Will draw the quadtree overlay if true
        self.draw_quadtree = False

        self.paused = False

        # When the user clicks on the screen it's position will be stored here
        self.mouse_screen_position = None
        self.mouse_real_position = None

        # How fast everything moves
        self.game_speed = 1.0

        self.selected_creature = None

        self.follow_creature = False

        self.breeder = Breeder()

        self.population_stats = StatsTracker()

        self.spinner = Background()


    def run(self):
        self.load()
        self.setup_keys()
        self.game_loop()

    def game_loop(self):
        while self.running:
            self.dt = self.clock.tick()
            self.screen.fill(BLACK)

            self.handle_events()
            self.handle_key_presses()

            self.update_creature_positions()
            self.scene_graph.update()

            self.quadtree.update_objects(self.get_creatures())

            self.handle_collisions()
            self.do_obj_events()
            self.render_frame()

    def render_frame(self):
        pygame.display.set_caption(str(self.clock.get_fps()))


        # Find all objects in nodes intersecting the screen
        objects_to_draw = self.quadtree.get_objects_at_bounds(self.camera.get_bounds())

        for scene_object in objects_to_draw:
            scene_object.draw(self.screen, self.camera)

        if self.draw_quadtree:
            self.quadtree.draw_tree(self.screen, self.camera)

        self.draw_ui()

        self.scene.end_frame()

        pygame.display.flip()

    def do_obj_events(self):
        if not self.paused:
            self.scene.handle_events(self.dt, self.game_speed)
            self.check_healths()

    def check_healths(self):
        def remove_obj(obj):
            self.scene.remove_child(obj)
            self.quadtree.remove(obj)

        for creature in self.get_creatures():
            if creature.health <= 0:
                if creature.selected:
                    self.unfollow_creature()
                remove_obj(creature)
                self.entities.remove(creature)

                self._breed_creature()

        for food in self.foods:
            if food.eaten == True:
                remove_obj(food)
                self.foods.remove(food)
                self._insert_new_food()

    def _insert_new_creature(self):
        new_creature = Creature(
            x=randrange(*self.game_bounds),
            y=randrange(*self.game_bounds),
            color=WHITE
        )

        self._insert_creature(new_creature)

        return new_creature

    def _insert_creature(self, creature):
        self.entities.append(creature)

        creature.calc_absolute_position()

        self.quadtree.insert(creature)

    def _insert_new_food(self):
        new_food = Food(
            x=randrange(*self.game_bounds),
            y=randrange(*self.game_bounds),
            color=DARKGREEN
        )

        self._insert_food(new_food)

        return new_food

    def _insert_food(self, food):
        self.foods.append(food)
        self.scene_graph.add_to_parent(food, self.spinner, transformer=OldStyleTransformer)
        food.calc_absolute_position()

        self.quadtree.insert(food)

    def _breed_creature(self):
        new_weights = self.breeder.breed(list(self.get_creatures()))

        new_creature = Creature(
            x=randrange(*self.game_bounds),
            y=randrange(*self.game_bounds),
            nn_weights=new_weights
        )

        self._insert_creature(new_creature)

        return new_creature

    def handle_collisions(self):
        # Handle collisions for each creature's vision cone
        for creature in self.get_creatures():
            # vision_cone = creature.vision_cone

            # Get rough idea of what things could be colliding
            first_pass = self.quadtree.get_objects_at_bounds(creature.get_bounds())

            if first_pass:
                for scene_object in first_pass:
                    # vision_cone.check_collision(scene_object)
                    creature.check_collision(scene_object)

        self.scene.finish_collisions()

    def handle_key_presses(self):
        # Camera Zoom
        if self.key_presses["zoom-in"]:
            self.camera.zoom_in(self.dt)
        if self.key_presses["zoom-out"]:
            self.camera.zoom_out(self.dt)

        # Camera movement
        if not self.follow_creature:
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

            if event.key == K_b:
                self.select_best()

            if event.key == K_F5:
                self.save_state()

            if event.key == K_F9:
                self.load_state()

            if event.key == K_p:
                self.paused = not self.paused

            if event.key == K_F11:
                self.toggle_fullscreen()

            if event.key == K_f:
                self.toggle_follow_creature()

            if event.key == K_RIGHTBRACKET:
                self.speedup_game()

            if event.key == K_LEFTBRACKET:
                self.slowdown_game()

        # Key Up
        ########################
        if event.type == KEYUP:
            try:
                self.key_presses[self.key_map[event.key]] = False
            except KeyError:
                pass

        # Mouse Down
        ########################
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_click()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            pygame.display.set_mode((self.CAM_WIDTH, self.CAM_HEIGHT), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((self.CAM_WIDTH, self.CAM_HEIGHT))

    def save_state(self):
        def export_items(items):
            with open('weight_data.pickle', 'wb+') as f:
                pickle.dump(items, f)
        # dump the creatures and food stuffs
        # let's get all the creatures first
        x = self.creatures
        y = self.foods
        export_items([x, y])

        self.ui.toast("Saved Simulation")

    def load_state(self):
        def retrieve_items():
            with open('weight_data.pickle', 'rb+') as f:
                return pickle.load(f)
        try:
            creatures, foods = retrieve_items()
        except:
            return
        self.reload(creatures, foods)

        self.ui.toast("Loaded Simulation")

    def toggle_follow_creature(self):
        if self.selected_creature:
            self.follow_creature = not self.follow_creature

            if self.follow_creature:
                self.attach_camera_to(self.selected_creature)
            else:
                self.detach_camera_from(self.selected_creature)

    def unfollow_creature(self):
        if self.selected_creature:
            if self.follow_creature:
                self.detach_camera_from(self.selected_creature)

            self.follow_creature = False

    def select_best(self):
        self.unselect_creature()
        self.unfollow_creature()

        best = self._find_best()

        self.select_creature(best)
        self.toggle_follow_creature()

    def _find_best(self):
        return max(self.get_creatures(), key=lambda c: c.total_food_eaten)

    def select_creature(self, creature):
        self.selected_creature = creature

        creature.selected = True
        creature.vision_cone.visible = True

    def unselect_creature(self):
        if self.selected_creature:
            self.selected_creature.selected = False
            self.selected_creature.vision_cone.visible = False

            self.selected_creature = None

            self.unfollow_creature()

    def attach_camera_to(self, scene_object):
        self.camera.set_position([0, 0])
        self.camera.reparent_to(scene_object)

    def detach_camera_from(self, scene_object):
        self.camera.reparent_to(self.scene)
        self.camera.set_position(scene_object.get_absolute_position())

    def handle_click(self):
        self.mouse_screen_position = pygame.mouse.get_pos()
        self.mouse_real_position = self.camera.real_position(self.mouse_screen_position)

        hit = self.quadtree.ray_cast(self.mouse_real_position)

        if hit:
            # If our hit is a Creature
            if issubclass(type(hit), Creature):
                self.unselect_creature()
                self.select_creature(hit)

                if self.follow_creature:
                    self.attach_camera_to(hit)

    def _reload_init(self):
        self.scene = Background()
        self.quadtree = QuadTree(
            bounds=(
                -self.WORLD_WIDTH/2,
                -self.WORLD_HEIGHT/2,
                self.WORLD_WIDTH,
                self.WORLD_HEIGHT),
            depth=9)
        self.ui = UserInterface(self.screen)
        self.dt = 0
        # When the user clicks on the screen it's position will be stored here
        self.mouse_screen_position = None
        self.mouse_real_position = None
        # How fast everything moves
        self.game_speed = 1.0
        self.selected_creature = None
        self.follow_creature = False
        self.population_stats = StatsTracker()

    def reload(self, creatures, foods):
        self._reload_init()
        self.load(creatures, foods)

    def load(self, creatures=None, foods=None):
        """Sets up various game world objects"""
        self.creatures = []
        self.foods = []
        self.entities = []
        self.scene_graph = SceneGraph()
        self.scene_graph.add(self.spinner)

        if creatures and foods:
            for creature in creatures:
                self._insert_creature(creature)
            for food in foods:
                self._insert_food(food)
        else:
            # Create creatures
            for x in range(self.num_of_creatures):
                self._insert_new_creature()

            # Create foods
            for x in range(self.num_of_food):
                self._insert_new_food()

        self.camera.reparent_to(self.scene)

        # Setup text boxes
        self.speed_textbox = TextBox("", (10, self.CAM_HEIGHT - 40))
        self.creature_stats_textbox = MultilineTextBox([""], (10, 10))
        self.population_stats_textbox = MultilineTextBox([""], (self.CAM_WIDTH-300, 10))
        num_creatures_text = "{} Creatures, {} Food".format(len(self.creatures), len(self.foods))
        self.num_creatures_textbox = TextBox(num_creatures_text, (10, self.CAM_HEIGHT - 70))

        self.ui.add(self.speed_textbox)
        self.ui.add(self.creature_stats_textbox)
        self.ui.add(self.num_creatures_textbox)
        self.ui.add(self.population_stats_textbox)

    def update_creature_positions(self):
        if not self.paused:
            for creature in self.get_creatures():
                network = creature.nn
                network.compute_network()

                creature.rotate((self.dt * creature.rotation_speed) * self.game_speed)
                creature.move_forward((self.dt * creature.speed) * self.game_speed)
                creature.calc_absolute_position()


    def speedup_game(self):
        self.game_speed = min(self.MAX_GAME_SPEED, self.game_speed + self.GAME_SPEED_INCREMENT)

    def slowdown_game(self):
        self.game_speed = max(self.MIN_GAME_SPEED, self.game_speed - self.GAME_SPEED_INCREMENT)

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

    def draw_ui(self):
        ui = self.ui

        if self.paused:
            speed_text = "Speed: Paused"
        else:
            speed_text = "Speed: {}x".format(self.game_speed)

        self.speed_textbox.set(speed_text)

        if self.selected_creature:
            self.creature_stats_textbox.set(self.selected_creature.get_stats())
        else:
            self.creature_stats_textbox.clear()

        stats = self.population_stats.update(list(self.get_creatures()))
        self.population_stats_textbox.set(stats)

        ui.draw()

    def get_creatures(self):
        return (entity for entity in self.entities if issubclass(type(entity), Creature))
