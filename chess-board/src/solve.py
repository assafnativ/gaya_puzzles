from builtins import range
import copy
import colorama
import colors
import time
colorama.init(True)

ANSI_COLORS = list(colors.COLORS)
ANSI_COLORS.remove('white')
ANSI_COLORS.remove('black')
ANSI_COLORS = ANSI_COLORS * 2
ANSI_COLORS = [(x, '') for x in ANSI_COLORS]
ANSI_COLORS.extend([(x, 'bold') for x, _, in ANSI_COLORS])

class Block(object):
    def __init__(self, lines):
        self.lines = lines
        countZeros = 0
        for x in lines[0]:
            if x != 0:
                break
            countZeros += 1
        self.leadingZeros = countZeros
        self.blockCount = 0
        for line in lines:
            self.blockCount += len(line) - line.count(0)
        self.len_x = len(lines[0])
        self.len_y = len(lines)

    def __eq__(self, other):
        if len(self.lines) != len(other.lines):
            return False
        for l1, l2 in zip(self.lines, other.lines):
            if l1 != l2:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        tempStr = '|'.join([''.join([str(x) for x in l]) for l in self.lines])
        return str(tempStr).__hash__()

    def count(self, x):
        return sum([self.linecount(x) for line in self.lines])

    def getSize(self):
        return (self.len_x, self.len_y)

    def toStr(self, color=None):
        if None == color:
            color = ('white', '')
        output = ''
        for line in self.lines:
            for val in line:
                if 1 == val:
                    output += colors.color('#', '', color[0], color[1])
                elif 2 == val:
                    output += colors.color('*', '', color[0], color[1])
                else:
                    output += ' '
            output += '\n'
        return output

def BlockRotate90(block):
    result = []
    block_len_x, block_len_y = block.getSize()
    for x in range(block_len_x):
        result.append([block.lines[y][x] for y in range(block_len_y)])
    return Block(result)

def BlockMirrorUpDown(block):
    result = [copy.deepcopy(x) for x in block.lines[::-1]]
    return Block(result)

def BlockMirrorLeftRight(block):
    result = []
    for line in block.lines:
        result.append(line[::-1])
    return Block(result)

