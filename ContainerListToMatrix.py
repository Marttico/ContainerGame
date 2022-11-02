import numpy as np
import pandas as pd


# ---------------------------------
# Input:  Container List Dataframe
#        Lot info Dataframe
#
# Output: Heightmap of lot np array
# ---------------------------------

# TODO: Add support for multiple lots.

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
        #f = df[np.all(df[["Lot", "X", "Y", "Z"]] == i,axis=1)].loc[:,"Priority"].values[0]
        #print(f)
        priomatrix[i[0]][i[1],i[2]] = df[np.all(df[["Lot", "X", "Y", "Z"]] == i,axis=1)].loc[:,"Priority"].values[0]
    #print(lots[lots[["Lot", "X", "Y", "Z"]].iterrows() == topcontainers])
    #print(df[["Lot", "X", "Y", "Z"]] == topcontainers)

    return priomatrix



def ContainerListToMatrix(df, lots):
    # Check if there's no duplicates.
    clearedChecks = True
    ErrorString = ""
    outputList = []
    if (df["ContainerID"].duplicated().sum()):
        print("There are duplicate ID's in your dataset.")
        clearedChecks = False
        ErrorString += "Duplicate ID's in your dataset. "

    if (df[["Lot", "X", "Y", "Z"]].duplicated().sum()):
        print("There are duplicate coordinates in your dataset.")
        clearedChecks = False
        ErrorString += "Duplicate coordinates in your dataset. "

    if (lots.dropna().empty):
        print("Your lots dataset is empty.")
        clearedChecks = False
        ErrorString += "Lots dataset empty. "

    if (lots.columns.to_list() != ["ID", "Name", "maxStack", "Size"]):
        print("Lots dataset is not formatted correctly.")
        clearedChecks = False
        ErrorString += "Lots dataset not formatted correctly. "

    if (not clearedChecks):
        raise ValueError(ErrorString)

    lotlist = []
    for i in lots.iterrows():
        lotlist.append(np.zeros((i[1]["Size"][0], i[1]["Size"][1], i[1]["maxStack"]), dtype=int))

    # Add containers to lotlists
    for i in df[["Lot", "X", "Y", "Z"]].iterrows():
        lotlist[i[1]["Lot"]][i[1]["X"], i[1]["Y"], i[1]["Z"]] = 1
        # print(i[1].to_numpy())
    for i in lotlist:
        result = np.where(i == 1)
        trueCoordinates = list(zip(result[0], result[1], result[2]))

        for o in trueCoordinates:
            belowContents = i[o[0], o[1], :o[2]]

            if not (np.array(belowContents).size == 0 or np.array(belowContents).sum() != 0):
                print("Floating containers found in container dataset.")
                raise ValueError("Floating Containers Found.")
        outputList.append(i.sum(axis=2))
    return outputList


def MatrixToCollisionMatrix(matrix, AgentSize=4):
    outputMatrix = np.array(matrix)
    for i in range(AgentSize):
        appendingMatrix = np.append(np.zeros((matrix.shape[0], (i)), dtype=int), matrix[:, :matrix.shape[1] - i], 1)
        # print(i,appendingMatrix)

        outputMatrix += appendingMatrix

    # print(outputMatrix)
    return np.array(outputMatrix != 0, dtype=int)


lotdata = {"ID": [0],
           "Name": ["lot1"],
           "maxStack": [5],
           "Size": [(5, 5)]
           }

data = {"ContainerID": [1, 2, 3, 4, 5, 6, 7, 8],
        "Name": ["InitContainer", "test1", "test2", "test3", "test4", "test5", "duplicateofInit", "test6"],
        "Lot": [0, 0, 0, 0, 0, 0, 0, 0],
        "X": [0, 1, 1, 0, 0, 0, 0, 3],
        "Y": [0, 0, 0, 1, 1, 1, 0, 4],
        "Z": [0, 0, 1, 0, 1, 2, 1, 0]}

# MatrixToCollisionMatrix(ContainerListToMatrix(pd.DataFrame(data=data),pd.DataFrame(data=lotdata)))


