from math import dist
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
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import LineSegs, NodePath
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
        ShowBaseGlobal.base.cTrav = self.cTrav
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
        self.accept("l", self.ToggleLanding)
        self.taskMgr.add(self.ApplyGravity, "ApplyGravity")
        self.accept("l", self.Land)
        self.accept("k", self.TakeOff)
        self.lockOn = False
        self.currentTarget = None
        self.lockText = OnscreenText(text='Lock On: None', pos=(-1.3, 0.9), scale=0.07, fg=(1, 1, 1, 1), align=0)
        self.accept("t", self.ToggleLock)
        self.taskMgr.add(self.UpdateLockUI, "UpdateLockOn")
        self.taskMgr.add(self.UpdateMissiles, "UpdateMissiles")
        self.takeoffTimer = 0
        self.accept("tab", self.NextTarget)
        self.lockTargets = []
        self.lockIndex = -1
        self.lockBox = self.createLockBox()
        self.lockBox.reparentTo(self.render)
        self.lockBox.hide()

    
    def UpdateMissiles(self, task):

        dt = ShowBaseGlobal.globalClock.getDt()

        for missileName in SpaceJamClasses.Missile.fireModels:

            missileNode = SpaceJamClasses.Missile.fireModels[missileName]

            if missileNode.isEmpty():
                continue
            
            if not missileNode.hasPythonTag("velocity") is None:
                missileNode.setPythonTag("velocity", Vec3(0, 0, 0))

            vel = missileNode.getPythonTag("velocity")
            missilePos = missileNode.getPos()

            if self.lockOn and self.IsDrone(self.currentTarget):

                targetPos = self.currentTarget.getPos()

                direction = targetPos - missilePos
                distance = direction.length()

                if distance > 0:
                    direction.normalize()

                turnStrength = 5.0
                vel += direction * turnStrength * dt

                maxSpeed = 150
                if vel.length() > maxSpeed:
                    vel.normalize()
                    vel *= maxSpeed

            missileNode.setPythonTag("velocity", vel)

            missileNode.setPos(missilePos + vel * dt)

        return task.cont
    


    def ToggleLanding(self):

        ship = self.Spaceship.modelNode
        shipPos = ship.getPos()

        for planet in self.planets:
            dist = (planet.modelNode.getPos() - shipPos).length()

            if dist < 150:
                self.isLanded = not self.isLanded

                if self.isLanded:
                    print("LANDED")
                    self.velocity = Vec3(0, 0, 0)
            else:
                print("TAKEOFF")

            return
         


    
    def ToggleLock(self):

        self.lockOn = not self.lockOn

        if not self.lockOn:
            self.currentTarget = None
            self.lockTargets = []
            self.lockIndex = -1
            self.lockText.setText("LOCK OFF")
        else:
            self.lockText.setText("LOCK ON")
    
    def UpdateLockUI(self, task):

        if not self.lockOn:
            return task.cont

        shipPos = self.Spaceship.modelNode.getPos()

        objects = []
        objects.extend(self.render.findAllMatches("**/Drone_*"))
        objects.extend(self.render.findAllMatches("**/Planet_*"))

        self.lockTargets = []

        for obj in objects:

            if obj.isEmpty():
                continue

            distVal = (obj.getPos() - shipPos).length()

            if distVal < 5000:
                self.lockTargets.append(obj)

        if not self.lockTargets:
            self.currentTarget = None
            self.lockText.setText("NO TARGET")
            return task.cont

        if self.lockIndex == -1:
            self.lockIndex = 0

        self.lockIndex %= len(self.lockTargets)

        candidate = self.lockTargets[self.lockIndex]

        if "Drone_" in candidate.getName():
            self.currentTarget = candidate
        else:
            self.currentTarget = None
        
        if self.currentTarget and "Drone_" in self.currentTarget.getName():
            droneName = self.currentTarget.getName()
            dist = (self.currentTarget.getPos() - self.Spaceship.modelNode.getPos()).length()

            self.lockText.setText(f"LOCKED ON: {droneName} | DIST: {int(dist)}")
        else:
            self.lockText.setText("NO DRONE LOCKED")

        if self.currentTarget and "Drone_" in self.currentTarget.getName():
            self.lockBox.show()
            self.lockBox.setPos(self.currentTarget.getPos())
            self.lockBox.setHpr(self.currentTarget.getHpr())
            self.lockBox.setScale(8)
        else:
            self.lockBox.hide()

        return task.cont

    def IsDrone(self, node):
        return node and (not node.isEmpty()) and "Drone_" in node.getName()
    

    def createLockBox(self):

        lines = LineSegs()
        lines.setColor(1, 0, 0, 1)  

        size = 5

        lines.moveTo(-size, -size, -size)
        lines.drawTo(size, -size, -size)
        lines.drawTo(size, size, -size)
        lines.drawTo(-size, size, -size)
        lines.drawTo(-size, -size, -size)

        lines.moveTo(-size, -size, size)
        lines.drawTo(size, -size, size)
        lines.drawTo(size, size, size)
        lines.drawTo(-size, size, size)
        lines.drawTo(-size, -size, size)

        lines.moveTo(-size, -size, -size)
        lines.drawTo(-size, -size, size)

        lines.moveTo(size, -size, -size)
        lines.drawTo(size, -size, size)

        lines.moveTo(size, size, -size)
        lines.drawTo(size, size, size)

        lines.moveTo(-size, size, -size)
        lines.drawTo(-size, size, size)

        node = lines.create()
        return NodePath(node)

    def GetHomingDirection(self, missilePos, targetPos):

        direction = targetPos - missilePos
        distance = direction.length()

        if distance > 0:
            direction.normalize()

        return direction
    


    def NextTarget(self):

        if not self.lockOn:
            return

        if not self.lockTargets:
            return

        self.lockIndex += 1

        if self.lockIndex >= len(self.lockTargets):
            self.lockIndex = 0

        self.currentTarget = self.lockTargets[self.lockIndex]

        self.lockText.setText(f"LOCKED: {self.currentTarget.getName()}")

    def ApplyGravity(self, task):

        dt = ShowBaseGlobal.globalClock.getDt()

        if self.takeoffTimer > 0:
            self.takeoffTimer -= dt

            self.Spaceship.modelNode.setFluidPos

        if self.isLanded:
             self.velocity = Vec3(0, 0, 0)
             return task.cont
        
        planetRadius = 100
        ship = self.Spaceship.modelNode
        shipPos = ship.getPos()
        self.canLand = False
        maxSpeed = 200

        if self.velocity.length() > maxSpeed:
            self.velocity.normalize()
            self.velocity *= maxSpeed 
        
        for planet in self.planets:
            planetPos = planet.modelNode.getPos()

            direction = planetPos - shipPos
            distance = direction.length()
            
            if distance < 1500:  
                direction.normalize()
                strength = 1000 / (distance * distance)
                pull = direction * strength
                self.velocity += pull
            
            dt = ShowBaseGlobal.globalClock.getDt()
            ship.setFluidPos(ship.getPos() + self.velocity * dt)
            
            if distance < planetRadius + 150:
                    self.canLand = True
                    self.currentPlanet = planet
                
            landingDistance = planetRadius + 15
            slowDownStart = planetRadius + 200
            landingDistance = planetRadius + 15

            if distance < slowDownStart:

                t = (distance - landingDistance) / (slowDownStart - landingDistance)
                t = max(0, min(1, t))
                self.velocity *= t

        if distance < landingDistance:
                normal = shipPos - planetPos
                normal.normalize()
                vel_along_normal = normal * self.velocity.dot(normal)
                self.velocity = vel_along_normal
        

        for missileName in SpaceJamClasses.Missile.fireModels:

            missileNode = SpaceJamClasses.Missile.fireModels[missileName]

            if missileNode.isEmpty():
                continue

            missilePos = missileNode.getPos()

            for planet in self.planets:
                planetPos = planet.modelNode.getPos()

            direction = planetPos - missilePos
            distance = direction.length()

            if distance < 2000:
                direction.normalize()

                strength = 10000 / (distance * distance)
                pull = direction * strength

            if hasattr(missileNode, "velocity"):
                missileNode.velocity += pull
            

        return task.cont
        
        
        


    
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

        ship = self.Spaceship.modelNode
        planetPos = self.currentPlanet.modelNode.getPos()
        shipPos = ship.getPos()

        direction = shipPos - planetPos
        direction.normalize()
        self.isLanded = False
        self.velocity = direction * 20
        self.takeoffTimer = 1.0
        print("Taking off...")
    
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
            self.Sentinal1 = SpaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet2, 900, "MLB", self.Spaceship)
            self.Sentinal2 = SpaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet5, 500, "Cloud", self.Spaceship)
            self.Sentinal3 = SpaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet1, 600, "MLB", self.Spaceship)
            self.Sentinal4 = SpaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet5, 300, "Cloud", self.Spaceship)
            self.Wanderer1 = SpaceJamClasses.Wanderer(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Spaceship)
            self.Wanderer2 = SpaceJamClasses.Wanderer(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Spaceship)

            

            
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
            SpaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone_X", "./Assets/DroneDefender/octotoad1_auv.png", (1000, 0, 0), 10)
            SpaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone_Y", "./Assets/DroneDefender/octotoad1_auv.png", (0, 1000, 0), 10)
            SpaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone_Z", "./Assets/DroneDefender/octotoad1_auv.png", (0, 0, 1000), 10)
            

    
    def SetCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.Spaceship.modelNode)
        self.camera.setPos(0, 1, 0)
   
    
    def HandleInto(self, entry):

        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()

        fromName = fromNode.getName()
        intoName = intoNode.getName()

        print(f"{fromName} HIT {intoName}")

        if "Missile" in fromName:

            missileNode = self.render.find("**/" + fromName)
            hitNode = self.render.find("**/" + intoName)

        if not hitNode.isEmpty():

            hitPos = entry.getSurfacePoint(self.render)
            hitNode.removeNode()

            self.explodeNode.setPos(hitPos)
            self.Explode()

        if not missileNode.isEmpty():
            missileNode.removeNode()
            SpaceJamClasses.Missile.fireModels.pop(fromName, None)
       
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
         if t == 0:
              self.explodeEffect.start(self.explodeNode)
         elif t >= 1.0:
              self.explodeEffect.disable()
              

       
    def SetParticles(self):
              self.enableParticles()
              self.explodeEffect = ParticleEffect()
              self.explodeEffect.loadConfig("./Assets/Part-Fx/Part-Efx/basic_xpld_efx.ptf")
              self.explodeEffect.setScale(20)
              self.explodeNode = self.render.attachNewNode('ExplosionEffects')
            




app = MyApp()
app.run()

