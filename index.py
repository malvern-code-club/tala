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
import datetime
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

LOG_FILENAME = STORAGE_DIR + "tala.log"
LOG_LEVEL = logging.INFO

DB_FILENAME = STORAGE_DIR + "tala.db"

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=2)
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

c.execute("SELECT * FROM `config` WHERE `option` = 'udid'")
if c.fetchone() == None:
    newUdid()

tala = talalib.Tala()

tala.clear()

c.execute("SELECT * FROM `config` WHERE `option` = 'name'")
if c.fetchone() == None:
    tala.message("First Run", "You don't have a name set! Why don't you introduce yourself? Press the checkmark button and then use the keys to type your name.")
    time.sleep(1)
    name = tala.type()
    c.execute("INSERT INTO `config` (`option`, `value`) VALUES ('name', ?)", [name])
    conn.commit()

def encode(data):
    data = json.dumps(data) #Json dump message
    return(data)
def decode(data):
    data = json.loads(data) #Load from json
    return(data)

while True:
    logger.info("Showing main menu")
    choice = tala.menu(["Public Message", "Memo", "Settings", "Power Off"])
    time.sleep(1)
    if choice == "Public Message":
        ## ![QUANTUMBLACK] TODO: Make the below threading code run forever while Tala is running

        #def recv_data(stop_event):
        #    while (not stop_event.is_set()):
        #        data = tala.receive()
        #        time.sleep(1)
        #        if data == "":
        #            pass
        #        else:
        #            tala.message("Message", data)

        #t_stop = threading.Event()
        #thread_recv_data = threading.Thread(target=recv_data, args=t_stop)
        #thread_recv_data.start()

        ## ![QUANTUMBLACK] /TODO

        content = tala.type()

        msg_id = generateId()

        timestamp = str(datetime.datetime.utcnow())

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
        time.sleep(1)
    elif choice == "Memo":
        c.execute("SELECT * FROM memos")
        memos = c.fetchall()
        if len(memos) > 0:
            logger.info("Showing memo menu.")
            memolist = ["New Memo", "Delete Memo"]
            for memo in memos:
                memolist.append(memo[0])
            choice = tala.menu(memolist)
            time.sleep(1)
        else:
            logger.info("No memos created, automatically choosing to create new memo.")
            choice = "New Memo"
        if choice == "New Memo":
            tala.popup(body="Input memo title")
            time.sleep(2)
            memo_name = tala.type()
            time.sleep(1)
            tala.popup(body="Input memo text")
            time.sleep(2)
            memo_data = tala.type()
            time.sleep(1)
            logger.info("Created new memo with title '" + memo_name + "' and body '" + memo_data + "'")
            c.execute("INSERT INTO memos (memo_name, memo_data) values (?, ?)", [memo_name, memo_data])
            conn.commit()
        elif choice == "Delete Memo":
            choice = tala.menu(memos)
            time.sleep(1)
            if choice == "empty":
                pass
            else:
                c.execute("DELETE FROM memos WHERE memo_name = ?", [choice])
                conn.commit()
        else:
            c.execute("SELECT memo_data FROM memos WHERE memo_name = ?", [choice])
            memo_data = c.fetchone()
            tala.message(choice, memo_data[0])
            time.sleep(1)
    elif choice == "Settings":
        while True:
            choice = tala.menu(["Change Name", "Reset Device ID", "Clear Data", "Update Tala", "Exit Options"])
            if choice == "Reset Device ID":
                time.sleep(1)
                result = tala.yn("Are you sure")
                if result:
                    newUdid()
                    tala.message("Reset UDID", "Device ID regenerated!")
                    time.sleep(1)
                elif not result:
                    tala.message("Reset UDID", "No changes made.")
                    time.sleep(1)
            elif choice == "Change Name":
                time.sleep(1)
                c.execute("SELECT `value` FROM `config` WHERE `option` = 'name'")
                name = c.fetchone()[0]
                result = tala.yn("Current name is " + name + ". Change")
                if result:
                    tala.popup(body="Please type new name")
                    time.sleep(1)
                    newname = tala.type()
                    c.execute("UPDATE `config` SET `value` = ? WHERE `option` = 'name'", [newname])
                    conn.commit()
                    tala.message("Changed", "Your name has been changed from " + name + " to " + newname + "!")
            elif choice == "Clear Data":
                time.sleep(1)
                result = tala.yn("Are you sure")
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
            elif choice == "Update Tala":
                time.sleep(1)
                result = tala.yn("Are you sure you'd like to update")
                if result:
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

                                tala.popup("Updated", "Update was successful! Tala will now restart in 3 seconds...")
                                time.sleep(3)
                                subprocess.call(["/etc/init.d/tala.sh", "restart"])
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

                        if device != None:
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
                                    if choice != "Exit":
                                        yn = tala.yn("Copy & Overwrite " + choice)
                                        if yn:
                                            logger.info("Copying file from " + os.path.join(mount.get_media_path(device), choice) + " to " + os.path.join(REPO_DIR, choice) + "...")
                                            shutil.move(os.path.join(mount.get_media_path(device), choice), os.path.join(REPO_DIR, choice))
                                            logger.info("Copy complete!")
                                            tala.popup("Updated", "Updated file " + choice + "!")
                                            time.sleep(1)
                                            restart = tala.yn("Restart")
                                            if restart:
                                                tala.popup("Restarting", "Tala will restart in 3 seconds.")
                                                time.sleep(3)
                                                subprocess.call(["/etc/init.d/tala.sh", "restart"])
                            else:
                                logger.info("Problem mounting drive " + device)
                                tala.message("Failure", "Problem mounting " + device + "!")

            elif choice == "Exit Options":
                break
    elif choice == "Power Off":
        time.sleep(1)
        option = tala.yn("Are you sure you'd like to power off")
        if option:
            logger.info("=== POWERING OFF DEVICE ===")
            tala.popup(body="Device shutting down. Wait up to 10s before removing power.")
            tala.cleanup()
            subprocess.call(["sudo", "halt"])
            break
