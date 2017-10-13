# Tala
A text only portable communication device designed for an apocolypse.

## talalib.py

talalib.py is a Python module to interact with *most* of the sensors in the Tala
project. You can read the documentation for this module [here](talalib.md).

## Wiring

![](tala_bb.png)

***Wiring for modules may not be as they show in this diagram! We bought 2 OLED
screens and the pinouts on both are different. Be careful!***

### Screen

| Screen | Raspberry Pi     |
| ------ | ---------------- |
| VCC    | 3v3 *(Pin 1)*    |
| GND    | Ground *(Pin 6)* |
| SCL    | SCL *(Pin 5)*    |
| SDA    | SDA *(Pin 3)*    |

### Keypad

| Keypad | Raspberry Pi      |
| ------ | ----------------- |
| Row 1  | BCM 26 *(Pin 37)* |
| Row 2  | BCM 19 *(Pin 35)* |
| Row 3  | BCM 13 *(Pin 33)* |
| Row 4  | BCM 6 *(Pin 31)*  |
| Col 1  | BCM 17 *(Pin 11)* |
| Col 2  | BCM 27 *(Pin 13)* |
| Col 3  | BCM 22 *(Pin 15)* |

### HC-12 Module

| HC-12 | Raspberry Pi      |
| ----- | ----------------- |
| VCC   | 3v3 *(Pin 17)*    |
| GND   | Ground *(Pin 9)*  |
| RXD   | BCM 14 *(Pin 8)*  |
| TXD   | BCM 15 *(Pin 10)* |

## Installation

```
sudo apt update
sudo apt install build-essential python3-dev python3-pip

sudo apt install python3-pil python3-smbus python3-serial git

git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python3 setup.py install
```
