#!/usr/bin/python
# Display a WeatherClock with double-buffering.
import os
import time
import datetime as dt
import requests
from base import BaseScene
from rgbmatrix import graphics
from PIL import Image


class WeatherClock(BaseScene):

    try:
        city_id = os.environ['WEATHER_CITY_ID']
        api_key = os.environ['WEATHER_API_KEY']
    except KeyError:
        print("WEATHER_CITY_ID or WEATHER_API_KEY is not set. Exiting.")
        exit(1)

    # endpoints for the weather APIs
    current_url = ("http://api.openweathermap.org/data/2.5/weather?id={}&APPID={}"
                   .format(city_id, api_key))
    day_url = ("http://api.openweathermap.org/data/2.5/forecast/daily?id={}&APPID={}&cnt=1"
               .format(city_id, api_key))

    weather_icons = {
        '01d': "img/sunny.bmp",                 # clear sky
        '02d': "img/partly-cloudy.bmp",         # few clouds
        '03d': "img/cloudy.bmp",                # scattered clouds
        '04d': "img/cloudy.bmp",                # broken clouds
        '09d': "img/rainy.bmp",                 # shower rain
        '10d': "img/rainy.bmp",                 # rain
        '11d': "img/thundery.bmp",              # thunderstorm
        '13d': "img/snowy.bmp",                 # snow
        '50d': "img/misty.bmp",                 # mist
        '01n': "img/moony.bmp",                 # night clear sky
        '02n': "img/partly-cloudy-night.bmp"    # night few clouds
    }

    # time styling and positioning
    time_font = graphics.Font()
    time_font.LoadFont("matrix/fonts/6x10.bdf")
    time_color = graphics.Color(255, 110, 255)
    time_x, time_y = 1, 10

    # weather icon styling and positioning
    icon_x, icon_y = 2, 16

    # temp styling and positioning
    temp_font = graphics.Font()
    temp_font.LoadFont("matrix/fonts/5x7.bdf")
    temp_color = graphics.Color(0, 179, 239)
    temp_x, temp_y = 17, 24

    temp_mm_font = graphics.Font()
    temp_mm_font.LoadFont("matrix/fonts/4x6.bdf")
    temp_mm_color = graphics.Color(100, 150, 0)
    temp_max_x, temp_max_y = 20, 17
    temp_min_x, temp_min_y = 20, 30

    def __init__(self, *args, **kwargs):
        super(WeatherClock, self).__init__(*args, **kwargs)

    def __k_to_f(self, kelvin):
        return int(kelvin * 9 / 5 - 459.67)

    def __get_weather(self):
        req = requests.get(self.current_url)
        json = req.json()
        if req.status_code != 200:
            print(req, json)
            exit(1)
        icon = json['weather'][0]['icon']
        # see if there is a night glyph else get the day variant
        try:
            icon_path = self.weather_icons[icon]
        except KeyError:
            icon_path = self.weather_icons[icon.replace('n', 'd')]
        glyph = Image.open(icon_path).convert('RGB')
        temperature = str(self.__k_to_f(json['main']['temp'])) + "F"

        # make a second requst to the daily forecast for temp high and low
        req = requests.get(self.day_url)
        json = req.json()
        if req.status_code != 200:
            print(req, json)
        temp_min = str(self.__k_to_f(json['list'][0]['temp']['min']))
        temp_max = str(self.__k_to_f(json['list'][0]['temp']['max']))

        return temperature, temp_min, temp_max, glyph

    def run(self, end_time):
        while True:
            if dt.time(end_time, 00) > \
                    dt.datetime.now().time() >= dt.time(7, 30):
                # schedule one weather update immediately
                time_to_update = dt.datetime.now()
                # colon toggle for time
                colon = True

                while True:
                    # when to go blank for the night
                    if dt.datetime.now().time() >= dt.time(end_time, 00):
                        self.matrix.Clear()
                        break

                    # make request for weather if enough time has passed
                    if dt.datetime.now() >= time_to_update:
                        temp, temp_min, temp_max, glyph = self.__get_weather()
                        time_to_update = dt.datetime.now() + \
                            dt.timedelta(hours=1)
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

                    # set up the time display
                    cur_time = dt.datetime.now().strftime('%H:%M')
                    if colon:
                        cur_time = cur_time.replace(':', ' ')
                    colon = not colon
                    # enough height to clear the whole time area
                    for y_val in range(0, 11):
                        graphics.DrawLine(self.matrix, 0, y_val, 32, y_val,
                                          graphics.Color(0, 0, 0))

                    graphics.DrawText(self.matrix, self.time_font, self.time_x,
                                      self.time_y, self.time_color, cur_time)

                    time.sleep(1)
            else:
                time.sleep(1)


# Main function
if __name__ == "__main__":
    end_time = 20
    weather_clock = WeatherClock()
    weather_clock.run(end_time)
