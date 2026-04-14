from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.core import Loader, NodePath, Vec3, CollisionNode, CollisionSphere, BitMask32 
from direct.task import Task
from panda3d.core import TransparencyAttrib
from CollideObjectBase import InverseSphereCollideObject, CapsuleCollideableObject, PlacedObject, SphereCollideObj 
from direct.showbase import ShowBaseGlobal
from panda3d.core import CollisionHandlerEvent
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
from direct.task.Task import TaskManager
import DefensePaths as DefensePaths
from direct.interval.IntervalGlobal import Sequence 

class UniverseModel(ShowBase):
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


class PlanetModel(ShowBase):
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
        self.collisionNode.reparentTo(self.modelNode)
        self.collisionNode.setPos(0, 0, 0)
        self.collisionNode.node().clearSolids()
        self.collisionNode.node().addSolid(CollisionSphere(0, 0, 0, 2.0))
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.collisionNode = self.modelNode.attachNewNode(CollisionNode(nodeName + "_cnode"))
        self.collisionNode.node().addSolid(CollisionSphere(0, 0, 0, 2.0))
        self.collisionNode.show()
        self.collisionNode.node().setIntoCollideMask(BitMask32.bit(1))
        self.collisionNode.node().setFromCollideMask(BitMask32.allOff())



class Wanderer(SphereCollideObj):
       numWanderers = 0

       def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, modelName: str, scaleVec: Vec3, texPath: str, staringAt: Vec3):
              super(Wanderer, self).__init__(loader, modelPath, parentNode, modelName, Vec3(0, 0, 0), 3.2)

              self.modelNode.setScale(scaleVec)
              tex = loader.loadTexture(texPath)
              self.modelNode.setTexture(tex, 1)
              self.staringAt = staringAt
              Wanderer.numWanderers += 1

              posInterval0 = self.modelNode.posInterval(20, Vec3(300, 6000, 500), startPos=Vec3(0, 0, 0))
              posInterval1 = self.modelNode.posInterval(20, Vec3(700, -2000, 100), startPos=Vec3(300, 6000, 500))
              posInterval2 = self.modelNode.posInterval(20, Vec3(0, -900, -1400), startPos=Vec3(700, -2000, 100))

              self.travelRoute = Sequence(posInterval0, posInterval1, posInterval2, name = "Traveler")

              self.travelRoute.loop()


class DroneModel(ShowBase):
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
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, colRadius: float = 3.0):
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, (0, 0, 0), colRadius)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.collisionNode.node().setIntoCollideMask(BitMask32.bit(1))
        self.collisionNode.node().setFromCollideMask(BitMask32.allOff())
        self.collisionNode.reparentTo(self.modelNode)
        self.collisionNode.setName(nodeName)
        self.collisionNode.setPos(0, 0, 0)

class Orbiter(SphereCollideObj):
       numOrbits = 0
       velocity = 0.005
       cloudTimer = 240
       def __init__(self, loader:Loader, taskMgr: TaskManager, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: float, texPath: str, centralObject: PlacedObject, orbitRadius: float, orbitType: str, staringAt: Vec3):
              super(Orbiter, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.2)
              self.taskMgr = taskMgr
              self.orbitType = orbitType
              self.modelNode.setScale(scaleVec)
              tex = loader.loadTexture(texPath)
              self.modelNode.setTexture(tex, 1)
              self.orbitObject = centralObject
              self.orbitRadius = orbitRadius
              self.staringAt = staringAt
              Orbiter.numOrbits += 1

              self.cloudTimer = 0
              self.taskFlag = "Traveler-" + str(Orbiter.numOrbits)
              taskMgr.add(self.Orbit, self.taskFlag)

       
       def Orbit(self, task):
              if self.orbitType == "MLB":
                     positionVec = DefensePaths.BaseballSeams(task.time * Orbiter.velocity, self.numOrbits, 2.0)
                     self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())

              elif self.orbitType == "Cloud":
                     if self.cloudTimer < Orbiter.cloudTimer:
                            self.cloudTimer += 1
                     
                     else:
                            self.cloudTimer = 0
                            positionVec = DefensePaths.Cloud()
                            self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())
              
              self.modelNode.lookAt(self.staringAt.modelNode)
              return Task.cont



class SpaceshipModel(ShowBase):
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

              self.cntExplode = 0
              self.explodeIntervals = {}
              self.traverser = ShowBaseGlobal.cTrav
              self.handler = CollisionHandlerEvent()
              self.handler.addInPattern('into')
              self.accept('into', self.HandleInto)
             

              self.SetKeyBindings()


       
       def DestroyObject(self, hitID, hitPosition):
              nodeID = self.render.find(hitID)
              nodeID.detachNode()

              self.explodeNode.setPos(hitPosition)
              self.Explode()

       
       def Explode(self):
              self.cntExplode += 1
              tag = 'particles-' + str(self.cntExplode)

              self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 4.0)
              self.explodeIntervals[tag].start()


       def ExplodeLight(self, t):
              if t == 1.0 and self.explodeEffect:
                     self.explodeEffect.disable()

              elif t == 0:
                     self.explodeEffect.start(self.explodeNode)

       
       def SetParticles(self):
              self.enableParticles()
              self.explodeEffect = ParticleEffect()
              self.explodeEffect.loadConfig("./Assets/ParticleEffects/Explosions/basic_xpld_efx.ptf")
              self.explodeEffect.setScale(20)
              self.explodeNode = self.render.attachNewNode('ExplosionEffects')
               
       
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
                     self.traverser.addCollider(currentMissile.collisionNode, self.handler)

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
              self.collisionNode.reparentTo(self.modelNode)
              self.collisionNode.setName(nodeName)
              self.collisionNode.setPos(0, 0, 0)
              self.velocity = Vec3(0, 0, 0)

       
       

       

class Space_StationModel(ShowBase):
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
        super(Space_Station, self).__init__(loader, modelPath, parentNode, nodeName, 1, -1, -5, 5, 10, 10, 5)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)














