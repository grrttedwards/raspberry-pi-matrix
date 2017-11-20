from PIL import Image
import random
from collections import deque


class SnowAnimator:

    last_frame = None
    frame_size = 32

    def __make_row(self):
        probability = 3
        row = [0] * self.frame_size
        for i, pixel in enumerate(row):
            if random.randint(1, self.frame_size) - probability <= 0:
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

    def create_image(self, image, tag):
        """From the map, generate a PNG along with the path overlaid"""
        output = Image.new('RGB', (32, 32))
        for y in range(32):
            for x in range(32):
                if image[y][x]:
                    color = (255, 255, 255)
                else:
                    color = (0,0,0)
                output.putpixel((x, y), color)
        # output.show()
        # output.save(f'out\out-{tag}.png')
        # return output

    #
    # frame = get_frame()
    # for i in range(60):
    #     new_frame = get_frame(frame)
    #     create_image(new_frame, i)
    #     frame = new_frame
