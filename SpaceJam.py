from direct.showbase.ShowBase import ShowBase
import DefensePaths as DefensePaths
import SpaceJamClasses
from panda3d.core import CollisionTraverser, CollisionHandlerPusher

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.SetupScene()
        self.InitializeDefenses() 
        self.SetCamera()
        self.cTrav = CollisionTraverser()
        self.cTrav.traverse(self.render)
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.Spaceship.collisionNode, self.Spaceship.modelNode)
        self.cTrav.addCollider(self.Spaceship.collisionNode, self.pusher)
        self.cTrav.showCollisions(self.render)
    
        
        
    def SetupScene(self):
            self.Universe = SpaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.glb", self.render, "Universe", "./Assets/Universe/Universe.png", (0, 0, 0), 15000)
            self.Planet1 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet1.x", self.render, "Planet1", "./Assets/Planets/Planet1.png", (150, 5000, 67), 100)
            self.Planet2 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet2.x", self.render, "Planet2", "./Assets/Planets/Planet2.png", (500, 5000, 67), 100)
            self.Planet3 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet3.x", self.render, "Planet3", "./Assets/Planets/Planet3.png", (1000, 5000, 67), 100)
            self.Planet4 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet4.x", self.render, "Planet4", "./Assets/Planets/Planet4.png", (1500, 5000, 67), 100)
            self.Planet5 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet5.x", self.render, "Planet5", "./Assets/Planets/Planet5.png", (2000, 5000, 67), 100)
            self.Planet6 = SpaceJamClasses.Planet(self.loader, "./Assets/Planets/Planet6.x", self.render, "Planet6", "./Assets/Planets/Planet6.png", (2500, 5000, 67), 100)
            self.Spaceship = SpaceJamClasses.Spaceship(self.loader, self.taskMgr, self.accept, "./Assets/Spaceships/Dumbledore.egg", self.render, "Spaceship", "./Assets/Spaceships/spacejet_C.png", (-1000, 4000, 67), 50)
            self.Space_Station = SpaceJamClasses.Space_Station(self.loader, self.taskMgr, "./Assets/Space Station/spaceStation.egg", self.render, "Space_Station", "./Assets/Space Station/SpaceStation1_Dif2.png", (2000, 3000, 67), 100)

            

            
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
            nickname = "Drone" + str(SpaceJamClasses.Drone.droneCount)
            self.DrawCloudDefense(self.Planet1, nickname)
            self.DrawBaseballSeams(self.Space_Station, nickname, j, fullcycle, 2)


    def SetCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.Spaceship.modelNode)
        self.camera.setPos(0, 1, 0)
   
            




app = MyApp()
app.run()

