# talalib.py
talalib.py is a small python module that allows easy interaction with the sensors used on the Tala project, without the need to know GPIO commands, PIL, etc..

## Supported Modules
- [x] **Screen** - [OLED SSD1306 (128x64)](http://www.ebay.co.uk/itm/I2C-OLED-Display-128X64-0-96-SSD1306-For-Arduino-Raspberry-Pi-ESP8266-etc-/172736606184)
- [ ] **Radio Module** - [HC-12 SI4463](http://www.ebay.co.uk/itm/433Mhz-HC-12-SI4463-Wireless-Serial-Port-Module-1000m-Replace-Bluetooth-TE296-/281772656589)
- [ ] **Keypad** - [4x3 Keypad](http://www.ebay.co.uk/itm/12-4x3-key-Switch-Membrane-Matrix-KeyPad-Self-Adhesive-Arduino-RPI-PIC-AVR-/131708189209)

## Usage

### UI
This class interacts with the screen and keypad.

#### Setup

```python
from talalib import UI
ui = UI()
```

#### Menu

Get the user to select from a list of items. The first parameter of the function
is the list of strings to ask the user to select, the output of the function will
be one of the items in the list as a string.

```python
ui.menu(["Item 1", "Item 2", "Item 3"])
# -> "Item 1"
```

#### Popup

This shows a message to the user. The first parameter of the function is the
title of the popup as a string and the second parameter is the body of the popup,
if the body is too long to fit on screen, the user can scroll using the up and
down keys.

```python
ui.popup("Example", "This is an example popup!")
```

Input a title then a body.

### Input
This class interacts with the keypad and collects inputs from it.

#### Setup

```python
from talalib import Input
inp = Input()
```

#### Single Button

This waits for a button on the keypad to be pressed, then returns the button as
a string (0-9, #, \*).

```python
inp.singlebutton()
# -> "1"
```
