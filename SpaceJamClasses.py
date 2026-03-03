from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.core import Loader, NodePath, Vec3
from direct.task import Task



class Universe(ShowBase):
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
              self.modelNode = loader.loadModel(modelPath)
              self.modelNode.reparentTo(parentNode)
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


class Spaceship(ShowBase):
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
              self.modelNode = loader.loadModel(modelPath)
              self.modelNode.reparentTo(parentNode)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
              self.taskManager = Task.TaskManager()
              self.render = parentNode
       
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
              
      

class Space_Station(ShowBase):
       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
              self.modelNode = loader.loadModel(modelPath)
              self.modelNode.reparentTo(parentNode)
              self.modelNode.setPos(posVec)
              self.modelNode.setScale(scaleVec)
       
              self.modelNode.setName(nodeName)
              tex = loader.loadTexture(texPath)
              self.modelNode.setTexture(tex, 1)







