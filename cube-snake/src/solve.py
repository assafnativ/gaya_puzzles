import time
import math

class Point3D( object ):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def __repr__(self):
        return repr((self.x, self.y, self.z))
    def __add__(self, other):
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
    def __hex__(self):
        return "0x%x, 0x%x, 0x%x" % (self.x, self.y, self.z)
    def __str__(self):
        return "%d,%d,%d" % (self.x, self.y, self.z)
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)
    def __ne__(self, other):
        return not self == other
    def __neg__(self):
        return Point3D(-self.x, -self.y, -self.z)
    def __mul__(self, scalar):
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)
    def __hash__(self):
        return int((2 ** self.x) * (3 ** self.y) * (5 ** self.z))

class Cube(object):
    def __init__(self, cubeSize):
        self.size = cubeSize
        self.topConner = Point3D(self.size-1, self.size-1, self.size-1)
        self.data = [[[0]*self.size for _ in range(self.size)] for _ in range(self.size)]

    def __repr__(self):
        result = ''
        for plan in self.data:
            for row in plan:
                for val in row:
                    if 0 == val:
                        result += '-'
                    elif val < 10:
                        result += str(val)
                    elif val < (10 + ord('z') - ord('a')):
                        result += chr(val - 10 + ord('a'))
                    else:
                        result += chr(val - 10 + ord('A') - ord('z') + ord('a'))
                result += '\n'
            result += '/' * self.size
            result += '\n'
        result += '\n'
        return result

    def isValidLocation(self, pos):
        if pos.x < 0 or pos.y < 0 or pos.z < 0:
            return False
        if self.topConner.x < pos.x or self.topConner.y < pos.y or self.topConner.z < pos.z:
            return False
        return True

    def writeSquares(self, pos, direction, length, value):
        for i in range(length):
            self.data[pos.z][pos.y][pos.x] = value
            pos += direction

    def get(self, pos):
        return self.data[pos.z][pos.y][pos.x]

class Puzzle(object):
    def __init__(self, jointsData):
        numSquares = sum(jointsData)
        self.size = int(math.ceil(numSquares ** (1.0/3)))
        assert(self.size ** 3 == sum(jointsData))
        self.cube = Cube(self.size)
        self.joints = jointsData
        XDirection = Point3D( 1,  0,  0)
        YDirection = Point3D( 0,  1,  0)
        ZDirection = Point3D( 0,  0,  1)
        self.AllDirections = [XDirection, -XDirection, YDirection, -YDirection, ZDirection, -ZDirection]

    def attemptMove(self, direction, length):
        endPos = self.pos + (direction * length)
        if not self.cube.isValidLocation(endPos):
            return False
        tempPos = self.pos
        for i in range(length):
            tempPos += direction
            if 0 != self.cube.get(tempPos):
                return False
        return True

    def isFreePlace(self, pos):
        if not self.cube.isValidLocation(pos):
            return False
        if 0 != self.cube.get(pos):
            return False
        return True

    def isThereAHole(self):
        for z in range(self.size):
            for y in range(self.size):
                for x in range(self.size):
                    if 0 != self.cube.get(Point3D(x,y,z)):
                        continue
                    for direction in self.AllDirections:
                        if self.isFreePlace(Point3D(x,y,z) + direction):
                            break
                    else:
                        return True
        return False

    def step(self, jointsLeft, done):
        blockIndex = len(jointsLeft)
        if 0 == blockIndex:
            self.cube.writeSquares(self.pos, self.pos, 1, 1)
            return done
        if 0 < len(done):
            lastDirection = done[-1]
        else:
            lastDirection = Point3D(0,0,0)
        length = jointsLeft[0]
        jointsLeft = jointsLeft[1:]
        for direction in self.AllDirections:
            if lastDirection == direction:
                continue
            if True == self.attemptMove(direction, length):
                self.cube.writeSquares(self.pos, direction, length, blockIndex)
                self.pos += direction * length
                if blockIndex < 4 or len(done) < 4 or not self.isThereAHole():
                    solution = self.step(jointsLeft[:], done + [direction])
                    if None != solution:
                        return solution
                self.cube.writeSquares(self.pos, -direction, length, 0)
                self.pos -= direction * length

    def solve(self):
        self.startTime = time.time()
        self.pos = Point3D(0,0,0)
        self.cube.writeSquares(self.pos, self.pos, 1, len(self.joints))
        self.joints = [self.joints[0] - 1] + self.joints[1:]
        solution = self.step(self.joints, [])
        self.endTime = time.time()
        return solution

cube4x4     = [3,1,2,1,1,3,1,2,1,2,1,2,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,2,3,1,1,1,3,1,2,1,1,1,1,1,1,1,1,1,3,1]
cube3x3     = [3,1,1,2,1,2,1,1,2,2,1,1,1,2,2,2,2]
cube3x3_v2  = [3,1,1,1,2,1,1,1,1,1,1,1,2,2,2,2,1,1,2]
puzzle = Puzzle(cube3x3)
solution = puzzle.solve()
print(puzzle.cube)
MOVES_NAMES = {
        Point3D(-1,  0,  0): 'L',
        Point3D( 1,  0,  0): 'R',
        Point3D( 0, -1,  0): 'D',
        Point3D( 0,  1,  0): 'U',
        Point3D( 0,  0, -1): 'I',
        Point3D( 0,  0,  1): 'O'}
print(','.join([MOVES_NAMES[step] for step in solution]))
print("Took %f sec" % (puzzle.endTime - puzzle.startTime))
