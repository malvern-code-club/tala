import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import textwrap

import RPi.GPIO as GPIO

class Input():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(26, GPIO.OUT) # row 1
        GPIO.setup(19, GPIO.OUT) # row 2
        GPIO.setup(13, GPIO.OUT) # row 3
        GPIO.setup(6, GPIO.OUT) # row 4

        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # col 1
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # col 2
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # col 3

        GPIO.output(26, GPIO.LOW)
        GPIO.output(19, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(6, GPIO.LOW)

    def singlebutton(self, wait=0.05):
        key = ""

        while key == "":
            GPIO.output(26, GPIO.HIGH)
            GPIO.output(19, GPIO.LOW)
            GPIO.output(13, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
            if GPIO.input(17):
                key = "1"
            if GPIO.input(27):
                key = "2"
            if GPIO.input(22):
                key = "3"

            GPIO.output(26, GPIO.LOW)
            GPIO.output(19, GPIO.HIGH)
            GPIO.output(13, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
            if GPIO.input(17):
                key = "4"
            if GPIO.input(27):
                key = "5"
            if GPIO.input(22):
                key = "6"

            GPIO.output(26, GPIO.LOW)
            GPIO.output(19, GPIO.LOW)
            GPIO.output(13, GPIO.HIGH)
            GPIO.output(6, GPIO.LOW)
            if GPIO.input(17):
                key = "7"
            if GPIO.input(27):
                key = "8"
            if GPIO.input(22):
                key = "9"

            GPIO.output(26, GPIO.LOW)
            GPIO.output(19, GPIO.LOW)
            GPIO.output(13, GPIO.LOW)
            GPIO.output(6, GPIO.HIGH)
            if GPIO.input(17):
                key = "*"
            if GPIO.input(27):
                key = "0"
            if GPIO.input(22):
                key = "#"

            time.sleep(wait)
        return key

    def cleanup(self):
        GPIO.cleanup()

class UI():
    def __init__(self):
        self.display = Adafruit_SSD1306.SSD1306_128_64(rst=24)

        self.display.begin()
        self.display.clear()
        self.display.display()

        self.width = self.display.width
        self.height = self.display.height

    def popup(self, title, body):
        wrapbody = textwrap.wrap(body, width=17)

        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)

        titlefont = ImageFont.truetype("leco1976.ttf", 15)
        font = ImageFont.truetype("FreePixel.ttf", 14)

        startline = 0

        while True:
            draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            titlewidth, titleheight = draw.textsize(title, font=titlefont)
            draw.rectangle((0, 0, self.width, titleheight+10), outline=255, fill=255)
            padding = 5
            draw.text((0+padding, 0+padding), title, font=titlefont, fill=0)

            linewidth, lineheight = draw.textsize("test", font=font)
            lines = 0
            for i in range(startline, len(wrapbody)):
                draw.text((0+padding, 0+padding+titleheight+padding+padding+((lineheight+2)*lines)), wrapbody[i], font=font, fill=255)
                lines += 1

            self.display.image(image)
            self.display.display()

            option = input("> ")
            if option == "up":
                if startline > 0:
                    startline = startline - 1
            elif option == "down":
                if startline < (len(wrapbody)-1):
                    startline = startline + 1
            elif option == "ok":
                return
            else:
                print("invalid")

    def menu(self, items):
        if len(items) < 2:
            raise ValueError("Items list given must contain 2 or more items!")

        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        font = ImageFont.truetype("leco1976.ttf", 15)

        selected = 0

        while True:
            draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            if selected == 0:
                draw.rectangle((0, 0, self.width, 32), outline=255, fill=255)
                tw, th = draw.textsize(items[selected], font=font)
                padding = (32-th)/2
                draw.text((0+padding, 0+padding), items[selected], font=font, fill=0)

                draw.rectangle((0, 32, self.width, 64), outline=0, fill=0)
                tw, th = draw.textsize(items[selected+1], font=font)
                padding = (32-th)/2
                draw.text((0+padding, 32+padding), items[selected+1], font=font, fill=255)
            elif selected == (len(items)-1):
                draw.rectangle((0, 0, self.width, 32), outline=0, fill=0)
                tw, th = draw.textsize(items[selected-1], font=font)
                padding = (32-th)/2
                draw.text((0+padding, 0+padding), items[selected-1], font=font, fill=255)

                draw.rectangle((0, 32, self.width, 64), outline=255, fill=255)
                tw, th = draw.textsize(items[selected], font=font)
                padding = (32-th)/2
                draw.text((0+padding, 32+padding), items[selected], font=font, fill=0)
            else:
                draw.rectangle((0, -16, self.width, 16), outline=0, fill=0)
                tw, th = draw.textsize(items[selected-1], font=font)
                padding = (32-th)/2
                draw.text((0+padding, -16+padding), items[selected-1], font=font, fill=1)

                draw.rectangle((0, 16, self.width, 48), outline=1, fill=1)
                tw, th = draw.textsize(items[selected], font=font)
                padding = (32-th)/2
                draw.text((0+padding, 16+padding), items[selected], font=font, fill=0)

                draw.rectangle((0, 48, self.width, 80), outline=0, fill=0)
                tw, th = draw.textsize(items[selected+1], font=font)
                padding = (32-th)/2
                draw.text((0+padding, 48+padding), items[selected+1], font=font, fill=1)

            self.display.image(image)
            self.display.display()

            option = input("> ")
            if option == "up":
                if selected > 0:
                    selected = selected - 1
            elif option == "down":
                if selected < (len(items)-1):
                    selected = selected + 1
            elif option == "ok":
                return selected
            else:
                print("invalid")
