import time

import serial

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import textwrap

import RPi.GPIO as GPIO

_FONT_LECO_PATH = "/opt/tala/leco1976.ttf"
_FONT_FREEPIXEL_PATH = "/opt/tala/FreePixel.ttf"

class Tala():
    def __init__(self):
        # Setup Display
        self.display = Adafruit_SSD1306.SSD1306_128_64(rst=24)

        self.display.begin()
        self.display.clear()
        self.display.display()

        self.width = self.display.width
        self.height = self.display.height

        # Setup Radio
        self.radio = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

        # Setup Keypad
        GPIO.setmode(GPIO.BCM)

        # Tell the Raspberry Pi that each row on the keypad is an output
        GPIO.setup(26, GPIO.OUT) # row 1
        GPIO.setup(19, GPIO.OUT) # row 2
        GPIO.setup(13, GPIO.OUT) # row 3
        GPIO.setup(6, GPIO.OUT) # row 4

        # Tell the Raspberry Pi that each column on the keypad is an input and
        # should have an (internal) pull down resistor.
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # col 1
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # col 2
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # col 3

        # Turn keypad rows off.
        GPIO.output(26, GPIO.LOW)
        GPIO.output(19, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(6, GPIO.LOW)

    def keypad_row(self, row):
        if row == 1:
            GPIO.output(26, GPIO.HIGH)
            GPIO.output(19, GPIO.LOW)
            GPIO.output(13, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
        if row == 2:
            GPIO.output(26, GPIO.LOW)
            GPIO.output(19, GPIO.HIGH)
            GPIO.output(13, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
        if row == 3:
            GPIO.output(26, GPIO.LOW)
            GPIO.output(19, GPIO.LOW)
            GPIO.output(13, GPIO.HIGH)
            GPIO.output(6, GPIO.LOW)
        if row == 4:
            GPIO.output(26, GPIO.LOW)
            GPIO.output(19, GPIO.LOW)
            GPIO.output(13, GPIO.LOW)
            GPIO.output(6, GPIO.HIGH)

    def singlebutton(self, wait=0.05):
        key = ""

        # Loop while we haven't got a key
        while key == "":
            # Turn on row 1 but turn off every other row
            self.keypad_row(1)
            # If the first column is turned on we know that the first
            # button has been pressed and so on.
            if GPIO.input(17):
                key = "1"
            if GPIO.input(27):
                key = "2"
            if GPIO.input(22):
                key = "3"

            self.keypad_row(2)
            if GPIO.input(17):
                key = "4"
            if GPIO.input(27):
                key = "5"
            if GPIO.input(22):
                key = "6"

            self.keypad_row(3)
            if GPIO.input(17):
                key = "7"
            if GPIO.input(27):
                key = "8"
            if GPIO.input(22):
                key = "9"

            self.keypad_row(4)
            if GPIO.input(17):
                key = "*"
            if GPIO.input(27):
                key = "0"
            if GPIO.input(22):
                key = "#"

            time.sleep(wait)
        return key

    def type_numbers(self, wait=0.5):
        doloop = True
        message = ""
        key = ""

        while doloop == True:
            self.keypad_row(1)
            if GPIO.input(17):
                key = "1"
            if GPIO.input(27):
                key = "2"
            if GPIO.input(22):
                key = "3"

            self.keypad_row(2)
            if GPIO.input(17):
                key = "4"
            if GPIO.input(27):
                key = "5"
            if GPIO.input(22):
                key = "6"

            self.keypad_row(3)
            if GPIO.input(17):
                key = "7"
            if GPIO.input(27):
                key = "8"
            if GPIO.input(22):
                key = "9"

            self.keypad_row(4)
            if GPIO.input(17):
                key = "*"
            if GPIO.input(27):
                key = "0"
            if GPIO.input(22):
                doloop = False
                key = ""
            message = message + key
            time.sleep(wait)
        return message

    def type(self, wait=0.5):
        # Make a new image/canvas with the width and height of the screen.
        image = Image.new("1", (self.width, self.height))
        # Make a new draw variable which draws shapes/text to the screen.
        draw = ImageDraw.Draw(image)

        # Define the fonts
        bigfont = ImageFont.truetype(_FONT_LECO_PATH, 45)
        font = ImageFont.truetype(_FONT_FREEPIXEL_PATH, 14)

        # Define the characters to cycle for each key on the keypad
        # Special:
        #   _ = Space
        #   <- = Backspace
        keypadkeys = {
            "2": ["a", "b", "c"],
            "3": ["d", "e", "f"],
            "4": ["g", "h", "i"],
            "5": ["j", "k", "l"],
            "6": ["m", "n", "o"],
            "7": ["p", "q", "r", "s"],
            "8": ["t", "u", "v"],
            "9": ["w", "x", "y", "z"],
            "0": ["_"],
            "*": ["<-", ".", ",", "!", "?"]
        }

        doloop = True
        message = ""
        keybefore = ""
        key = ""
        currentletter = ""

        while doloop:
            key = ""

            self.keypad_row(1)
            if GPIO.input(17):
                key = ""
            if GPIO.input(27):
                key = "2"
            if GPIO.input(22):
                key = "3"

            self.keypad_row(2)
            if GPIO.input(17):
                key = "4"
            if GPIO.input(27):
                key = "5"
            if GPIO.input(22):
                key = "6"

            self.keypad_row(3)
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
                self.clear()
                message = message + currentletter
                doloop = False

            if key != "":
                # If the key is the same as the key before (aka the button is
                # being held down.)
                if key == keybefore:
                    # Get the current index of the letter
                    index = keypadkeys[key].index(currentletter)
                    # Check if adding 1 to the key will make it go off the list
                    if (index+1) < len(keypadkeys[key]):
                        # Nope, add 1 to the key
                        currentletter = keypadkeys[key][index+1]
                    else:
                        # Yep, set the list to 0
                        currentletter = keypadkeys[key][0]
                else:
                    # Key has not being held, so set the current letter to the
                    # first on the list of the button.
                    currentletter = keypadkeys[key][0]

                # Clear the canvas by drawing a blank rectangle.
                draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

                # Get the width and height of the letter
                w, h = draw.textsize(currentletter, font=bigfont)
                # Draw the letter in the middle of the screen
                draw.text(((self.width-w)/2, (self.height-h)/2), currentletter, font=bigfont, fill=255)

                # Display the canvas on the screen.
                self.display.image(image)
                self.display.display()

                keybefore = key
                time.sleep(wait)
            else:
                if currentletter != "":
                    # Check for special keys
                    if currentletter != "<-":
                        if currentletter == "_":
                            currentletter = " "
                        message = message + currentletter
                    else:
                        message = message[:-1]
                    currentletter = ""

                # if a key is not pressed show the text being typed

                # clear the canvas by drawing a blank rectangle
                draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

                # make the message wrap (aka if the message goes off the screen
                # make it start on a new line)
                messagewrap = textwrap.wrap(message, width=17)

                # get the height of a line
                linewidth, lineheight = draw.textsize("test", font=font)
                lines = 0
                # draw each line
                for i in range(0, len(messagewrap)):
                    draw.text((5, 5+((lineheight+2)*lines)), messagewrap[i], font=font, fill=255)
                    lines += 1

                # display the canvas to the screen
                self.display.image(image)
                self.display.display()

                keybefore = ""
                time.sleep(0.1)
        return message

    def cleanup(self):
        # clean up the raspberry pi's gpio
        # ie turn off pins, etc..
        GPIO.cleanup()

    def yn(self, question):
        self.popup(body=question + "?")

        while True:
            # check for button presses
            btn = self.singlebutton()
            # if button * is pressed return yes
            if btn == "#":
                return True
            # if # button is pressed return no
            elif btn == "*":
                return False

    def popup(self, title="", body=""):
        # make the message wrap (aka if it goes off the screen make it start on
        # a new line)
        wrapbody = textwrap.wrap(body, width=17)

        # make a new image
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # define the fonts
        titlefont = ImageFont.truetype(_FONT_LECO_PATH, 15)
        font = ImageFont.truetype(_FONT_FREEPIXEL_PATH, 11)

        # clear the canvas
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        padding = 5

        if title != "":
            # get width and height of title
            titlewidth, titleheight = draw.textsize(title, font=titlefont)
            # draw a box to put the title in
            draw.rectangle((0, 0, self.width, titleheight+10), outline=255, fill=255)
            # draw the title text
            draw.text((0+padding, 0+padding), title, font=titlefont, fill=0)
        else:
            titlewidth = 0
            titleheight = 0

        # get line width and height
        linewidth, lineheight = draw.textsize("test", font=font)
        lines = 0
        # draw each line on the screen
        for i in range(0, len(wrapbody)):
            draw.text((0+padding, 0+((padding+padding) if title != "" else 0)+titleheight+padding+((lineheight+2)*lines)), wrapbody[i], font=font, fill=255)
            lines += 1

        # draw the canvas to the screen
        self.display.image(image)
        self.display.display()

    def message(self, title, body):
        # make the message wrap (aka if it goes off the screen make it start on
        # a new line)
        wrapbody = textwrap.wrap(body, width=17)

        # make a new image
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # define the fonts
        titlefont = ImageFont.truetype(_FONT_LECO_PATH, 15)
        font = ImageFont.truetype(_FONT_FREEPIXEL_PATH, 11)

        startline = 0

        while True:
            # clear the canvas
            draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            # get width and height of title
            titlewidth, titleheight = draw.textsize(title, font=titlefont)
            # draw a box to put the title in
            draw.rectangle((0, 0, self.width, titleheight+10), outline=255, fill=255)
            padding = 5
            # draw the title text
            draw.text((0+padding, 0+padding), title, font=titlefont, fill=0)

            # get line width and height
            linewidth, lineheight = draw.textsize("test", font=font)
            lines = 0
            # draw each line on the screen
            for i in range(startline, len(wrapbody)):
                draw.text((0+padding, 0+padding+titleheight+padding+padding+((lineheight+2)*lines)), wrapbody[i], font=font, fill=255)
                lines += 1

            # draw the canvas to the screen
            self.display.image(image)
            self.display.display()

            # check for button presses
            btn = self.singlebutton()
            # if button 2 is pressed scroll up
            if btn == "2":
                if startline > 0:
                    startline = startline - 1
            # if button 8 is pressed scroll down
            elif btn == "8":
                if startline < (len(wrapbody)-1):
                    startline = startline + 1
            # if # button is pressed dismiss the message
            elif btn == "#":
                return

    def menu(self, items):
        if len(items) < 2:
            raise ValueError("Items list given must contain 2 or more items!")

        # make a canvas
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # clear the canvas
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        # define font
        font = ImageFont.truetype(_FONT_LECO_PATH, 15)

        selected = 0

        while True:
            # clear the screen
            draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            # if the first item is selected
            if selected == 0:
                self.draw_rectangle(draw, 0, 0, 32, 255, 255, 0, selected, items, 0, font)
                self.draw_rectangle(draw, 0, 32, 64, 0, 0, 255, selected, items, 1, font)
            elif selected == (len(items)-1):
                self.draw_rectangle(draw, 0, 0, 32, 0, 0, 255, selected, items, -1, font)
                self.draw_rectangle(draw, 0, 32, 64, 255, 255, 0, selected, items, 0, font)
            else:
                self.draw_rectangle(draw, 0, -16, 16, 0, 0, 255, selected, items, -1, font)
                self.draw_rectangle(draw, 0, 16, 48, 255, 255, 0, selected, items, 0, font)
                self.draw_rectangle(draw, 0, 48, 80, 0, 0, 255, selected, items, 1, font)

            self.display.image(image)
            self.display.display()

            btn = self.singlebutton()
            if btn == "2":
                if selected > 0:
                    selected = selected - 1
            elif btn == "8":
                if selected < (len(items)-1):
                    selected = selected + 1
            elif btn == "#":
                return items[selected]


    def draw_rectangle(self, draw, x, y, h, o, f1, f2, selected, items, s, font):
        draw.rectangle((x, y, self.width, h), outline=o, fill=f1)
        tw, th = draw.textsize(items[selected+s], font=font)
        padding = (32-th)/2
        draw.text((x+padding, y+padding), items[selected+s], font=font, fill=f2)

    def clear(self):
        self.display.clear()
        self.display.display()

    def send(self, message):
        message = message.encode()
        self.radio.write(message)

    def waitForReceive(self):
        while True:
            response = self.radio.readline().decode("utf-8")
            if not response == "":
                return response

    def receive(self):
        return self.radio.readline().decode("utf-8")

    def closeRadio(self):
        self.radio.close()
