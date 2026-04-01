from platform import node
import re
from turtle import distance
from direct.showbase.ShowBase import ShowBase
import DefensePaths as DefensePaths
import SpaceJamClasses
import Player as Player
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.core import CollisionHandlerEvent
from direct.particles.ParticleEffect import ParticleEffect
from direct.interval.LerpInterval import LerpFunc
from panda3d.core import Vec3
from direct.showbase import ShowBaseGlobal
class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.SetupScene()
        self.InitializeDefenses() 
        self.SetCamera()
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.Spaceship.collisionNode, self.Spaceship.modelNode)
        self.cTrav.addCollider(self.Spaceship.collisionNode, self.pusher)
        self.cTrav.showCollisions(self.render)
        self.eventHandler = CollisionHandlerEvent()
        ShowBaseGlobal.base.eventHandler = self.eventHandler
        self.eventHandler.addInPattern('%fn-into-%in')
        self.accept('%fn-into-%in', self.HandleInto)
        self.taskMgr.add(self.updateCollisions, "updateCollisions")
        self.cTrav.showCollisions(self.render)
        self.SetParticles()
        self.cntExplode = 0
        self.explodeIntervals = {}
        self.planets = [self.Planet1, self.Planet2, self.Planet3, self.Planet4, self.Planet5, self.Planet6]
        self.velocity = Vec3(0, 0, 0)
        self.canLand = False
        self.currentPlanet = None
        self.isLanded = False
        self.taskMgr.add(self.ApplyGravity, "ApplyGravity")
        self.accept("l", self.Land)
        self.accept("k", self.TakeOff)

    def ApplyGravity(self, task):
        planetRadius = 100
        ship = self.Spaceship.modelNode
        shipPos = ship.getPos()
        self.canLand = False  
        
        for planet in self.planets:
            planetPos = planet.modelNode.getPos()

            direction = planetPos - shipPos
            distance = direction.length()
            
            if distance < 1500:  
                direction.normalize()
                strength = 1000 / (distance * distance)
                pull = direction * strength

                self.velocity += pull
                ship.setFluidPos(ship.getPos() + self.velocity)
            
            if distance < planetRadius + 150:
                    self.canLand = True
                    self.currentPlanet = planet
    
    def Land(self):

        if not self.canLand or self.isLanded:
            print("Cannot land")
            return

        print("Landing...")

        ship = self.Spaceship.modelNode
        planet = self.currentPlanet.modelNode

        planetPos = planet.getPos()

        normal = ship.getPos() - planetPos
        normal.normalize()

        planetRadius = 100

        ship.setPos(planetPos + normal * (planetRadius + 10))
        ship.lookAt(planetPos)
        ship.setP(ship.getP() + 90)
        self.velocity = Vec3(0, 0, 0)
        self.isLanded = True

    def TakeOff(self):
        if not self.isLanded:
            return

        print("Taking off...")

        self.Spaceship.modelNode.setZ(self.Spaceship.modelNode.getZ() + 200)

        self.isLanded = False
    
    def updateCollisions(self, task):
         self.cTrav.traverse(self.render)
         return task.cont
    
        
    def SetupScene(self):
            self.Universe = SpaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.x", self.render, "Universe", "./Assets/Universe/Universe.png", (0, 0, 0), 15000)
            self.Planet1 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet1.x", self.render, "Planet_1", "./Assets/Planets/Planet1.png", (150, 5000, 67), 100)
            self.Planet2 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet2.x", self.render, "Planet_2", "./Assets/Planets/Planet2.png", (500, 5000, 67), 100)
            self.Planet3 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet3.x", self.render, "Planet_3", "./Assets/Planets/Planet3.png", (1000, 5000, 67), 100)
            self.Planet4 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet4.x", self.render, "Planet_4", "./Assets/Planets/Planet4.png", (1500, 5000, 67), 100)
            self.Planet5 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet5.x", self.render, "Planet_5", "./Assets/Planets/Planet5.png", (2000, 5000, 67), 100)
            self.Planet6 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet6.x", self.render, "Planet_6", "./Assets/Planets/Planet6.png", (2500, 5000, 67), 100)
            self.Spaceship = Player.Spaceship(self.loader, self.taskMgr, self.accept, "./Assets/Spaceships/Dumbledore.egg", self.render, "Spaceship", "./Assets/Spaceships/spacejet_C.png", (-1000, 4000, 67), 50)
            self.Space_Station = SpaceJamClasses.Space_Station(self.loader, "./Assets/Space Station/spaceStation.egg", self.render, "Space_Station", "./Assets/Space Station/SpaceStation1_Dif2.png", (2000, 3000, 67), 100)

            

            
    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
            unitVec = DefensePaths.BaseballSeams(step, numSeams, B = 0.4)
            unitVec.normalize()
            position = unitVec * radius * 250 + centralObject.modelNode.getPos()
            SpaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)


    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = DefensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralObject.modelNode.getPos()
        SpaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 10)

   
    def InitializeDefenses(self):
        fullcycle = 60
        for j in range(fullcycle):
            SpaceJamClasses.Drone.droneCount += 1
            nickname = "Drone_" + str(SpaceJamClasses.Drone.droneCount)
            self.DrawCloudDefense(self.Planet1, nickname)
            self.DrawBaseballSeams(self.Space_Station, nickname, j, fullcycle, 2)


    def SetCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.Spaceship.modelNode)
        self.camera.setPos(0, 1, 0)
   
    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        intoNode = entry.getIntoNodePath().getName()

        print(f"{fromNode} hit {intoNode}")
        if "Missile" not in fromNode:
            return

        missileNode = entry.getFromNodePath().getParent()
        hitNode = entry.getIntoNodePath().getParent()

        if "Planet" in intoNode:
            print("Missile hit a planet")
            if not missileNode.isEmpty():
                missileNode.removeNode()
                return

        if "Drone" in intoNode:
            print("Missile hit a drone")
            hitPos = entry.getSurfacePoint(self.render)
            self.explodeNode.setPos(hitPos)
            self.Explode()
            if not hitNode.isEmpty():
                hitNode.removeNode()
                if not missileNode.isEmpty():
                    missileNode.removeNode()
                    return
        
        if "Space_Station" in intoNode:
            print("Missile hit space station")

        if not missileNode.isEmpty():
            missileNode.removeNode()
            return

       
    def DestroyObject(self, hitID, hitPosition):
              nodeID = self.render.find("**/" + hitID)
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
              self.explodeEffect.loadConfig("./Assets/Part-Fx/Part-Efx/basic_xpld_efx.ptf")
              self.explodeEffect.setScale(20)
              self.explodeNode = self.render.attachNewNode('ExplosionEffects')
            




app = MyApp()
app.run()

