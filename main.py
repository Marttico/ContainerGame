import math
import numpy as np
import pandas as pd
import pygame
import time
from ContainerListToMatrix import *
from BFS import *

pygame.init()

#TestData
lotdata = {"ID":[0,1,2],
            "Name":["lot1","lot2","YEA"],
            "maxStack":[5,5,5],
            "Size":[(15,15),(5,5),(15,15)]
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

#Create list with lots
lots = []

# Set up the drawing window
screen = pygame.display.set_mode([1000, 1000])

#Scoring variable
score = [0]

def addScore(var):
    if var != -1:
        score[0] += var

#Rendering options
StretchFactor = 2
ScaleFactor = 10
Offset = (0,0)


def moveContainerPos(pos1,pos2):

    # Generate 2D matrix heightmap per lot in a list.
    HeightMapLot1 = ContainerListToSingleMatrix(containerDF,lotDF,pos1[0])[0]
    HeightMapLot2 = ContainerListToSingleMatrix(containerDF,lotDF,pos2[0])[0]


    # Get First Height
    FirstHeight = HeightMapLot1[pos1[1],pos1[2]]

    # Get Second Height
    SecondHeight = HeightMapLot2[pos2[1],pos2[2]]

    # Get the positions to replace in the dataframe
    FirstIndex = [pos1[0],pos1[1],pos1[2],FirstHeight-1]
    SecondIndex = [pos2[0],pos2[1],pos2[2],SecondHeight]

    #InsertCheck
    if IsMoveLegal(pos1, pos2, HeightMapLot1, HeightMapLot2, SecondHeight) and posHasContainer(FirstIndex,containerDF):

        #Replace coordinates of container
        containerDF.loc[(containerDF[["Lot", "X", "Y", "Z"]] == FirstIndex).all(axis=1),["Lot", "X", "Y", "Z"]] = SecondIndex

        lots[pos1[0]].setLagsBehind()
        lots[pos2[0]].setLagsBehind()

        #This scoring does not account for just moving a container within a plot.
        if(FirstIndex[0] == SecondIndex[0]):
            return minDistance2Points(lots[FirstIndex[0]].getArray(), (FirstIndex[1], FirstIndex[2]),(SecondIndex[1], SecondIndex[2]))
        else:
            return minDistance(lots[FirstIndex[0]].getArray(), (FirstIndex[1],FirstIndex[2])) + minDistance(lots[SecondIndex[0]].getArray(), (SecondIndex[1],SecondIndex[2]))
    else:
        return -1

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


    def mousePressed(self,scf,offset,stretchfac):
        self.scf = scf
        self.offset = offset

        #Get Screen Position of mouse
        pos = pygame.mouse.get_pos()

        #Get scaled and offset mouse position.
        pos = ((pos[0] - self.offset[0]) / self.scf, (pos[1] - self.offset[1]) / self.scf)

        #Check for overlap with lots and return coordinates
        LotPosition = self.checkMousePos(pos,stretchfac)

        if (self.mouseGrabberState == 0):
            #Check if selected container is empty.
            if(posHasContainer(below(LotPosition),containerDF)):
                self.FirstGrabPos = LotPosition
                self.FirstGrabTime = time.time()
                self.mouseGrabberState = 1

                self.setText(str(getContainerAttributes(below(LotPosition),containerDF)["Name"].values[0]))
            else:
                print("Position has no container. Try again.")
        elif (self.mouseGrabberState == 1):
            result = moveContainerPos(self.FirstGrabPos, LotPosition)

            #if result != -1:
                #score += result
            #    print("Move Cost: %i"%(result))

            self.__init__(self.scf,self.scr,offset=self.offset)
            return result

    def checkMousePos(self,pos,StretchFac):
        #Input = Screen Position
        #Output = Container Coordinates including lot

        outputCoord = (-1, 0, 0, 0)
        resultSize = 0

        pos = pos[0]/StretchFac,pos[1]

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

    def render(self,scf,Offset,strtchfctr):
        self.text = self.font.render("Selected Container: " + self.textValue + " Score: " + str(score[0]), True, (255, 255, 255))
        textRect = self.text.get_rect()
        textRect.bottomleft = (0,self.scr.get_size()[1])
        #textRect.center = (self.scr.get_size()[0]//2,self.scr.get_size()[1]//2)
        self.scr.blit(self.text, textRect)

        if(self.FirstGrabPos != (-1,0,0,0)):
            lotpos = lots[self.FirstGrabPos[0]].getPos()
            lotpos = lotpos[0] + self.FirstGrabPos[1],lotpos[1] + self.FirstGrabPos[2]
            pygame.draw.rect(self.scr, (255,255,0), ((lotpos[0]) * scf * strtchfctr + Offset[0],
                                                 lotpos[1] * scf + Offset[1],
                                                 scf * strtchfctr,
                                                 scf))

heightOffset = 1
#Generate lots based on the lot dataset
for i in lotDF.index:
    lots.append(Lot((1, heightOffset), lotDF.loc[i,"ID"], lotDF.loc[i, "Size"], lotDF.loc[i, "maxStack"], screen, ScaleFactor, name=lotDF.loc[i,"Name"]))
    heightOffset += lotDF.loc[i,"Size"][1] + 5

ms = MouseClass(ScaleFactor, screen, offset=Offset)
lots[0].setBorderColor(252, 61, 3)

#Temporary Testing Variables
x = 0
y = 0
z = 0
lot = True


# Run until the user asks to quit
running = True
while running:
    begintime = time.time_ns()
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
                ms.mousePressed(ScaleFactor,Offset,StretchFactor)


        if event.type == pygame.MOUSEWHEEL:
            if event.y == -1:
                ScaleFactor /= 1.125
            if event.y == 1:
                ScaleFactor *= 1.125
    #Check if the lots are lagging behind.


    if z >= 5:
        z = 0
        x += 1

    if x >= 15:
        x = 0
        y += 1
    if y >= 15:
        y = 0
        lot = not lot

    if lot:
        addScore(moveContainerPos((0,x,y,z),(2,x,y,z)))
    if not lot:
        addScore(moveContainerPos((2,x,y,z),(0,x,y,z)))

    z += 1
    # Fill the background with white
    #screen.fill((0, 0, 255))
    #for i in lots:
    #    if i.lagsbehind:
    #        lots[i.id].loadData(ContainerListToSingleMatrix(containerDF, lotDF, i.id)[0])
    #    i.render(ScaleFactor,Offset,StretchFactor)
    #ms.checkState()
    #ms.render(ScaleFactor,Offset,StretchFactor)
    ## Flip the display
    #pygame.display.flip()
    endtime = time.time_ns()

    print("This loop took %i nanoseconds"%(endtime-begintime))
# Done! Time to quit.
pygame.quit()