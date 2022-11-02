import math
import numpy as np
import pandas as pd
import pygame
import time
from ContainerListToMatrix import ContainerListToMatrix, MatrixToCollisionMatrix, ContainerListToPrioMatrix
from BFS import *

pygame.init()

#TestData
lotdata = {"ID":[0,1,2],
            "Name":["lot1","lot2","YEA"],
            "maxStack":[5,5,5],
            "Size":[(15,15),(5,5),(20,20)]
           }

data = {"ContainerID":[1,2,3,4,5,6,7,8,9],
           "Name":["InitContainer","test1","test2","test3","test4","test5","duplicateofInit","test6","test7"],
           "Lot":[0,0,0,0,0,0,0,0,0],
           "X":[0,1,1,0,0,0,0,3,5],
           "Y":[0,0,0,1,1,1,0,4,9],
           "Z":[0,0,1,0,1,2,1,0,0],
           "Priority":[True,True,False,False,True,False,True,False,False]}

# Define dataframes
lotDF = pd.DataFrame(data=lotdata)
containerDF = pd.DataFrame(data=data)
lotLag = True

# Set up the drawing window
screen = pygame.display.set_mode([1000, 1000])

StretchFactor = 2
ScaleFactor = 10
Offset = (0,0)

def moveContainerPos(pos1,pos2):

    # Generate 2D matrix heightmap per lot in a list.
    GeneratedMatrices = ContainerListToMatrix(containerDF,lotDF)

    # Get First Height
    FirstHeight = GeneratedMatrices[pos1[0]][pos1[1],pos1[2]]

    # Get Second Height
    SecondHeight = GeneratedMatrices[pos2[0]][pos2[1],pos2[2]]

    # Get the positions to replace in the dataframe
    FirstIndex = [pos1[0],pos1[1],pos1[2],FirstHeight-1]
    SecondIndex = [pos2[0],pos2[1],pos2[2],SecondHeight]

    #InsertCheck
    if IsMoveLegal(pos1, pos2, GeneratedMatrices, SecondHeight):

        #Replace coordinates of container
        containerDF.loc[(containerDF[["Lot", "X", "Y", "Z"]] == FirstIndex).all(axis=1),["Lot", "X", "Y", "Z"]] = SecondIndex
        #This scoring does not account for just moving a container within a plot.
        if(FirstIndex[0] == SecondIndex[0]):
            return minDistance2Points(lots[FirstIndex[0]].getArray(), (FirstIndex[1], FirstIndex[2]),(SecondIndex[1], SecondIndex[2]))
        else:
            return minDistance(lots[FirstIndex[0]].getArray(), (FirstIndex[1],FirstIndex[2])) + minDistance(lots[SecondIndex[0]].getArray(), (SecondIndex[1],SecondIndex[2]))
    else:
        return -1


def IsMoveLegal(pos1, pos2, GeneratedMatrices, SecondHeight):
    # max hoogte
    if SecondHeight >= 5:
        print('Max hoogte overstreden, zet de container ergens anders neer')
        return False

    pos = [pos1, pos2]
    if pos1[3] == 1 and pos1[2] == pos2[2]:
        if pos2[2] == pos1[2] + 1 or pos2[2] == pos1[2] - 1:
            return True

    for i in pos:

        # container buiten lot
        if i[0] == -1:
            print("Container buiten lot")
            return False

            # container oppakken en neerzetten
        pos1_x = i[1]
        pos1_y = i[2]
        lot = GeneratedMatrices[i[0]]

        if pos1_y + 1 != len(lot) and pos1_y - 1 != -1 and lot[pos1_x, pos1_y - 1] != 0 and lot[
            pos1_x, pos1_y + 1] != 0:
            print("Container staat ingebouwd")
            return False

    return True

def posHasContainer(lotpos):
    return not (containerDF.loc[(containerDF[["Lot","X","Y","Z"]] == lotpos).all(axis=1)]).empty

def getContainerAttributes(lotpos):
    return (containerDF.loc[(containerDF[["Lot","X","Y","Z"]] == lotpos).all(axis=1)])

def below(pos):
    return pos[0],pos[1],pos[2],max(pos[3]-1,0)

