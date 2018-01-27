import random
import time

class GameOfLifeAnimator:

    FRAME_SIZE = 32


    def __init__(self):
        self.last_frame = None

    def __make_row(self):
        probability = 8
        row = [0] * GameOfLifeAnimator.FRAME_SIZE

        for i, pixel in enumerate(row):
            if random.randint(1, probability) == 1:
                row[i] = 1
        return row

    def __get_first_frame(self):
        # initialize the frame
        return [self.__make_row() for _ in range(self.FRAME_SIZE)]


    def decide_fate(self, x, y):
        """
        1 Any live cell with fewer than two live neighbours dies
        2 Any live cell with two or three live neighbours lives on
        3 Any live cell with more than three live neighbours dies
        4 Any dead cell with exactly three live neighbours becomes a live cell
        """
        alive = 0
        dead = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if (dy != 0 or dx != 0) and (x + dx >= 0 and y + dy >= 0):
                    # do not allow dx=0 dy=0 to avoid checking the same Point,
                    try:
                        neighbor = self.last_frame[y + dy][x + dx]
                        if neighbor:  # neighbor is alive
                            alive += 1
                        else:
                            dead += 1
                    except IndexError:
                        # an "edge" of the map was hit, which is a dead cell
                        dead += 1

        if self.last_frame[y][x]:
            # cell is alive, check 1,2,3
            if alive < 2 or alive > 3:
                result = 0
            else:
                result = 1
        else:
            # cell is dead, check 4
            if alive == 3:
                result = 1
            else: 
                result = 0
            
        return result

    def next_iteration(self):
        size = self.FRAME_SIZE
        next_frame = []
        for _ in range(size):
            next_frame.append([0] * 32)

        for y in range(size):
            for x in range(size):
                next_frame[y][x] = self.decide_fate(x, y)
        return next_frame

    def get_frame(self):
        if self.last_frame is None:
            frame = self.__get_first_frame()
        else:
            # do next iteration
            frame = self.next_iteration()

        self.last_frame = frame
        return frame
