#!/usr/bin/python3
# -*- coding:utf-8 -*-

import sys
import os
import time
import random

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

DIR_LIB = os.path.join(DIRECTORY, 'lib')
DIR_MEDIA = os.path.join(DIRECTORY, 'media')
if os.path.exists(DIR_LIB):
    sys.path.append(DIR_LIB)

from lib import epd2in13_V2
from PIL import Image, ImageDraw, ImageFont

import logging

FONT_FILE_NAME = 'UbuntuBoldItalic-Rg86.ttf'
IMAGE_FILE_NAME = 'bitcoin122x122_b.bmp'

WHITE = 255
BLACK = 0

class PriceTicker(object):
    def __init__(self, price_client, price_extractor):
        self.price_client = price_client
        self.price_extractor = price_extractor

        self.WIDTH = 0
        self.HEIGHT = 0
        self.RUNNING = True
        self.IMAGE_MODE = '1' # 1 (1-bit pixels, black and white, stored with one pixel per byte)

        self.init_epaper_display()

    def init_epaper_display(self):
        self.epd = epd2in13_V2.EPD()
        self.epd.init(self.epd.FULL_UPDATE)
        self.epd.Clear(0xFF)

        self.WIDTH = self.epd.height # 250 pixels
        self.HEIGHT = self.epd.width # 122 pixels

    def start(self):
        try:
            self.display_image()
            self.wait()
            self.display_price()
        except Exception as ex:
            logging.error(ex)
            self.stop()
        self.stop()

    def stop(self):
        logging.info("shutting down")
        if self.RUNNING:
            self.RUNNING = False
            self.shutdown()

    def shutdown(self):
        self.clear_display()
        self.epd.sleep()

    def display_image(self):
        image = self.load_image()
        image_width, image_height = image.size
        padding_left = int((self.WIDTH - image_width) / 2)

        frame = self.create_frame()
        frame.paste(image, (padding_left,0))

        self.epd.display(self.epd.getbuffer(frame))

    def display_price(self):
        frame = self.create_frame()
        draw = ImageDraw.Draw(frame)

        font = self.load_font()

        counter = 0
        seconds_to_sleep = 1
        price_refresh_interval_in_seconds = 300 # refresh the price every 5 minutes
        current_price = 'N/A'

        while (self.RUNNING):
            if counter % price_refresh_interval_in_seconds == 0:
                self.clear_display()

                color_bg = self.get_random_color()
                draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill = color_bg)

                color_text = WHITE if color_bg == BLACK else BLACK
                current_price = self.get_price()

                x = 50 # 0, 0 top right
                y = 33
                draw.text((x, y), current_price, font = font, fill = color_text, align='left')

                self.epd.display(self.epd.getbuffer(frame))
                self.epd.sleep()

            counter = counter + seconds_to_sleep
            time.sleep(seconds_to_sleep)

            if counter >= price_refresh_interval_in_seconds:
                counter = 0 # reset counter

            #logging.info(counter)

    def get_random_color(self):
        r = random.randint(0, 1)
        # logging.info('r: {}'.format(r))
        return WHITE if r == 1 else BLACK

    def create_frame(self):
        return Image.new(self.IMAGE_MODE, (self.WIDTH, self.HEIGHT))

    def wait(self):
        time.sleep(3)

    def clear_display(self):
        self.epd.init(self.epd.FULL_UPDATE)
        self.epd.Clear(0xFF)

    def get_price(self):
        data = self.price_client.retrieve_data()
        return self.price_extractor.formatted_price_from_data(data)

    def load_image(self):
        try:
            return Image.open(os.path.join(DIR_MEDIA, IMAGE_FILE_NAME))
        except IOError as e:
            logging.error(e)

    def load_font(self):
        try:
            font_file = os.path.join(DIR_MEDIA, FONT_FILE_NAME)
            FONT_SIZE_IN_POINTS = 48 # 48 points = 64 pixels
            return ImageFont.truetype(font_file, FONT_SIZE_IN_POINTS)
        except IOError as e:
            logging.error(e)
