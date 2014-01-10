import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
#for Pandai
from panda3d.ai import *
#for Onscreen GUI
from direct.gui.OnscreenText import OnscreenText
import sys

 
class CreatureSim(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
 
        # Disable the camera trackball controls.
        base.disableMouse()
        self.setup_keys()
 
        # Load the environment model.
        self.environ = loader.loadModel("models/environment")
        # Reparent the model to render.
        self.environ.reparentTo(render)
        # Apply scale and position transforms on the model.
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)
 
        taskMgr.add(self.move,"moveTask")

    def setup_keys(self):
        self.keyMap = {"cam-up": 0, "cam-left": 0, "cam-down": 0,"cam-right": 0}
        self.accept("escape", sys.exit)

        # Key down
        self.accept("w", self.setKey, ["cam-up",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-down",1])
        self.accept("d", self.setKey, ["cam-right",1])
        # Key up
        self.accept("w-up", self.setKey, ["cam-up",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-down",0])
        self.accept("d-up", self.setKey, ["cam-right",0])

    def move(self, task):
        if (self.keyMap["cam-left"]!=0):
            camera.setX(camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            camera.setX(camera, +20 * globalClock.getDt())
        if (self.keyMap["cam-up"]!=0):
            camera.setY(camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-down"]!=0):
            camera.setY(camera, +20 * globalClock.getDt())

        return task.cont

    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
 
app = CreatureSim()
run()