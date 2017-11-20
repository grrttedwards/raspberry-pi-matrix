from PIL import Image
import random
from collections import deque


class SnowAnimator:

    last_frame = None
    frame_size = 32

    def __make_row(self):
        probability = 32
        row = [0] * self.frame_size
        for i, pixel in enumerate(row):
            if random.randint(1, probability) == 1:
                row[i] = 1
        return row

    def get_frame(self):
        if self.last_frame is None:
            frame = [self.__make_row() for _ in range(self.frame_size)]
        else:
            frame = deque(self.last_frame)
            frame.rotate(1)
        self.last_frame = frame
        return frame
