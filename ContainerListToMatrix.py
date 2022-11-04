import numpy as np
import pandas as pd
import math
import pygame
# ---------------------------------
# Input:  Container List Dataframe
#        Lot info Dataframe
#
# Output: Heightmap of lot np array
# ---------------------------------


def ContainerListToPrioMatrix(df, lots):
    GeneratedMatrices = ContainerListToMatrix(df, lots)
    topcontainers = []
    priomatrix = []
    for i, val in enumerate(GeneratedMatrices):
        for x, valx in enumerate(val):
            for y, height in enumerate(valx):
                if height > 0:
                    topcontainers.append((i,x,y,height-1))
        priomatrix.append(np.full(val.shape,np.nan))


    for i in topcontainers:
        priomatrix[i[0]][i[1],i[2]] = df[np.all(df[["Lot", "X", "Y", "Z"]] == i,axis=1)].loc[:,"Priority"].values[0]

    return priomatrix

def ContainerListToSingleMatrix(df, lots, index):
    lotproperties = lots[lots["ID"] == index]

    heightLot = np.zeros((lotproperties["Size"].values[0][0], lotproperties["Size"].values[0][1], lotproperties["maxStack"].values[0]), dtype=int)
    prioLot = np.zeros((lotproperties["Size"].values[0][0], lotproperties["Size"].values[0][1]), dtype=bool)
    containersinlot = df[df["Lot"] == index].sort_values(by=["Z"])


    for i in containersinlot.iterrows():
        container = tuple(i[1][["X","Y","Z"]].to_list())
        if heightLot[container[0],container[1],:container[2]].sum() == container[2]:
            heightLot[container] = 1
            prioLot[container[0],container[1]] = i[1]["Priority"]
        else:
            raise ValueError("Floating Containers :P")
    return heightLot.sum(axis=2), prioLot



#def ContainerListToMatrix(df, lots):
#    # Check if there's no duplicates.
#    clearedChecks = True
#    ErrorString = ""
#    outputList = []
#    if (df["ContainerID"].duplicated().sum()):
#        print("There are duplicate ID's in your dataset.")
#        clearedChecks = False
#        ErrorString += "Duplicate ID's in your dataset. "
#
#    if (df[["Lot", "X", "Y", "Z"]].duplicated().sum()):
#        print("There are duplicate coordinates in your dataset.")
#        clearedChecks = False
#        ErrorString += "Duplicate coordinates in your dataset. "
#
#    if (lots.dropna().empty):
#        print("Your lots dataset is empty.")
#        clearedChecks = False
#        ErrorString += "Lots dataset empty. "
#
#    if (lots.columns.to_list() != ["ID", "Name", "maxStack", "Size"]):
#        print("Lots dataset is not formatted correctly.")
#        clearedChecks = False
#        ErrorString += "Lots dataset not formatted correctly. "
#
#    if (not clearedChecks):
#        raise ValueError(ErrorString)
#
#    lotlist = []
#    for i in lots.iterrows():
#        lotlist.append(np.zeros((i[1]["Size"][0], i[1]["Size"][1], i[1]["maxStack"]), dtype=int))
#
#    # Add containers to lotlists
#    for i in df[["Lot", "X", "Y", "Z"]].iterrows():
#        lotlist[i[1]["Lot"]][i[1]["X"], i[1]["Y"], i[1]["Z"]] = 1
#        # print(i[1].to_numpy())
#    for i in lotlist:
#        result = np.where(i == 1)
#        trueCoordinates = list(zip(result[0], result[1], result[2]))
#
#        for o in trueCoordinates:
#            belowContents = i[o[0], o[1], :o[2]]
#
#            if not (np.array(belowContents).size == 0 or np.array(belowContents).sum() != 0):
#                print("Floating containers found in container dataset.")
#                raise ValueError("Floating Containers Found.")
#        outputList.append(i.sum(axis=2))
#    return outputList

def MatrixToCollisionMatrix(matrix, AgentSize=4):
    outputMatrix = np.array(matrix)
    for i in range(AgentSize):
        appendingMatrix = np.append(np.zeros((matrix.shape[0], (i)), dtype=int), matrix[:, :matrix.shape[1] - i], 1)
        # print(i,appendingMatrix)

        outputMatrix += appendingMatrix

    # print(outputMatrix)
    return np.array(outputMatrix != 0, dtype=int)

def IsMoveLegal(pos1, pos2, HeightMapLot1, HeightMapLot2, SecondHeight):
    # max hoogte
    if SecondHeight >= 5:
        print('Max hoogte overstreden, zet de container ergens anders neer')
        return False

    if pos1 == pos2:
        print("Hij probeert t op zichzelf te zetten... :/")
        return False

    pos = [pos1, pos2]
    heights = [HeightMapLot1, HeightMapLot2]
    if pos1[3] == 1 and pos1[2] == pos2[2]:
        if pos2[2] == pos1[2] + 1 or pos2[2] == pos1[2] - 1:
            return True

    for index, i in enumerate(pos):

        # container buiten lot
        if i[0] == -1:
            print("Container buiten lot")
            return False

            # container oppakken en neerzetten
        pos1_x = i[1]
        pos1_y = i[2]
        lot = heights[index]

        if pos1_y + 1 != len(lot) and pos1_y - 1 != -1 and lot[pos1_x, pos1_y - 1] != 0 and lot[
            pos1_x, pos1_y + 1] != 0:
            print("Container staat ingebouwd")
            return False

    return True

def posHasContainer(lotpos,containerDF):
    return not (containerDF.loc[(containerDF[["Lot","X","Y","Z"]] == lotpos).all(axis=1)]).empty

def getContainerAttributes(lotpos,containerDF):
    return (containerDF.loc[(containerDF[["Lot","X","Y","Z"]] == lotpos).all(axis=1)])

def below(pos):
    return pos[0],pos[1],pos[2],max(pos[3]-1,0)

class Lot:
    def __init__(self, pos, id, size, maxStackSize, scr, scfac = 50, offset = (0, 0), name = ""):
        self.id = id
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
        self.lagsbehind = True

    def setLagsBehind(self):
        self.lagsbehind = True

    def getArray(self):
        return self.nparr

    def loadData(self, data):
        self.lagsbehind = False
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

    def render(self,scale,offset,StretchFactor):
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

if __name__ == "__main__":
    lotdata = {"ID": [0, 1, 2],
               "Name": ["lot1", "lot2", "YEA"],
               "maxStack": [5, 5, 5],
               "Size": [(15, 15), (5, 5), (15, 15)]
               }

    data = {"ContainerID": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "Name": ["InitContainer", "test1", "test2", "test3", "test4", "test5", "duplicateofInit", "test6", "test7"],
            "Lot": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "X": [0, 1, 1, 0, 0, 0, 0, 3, 5],
            "Y": [0, 0, 0, 1, 1, 1, 0, 4, 9],
            "Z": [0, 0, 1, 0, 1, 2, 1, 0, 0],
            "Priority": [True, True, False, False, True, False, True, False, False]}

    lotdf = pd.DataFrame(data=lotdata)
    datadf = pd.DataFrame(data=data)

    print(ContainerListToSingleMatrix(datadf, lotdf, 0))
    #print("Hello, World!")