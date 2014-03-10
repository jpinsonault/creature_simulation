from timeit import timeit
from QuadTree import QuadTree
from GameObjects import Creature
from Window import Window
from random import randrange
from time import time



BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)


def make_tree(creatures):
    tree = QuadTree(bounds=(-2000, -2000, 4000, 4000), depth=3)
    tree.insert_objects(creatures)

    return tree


def move_creatures(creatures):
    for creature in creatures:
        x_change = randrange(-30, 30)
        y_change = randrange(-30, 30)
        creature.move(x_change=x_change, y_change=y_change)
        creature.calc_absolute_position()


def main():
    
    creatures = []

    camera = Window(800, 800, x=0, y=0)

    for x in range(500):
        new_creature = Creature(x=randrange(-1500, 1500), y=randrange(-1500, 1500), color=WHITE)
        creatures.append(new_creature)
        new_creature.calc_absolute_position()

    start_time = time()
    # Simulate 60 frames
    tree = make_tree(creatures)
    print("{} scene objects".format(len(creatures)))
    for x in xrange(60):
        move_creatures(creatures)
        tree.update_objects(creatures)
        # make_tree(creatures)

    end_time= time()
    print("time: {:.2f}ms".format((end_time - start_time)*1000))

    x, y = camera.position[0], camera.position[1]
    camera_bounds = (0, 0, 100, 100)
    # tree.print_tree()
    # print(len(tree.get_objects_at_bounds(camera_bounds)))

if __name__ == '__main__':
    main()