from inspect import currentframe

from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.core import Loader, NodePath, Vec3
from direct.task import Task
from direct.task.Task import TaskManager
from panda3d.core import TransparencyAttrib
from CollideObjectBase import InverseSphereCollideObject, CapsuleCollideableObject, SphereCollideObj 
from typing import Callable
from direct.showbase import ShowBaseGlobal

class Universe(ShowBase):
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
              self.modelNode = loader.loadModel(modelPath)
              self.modelNode.reparentTo(parentNode)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
       
              self.modelNode.setName(nodeName)
              tex = loader.loadTexture(texPath)
              self.modelNode.setTexture(tex, 1)


class Universe(InverseSphereCollideObject):
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
              super(Universe, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 0.9)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
              self.modelNode.setName(nodeName)
              tex = loader.loadTexture(texPath)
              self.modelNode.setTexture(tex, 1)


class Planet(ShowBase):
        def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
            self.modelNode = loader.loadModel(modelPath)
            self.modelNode.reparentTo(parentNode)
            self.modelNode.setPos(posVec)
            self.modelNode.setScale(scaleVec)

            self.modelNode.setName(nodeName)
            tex = loader.loadTexture(texPath)
            self.modelNode.setTexture(tex, 1)


class Planet(SphereCollideObj):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, colRadius=1.0, colPositionVec=Vec3(0, 0, 0))
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
            

class Drone(ShowBase):
    droneCount = 0
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
            self.modelNode = loader.loadModel(modelPath)
            self.modelNode.reparentTo(parentNode)
            self.modelNode.setPos(posVec)
            self.modelNode.setScale(scaleVec)

            self.modelNode.setName(nodeName)
            tex = loader.loadTexture(texPath)
            self.modelNode.setTexture(tex, 1)


class Drone(SphereCollideObj):
    droneCount = 0
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, colRadius: float = 1.0):
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, colRadius)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)


