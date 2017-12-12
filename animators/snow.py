import random
from collections import deque


class SnowAnimator:

    MINUTE = 120  # depends on clock speed

    FRAME_SIZE = 32
    MIN_WIND_DURATION = 1 * MINUTE
    MAX_WIND_DURATION = 10 * MINUTE

    def __init__(self):
        self.last_frame = None
        self.duration = 0

    def __make_row(self):
        probability = 32
        row = [0] * SnowAnimator.FRAME_SIZE

        for i, pixel in enumerate(row):
            if random.randint(1, probability) == 1:
                row[i] = 1
        return row

    def __apply_wind(self, frame):
        if self.duration == 0:
            # wind is allowed to change direction
            self.direction = random.randint(-1, 1)  # -1 left, 0 none, 1 right
            self.duration = random.randint(
                SnowAnimator.MIN_WIND_DURATION, SnowAnimator.MAX_WIND_DURATION)
        else:
            # reduce duration
            self.duration -= 1

        for i, row in enumerate(frame):
            shifted_row = deque(row)
            shifted_row.rotate(self.direction)
            frame[i] = shifted_row

    def get_frame(self):
        if self.last_frame is None:
            frame = [self.__make_row() for _ in range(SnowAnimator.FRAME_SIZE)]
        else:
            frame = deque(self.last_frame)
            frame.rotate(1)
            # add a new random row at the top
            frame[0] = self.__make_row()
            self.__apply_wind(frame)
        self.last_frame = frame
        return frame
