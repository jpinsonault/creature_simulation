from QuadTree import QuadTree
from GameObjects import Creature
from Window import Window


BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)


def main():
    tree = QuadTree(bounds=(-1500, -1500, 3000, 3000))
    creatures = []

    camera = Window(800, 800, x=0, y=0)

    for x in range(-1000, 1000, 50):
        for y in range(-1000, 1000, 50):
            new_creature = Creature(x=x, y=y, color=WHITE)
            creatures.append(new_creature)

    tree.insert_objects(creatures)

    x, y = camera.position[0], camera.position[1]
    camera_bounds = (0, 0, 100, 100)
    tree.print_tree()

if __name__ == '__main__':
    main()