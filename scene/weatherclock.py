#!/usr/bin/env python3

# Display a WeatherClock with double-buffering.
import os
import time
import datetime as dt
import requests
from base import BaseScene
from rgbmatrix import graphics
from PIL import Image


class WeatherClock(BaseScene):

    def __init__(self, *args, **kwargs):
        super(WeatherClock, self).__init__(*args, **kwargs)

        try:
            self.city_id = self.config['weather']['city_id']
            self.api_key = self.config['weather']['api_key']
            self.start_time = (self.config['time'].getint('start_hr'), self.config['time'].getint('start_min'))
            self.end_time = (self.config['time'].getint('end_hr'), self.config['time'].getint('end_min'))
        except KeyError as err:
            print("Settings file error: {0}".format(err))
            exit(1)

        # endpoints for the weather APIs
        self.current_url = ("http://api.openweathermap.org/data/2.5/weather?id={}&APPID={}"
                    .format(self.city_id, self.api_key))
        self.day_url = ("http://api.openweathermap.org/data/2.5/forecast/daily?id={}&APPID={}&cnt=1"
               .format(self.city_id, self.api_key))

    img_path = "../img/"
    weather_icons = {
        '01d': "sunny.bmp",                 # clear sky
        '02d': "partly-cloudy.bmp",         # few clouds
        '03d': "cloudy.bmp",                # scattered clouds
        '04d': "cloudy.bmp",                # broken clouds
        '09d': "rainy.bmp",                 # shower rain
        '10d': "rainy.bmp",                 # rain
        '11d': "thundery.bmp",              # thunderstorm
        '13d': "snowy.bmp",                 # snow
        '50d': "misty.bmp",                 # mist
        '01n': "moony.bmp",                 # night clear sky
        '02n': "partly-cloudy-night.bmp"    # night few clouds
    }

    font_path = "../matrix/fonts/"
    # time styling and positioning
    time_font = graphics.Font()
    time_font.LoadFont(font_path + "6x10.bdf")
    time_color = graphics.Color(255, 110, 255)
    time_x, time_y = 1, 10

    # weather icon styling and positioning
    icon_x, icon_y = 2, 16

    # temp styling and positioning
    temp_font = graphics.Font()
    temp_font.LoadFont(font_path + "5x7.bdf")
    temp_color = graphics.Color(0, 179, 239)
    temp_x, temp_y = 17, 24

    temp_mm_font = graphics.Font()
    temp_mm_font.LoadFont(font_path + "4x6.bdf")
    temp_mm_color = graphics.Color(100, 150, 0)
    temp_max_x, temp_max_y = 20, 17
    temp_min_x, temp_min_y = 20, 30

    def __k_to_f(self, kelvin):
        return str(kelvin * 9 / 5 - 459.67)

    def get_weather_icon(self, icon):
        try:
            icon_path = self.weather_icons[icon]
        except KeyError:
            # if no night glyph then get the day variant
            icon_path = self.weather_icons[icon.replace('n', 'd')]
        return self.img_path + icon_path

    def __make_request(self, url):
        req = requests.get(url)
        json = req.json()
        if req.status_code != 200:
            print(req, json)
            exit(1)
        return json

    def __get_weather(self):
        json = self.__make_request(self.current_url)
        icon = json['weather'][0]['icon']
        icon_path = self.get_weather_icon(icon)
        glyph = Image.open(icon_path).convert('RGB')
        temperature = self.__k_to_f(json['main']['temp']) + "F"

        # make a second request to the daily forecast for temp high and low
        json = self.__make_request(self.day_url)
        temp_min = self.__k_to_f(json['list'][0]['temp']['min'])
        temp_max = self.__k_to_f(json['list'][0]['temp']['max'])

        return temperature, temp_min, temp_max, glyph

    def draw_time(self, colon):
        # set up the time display
        cur_time = dt.datetime.now().strftime('%H:%M')
        if colon:
            cur_time = cur_time.replace(':', ' ')
        # enough height to clear the whole time area
        for y_val in range(0, 11):
            graphics.DrawLine(self.matrix, 0, y_val, 32, y_val,
                              graphics.Color(0, 0, 0))

        graphics.DrawText(self.matrix, self.time_font, self.time_x,
                          self.time_y, self.time_color, cur_time)

    def get_and_draw_weather(self):
        temp, temp_min, temp_max, glyph = self.__get_weather()
        self.matrix.Clear()
        # set up the weather glyph to display
        self.matrix.SetImage(glyph, self.icon_x, self.icon_y)
        # set up the temperature display
        graphics.DrawText(self.matrix, self.temp_mm_font,
                          self.temp_max_x, self.temp_max_y,
                          self.temp_mm_color, temp_max)
        graphics.DrawText(self.matrix, self.temp_font,
                          self.temp_x, self.temp_y,
                          self.temp_color, temp)
        graphics.DrawText(self.matrix, self.temp_mm_font,
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
                        self.get_and_draw_weather()
                        time_to_update = dt.datetime.now() + \
                            dt.timedelta(hours=1)

                    self.draw_time(colon)
                    colon = not colon

                    time.sleep(1)
            else:
                time.sleep(1)


# Main function
if __name__ == "__main__":
    WeatherClock().run()