class ChessPuzzel(object):
    def __init__(self, blocks, BOARD_X=8, BOARD_Y=8, withColors=True):
        self.BOARD_X = BOARD_X
        self.BOARD_Y = BOARD_Y
        self.board = [[0] * self.BOARD_X for _ in range(self.BOARD_Y)]
        self.blocks = blocks
        total = 0

        self.validateBlocksAndBoard(blocks)
        if not withColors:
            self.blocks = self.removeColors(blocks)
        else:
            self.blocks = blocks

        self.blocksWithVariations = [self.generateBlockVariants(block) for block in self.blocks]
        self.blocksLeft = [count for count, _ in blocks]

    def validateBlocksAndBoard(self, blocks):
        total = sum([count * block.blockCount for count, block in blocks])
        assert((self.BOARD_X * self.BOARD_Y) == total)

    def removeColors(self, blocks):
        noColors = []
        for count, block in blocks:
            blockWithoutColors = []
            for line in block.lines:
                blockWithoutColors.append([[0,1][x!=0] for x in line])
            noColors.append((count, Block(blockWithoutColors)))
        return noColors

    def isblockInList(self, block, lst):
        for blockFromList in lst:
            if blockFromList == block:
                return True
        return False

    def generateBlockVariants(self, block):
        count, block = block
        result = set()
        result.add(block)
        transformers = [
                BlockRotate90,
                lambda x:BlockRotate90(BlockRotate90(x)),
                lambda x:BlockRotate90(BlockRotate90(BlockRotate90(x))),
                BlockMirrorUpDown,
                lambda x:BlockMirrorUpDown(BlockRotate90(x)),
                lambda x:BlockMirrorUpDown(BlockRotate90(BlockRotate90(x))),
                lambda x:BlockMirrorUpDown(BlockRotate90(BlockRotate90(BlockRotate90(x)))),
                BlockMirrorLeftRight,
                lambda x:BlockMirrorLeftRight(BlockRotate90(x)),
                lambda x:BlockMirrorLeftRight(BlockRotate90(BlockRotate90(x))),
                lambda x:BlockMirrorLeftRight(BlockRotate90(BlockRotate90(BlockRotate90(x)))),
                lambda x:BlockMirrorLeftRight(BlockMirrorUpDown(x)),
                lambda x:BlockMirrorLeftRight(BlockMirrorUpDown(BlockRotate90(x))),
                lambda x:BlockMirrorLeftRight(BlockMirrorUpDown(BlockRotate90(BlockRotate90(x)))),
                lambda x:BlockMirrorLeftRight(BlockMirrorUpDown(BlockRotate90(BlockRotate90(BlockRotate90(x))))),
                lambda x:BlockMirrorUpDown(BlockMirrorLeftRight(x)),
                lambda x:BlockMirrorUpDown(BlockMirrorLeftRight(BlockRotate90(x))),
                lambda x:BlockMirrorUpDown(BlockMirrorLeftRight(BlockRotate90(BlockRotate90(x)))),
                lambda x:BlockMirrorUpDown(BlockMirrorLeftRight(BlockRotate90(BlockRotate90(BlockRotate90(x))))) ]

        for transformetion in transformers:
            result.add(transformetion(block))
        return list(result)

    def doesBlockFit(self, x, y, board, block):
        if x < 0:
            return False
        block_len_x, block_len_y = block.getSize()
        if self.BOARD_X < block_len_x + x:
            return False
        if self.BOARD_Y < block_len_y + y:
            return False
        for offset_y, line in enumerate(block.lines):
            for offset_x, val in enumerate(line):
                if 0 == val:
                    continue
                board_x = x + offset_x
                board_y = y + offset_y
                if 0 != self.board[board_y][board_x]:
                    return False
                # Check black/white
                if (val - 1) != ((board_x + board_y) & 1):
                    return False
        return True

    def findNextEmptySpace(self):
        for y in range(self.BOARD_Y):
            for x in range(self.BOARD_X):
                if 0 == self.board[y][x]:
                    return x, y
        return self.BOARD_X, self.BOARD_Y

    def isNotFreeSpace(self, board, x, y):
        if x < 0 or self.BOARD_X <= x:
            return True
        if y < 0 or self.BOARD_Y <= y:
            return True
        return 0 != self.board[y][x]

    def isThereAHole(self, min_y):
        for y in range(min_y, self.BOARD_Y):
            for x in range(self.BOARD_X):
                if 0 == self.board[y][x]:
                    if      self.isNotFreeSpace(self.board,x-1,y) and \
                            self.isNotFreeSpace(self.board,x+1,y) and \
                            self.isNotFreeSpace(self.board,x,y-1) and \
                            self.isNotFreeSpace(self.board,x,y+1):
                                return True
        return False

    def maskBlock(self, x, y, block, val):
        for offset_y, line in enumerate(block.lines):
            for offset_x, square in enumerate(line):
                if 0 != square:
                    self.board[y + offset_y][x + offset_x] = val


    def nextBlock(self):
        x, y = self.findNextEmptySpace()
        numBlocksLeft = sum(self.blocksLeft)
        for blockIndex, count in enumerate(self.blocksLeft):
            if 0 == count:
                continue

            blockId = blockIndex + 1
            for variation in self.blocksWithVariations[blockIndex]:

                temp_x = x - variation.leadingZeros
                if False == self.doesBlockFit(temp_x, y, self.board, variation):
                    continue

                # Put block
                self.maskBlock(temp_x, y, variation, blockId)

                if not self.isThereAHole(y):
                    self.blocksLeft[blockIndex] -= 1
                    numBlocksLeft -= 1

                    if 0 == numBlocksLeft:
                        return [(y, temp_x, variation, blockId)]
                    result = self.nextBlock()
                    if None != result:
                        return [(y, temp_x, variation, blockId)] + result
                    self.blocksLeft[blockIndex] += 1
                    numBlocksLeft += 1

                # Undo block put
                self.maskBlock(temp_x, y, variation, 0)

        return None

    def solve(self):
        return self.nextBlock()

    def printBoard(self):
        left = 0
        print('*' * 20)
        for line in self.board:
            output_line = ''
            for val in line:
                if 0 == val:
                    output_line += '.'
                    left += 1
                else:
                    output_line += colors.color('%x' % val, 'black', ANSI_COLORS[val][0], ANSI_COLORS[val][1])
            print(output_line)
        print("Squares left: %d" % left)

    def printSolution(self, solution):
        self.printBoard()

        for x, y, block, blockId in solution:
            print('Block: %d' % blockId)
            print('position: (%d, %d)' % (x, y))
            print(block.toStr(ANSI_COLORS[blockId]))

