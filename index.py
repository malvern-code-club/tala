#!/usr/bin/env python3

import talalib
import sqlite3
import threading
import random
import string
import datetime
import json
import time
import subprocess
import os
import urllib.request
import urllib.error
import sys
import logging
import logging.handlers
import mount
import shutil

REPO_DIR = "/opt/tala/"
STORAGE_DIR = "/opt/"

os.chdir(REPO_DIR)

LOG_NAME = "tala.log"
LOG_FILENAME = STORAGE_DIR + LOG_NAME
LOG_LEVEL = logging.INFO

DB_FILENAME = STORAGE_DIR + "tala.db"

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.FileHandler(LOG_FILENAME)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class TalaLogger(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())


sys.stdout = TalaLogger(logger, logging.INFO)
sys.stderr = TalaLogger(logger, logging.ERROR)

conn = None
c = None

logger.info("=== STARTED TALA ===")


def setupDb():
    global conn
    global c

    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()

    tables = [
        {
            "name": "memos",
            "columns": "memo_name TEXT, memo_data TEXT"
        },
        {
            "name": "config",
            "columns": "option TEXT, value TEXT"
        }
    ]

    for table in tables:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [
                  table["name"]])
        data = c.fetchall()

        if len(data) <= 0:  # If table doesn't exist
            logger.info("Creating table " + table["name"] + " with query: CREATE TABLE " + table["name"] + " (" + table["columns"] + ")")
            c.execute("CREATE TABLE " +
                      table["name"] + " (" + table["columns"] + ")")
            conn.commit()


setupDb()


def generateId():
    return "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))


def newUdid():
    udid = generateId()
    c.execute("DELETE FROM `config` WHERE option = 'udid'")
    c.execute("INSERT INTO `config` (`option`, `value`) VALUES ('udid', ?)", [udid])
    conn.commit()
    logger.info("Created new Unique Device ID: " + udid + ".")

def encode(data):
    data = json.dumps(data) #Json dump message
    return(data)
def decode(data):
    data = json.loads(data) #Load from json
    return(data)

def restart_tala():
     tala.popup("Updated", "Update was successful! Tala will now restart in 3 seconds...")
     time.sleep(3)
     tala.clear()
     subprocess.call(["/etc/init.d/tala.sh", "restart"])

c.execute("SELECT * FROM `config` WHERE `option` = 'udid'")
if c.fetchone() is None:
    newUdid()

c.execute("SELECT `value` FROM `config` WHERE `option` = 'typespeed'")
if c.fetchone() is None:
    c.execute("INSERT INTO `config` (`option`, `value`) VALUES ('typespeed', '0.5')")
    conn.commit()
    logger.info("Set type speed as 0.5 as it hasn't been set.")

tala = talalib.Tala()

tala.clear()

c.execute("SELECT * FROM `config` WHERE `option` = 'name'")
if c.fetchone() is None:
    tala.message("First Run", "You don't have a name set! Why don't you introduce yourself? Press the checkmark button and then use the keys to type your name.")
    time.sleep(0.5)
    c.execute("SELECT `value` FROM `config` WHERE `option` = 'typespeed'")
    typespeed = c.fetchone()
    typespeed = (float(typespeed[0]) if typespeed is not None else 0.5)
    name = tala.type(wait=typespeed)
    if name is not None:
        c.execute("INSERT INTO `config` (`option`, `value`) VALUES ('name', ?)", [name])
        conn.commit()

def recv_data():
        while True:
            msg = tala.receive()
            if not msg == "":
                msg = decode(msg)
                if msg is not None:
                    tala.interrupt = True

                    tala.message("Message", "MESSAGE: " + msg["content"] +
                                 " | SENT: " + msg["timestamp"] +
                                 " | FROM: " + msg["sender"]["name"],
                                 interrupt_bypass=True)

                    tala.interrupt = False


thread_recv_data = threading.Thread(target=recv_data)
thread_recv_data.start()

