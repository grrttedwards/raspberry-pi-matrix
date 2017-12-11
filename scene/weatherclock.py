#!/usr/bin/env python3

# Display a WeatherClock with double-buffering.
import sys
import os
import time
import datetime as dt
import requests
from base import BaseScene
from rgbmatrix import graphics
from PIL import Image
sys.path.append('../')
from animators import snow


class WeatherClock(BaseScene):

    def __init__(self):
        super().__init__()

        try:
            self.city_id = self.config['weather']['city_id']
            self.api_key = self.config['weather']['api_key']
            self.start_time = (self.config['time'].getint('start_hr'), self.config['time'].getint('start_min'))
            self.end_time = (self.config['time'].getint('end_hr'), self.config['time'].getint('end_min'))
        except KeyError as err:
            self.settings_error(err)

        # endpoints for the weather APIs
        self.base_url = 'http://api.openweathermap.org/data/2.5'
        self.current_url = (self.base_url + '/weather?id={}&APPID={}'
                    .format(self.city_id, self.api_key))
        self.day_url = (self.base_url + '/forecast/daily?id={}&APPID={}&cnt=1'
               .format(self.city_id, self.api_key))

        self.last_weather = None
        self.animator = None
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()


    img_path = '../img/weather/'
    weather_icons = {
        '01d': 'sunny.bmp',                 # clear sky
        '02d': 'partly-cloudy.bmp',         # few clouds
        '03d': 'cloudy.bmp',                # scattered clouds
        '04d': 'cloudy.bmp',                # broken clouds
        '09d': 'rainy.bmp',                 # shower rain
        '10d': 'rainy.bmp',                 # rain
        '11d': 'thundery.bmp',              # thunderstorm
        '13d': 'snowy.bmp',                 # snow
        '50d': 'misty.bmp',                 # mist
        '01n': 'moony.bmp',                 # night clear sky
        '02n': 'partly-cloudy-night.bmp'    # night few clouds
    }

    font_path = '../matrix/fonts/'
    # time styling and positioning
    time_font = graphics.Font()
    time_font.LoadFont(font_path + '6x10.bdf')
    time_color = graphics.Color(255, 110, 255)
    time_x, time_y = 1, 10

    # weather icon styling and positioning
    icon_x, icon_y = 2, 16

    # temp styling and positioning
    temp_font = graphics.Font()
    temp_font.LoadFont(font_path + '5x7.bdf')
    temp_color = graphics.Color(0, 179, 239)
    temp_x, temp_y = 17, 24

    temp_mm_font = graphics.Font()
    temp_mm_font.LoadFont(font_path + '4x6.bdf')
    temp_mm_color = graphics.Color(100, 150, 0)
    temp_max_x, temp_max_y = 20, 17
    temp_min_x, temp_min_y = 20, 30

    def __k_to_f(self, kelvin):
        return str(round(kelvin * 9 / 5 - 459.67))

    def get_weather_icon(self, icon):
        try:
            icon_path = self.weather_icons[icon]
        except KeyError:
            # if no night glyph then get the day variant
            icon_path = self.weather_icons[icon.replace('n', 'd')]
        return icon_path

    def __backoff(self):
        for attempts in range(5):
            # raise the power of exponential backoff
            yield 5**attempts

    def __make_request(self, url):
        backoff = self.__backoff()
        for attempt in backoff:
            try:
                req = requests.get(url)
                if not req.ok:
                    raise Exception(req.status_code, req.content)
                json = req.json()
                return json
            except Exception as e:
                print(e)
                print('Attempting {0}-second backoff...'.format(attempt))
                time.sleep(attempt)
        raise Exception('5 requests failed.')

    def __get_weather(self):
        json = self.__make_request(self.current_url)
        icon = json['weather'][0]['icon']
        icon_path = self.img_path + self.get_weather_icon(icon)
        glyph = Image.open(icon_path).convert('RGB')
        temperature = self.__k_to_f(json['main']['temp']) + 'F'

        # make a second request to the daily forecast for temp high and low
        json = self.__make_request(self.day_url)
        temp_min = self.__k_to_f(json['list'][0]['temp']['min'])
        temp_max = self.__k_to_f(json['list'][0]['temp']['max'])

        self.last_weather = (temperature, temp_min, temp_max, glyph, self.get_weather_icon(icon))

    def draw_time(self):
        # set up the time display
        cur_time = dt.datetime.now().strftime('%I %M')
        # if the time is 0X XX then replace the 0 with a space
        if cur_time.startswith('0'):
            cur_time = ' ' + cur_time[1:]

        graphics.DrawText(self.offscreen_canvas, self.time_font, self.time_x,
                          self.time_y, self.time_color, cur_time)

    def draw_weather(self):
        temp, temp_min, temp_max, glyph, icon_path = self.last_weather

        if icon_path == 'snowy.bmp':
            if self.animator is None:
                self.animator = snow.SnowAnimator()
            frame = self.animator.get_frame()
            for y, row in enumerate(frame):
                for x, pixel in enumerate(row):
                    if pixel:
                        self.offscreen_canvas.SetPixel(x, y, 255, 255, 255)
                    else:
                        self.offscreen_canvas.SetPixel(x, y, 0, 0, 0)
        else:
            self.animator = None


        self.offscreen_canvas.SetImage(glyph, self.icon_x, self.icon_y)
        # set up the temperature display
        graphics.DrawText(self.offscreen_canvas, self.temp_mm_font,
                          self.temp_max_x, self.temp_max_y,
                          self.temp_mm_color, temp_max)
        graphics.DrawText(self.offscreen_canvas, self.temp_font,
                          self.temp_x, self.temp_y,
                          self.temp_color, temp)
        graphics.DrawText(self.offscreen_canvas, self.temp_mm_font,
                          self.temp_min_x, self.temp_min_y,
                          self.temp_mm_color, temp_min)

    def run(self):
        while True:
            if dt.time(*self.end_time) > \
                    dt.datetime.now().time() >= dt.time(*self.start_time):

                # schedule one weather update immediately
                time_to_update = dt.datetime.now()

                # colon toggle for time
                colon = True
                while True:
                    # when to go blank for the night
                    if dt.datetime.now().time() >= dt.time(*self.end_time):
                        self.matrix.Clear()
                        break

                    # do weather if enough time has passed
                    if dt.datetime.now() >= time_to_update:
                        self.__get_weather()
                        time_to_update = dt.datetime.now() + \
                            dt.timedelta(hours=1)

                    self.offscreen_canvas.Clear()
                    self.draw_weather()
                    self.draw_time()
                    self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

                    time.sleep(0.5)
            else:
                time.sleep(1)


# Main function
if __name__ == '__main__':
    WeatherClock().run()
