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
    tree = QuadTree(bounds=(-1500, -1500, 3000, 3000))
    tree.insert_objects(creatures)

    return tree


def main():
    
    creatures = []

    camera = Window(800, 800, x=0, y=0)

    for x in range(400):
        new_creature = Creature(x=randrange(-1500, 1500), y=randrange(-1500, 1500), color=WHITE)
        creatures.append(new_creature)
        new_creature.calc_absolute_position()

    start_time = time()
    for x in xrange(60):
        tree = make_tree(creatures)

    end_time= time()
    print("time: {:.4f}ms".format((end_time - start_time)*1000))

    x, y = camera.position[0], camera.position[1]
    camera_bounds = (0, 0, 100, 100)
    # tree.print_tree()
    # print(len(tree.get_objects_at_bounds(camera_bounds)))

if __name__ == '__main__':
    main()