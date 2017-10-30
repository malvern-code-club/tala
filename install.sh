#!/bin/sh

echo -e "\e[1;34m  _____     _        ___         _        _ _ "
echo -e "\e[1;34m |_   _|_ _| |__ _  |_ _|_ _  __| |_ __ _| | |"
echo -e "\e[1;34m   | |/ _\` | / _\` |  | || ' \(_-<  _/ _\` | | |"
echo -e "\e[1;34m   |_|\__,_|_\__,_| |___|_||_/__/\__\__,_|_|_|"

echo -e ""

if [[ $EUID -ne 0 ]]; then
  echo -e "\e[0;31m[\e[1;31m!\e[0;31m]\e[0;1m Oops! You need to run this script as root (or by using sudo)\e[0m"
  exit 1
fi

echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m cd /opt\e[0m"
cd /opt

echo -e "\e[0;44m [1/4] INSTALLING PREREQUISITES... \e[0m"

echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m apt update\e[0m"
apt update
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m apt install build-essential python3-dev python3-pip python3-pil python3-smbus python3-serial\e[0m"
apt install build-essential python3-dev python3-pip python3-pil python3-smbus python3-serial git -y
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git\e[0m"
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m cd Adafruit_Python_SSD1306\e[0m"
cd Adafruit_Python_SSD1306
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m python3 setup.py install\e[0m"
python3 setup.py install
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m cd ../\e[0m"
cd ../
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m rm -rf Adafruit_Python_SSD1306\e[0m"
rm -rf Adafruit_Python_SSD1306
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m git clone https://github.com/MrVallentin/mount.py\e[0m"
git clone https://github.com/MrVallentin/mount.py
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m python3 mount.py/setup.py install\e[0m"
python3 mount.py/setup.py install
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m rm -rf mount.py\e[0m"
rm -rf mount.py

echo -e "\e[0;44m [2/4] DOWNLOAD AND SETUP TALA... \e[0m"

echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m git clone https://github.com/malvern-code-club/tala.git\e[0m"
git clone https://github.com/malvern-code-club/tala.git
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m cd tala\e[0m"
cd tala
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m chmod 755 index.py\e[0m"
chmod 755 index.py
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m python3 -m pip install -r requirements.txt\e[0m"
python3 -m pip install -r requirements.txt

echo -e "\e[0;44m [3/4] INSTALL TALA... \e[0m"

echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m cp tala.sh /etc/init.d\e[0m"
cp tala.sh /etc/init.d
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m chmod 755 /etc/init.d/tala.sh\e[0m"
chmod 755 /etc/init.d/tala.sh
echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m update-rc.d tala.sh defaults\e[0m"
update-rc.d tala.sh defaults

echo -e "\e[0;44m [4/4] START TALA... \e[0m"

echo -e "\e[0;34m[\e[1;34m#\e[0;34m]\e[0;1m sudo /etc/init.d/tala.sh start \e[0m"
sudo /etc/init.d/tala.sh start

echo -e "\e[0;44m TALA IS NOW INSTALLED ;) \e[0m"
