
from turtle import forward
from panda3d.core import *
from panda3d.core import Loader, NodePath, Vec3
from direct.task.Task import Task, TaskManager
from CollideObjectBase import SphereCollideObj 
from typing import Callable
from  direct.task import Task
from direct.task.Task import TaskManager
from direct.showbase import ShowBaseGlobal
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
import SpaceJamClasses
from panda3d.core import BitMask32
from direct.interval.LerpInterval import LerpPosInterval

class Spaceship(SphereCollideObj):
    def __init__( self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Spaceship, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1)
        self.loader = loader
        self.taskMgr = taskMgr
        self.accept = accept
        self.render = parentNode
        self.modelNode.setPos(posVec) 
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.SetKeyBindings()
        self.EnableHUD()

 
    def Thrust(self, keyDown):
              if keyDown:
                     self.taskMgr.add(self.ApplyThrust, 'forward-thrust')
              else:
                     self.taskMgr.remove('forward-thrust')
       
    def ApplyThrust(self, task):
              rate = 5
              trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
              trajectory.normalize()
              self.modelNode.setFluidPos(self.modelNode.getPos()+ trajectory * rate)
              return Task.cont
       
       

    def LeftTurn(self, keyDown):
              if keyDown:
                     self.taskMgr.add(self.ApplyLeftTurn, 'left-turn')
              else:
                     self.taskMgr.remove('left-turn')
       
       
    def ApplyLeftTurn(self, task):
              rate = .5
              self.modelNode.setH(self.modelNode.getH() + rate)
              return Task.cont
       
       
    def RightTurn(self, keyDown):
              if keyDown:
                     self.taskMgr.add(self.ApplyRightTurn, 'right-turn')
              else:
                     self.taskMgr.remove('right-turn')
       
       
    def ApplyRightTurn(self, task):
              rate = .5
              self.modelNode.setH(self.modelNode.getH() - rate)
              return Task.cont
       

    def MoveUp(self, keyDown):
              if keyDown:
                     self.taskMgr.add(self.ApplyMoveUp, 'move-up')
              else:
                     self.taskMgr.remove('move-up')
       
       
    def ApplyMoveUp(self, task):
              rate = 5
              self.modelNode.setZ(self.modelNode.getZ() + rate)
              return Task.cont
       

       
    def MoveDown(self, keyDown):
              if keyDown:
                     self.taskMgr.add(self.ApplyMoveDown, 'move-down')
              else:
                     self.taskMgr.remove('move-down')
       
       
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
              self.accept('f', self.Fire)
              self.reloadTime = .25
              self.missileDistance = 4000
              self.missileBay = 1



    def Fire(self):
        if self.missileBay == 0:
                return
        self.missileBay -= 1
        self.taskMgr.doMethodLater(self.reloadTime, self.Reload, "reload")
        forward = self.render.getRelativeVector(self.modelNode, Vec3(0, 1, 0))
        forward.normalize()

        startPos = self.modelNode.getPos() + forward * 150

        tag = "Missile_" + str(SpaceJamClasses.Missile.missileCount)

    
        currentMissile = SpaceJamClasses.Missile(self.loader,'./Assets/Phaser/phaser.egg', self.render, tag, startPos, 4.0)
        ShowBaseGlobal.base.cTrav.addCollider(currentMissile.collisionNode, ShowBaseGlobal.base.eventHandler)
        speed = 2000
        endPos = startPos + forward * speed
        interval = LerpPosInterval(currentMissile.modelNode, 2.0, endPos, startPos=startPos)
        interval.start()
        SpaceJamClasses.Missile.Intervals[tag] = interval
        ShowBaseGlobal.base.taskMgr.doMethodLater(3, lambda task: currentMissile.modelNode.removeNode(), "remove-" + tag)   
            
                     
       
       
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
                     
                     current_time = ShowBaseGlobal.globalClock.getFrameTime()
                     if current_time - Missile.lifetime[i] > Missile.maxLifetime:
                            Missile.cNodes[i].detachNode()
                            Missile.fireModels[i].detachNode()
                            del Missile.Intervals[i]
                            del Missile.fireModels[i]
                            del Missile.cNodes[i]
                            del Missile.collisionSolids[i]
                            del Missile.lifetime[i]
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
              self.modelNode.setName(nodeName)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
              Missile.lifetime[nodeName] = ShowBaseGlobal.globalClock.getFrameTime()
              Missile.missileCount += 1
              Missile.fireModels[nodeName] = self.modelNode
              Missile.cNodes[nodeName] = self.collisionNode
              Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
              Missile.cNodes[nodeName].show()
              print("Fire torpedo #" + str(Missile.missileCount))
              self.collisionNode.node().setFromCollideMask(BitMask32.bit(1))
              self.collisionNode.node().setIntoCollideMask(BitMask32.allOff())

            