while True:
    logger.info("Showing main menu")
    choice = tala.menu(["Public Message", "Memo", "Settings", "Power Off"])
    time.sleep(0.5)
    if choice == "Public Message":
        c.execute("SELECT `value` FROM `config` WHERE `option` = 'typespeed'")
        typespeed = c.fetchone()
        typespeed = (float(typespeed[0]) if typespeed is not None else 0.5)
        content = tala.type(wait=typespeed)

        if content is not None:
            msg_id = generateId()

            timestamp = datetime.datetime.utcnow()
            timestamp = timestamp.strftime("%a %-d %b @ %-I:%M:%S")

            c.execute("SELECT `value` FROM `config` WHERE `option` = 'udid'")
            udid = c.fetchone()[0]

            c.execute("SELECT `value` FROM `config` WHERE `option` = 'name'")
            name = c.fetchone()[0]

            message = {
                "content": content,
                "id": msg_id,
                "timestamp": timestamp,
                "sender": {
                    "name": name,
                    "udid": udid
                }
            }

            logger.info("Sending Public Message: " + encode(message))
            
            tala.send(encode(message))
            time.sleep(0.5)
    elif choice == "Memo":
        c.execute("SELECT * FROM memos")
        memos = c.fetchall()
        if len(memos) > 0:
            logger.info("Showing memo menu.")
            memolist = ["New Memo", "Delete Memo"]
            for memo in memos:
                memolist.append(memo[0])
            choice = tala.menu(memolist)
            time.sleep(0.5)
        else:
            logger.info("No memos created, automatically choosing to create new memo.")
            choice = "New Memo"

        if choice == "New Memo":
            tala.popup(body="Input memo title")
            time.sleep(2)
            c.execute("SELECT `value` FROM `config` WHERE `option` = 'typespeed'")
            typespeed = c.fetchone()
            typespeed = (float(typespeed[0]) if typespeed is not None else 0.5)
            memo_name = tala.type(wait=typespeed)
            time.sleep(1)
            tala.popup(body="Input memo text")
            time.sleep(2)
            memo_data = tala.type(wait=typespeed)
            time.sleep(1)
            logger.info("Created new memo with title '" + memo_name + "' and body '" + memo_data + "'")
            c.execute("INSERT INTO memos (memo_name, memo_data) values (?, ?)", [memo_name, memo_data])
            conn.commit()
        """ 
        elif choice == "Delete Memo":
            if len(memos) < 2:
                c.execute("DELETE FROM memos WHERE memo_name = ?", [choice])
            else:
                choice = tala.menu(memos)
                time.sleep(0.5)
                if choice == "empty":
                    pass
                elif choice is None:
                    pass
                else:
                    c.execute("DELETE FROM memos WHERE memo_name = ?", [choice])
                    conn.commit()
        """
        else:
            c.execute("SELECT memo_data FROM memos WHERE memo_name = ?", [choice])
            memo_data = c.fetchone()
            tala.message(choice, memo_data[0])
            time.sleep(0.5)
    elif choice == "Settings":
        while True:
            choice = tala.menu(["Change Name", "Change Type Speed", "Reset Device ID", "Clear Data", "Update Tala", "Save Log to USB", "Exit Options"])
            if choice == "Reset Device ID":
                time.sleep(0.5)
                result = tala.yn("Are you sure")
                if result:
                    newUdid()
                    tala.message("Reset UDID", "Device ID regenerated!")
                    time.sleep(1)
                elif result is None:
                    pass
                elif not result:
                    tala.message("Reset UDID", "No changes made.")
                    time.sleep(1)
            elif choice == "Change Type Speed":
                time.sleep(1)
                c.execute("SELECT `value` FROM `config` WHERE `option` = 'typespeed'")
                typespeed = c.fetchone()
                typespeed = (typespeed[0] if typespeed is not None else "0.5")
                result = tala.yn("Type speed is " + typespeed + ". Change")
                if result:
                    tala.popup(body="Please insert new type speed (seconds)")
                    time.sleep(1.5)
                    c.execute("SELECT `value` FROM `config` WHERE `option` = 'typespeed'")
                    typespeed = c.fetchone()
                    typespeed = (float(typespeed[0]) if typespeed is not None else 0.5)
                    newtypespeed = tala.type(wait=typespeed)
                    typespeedfloat = None
                    try:
                        typespeedfloat = float(newtypespeed)
                    except ValueError:
                        tala.message("Type Speed", "Failed to update type speed because the inputted value was not a number!")

                    if typespeedfloat is not None:
                        c.execute("UPDATE `config` SET `value` = ? WHERE `option` = 'typespeed'", [typespeedfloat])
                        conn.commit()
                        tala.message("Type Speed", "Your type speed has been changed from " + str(typespeed) + " to " + newtypespeed + "!")
            elif choice == "Change Name":
                time.sleep(0.5)
                c.execute("SELECT `value` FROM `config` WHERE `option` = 'name'")
                name = c.fetchone()[0]
                result = tala.yn("Current name is " + name + ". Change")
                if result:
                    tala.popup(body="Please type new name")
                    time.sleep(1)
                    c.execute("SELECT `value` FROM `config` WHERE `option` = 'typespeed'")
                    typespeed = c.fetchone()
                    typespeed = (float(typespeed[0]) if typespeed is not None else 0.5)
                    newname = tala.type(wait=typespeed)
                    if newname is not None:
                        c.execute("UPDATE `config` SET `value` = ? WHERE `option` = 'name'", [newname])
                        conn.commit()
                        tala.message("Changed", "Your name has been changed from " + name + " to " + newname + "!")
            elif choice == "Clear Data":
                time.sleep(0.5)
                result = tala.yn("Are you sure")
                if result is not None:
                    if result:
                        logger.info("Deleting database...")
                        os.remove(DB_FILENAME)
                        tala.popup("Purging...", "Database purged!")
                        time.sleep(2)
                        tala.popup("Purging...", "Recreating Database...")
                        logger.info("Setting up database...")
                        setupDb()
                        tala.message("Purged", "Successfully cleared data.")
                        time.sleep(1)
                        logger.info("Database purge complete!")
                    elif not result:
                        tala.message("Alert", "No changed made.")
                        time.sleep(1)
            elif choice == "Save Log to USB":
                time.sleep(1)
                result = tala.yn("Save log to usb")
                if result is not None:
                    if result:
                        tala.message("Update", "Please PLUG IN your USB drive to save log to then press the checkmark to continue.")

                        devices = mount.list_media_devices()

                        logger.info(str(len(devices)) + " device(s) found.")

                        device = None

                        if len(devices) <= 0:
                            tala.message("Failure", "Couldn't detect any USB drives.")
                        elif len(devices) == 1:
                            tala.popup("Update", "Only 1 drive found, using that one.")
                            time.sleep(2)
                            device = devices[0]
                        else:
                            tala.popup(body="Select a drive to save to")
                            time.sleep(2)
                            tala.menu(devices)

                        if device is not None:
                            logger.info("Using device " + device)

                            mount.mount(device)

                            if mount.is_mounted(device):
                                files = []

                                for filename in os.listdir(mount.get_media_path(device)):
                                    path = os.path.join(mount.get_media_path(device), filename)
                                    if os.path.isfile(path):
                                        files.append(filename)

                                tala.popup("Copying...", "Copying log file...")
                                logger.info("Copying file from " + LOG_FILENAME + " to " + os.path.join(mount.get_media_path(device), LOG_NAME) + "...")
                                shutil.copy(LOG_FILENAME, os.path.join(mount.get_media_path(device), LOG_NAME))
                                logger.info("Copy complete!")
                                tala.popup("Copyied", "Copy complete!")
                                time.sleep(2)

                            mount.unmount(device)
            elif choice == "Update Tala":
                time.sleep(0.5)
                result = tala.yn("Are you sure you'd like to update")
                if result is None:
                    pass
                elif result:
                    tala.message("Information", "Tala will update even if there's no new version. On the next screen select a way to update.")
                    choice = tala.menu(["Via Internet", "Via USB"])
                    if choice == "Via Internet":
                        tala.popup("Updating...", "Checking internet connection...")
                        # Check for connection
                        connection = False
                        try:
                            urllib.request.urlopen("http://216.58.192.142", timeout=1)
                            connection = True
                        except urllib.error.URLError as e:
                            connection = False

                        if connection:
                            tala.popup("Updating...", "Preparing for update...")
                            if os.path.exists(REPO_DIR + "updatetest"):
                                logger.info("Deleting `updatetest` file")
                                os.remove(REPO_DIR + "updatetest")
                            else:
                                logger.info("There is no `updatetest` file, updating anyway.")

                            tala.popup("Updating...", "Please wait while updating...")

                            # This should update tala from github (in theory)
                            p = subprocess.Popen(["git", "fetch", "--all"], cwd=REPO_DIR)
                            p.wait()
                            p = subprocess.Popen(["git", "reset", "--hard", "origin/master"], cwd=REPO_DIR)
                            p.wait()

                            if os.path.exists(REPO_DIR + "updatetest"):
                                logger.info("`updatetest` file exists. Update successful.")

                                tala.popup("Updating...", "Changing file permissions...")
                                subprocess.call(["chmod", "755", REPO_DIR + "index.py"])
                                tala.popup("Updating...", "Installing Python modules...")
                                p = subprocess.Popen(["python3", "-m", "pip", "install", "-r", "requirements.txt"], cwd=REPO_DIR)
                                p.wait()
                                tala.popup("Updating...", "Updating daemon script...")
                                subprocess.call(["cp", REPO_DIR + "tala.sh", "/etc/init.d"])
                                subprocess.call(["chmod", "755", "/etc/init.d/tala.sh"])

                                restart_tala()
                                break
                            else:
                                logger.info("`updatetest` file doesn't exist. Update unsuccessful.")
                                tala.message("Update", "Update was unsuccessful. You could try updating via USB.")
                        else:
                            logger.info("Couldn't connect to the internet for update")
                            tala.message("Error", "Failed to update, couldn't connect to the internet")
                    elif choice == "Via USB":
                        tala.message("Update", "Please PLUG IN your USB drive to update from then press the checkmark to continue.")

                        devices = mount.list_media_devices()

                        logger.info(str(len(devices)) + " device(s) found.")

                        device = None

                        if len(devices) <= 0:
                            tala.message("Failure", "Couldn't detect any USB drives.")
                        elif len(devices) == 1:
                            tala.popup("Update", "Only 1 drive found, using that one.")
                            time.sleep(2)
                            device = devices[0]
                        else:
                            tala.popup(body="Select a drive to copy from")
                            time.sleep(2)
                            tala.menu(devices)

                        if device is not None:
                            logger.info("Using device " + device)

                            mount.mount(device)

                            if mount.is_mounted(device):
                                files = []

                                for filename in os.listdir(mount.get_media_path(device)):
                                    path = os.path.join(mount.get_media_path(device), filename)
                                    if os.path.isfile(path):
                                        files.append(filename)

                                if len(files) <= 0:
                                    tala.message("Failure", "No files found on drive!")
                                    logger.info("No files found on " + device + "!")
                                else:
                                    files.append("Exit")
                                    choice = tala.menu(files)
                                    if choice is None:
                                        pass
                                    elif choice != "Exit":
                                        yn = tala.yn("Copy & Overwrite " + choice)
                                        if yn:
                                            logger.info("Copying file from " + os.path.join(mount.get_media_path(device), choice) + " to " + os.path.join(REPO_DIR, choice) + "...")
                                            shutil.copy(os.path.join(mount.get_media_path(device), choice), os.path.join(REPO_DIR, choice))
                                            logger.info("Copy complete!")
                                            tala.popup("Updated", "Updated file " + choice + "!")
                                            time.sleep(0.5)
                                            restart = tala.yn("Restart")
                                            if restart:
                                                restart_tala()
                            else:
                                logger.info("Problem mounting drive " + device)
                                tala.message("Failure", "Problem mounting " + device + "!")

            elif choice == "Exit Options":
                break
    elif choice == "Power Off":
        time.sleep(0.5)
        option = tala.yn("Are you sure you'd like to power off")
        if option:
            logger.info("=== POWERING OFF DEVICE ===")
            tala.popup(body="Device shutting down. Wait up to 10s before removing power.")
            tala.cleanup()
            subprocess.call(["sudo", "halt"])
            break