class Spaceship(ShowBase):
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
              self.modelNode = loader.loadModel(modelPath)
              self.modelNode.reparentTo(parentNode)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
              self.taskManager = Task.TaskManager()
              self.render = parentNode
              self.taskMgr.add(self.CheckIntervals, 'checkMissile')
              self.EnableHUD()
              
              self.modelNode.setName(nodeName)
              tex = loader.loadTexture(texPath)
              self.modelNode.setTexture(tex, 1)
             

              self.SetKeyBindings()
       
       def Thrust(self, keyDown):
              if keyDown:
                     self.taskManager.add(self.ApplyThrust, 'forward-thrust')
              else:
                     self.taskManager.remove('forward-thrust')
       
       def ApplyThrust(self, task):
              rate = 5
              trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
              trajectory.normalize()
              self.modelNode.setFluidPos(self.modelNode.getPos()+ trajectory * rate)
              return Task.cont
       
       

       def LeftTurn(self, keyDown):
              if keyDown:
                     self.taskManager.add(self.ApplyLeftTurn, 'left-turn')
              else:
                     self.taskManager.remove('left-turn')
       
       
       def ApplyLeftTurn(self, task):
              rate = .5
              self.modelNode.setH(self.modelNode.getH() + rate)
              return Task.cont
       
       
       def RightTurn(self, keyDown):
              if keyDown:
                     self.taskManager.add(self.ApplyRightTurn, 'right-turn')
              else:
                     self.taskManager.remove('right-turn')
       
       
       def ApplyRightTurn(self, task):
              rate = .5
              self.modelNode.setH(self.modelNode.getH() - rate)
              return Task.cont
       

       def MoveUp(self, keyDown):
              if keyDown:
                     self.taskManager.add(self.ApplyMoveUp, 'move-up')
              else:
                     self.taskManager.remove('move-up')
       
       
       def ApplyMoveUp(self, task):
              rate = 5
              self.modelNode.setZ(self.modelNode.getZ() + rate)
              return Task.cont
       

       
       def MoveDown(self, keyDown):
              if keyDown:
                     self.taskManager.add(self.ApplyMoveDown, 'move-down')
              else:
                     self.taskManager.remove('move-down')
       
       
       def ApplyMoveDown(self, task):
              rate = 5
              self.modelNode.setZ(self.modelNode.getZ() - rate)
              return Task.cont
       

       def SetKeyBindings(self):
              self.accept('space', self.Thrust, [1])
              self.accept('space-up', self.Thrust, [0])
              self.accept('arrow_left', self.LeftTurn, [1])
              self.accept('arrow_left-up', self.LeftTurn, [0])
              self.accept('arrow_right', self.RightTurn, [1])
              self.accept('arrow_right-up', self.RightTurn, [0])
              self.accept('arrow_up', self.MoveUp, [1])
              self.accept('arrow_up-up', self.MoveUp, [0])
              self.accept('arrow_down', self.MoveDown, [1])
              self.accept('arrow_down-up', self.MoveDown, [0])
              self.reloadTime = .25
              self.missileDistance = 4000
              self.missileBay = 1
              self.accept('f', self.Fire)

       
       
       def Fire(self):
              if self.missileBay > 0:
                     travRate = self.missileDistance
                     aim = self.render.getRelativeVector(self.modelNode, Vec3.forward())
                     aim.normalize()

                     fireSolution = aim * travRate
                     inFront = aim * 150
                     travVec = fireSolution + self.modelNode.getPos()
                     self.missileBay -= 1
                     tag = 'Missile' + str(Missile.missileCount)
                     posVec = self.modelNode.getPos() + inFront
                     currentMissile = Missile(self.loader, './Assets/Phaser/phaser.egg', self.render, tag, posVec, 4.0)
                     Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos=posVec, fluid=1)
                     Missile.Intervals[tag].start()

              else:
                     if not self.taskMgr.hasTaskNamed('reload'):
                            print("Reloading...")
                            self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                     
       
       
       def Reload(self, task):
              if task.time > self.reloadTime:
                     self.missileBay += 1
              if self.missileBay > 1:
                     self.missileBay = 1
                     print("Reloaded!")
                     return Task.done
              elif task.time <= self.reloadTime:
                     print("Reload proceeding...")
                     return Task.cont
              
       def CheckIntervals(self, task):
              for i in Missile.Intervals:
                     if not Missile.Intervals[i].isPlaying():
                            Missile.cNodes[i].detachNode()
                            Missile.fireModels[i].detachNode()
                            del Missile.Intervals[i]
                            del Missile.fireModels[i]
                            del Missile.cNodes[i]
                            del Missile.collisionSolids[i]
                            print(i + " has reached the end of its fire solution.")
                     if currentframe - Missile.lifetimes[i] > Missile.maxLifetime:
                            Missile.cNodes[i].detachNode()
                            Missile.fireModels[i].detachNode()
                            del Missile.Intervals[i]
                            del Missile.fireModels[i]
                            del Missile.cNodes[i]
                            del Missile.collisionSolids[i]
                            del Missile.lifetimes[i]
                            print(i + " expired.")      
                            break
                     return Task.cont
              
              
              
       def EnableHUD(self):
              self.Hud = OnscreenImage(image = "./Assets/Hud/Reticle3b.png", pos = Vec3(0, 0, 0), scale = 0.1)
              self.Hud.setTransparency(TransparencyAttrib.MAlpha)

       
class Missile(SphereCollideObj):
       fireModels = {}
       cNodes = {}
       collisionSolids = {}
       Intervals = {}
       lifetime = {}
       maxLifetime = 3.0
       missileCount = 0
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float):
              super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
              Missile.lifetime[nodeName] = ShowBaseGlobal.globalClock.getFrameTime()
              Missile.missileCount += 1
              Missile.fireModels[nodeName] = self.modelNode
              Missile.cNodes[nodeName] = self.collisionNode
              Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
              Missile.cNodes[nodeName].show()
              print("Fire torpedo #" + str(Missile.missileCount))
       
       
       
       
class Spaceship(InverseSphereCollideObject):
    def __init__( self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Spaceship, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1)
        self.taskMgr = taskMgr
        self.accept = accept
        self.modelNode.setPos(posVec) 
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)


              


       
class Missile(SphereCollideObj):
       fireModels = {}
       cNodes = {}
       collisionSolids = {}
       Intervals = {}
       missilecount = 0
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float):
              super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
              Missile.missileCount += 1
              Missile.fireModels[nodeName] = self.modelNode
              Missile.cNodes[nodeName] = self.collisionNode
              Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
              Missile.cNodes[nodeName].show()
              print("Fire torpedo #" + str(Missile.missileCount))

       

class Space_Station(ShowBase):
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
              self.modelNode = loader.loadModel(modelPath)
              self.modelNode.reparentTo(parentNode)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
       
              self.modelNode.setName(nodeName)
              tex = loader.loadTexture(texPath)
              self.modelNode.setTexture(tex, 1)


class Space_Station(CapsuleCollideableObject):
    def __init__(self, loader: Loader,  modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Space_Station, self).__init__(loader, modelPath, parentNode, nodeName, texPath, scaleVec, 1, -1, -5, 5, 10)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)