class MouseClass:
    def __init__(self,scf,scr,offset=(0,0)):
        self.scr = scr
        self.scf = scf
        self.mouseGrabberState = 0
        self.FirstGrabLot = 0
        self.FirstGrabPos = (-1, 0, 0, 0)
        self.FirstGrabTime = 0
        self.offset = offset
        self.textValue = ""
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.text = self.font.render(self.textValue, True, (255,255,255))
        self.changesMade = True

    def mousePressed(self,scf):
        self.scf = scf
        #Get Screen Position of mouse
        pos = pygame.mouse.get_pos()

        #Get scaled and offset mouse position.
        pos = ((pos[0] - self.offset[0]) / self.scf, (pos[1] - self.offset[1]) / self.scf)

        #Check for overlap with lots and return coordinates
        LotPosition = self.checkMousePos(pos)

        if (self.mouseGrabberState == 0):
            #Check if selected container is empty.
            if(posHasContainer(below(LotPosition))):
                self.FirstGrabPos = LotPosition
                self.FirstGrabTime = time.time()
                self.mouseGrabberState = 1

                self.setText(str(getContainerAttributes(below(LotPosition))["Name"].values[0]))
            else:
                print("Position has no container. Try again.")
        elif (self.mouseGrabberState == 1):
            result = moveContainerPos(self.FirstGrabPos, LotPosition)
            if result != -1:
                print("Move Cost: %i"%(result))
                self.changesMade = True
            self.__init__(self.scf,self.scr,offset=self.offset)

    def checkMousePos(self,pos):
        #Input = Screen Position
        #Output = Container Coordinates including lot

        outputCoord = (-1, 0, 0, 0)
        resultSize = 0

        pos = pos[0]/StretchFactor,pos[1]

        for index, val in enumerate(lots):
            #Verify Dimensions of lot
            lotSize, lotPos = val.getSize(), val.getPos()


            #Check if mouse is within lot
            if pos[0] < lotSize[0] + lotPos[0] and pos[0] >= lotPos[0] and pos[1] < lotSize[1] + lotPos[1] and pos[1] >= lotPos[1]:
                #Define outputcoord as [Lot,X,Y,Z]
                outputCoord = (index,
                               int(pos[0] - lotPos[0]),
                               int(pos[1] - lotPos[1]),
                               val.getArray()[int(pos[0] - lotPos[0]), int(pos[1] - lotPos[1])])
                resultSize += 1

        if resultSize > 1:
            print("Unstable Output, more than 1 overlap detected")
        return outputCoord

    def checkState(self):
        if (time.time() - self.FirstGrabTime > 10 and self.mouseGrabberState == 1):
            # Reset Self
            self.__init__(self.scf,self.scr,offset=self.offset)
            print("User took too long. Resetting...")

    def setText(self,text):
        self.textValue = text

    def render(self):
        self.text = self.font.render("Selected Container: " + self.textValue, True, (255, 255, 255))
        textRect = self.text.get_rect()
        textRect.bottomleft = (0,self.scr.get_size()[1])
        #textRect.center = (self.scr.get_size()[0]//2,self.scr.get_size()[1]//2)
        self.scr.blit(self.text, textRect)

        if(self.FirstGrabPos != (-1,0,0,0)):
            lotpos = lots[self.FirstGrabPos[0]].getPos()
            lotpos = lotpos[0] + self.FirstGrabPos[1],lotpos[1] + self.FirstGrabPos[2]
            pygame.draw.rect(self.scr, (255,255,0), ((lotpos[0]) * self.scf * StretchFactor + self.offset[0],
                                                 lotpos[1] * self.scf + self.offset[1],
                                                 self.scf * StretchFactor,
                                                 self.scf))

    def getChanges(self):
        return self.changesMade

    def setChanges(self,bo):
        self.changesMade = bo

