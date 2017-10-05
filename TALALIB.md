# talalib.py
talalib.py is a small python module that allows easy interaction with the sensors used on the Tala project, without the need to know GPIO commands, PIL, etc..

## Supported Modules
- [x] **Screen** - [OLED SSD1306 (128x64)](http://www.ebay.co.uk/itm/I2C-OLED-Display-128X64-0-96-SSD1306-For-Arduino-Raspberry-Pi-ESP8266-etc-/172736606184)
- [ ] **Radio Module** - [HC-12 SI4463](http://www.ebay.co.uk/itm/433Mhz-HC-12-SI4463-Wireless-Serial-Port-Module-1000m-Replace-Bluetooth-TE296-/281772656589)
- [ ] **Keypad** - [4x3 Keypad](http://www.ebay.co.uk/itm/12-4x3-key-Switch-Membrane-Matrix-KeyPad-Self-Adhesive-Arduino-RPI-PIC-AVR-/131708189209)

## Usage

### UI
Interacting with the display.

#### Setup

```python
from talalib import ui
ui = UI()
```

#### Menu

Get the user to select from a list of items.

```python
ui.menu(["Item 1", "Item 2", "Item 3"])
# -> "Item 1"
```

Input a list of items to put in the menu. The output will be one of those items.

#### Popup

This shows a message to the user.

```python
ui.popup("Example", "This is an example popup!")
```

Input a title then a body.
