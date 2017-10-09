import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import textwrap

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
                draw_rectangle(draw, 0, 0, 32, 255, 255, 0, 0)
                draw_rectangle(draw, 0, 48, 80, 0, 0, 255, 1)                
                draw_rectangle(draw, 0, 32, 64, 0, 0, 255, 1)
            elif selected == (len(items)-1):
                draw_rectangle(draw, 0, 0, 32, 0, 0, 255, -1)
                draw_rectangle(draw, 0, 32, 64, 255, 255, 0, 0)
            else:
                draw_rectangle(draw, 0, -16, 16, 0, 0, 255, -1)
                draw_rectangle(draw, 0, 16, 48, 255, 255, 0, 0)       

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
               
            
        def draw_rectangle(self, draw, x, y, h, o, f1, f2, s):
            draw.rectangle((x, y, self.width, h), outline=o, fill=f1)                
            tw, th = draw.textsize(items[selected+s], font=font)                
            padding = (32-th)/2                
            draw.text((x+padding, y+padding), items[selected+s], font=font, fill=f2)
            
