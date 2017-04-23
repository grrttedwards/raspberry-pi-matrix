#!/usr/bin/python
# Display a WeatherClock with double-buffering.
import sys
import os
import time as time_sleep
from datetime import datetime, time, timedelta
import requests
from PIL import Image
sys.path.append('./matrix/python')
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions


try:
    CITY_ID = os.environ['WEATHER_CITY_ID']
    API_KEY = os.environ['WEATHER_API_KEY']
except KeyError:
    print("WEATHER_CITY_ID or WEATHER_API_KEY is not set. Exiting.")
    exit(1)

# endpoints for the weather APIs
current_url = ("http://api.openweathermap.org/data/2.5/weather?id={}&APPID={}"
               .format(CITY_ID, API_KEY))
day_url = ("http://api.openweathermap.org/data/2.5/forecast/daily?id={}&APPID={}&cnt=1"
           .format(CITY_ID, API_KEY))

WEATHER_ICONS = {
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

# configuration for the matrix
matrix_options = RGBMatrixOptions()
matrix_options.rows = 16
matrix_options.chain_length = 1
matrix_options.parallel = 2
matrix_options.brightness = 50

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

matrix = RGBMatrix(options=matrix_options)


def run(end_time):
    offscreen_canvas = matrix.CreateFrameCanvas()

    # schedule one weather update immediately
    time_to_update = datetime.now()
    # colon toggle for time
    colon = True

    while True:
        offscreen_canvas.Clear()

        # when to go blank for the night
        if datetime.now().time() >= time(end_time, 00):
            matrix.Clear()
            return

        # set up the time display
        cur_time = datetime.now().strftime('%H:%M')
        if colon:
            cur_time = cur_time.replace(':', ' ')
        colon = not colon
        graphics.DrawText(offscreen_canvas, time_font, time_x, time_y,
                          time_color, cur_time)

        # make request for weather if enough time has passed
        if datetime.now() >= time_to_update:
            temperature, temp_min, temp_max, glyph = get_weather()
            time_to_update = datetime.now() + timedelta(hours=1)
        # set up the weather glyph to display
        offscreen_canvas.SetImage(glyph, icon_x, icon_y)
        # set up the temperature display
        graphics.DrawText(offscreen_canvas, temp_mm_font, temp_max_x,
                          temp_max_y, temp_mm_color, temp_max)
        graphics.DrawText(offscreen_canvas, temp_font, temp_x, temp_y,
                          temp_color, temperature)
        graphics.DrawText(offscreen_canvas, temp_mm_font, temp_min_x,
                          temp_min_y, temp_mm_color, temp_min)

        # swap the canvas with the offscreen
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

        time_sleep.sleep(1)

def k_to_f(kelvin):
    return int(kelvin * 9 / 5 - 459.67)

def get_weather():
    req = requests.get(current_url)
    json = req.json()
    if req.status_code != 200:
        print(req, json)
        exit(1)
    icon = json['weather'][0]['icon']
    # see if there is a night glyph else get the day variant
    try:
        icon_path = WEATHER_ICONS[icon]
    except KeyError:
        icon_path = WEATHER_ICONS[icon.replace('n', 'd')]
    glyph = Image.open(icon_path).convert('RGB')
    temperature = str(k_to_f(json['main']['temp'])) + "F"

    # make a second requst to the daily forecast for temp high and low
    req = requests.get(day_url)
    json = req.json()
    if req.status_code != 200:
        print(req, json)
    temp_min = str(k_to_f(json['list'][0]['temp']['min']))
    temp_max = str(k_to_f(json['list'][0]['temp']['max']))

    return temperature, temp_min, temp_max, glyph


# Main function
if __name__ == "__main__":
    end = 20
    while True:
        print(datetime.now().time())
        if time(end, 00) > datetime.now().time() >= time(7, 30):
            run(end)
        time_sleep.sleep(1)
