import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpPosInterval
from direct.task import Task
from direct.actor.Actor import Actor
#for Pandai
from panda3d.ai import *
#for Onscreen GUI
from direct.gui.OnscreenText import OnscreenText
import sys

MAX_ZOOM_SPEED = 500

CAMERA_START_POSITION = Point3(0, -5, 5)
ZOOM_INCREMENT = 15
SCROLL_SPEED = 1

 
class CreatureSim(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
 
        # Disable the camera trackball controls.
        base.disableMouse()
        self.setupKeys()
        self.textures = {}
        self.loadTextures()
 
        # Load the environment model.
        self.terrain = loader.loadModel("/c/Users/joe/Documents/terrain.x")
        # Reparent the model to render.
        self.terrain.reparentTo(render)
        # Apply scale and position transforms on the model.
        self.terrain.setScale(400, 400, 400)
        self.terrain.setTexture(self.textures["dirt"], 1)
        self.terrain.setPos(0, 0, 0)
        # Dummy node for the camera to look at
        self.cameraLookAt = render.attachNewNode("cameraLookAt")
        self.cameraLookAt.setHpr(0,0,0)

        camera.reparentTo(self.cameraLookAt)
        camera.setPos(CAMERA_START_POSITION)
        
        camera.lookAt(self.cameraLookAt)
        self.setupLerps()
 
        taskMgr.add(self.move,"moveTask")

    def setupKeys(self):
        self.keyMap = {
            "cam-up": 0,
            "cam-left": 0,
            "cam-down": 0,
            "cam-right": 0,
            "zoom": 0
        }

        self.accept("escape", sys.exit)

        # Scroll Wheel
        self.accept("wheel_down", self.setZoomOut)
        self.accept("wheel_up", self.setZoomIn)

        # Key down
        self.accept("w", self.setKey, ["cam-down",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-up",1])
        self.accept("d", self.setKey, ["cam-right",1])
        # Key up
        self.accept("w-up", self.setKey, ["cam-down",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-up",0])
        self.accept("d-up", self.setKey, ["cam-right",0])

    def loadTextures(self):
        self.textures["dirt"] = loader.loadTexture("/c/Users/joe/Documents/dirt.png")

    def setupLerps(self):
        self.cameraLerp = PositionLerper(startPosition=self.cameraLookAt.getPos())

    def move(self, task):
        deltaTime = globalClock.getDt()
        cameraPosition = self.cameraLookAt.getPos()

        if (self.keyMap["cam-left"]!=0):
            self.cameraLerp.updateEnd(cameraPosition, -SCROLL_SPEED, 0, 0)
        if (self.keyMap["cam-right"]!=0):
            self.cameraLerp.updateEnd(cameraPosition, SCROLL_SPEED, 0, 0)
        if (self.keyMap["cam-up"]!=0):
            self.cameraLerp.updateEnd(cameraPosition, 0, -SCROLL_SPEED, 0)
        if (self.keyMap["cam-down"]!=0):
            self.cameraLerp.updateEnd(cameraPosition, 0, SCROLL_SPEED, 0)
        if (self.keyMap["zoom"]!=0):
            self.cameraLerp.updateEnd(cameraPosition, 0, 0, self.keyMap["zoom"])
            self.keyMap["zoom"] = 0

        self.cameraLookAt.setPos(self.cameraLerp.next(deltaTime))

        return task.cont

    # Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value

    # Records a scroll event
    def setZoomOut(self):
        self.keyMap["zoom"] = min(MAX_ZOOM_SPEED, self.keyMap["zoom"] + ZOOM_INCREMENT)

    def setZoomIn(self):
        self.keyMap["zoom"] = max(-MAX_ZOOM_SPEED, self.keyMap["zoom"] - ZOOM_INCREMENT)


class PositionLerper:
    """Handles lerping from one point to another"""
    def __init__(self, duration=.08, startPosition=(0,0,0), endPosition=None):
        if not endPosition:
            endPosition = startPosition
            self.done = True
        else:
            self.done = False

        # Time in seconds to complete lerp
        self.duration = duration
        self.startPosition = startPosition
        self.endPosition = endPosition
        self.stepX = 0
        self.stepY = 0
        self.stepZ = 0
        self.totalDeltaTime = 0

    def updateEnd(self, newStart, x, y, z):
        self.startPosition = newStart
        self.endPosition.setX(self.endPosition.getX() + x)
        self.endPosition.setY(self.endPosition.getY() + y)
        self.endPosition.setZ(self.endPosition.getZ() + z)
        self.stepX = (self.endPosition.getX() - self.startPosition.getX()) / self.duration
        self.stepY = (self.endPosition.getY() - self.startPosition.getY()) / self.duration
        self.stepZ = (self.endPosition.getZ() - self.startPosition.getZ()) / self.duration
        self.done = False
        self.totalDeltaTime = 0

    def next(self, deltaTime):
        if not self.done:
            self.totalDeltaTime = min(self.totalDeltaTime + deltaTime, self.duration)
            if self.totalDeltaTime == self.duration:
                self.reset()
                return self.endPosition
            else:
                newX = self.startPosition.getX() + (self.stepX * self.totalDeltaTime)
                newY = self.startPosition.getY() + (self.stepY * self.totalDeltaTime)
                newZ = self.startPosition.getZ() + (self.stepZ * self.totalDeltaTime)
                return Point3(newX, newY, newZ)
        else:
            return self.endPosition

    def reset(self):
        self.done = True
        self.startPosition = self.endPosition
        self.stepX = 0
        self.stepY = 0
        self.stepZ = 0
        self.totalDeltaTime = 0


app = CreatureSim()
run()