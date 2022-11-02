def minDistance(inputLot,startingPoint):

    grid = inputLot.tolist()
    for i in grid:
        i.insert(0,'d')


    grid[startingPoint[0]][startingPoint[1]+1] = 's'

    source = [0,0,0]

    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == 's':
                source[0] = row
                source[1] = col
                break

    # To maintain location visit status
    visited = [[False for _ in range(len(grid[0]))]
               for _ in range(len(grid))]

    # applying BFS on matrix cells starting from source
    queue = []
    queue.append(source)
    visited[source[0]][source[1]] = True
    while len(queue) != 0:
        source = queue.pop(0)
        # Destination found;
        if (grid[source[0]][source[1]] == 'd'):
            return source[2]

        # moving up
        if isValid(source[0] - 1, source[1], grid, visited):
            queue.append((source[0] - 1, source[1], source[2] + 1))
            visited[source[0] - 1][source[1]] = True

        # moving down
        if isValid(source[0] + 1, source[1], grid, visited):
            queue.append((source[0] + 1, source[1], source[2] + 1))
            visited[source[0] + 1][source[1]] = True

        # moving left
        if isValid(source[0], source[1] - 1, grid, visited):
            queue.append((source[0], source[1] - 1, source[2] + 1))
            visited[source[0]][source[1] - 1] = True

        # moving right
        if isValid(source[0], source[1] + 1, grid, visited):
            queue.append((source[0], source[1] + 1, source[2] + 1))
            visited[source[0]][source[1] + 1] = True

    return -1

def minDistance2Points(inputLot,startingPoint,EndPoint):

    grid = inputLot.tolist()


    grid[startingPoint[0]][startingPoint[1]] = 's'

    grid[EndPoint[0]][EndPoint[1]] = 'd'

    source = [0,0,0]

    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == 's':
                source[0] = row
                source[1] = col
                break

    # To maintain location visit status
    visited = [[False for _ in range(len(grid[0]))]
               for _ in range(len(grid))]

    # applying BFS on matrix cells starting from source
    queue = []
    queue.append(source)
    visited[source[0]][source[1]] = True
    while len(queue) != 0:
        source = queue.pop(0)
        # Destination found;
        if (grid[source[0]][source[1]] == 'd'):
            return source[2]

        # moving up
        if isValid(source[0] - 1, source[1], grid, visited):
            queue.append((source[0] - 1, source[1], source[2] + 1))
            visited[source[0] - 1][source[1]] = True

        # moving down
        if isValid(source[0] + 1, source[1], grid, visited):
            queue.append((source[0] + 1, source[1], source[2] + 1))
            visited[source[0] + 1][source[1]] = True

        # moving left
        if isValid(source[0], source[1] - 1, grid, visited):
            queue.append((source[0], source[1] - 1, source[2] + 1))
            visited[source[0]][source[1] - 1] = True

        # moving right
        if isValid(source[0], source[1] + 1, grid, visited):
            queue.append((source[0], source[1] + 1, source[2] + 1))
            visited[source[0]][source[1] + 1] = True

    return -1

# checking where move is valid or not
def isValid(x, y, grid, visited):
    if ((x >= 0 and y >= 0) and
            (x < len(grid) and y < len(grid[0])) and
            (grid[x][y] != '0') and (visited[x][y] == False)):
        return True
    return False

    # This code is contributed by sajalmittaldei.