class Lot:
    def __init__(self, pos, size, maxStackSize, scr, scfac = 50, offset = (0, 0), name = ""):
        self.name = name
        self.size = size
        self.maxStackSize = maxStackSize
        self.psc = int(math.floor(256 / maxStackSize))
        self.scr = scr
        self.scfac = scfac
        self.offset = offset
        self.nparr = np.zeros(self.size, dtype=int)
        self.pos = pos
        self.bordercolor = (128, 128, 128)
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.text = self.font.render(self.name, True, (255,255,255))
    def getArray(self):
        return self.nparr

    def loadData(self, data):
        self.nparr = data
        self.size = data.shape

    def getPos(self):
        return self.pos

    def getSize(self):
        return self.size

    def generateRandom(self):
        self.nparr = np.random.randint(0, self.maxStackSize, size=self.size)

    def setBorderColor(self, r, g, b):
        self.bordercolor = (r, g, b)

    def render(self,scale,offset):
        self.scfac = scale
        self.offset = offset
        widthcorrection,heightcorrection = pygame.display.get_surface().get_size()
        widthcorrection /= 2
        heightcorrection /= 2



        for x, line in enumerate(self.nparr):
            for y, val in enumerate(line):
                pxcolor = (val * self.psc, val * self.psc, val * self.psc)
                pygame.draw.rect(self.scr, pxcolor, ((x + self.pos[0]) * StretchFactor * self.scfac + self.offset[0],
                                                     (y + self.pos[1]) * self.scfac + self.offset[1],
                                                     self.scfac * StretchFactor,
                                                     self.scfac))
        # Top
        pygame.draw.rect(self.scr, self.bordercolor, (self.pos[0] * self.scfac * StretchFactor + self.offset[0],
                                                    (self.pos[1] - 0.5) * self.scfac + self.offset[1],
                                                    self.nparr.shape[0] * self.scfac * StretchFactor,
                                                    0.5 * self.scfac))

        # Bottom
        pygame.draw.rect(self.scr, self.bordercolor, (self.pos[0] * self.scfac * StretchFactor + self.offset[0],
                                                    (self.pos[1] + self.nparr.shape[1]) * self.scfac + self.offset[1],
                                                    self.nparr.shape[0] * self.scfac * StretchFactor,
                                                    0.5 * self.scfac))

        # Left
        pygame.draw.rect(self.scr, self.bordercolor, (
                                                    (self.pos[0]*StretchFactor - 0.5) * self.scfac + self.offset[0],
                                                    self.pos[1] * self.scfac + self.offset[1],
                                                    0.5 * self.scfac,
                                                    self.nparr.shape[1] * self.scfac))

        # Right
        pygame.draw.rect(self.scr, self.bordercolor, (
                                                    (self.pos[0] + self.nparr.shape[0]) * StretchFactor * self.scfac + self.offset[0],
                                                    self.pos[1] * self.scfac + self.offset[1],
                                                    0.5 * self.scfac,
                                                    self.nparr.shape[1] * self.scfac))
        # Text Renderer
        textRect = self.text.get_rect()
        textRect.center = ((self.pos[0] + self.size[0] // 2) * StretchFactor * self.scfac + self.offset[0],
                           (self.size[1] + self.pos[1]+2) * self.scfac + self.offset[1])

        self.scr.blit(self.text,textRect)

lots = []
heightOffset = 1
#Generate lots based on the lot dataset
for i in lotDF.index:
    lots.append(Lot((1, heightOffset), lotDF.loc[i, "Size"], lotDF.loc[i, "maxStack"], screen, ScaleFactor, name=lotDF.loc[i,"Name"]))
    #widthOffset += lotDF.loc[i,"Size"][0] + 2
    heightOffset += lotDF.loc[i,"Size"][1] + 5


ms = MouseClass(ScaleFactor, screen, offset=Offset)
lots[0].setBorderColor(252, 61, 3)

# Run until the user asks to quit
running = True
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a: Offset = (Offset[0]+100,Offset[1])
            if event.key == pygame.K_d: Offset = (Offset[0]-100,Offset[1])
            if event.key == pygame.K_w: Offset = (Offset[0],Offset[1]+100)
            if event.key == pygame.K_s: Offset = (Offset[0],Offset[1]-100)

            if event.key == pygame.K_r: Offset = (0,0);ScaleFactor = 10

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                ms.mousePressed(ScaleFactor)


        if event.type == pygame.MOUSEWHEEL:
            if event.y == -1:
                ScaleFactor /= 1.125
            if event.y == 1:
                ScaleFactor *= 1.125
    if ms.getChanges():
        print("Refreshing Screen")
        #Fill lots with new data
        GeneratedMatrices = ContainerListToMatrix(containerDF, lotDF)
        GeneratedPrioMatrices = ContainerListToPrioMatrix(containerDF, lotDF)
        #print(GeneratedPrioMatrices)
        for i, val in enumerate(GeneratedMatrices):
            lots[i].loadData(val)



        #Calculate Score
        MoveDistance = minDistance(lots[0].getArray(),(7,10))
        ms.setChanges(False)

    # Fill the background with white
    screen.fill((0, 0, 255))
    for i in lots:
        i.render(ScaleFactor,Offset)
    ms.checkState()
    ms.render()
    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()