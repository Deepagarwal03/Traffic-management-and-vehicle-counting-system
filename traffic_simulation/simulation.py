
import random
import threading
import math
import pygame
import time
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

running = True
defGreen = 20
defyellow = 5
defRed = 150
target_width = 1920
target_height = 1080

defMin = 10
defMax = 60

noOfSig = 4
sig = []       
simTime = 300       
timeElapsed = 0

currGreen = 0   
nxtGreen = (currGreen+1)%noOfSig
currYellow = 0   


carTime = 3
bikeTime = 1.5
cycleTime = 1 
busTime = 2.5
truckTime = 1.5

noOfCars = 0
noOfBikes = 0
noOfBuses =0
noOfTrucks = 0
noOfCycles = 0
noOfLanes = 2


detectionTime = 5

speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'cycle':2, 'bike':2.5} 

x = {'right':[0,0,0], 'down':[983,946,905], 'left':[1742,1742,1742], 'up':[794,829,871]}    
y = {'right':[664,701,733], 'down':[0,0,0], 'left':[838,807,777], 'up':[1488,1488,1488]}

VEHICLES = { 'down': {0:[], 1:[], 2:[], 'crossed':0},'up': {0:[], 1:[], 2:[], 'crossed':0},'right':{0:[], 1:[], 2:[],'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0} }
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'cycle', 4:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

signalCoods = [(630, 490), (1070, 490), (1070, 920), (630, 920)]

signalTimerCoods = [(630, 450), (1070, 450), (1070, 880), (630, 880)]

vehicleCountCoods = [(630, 530), (1070, 530), (1070, 960), (630, 960)]
vehicleCountTexts = ["0", "0", "0", "0"]



stopLines = {'right': 797, 'down': 666, 'left': 1000, 'up': 860}
defaultStop = {'right': 787, 'down': 656, 'left': 1010, 'up': 870}
stops = {'right': [787,787,787], 'down': [656,656,656], 'left': [1010,1010,1010], 'up': [870,870,870]}
mid = {'right': {'x': 916, 'y': 782},
       'down': {'x': 901, 'y': 782},
       'left': {'x': 901, 'y': 741},
       'up': {'x': 901, 'y': 718}}
rotationAngle = 3

JUNCTION_CENTER = (
    (stopLines['right'] + stopLines['left']) // 2,
    (stopLines['down'] + stopLines['up']) // 2,
)


gap = 15    
gap2 = 15   

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, rd, yellow, green, mini, maxi):
        self.red = rd
        self.yellow = yellow
        self.green = green
        self.minimum = mini
        self.maximum = maxi
        self.signalText = "30"
        self.totalGreenTime = 0
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        VEHICLES[direction][lane].append(self)
        
        self.index = len(VEHICLES[direction][lane]) - 1
        path = os.path.join(ASSETS_DIR, direction, vehicleClass + ".png")
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)

    
        if(direction=='right'):
            if(len(VEHICLES[direction][lane])>1 and VEHICLES[direction][lane][self.index-1].crossed==0):   
                self.stop = VEHICLES[direction][lane][self.index-1].stop - VEHICLES[direction][lane][self.index-1].currentImage.get_rect().width - gap         
            else:
                self.stop = defaultStop[direction]
           
            temp = self.currentImage.get_rect().width + gap    
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='left'):
            if(len(VEHICLES[direction][lane])>1 and VEHICLES[direction][lane][self.index-1].crossed==0):
                self.stop = VEHICLES[direction][lane][self.index-1].stop + VEHICLES[direction][lane][self.index-1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif(direction=='down'):
            if(len(VEHICLES[direction][lane])>1 and VEHICLES[direction][lane][self.index-1].crossed==0):
                self.stop = VEHICLES[direction][lane][self.index-1].stop - VEHICLES[direction][lane][self.index-1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='up'):
            if(len(VEHICLES[direction][lane])>1 and VEHICLES[direction][lane][self.index-1].crossed==0):
                self.stop = VEHICLES[direction][lane][self.index-1].stop + VEHICLES[direction][lane][self.index-1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        if(self.direction=='right'):
            if(self.crossed==0 and self.x+self.currentImage.get_rect().width>stopLines[self.direction]):   # if the image has crossed stop line now
                self.crossed = 1
                VEHICLES[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x+self.currentImage.get_rect().width<mid[self.direction]['x']):
                    if((self.x+self.currentImage.get_rect().width<=self.stop or (currGreen==0 and currYellow==0) or self.crossed==1) and (self.index==0 or self.x+self.currentImage.get_rect().width<(VEHICLES[self.direction][self.lane][self.index-1].x - gap2) or VEHICLES[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x += self.speed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8
                        if(self.rotateAngle==90):
                            self.turned = 1
                            
                    else:
                        if(self.index==0 or self.y+self.currentImage.get_rect().height<(VEHICLES[self.direction][self.lane][self.index-1].y - gap2) or self.x+self.currentImage.get_rect().width<(VEHICLES[self.direction][self.lane][self.index-1].x - gap2)):
                            self.y += self.speed
            else: 
                if((self.x+self.currentImage.get_rect().width<=self.stop or self.crossed == 1 or (currGreen==0 and currYellow==0)) and (self.index==0 or self.x+self.currentImage.get_rect().width<(VEHICLES[self.direction][self.lane][self.index-1].x - gap2) or (VEHICLES[self.direction][self.lane][self.index-1].turned==1))):                
                
                    self.x += self.speed  



        elif(self.direction=='down'):
            if(self.crossed==0 and self.y+self.currentImage.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                VEHICLES[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y+self.currentImage.get_rect().height<mid[self.direction]['y']):
                    if((self.y+self.currentImage.get_rect().height<=self.stop or (currGreen==1 and currYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.currentImage.get_rect().height<(VEHICLES[self.direction][self.lane][self.index-1].y - gap2) or VEHICLES[self.direction][self.lane][self.index-1].turned==1)):                
                        self.y += self.speed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2
                        if(self.rotateAngle==90):
                            self.turned = 1
                    else:
                        if(self.index==0 or self.x>(VEHICLES[self.direction][self.lane][self.index-1].x + VEHICLES[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or self.y<(VEHICLES[self.direction][self.lane][self.index-1].y - gap2)):
                            self.x -= self.speed
            else: 
                if((self.y+self.currentImage.get_rect().height<=self.stop or self.crossed == 1 or (currGreen==1 and currYellow==0)) and (self.index==0 or self.y+self.currentImage.get_rect().height<(VEHICLES[self.direction][self.lane][self.index-1].y - gap2) or (VEHICLES[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y += self.speed
            
        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                VEHICLES[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x>mid[self.direction]['x']):
                    if((self.x>=self.stop or (currGreen==2 and currYellow==0) or self.crossed==1) and (self.index==0 or self.x>(VEHICLES[self.direction][self.lane][self.index-1].x + VEHICLES[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or VEHICLES[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x -= self.speed
                else: 
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if(self.rotateAngle==90):
                            self.turned = 1
                           
                    else:
                        if(self.index==0 or self.y>(VEHICLES[self.direction][self.lane][self.index-1].y + VEHICLES[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or self.x>(VEHICLES[self.direction][self.lane][self.index-1].x + gap2)):
                            self.y -= self.speed
            else: 
                if((self.x>=self.stop or self.crossed == 1 or (currGreen==2 and currYellow==0)) and (self.index==0 or self.x>(VEHICLES[self.direction][self.lane][self.index-1].x + VEHICLES[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or (VEHICLES[self.direction][self.lane][self.index-1].turned==1))):                
                    self.x -= self.speed     
           
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                VEHICLES[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y>mid[self.direction]['y']):
                    if((self.y>=self.stop or (currGreen==3 and currYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(VEHICLES[self.direction][self.lane][self.index-1].y + VEHICLES[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or VEHICLES[self.direction][self.lane][self.index-1].turned==1)):
                        self.y -= self.speed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 1
                        self.y -= 1
                        if(self.rotateAngle==90):
                            self.turned = 1
                    else:
                        if(self.index==0 or self.x<(VEHICLES[self.direction][self.lane][self.index-1].x - VEHICLES[self.direction][self.lane][self.index-1].currentImage.get_rect().width - gap2) or self.y>(VEHICLES[self.direction][self.lane][self.index-1].y + gap2)):
                            self.x += self.speed
            else: 
                if((self.y>=self.stop or self.crossed == 1 or (currGreen==3 and currYellow==0)) and (self.index==0 or self.y>(VEHICLES[self.direction][self.lane][self.index-1].y + VEHICLES[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or (VEHICLES[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y -= self.speed


def initialize():
    ts1 = TrafficSignal(0, defyellow, defGreen, defMin, defMax)
    sig.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defyellow, defGreen, defMin, defMax)
    sig.append(ts2)
    ts3 = TrafficSignal(defRed, defyellow, defGreen, defMin, defMax)
    sig.append(ts3)
    ts4 = TrafficSignal(defRed, defyellow, defGreen, defMin, defMax)
    sig.append(ts4)
    repeat()


def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfCycles, noOfLanes
    global carTime, busTime, truckTime, cycleTime, bikeTime
    os.system("say detecting vehicles, "+directionNumbers[(currGreen+1)%noOfSig])

    noOfCars, noOfBuses, noOfTrucks, noOfCycles, noOfBikes = 0,0,0,0,0
    for j in range(len(VEHICLES[directionNumbers[nxtGreen]][0])):
        vehicles1 = VEHICLES[directionNumbers[nxtGreen]][0][j]
        if(vehicles1.crossed==0):
            vclass = vehicles1.vehicleClass
           
            noOfBikes += 1
    for i in range(1,3):
        for j in range(len(VEHICLES[directionNumbers[nxtGreen]][i])):
            vehicles1 = VEHICLES[directionNumbers[nxtGreen]][i][j]
            if(vehicles1.crossed==0):
                vclass = vehicles1.vehicleClass
               
                if(vclass=='car'):
                    noOfCars += 1
                elif(vclass=='bus'):
                    noOfBuses += 1
                elif(vclass=='truck'):
                    noOfTrucks += 1
                elif(vclass=='cycle'):
                    noOfCycles += 1
    
    greenTime = math.ceil(((noOfCars*carTime) + (noOfCycles*cycleTime) + (noOfBuses*busTime) + (noOfTrucks*truckTime)+ (noOfBikes*bikeTime))/(noOfLanes+1))
     
    print('Green Time: ',greenTime)
    if(greenTime<defMin):
        greenTime = defMin
    elif(greenTime>defMax):
        greenTime = defMax
    
    sig[(currGreen+1)%(noOfSig)].green = greenTime
   
def repeat():
    global currGreen, currYellow, nxtGreen
    while(sig[currGreen].green>0):  
        printStatus()
        updateValues()
        if(sig[(currGreen+1)%(noOfSig)].red==detectionTime):    
            thread = threading.Thread(name="detection",target=setTime, args=())
            thread.daemon = True
            thread.start()
           
        time.sleep(1)
    currYellow = 1   
    vehicleCountTexts[currGreen] = "0"
    
    for i in range(0,3):
        stops[directionNumbers[currGreen]][i] = defaultStop[directionNumbers[currGreen]]
        for vehicles1 in VEHICLES[directionNumbers[currGreen]][i]:
            vehicles1.stop = defaultStop[directionNumbers[currGreen]]
    while(sig[currGreen].yellow>0):  
        printStatus()
        updateValues()
        time.sleep(1)
    currYellow = 0   
    
    
    sig[currGreen].green = defGreen
    sig[currGreen].yellow = defyellow
    sig[currGreen].red = defRed
       
    currGreen = nxtGreen 
    nxtGreen = (currGreen+1)%noOfSig    
    sig[nxtGreen].red = sig[currGreen].yellow+sig[currGreen].green    
    repeat()     


def printStatus():                                                                                           
	for i in range(0, noOfSig):
		if(i==currGreen):
			if(currYellow==0):
				print(" GREEN TS",i+1,"-> r:",sig[i].red," y:",sig[i].yellow," g:",sig[i].green)
			else:
				print("YELLOW TS",i+1,"-> r:",sig[i].red," y:",sig[i].yellow," g:",sig[i].green)
		else:
			print("   RED TS",i+1,"-> r:",sig[i].red," y:",sig[i].yellow," g:",sig[i].green)
	print()

def updateValues():
    for i in range(0, noOfSig):
        if(i==currGreen):
            if(currYellow==0):
                sig[i].green-=1
                sig[i].totalGreenTime+=1
            else:
                sig[i].yellow-=1
        else:
            sig[i].red-=1

def generateVehicles():
    while(True):
        vehicle_type = random.randint(0,4)
        if(vehicle_type==4):
            lane_number = 0
        else:
            lane_number = random.randint(0,1) + 1
        will_turn = 0
        if(lane_number==2):
            temp = random.randint(0,4)
            if(temp<=2):
                will_turn = 1
            elif(temp>2):
                will_turn = 0
        temp = random.randint(0,999)
        direction_number = 0
        a = [400,800,900,1000]
        if(temp<a[0]):
            direction_number = 0
        elif(temp<a[1]):
            direction_number = 1
        elif(temp<a[2]):
            direction_number = 2
        elif(temp<a[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(0.75)

def simulationTime():
    global timeElapsed, simTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')
            for i in range(noOfSig):
                print('Lane',i+1,':',VEHICLES[directionNumbers[i]]['crossed'])
                totalVehicles += VEHICLES[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ',totalVehicles)
            print('Total time passed: ',timeElapsed)
            print('No. of vehicles passed per unit time: ',(float(totalVehicles)/float(timeElapsed)))
            os._exit(1)
    

class Main:
    thread4 = threading.Thread(name="simulationTime",target=simulationTime, args=()) 
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread2.daemon = True
    thread2.start()

    black = (0, 0, 0)
    white = (255, 255, 255)

    background = pygame.image.load(os.path.join(ASSETS_DIR, 'mod_int.png'))
    background_width, background_height = background.get_size()
    scene_width = 2 * max(JUNCTION_CENTER[0], background_width - JUNCTION_CENTER[0])
    scene_height = 2 * max(JUNCTION_CENTER[1], background_height - JUNCTION_CENTER[1])
    scene_offset_x = (scene_width // 2) - JUNCTION_CENTER[0]
    scene_offset_y = (scene_height // 2) - JUNCTION_CENTER[1]
    screen = pygame.display.set_mode((1300,800), pygame.RESIZABLE)
    pygame.display.set_caption("SIMULATION")
    scene = pygame.Surface((scene_width, scene_height))

    signalred = pygame.image.load(os.path.join(ASSETS_DIR, 'signals', 'signalred.png'))
    signalyellow = pygame.image.load(os.path.join(ASSETS_DIR, 'signals', 'signalyellow.png'))
    signalgreen = pygame.image.load(os.path.join(ASSETS_DIR, 'signals', 'signalgreen.png'))
    font = pygame.font.Font(None, 30)

    thread3 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        scene.fill(black)
        scene.blit(background, (scene_offset_x, scene_offset_y))
   
        for i in range(0,noOfSig):  
            if(i==currGreen):
                if(currYellow==1):
                    if(sig[i].yellow==0):
                        sig[i].signalText = "STOP"
                    else:
                        sig[i].signalText = sig[i].yellow
                    scene.blit(signalyellow, (signalCoods[i][0] + scene_offset_x, signalCoods[i][1] + scene_offset_y))
                else:
                    if(sig[i].green==0):
                        sig[i].signalText = "SLOW"
                    else:
                        sig[i].signalText = sig[i].green
                    scene.blit(signalgreen, (signalCoods[i][0] + scene_offset_x, signalCoods[i][1] + scene_offset_y))
            else:
                if(sig[i].red<=10):
                    if(sig[i].red==0):
                        sig[i].signalText = "GO"
                    else:
                        sig[i].signalText = sig[i].red
                else:
                    sig[i].signalText = "---"
                scene.blit(signalred, (signalCoods[i][0] + scene_offset_x, signalCoods[i][1] + scene_offset_y))
        signalTexts = ["","","",""]

      
        for i in range(0,noOfSig):  
            signalTexts[i] = font.render(str(sig[i].signalText), True, white, black)
            scene.blit(signalTexts[i], (signalTimerCoods[i][0] + scene_offset_x, signalTimerCoods[i][1] + scene_offset_y)) 
            displayText = VEHICLES[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            scene.blit(vehicleCountTexts[i], (vehicleCountCoods[i][0] + scene_offset_x, vehicleCountCoods[i][1] + scene_offset_y))

        timeElapsedText = font.render(("Time Elapsed: "+str(timeElapsed)), True, black, white)
        scene.blit(timeElapsedText, (1100 + scene_offset_x, 50 + scene_offset_y))

       
        for vehicles1 in simulation:  
            scene.blit(vehicles1.currentImage, [vehicles1.x + scene_offset_x, vehicles1.y + scene_offset_y])
            
            vehicles1.move()

        window_width, window_height = screen.get_size()
        scale = min(window_width / scene_width, window_height / scene_height)
        scaled_size = (max(1, int(scene_width * scale)), max(1, int(scene_height * scale)))
        scaled_scene = pygame.transform.smoothscale(scene, scaled_size)
        offset_x = (window_width - scaled_size[0]) // 2
        offset_y = (window_height - scaled_size[1]) // 2

        screen.fill(black)
        screen.blit(scaled_scene, (offset_x, offset_y))
        pygame.display.update()

if __name__ == "__main__":
    Main()

  
