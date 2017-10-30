# talalib.py
talalib.py is a small python module that allows easy interaction with the sensors used on the Tala project, without the need to know GPIO commands, PIL, etc..

## Supported Modules
- [x] **Screen** - [OLED SSD1306 (128x64)](http://www.ebay.co.uk/itm/I2C-OLED-Display-128X64-0-96-SSD1306-For-Arduino-Raspberry-Pi-ESP8266-etc-/172736606184)
- [x] **Radio Module** - [HC-12 SI4463](http://www.ebay.co.uk/itm/433Mhz-HC-12-SI4463-Wireless-Serial-Port-Module-1000m-Replace-Bluetooth-TE296-/281772656589)
- [x] **Keypad** - [4x3 Keypad](http://www.ebay.co.uk/itm/12-4x3-key-Switch-Membrane-Matrix-KeyPad-Self-Adhesive-Arduino-RPI-PIC-AVR-/131708189209)

## Setup

```python
import talalib
tala = talalib.Tala()
```

## Methods

### `menu(items[List of String])` *[Screen, Keypad]*

Get the user to select from a list of items. The first parameter of the function
is the list of strings to ask the user to select, the output of the function will
be one of the items in the list as a string.

```python
tala.menu(["Item 1", "Item 2", "Item 3"])
# -> "Item 1"
```

### `message(title[String], body[String])` *[Screen, Keypad]*

This shows a message to the user. The first parameter of the function is the
title of the message as a string and the second parameter is the body of the message,
if the body is too long to fit on screen, the user can scroll using the up and
down keys. **The user needs to manually dismiss a message!**

```python
tala.message("Example", "This is an example popup!")
```

Input a title then a body.

### `popup(title[String], body[String])` *[Screen]*

This is similar to the above `message` method, but **does not require user input to
be dismissed** (*the screen needs to be cleared to remove it*). The title parameter
is optional but body is required. **After calling this function, you might want
`tala.singlebutton()` to get user input.**

```python
tala.popup("Popup", "You have mail!")
```

```python
tala.popup(body="You have mail!")
```

### `yn(question[String])` *[Screen, Keypad]*

This uses the above `popup` method and combines it with `singlebutton` to ask the
user a yes/no question. The question parameter is required and needs to be a
string.

```python
tala.yn("Do you like ice cream")
```

### `singlebutton()` *[Keypad]*

This waits for a button on the keypad to be pressed, then returns the button as
a string (0-9, #, \*).

```python
tala.singlebutton()
# -> "1"
```

### `type(wait[Integer]{optional})` *[Screen, Keypad]*

This allows the user to type on the keypad by holding a key to cycle through the
letters and unpressing to type the letter that is currently on the screen. The
user can then press the `#` button to enter the text. An *optional* parameter is
`wait` which is how fast move onto the next letter in the sequence when the button
is held down in seconds (the default is `0.5`). The function returns the message
as a string.

```python
tala.type()
# -> "Hello World!"
```

## `send(message[String])` *[Radio]*

This sends a message via the HC-12 module. The first and only parameter is the
message to send as a string, there is no output.

```python
tala.send("Hello World!")
```

## `waitForReceive()` *[Radio]*

This waits for a message to be received via the HC-12 module. There are no
parameters and the output is the message received as a string.

```python
tala.waitForReceive()
# -> "Hello World!"
```

## `receive()` *[Radio]*

This receives a message from the HC-12 module. There are no parameters and the
output will be the message as a string. The string may be empty, in which case
no message has been received. `waitForReceive()` is the output of this command,
but in a loop.

```python
tala.receive()
# -> "Hello World!"
```

### `cleanup()` *[Keypad]*

This cleans up the GPIO pins. **This should be run when the program quits.**

```python
tala.cleanup()
```

### `clear()` *[Screen]*

This clears the screen.

```python
tala.clear()
```