blocks_v1 = [
        (1,Block([
            [0, 0, 1],
            [0, 1, 2],
            [1, 2, 1]
            ])),
        (1,Block([
            [0, 0, 2],
            [0, 2, 1],
            [2, 1, 2]
            ])),
        (1,Block([
            [1, 2, 1, 0],
            [0, 1, 2, 1]
            ])),
        (1,Block([
            [2, 0, 2],
            [1, 2, 1]
            ])),
        (1,Block([
            [1, 2, 1, 2],
            [2, 0, 0, 0],
            [1, 0, 0, 0]
            ])),
        (1,Block([
            [0, 2],
            [2, 1],
            [1, 0]
            ])),
        (1,Block([
            [0, 1, 0],
            [1, 2, 1]
            ])),
        (2,Block([
            [1, 2, 1, 2],
            [0, 1, 0, 0]
            ])),
        (2,Block([
            [2, 1, 2, 1],
            [0, 0, 0, 2]
            ])),
        (1,Block([
            [2, 0, 2],
            [1, 2, 1],
            [2, 0, 2]
            ]))
        ]

blocks_v2 = [
        (1,Block([
            [0, 2, 1],
            [2, 1, 0],
            [1, 0, 0]
            ])),
        (1,Block([
            [2, 1, 2],
            [0, 0, 1],
            [0, 0, 2]
            ])),
        (1,Block([
            [2, 1, 2, 1],
            [0, 2, 0, 0]
            ])),
        (1,Block([
            [2, 1, 2, 1],
            [1, 0, 0, 0]
            ])),
        (1,Block([
            [2, 1, 2, 0],
            [0, 0, 1, 2]
            ])),
        (1,Block([
            [1, 2, 1, 2],
            [0, 0, 0, 1]
            ])),
        (1,Block([
            [1, 2, 1],
            [2, 0, 0]
            ])),
        (1,Block([
            [0, 2, 0],
            [2, 1, 2],
            [0, 2, 0]
            ])),
        (1,Block([
            [2, 1, 2],
            [0, 2, 0]
            ])),
        (1,Block([
            [2, 1, 2],
            [1, 0, 1]
            ])),
        (1,Block([
            [1, 2, 1]
            ])),
        (1,Block([
            [2, 1, 0],
            [0, 2, 1],
            [0, 1, 0]
            ])),
        (1,Block([
            [1, 2, 0],
            [0, 1, 0],
            [0, 2, 1]
            ])),
        (1, Block([
            [2, 1],
            [1, 0]
            ]))
        ]


chessPuzzel = ChessPuzzel(blocks_v1)

startTime = time.time()
solution = chessPuzzel.solve()
endTime = time.time()
chessPuzzel.printSolution(solution)
print("Total time: %f" % (endTime - startTime))


