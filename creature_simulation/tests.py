from GameObjects import *
first = Creature(x=20, y=28, color=WHITE)
second = Creature(x=20, y=20, color=WHITE)
scene = Background()


for thing in [first, second]:
    #print(thing.shape)
    thing.reparent_to(scene)
    thing.calc_absolute_position()
    thing.calc_shape_rotation()
    
    #print(thing.absolute_shape)

result = first.collidepoly(second)

if result:
    print("Collided")
else:
    print("Didn't collide")