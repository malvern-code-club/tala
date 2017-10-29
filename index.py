import talalib
import sqlite3
import threading
import random
import string
import datetime
import json
import time
from subprocess import call
import os
import datetime

conn = None
c = None

def log(level, content):
    print("[" + str(datetime.datetime.utcnow()) + "] (TALA) {" + level + "} -> " + content)

log("info", "=== STARTED TALA ===")

def setupDb():
    global conn
    global c

    conn = sqlite3.connect("database.db")
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
            log("info", "Creating table " + table["name"] + " with query: CREATE TABLE " + table["name"] + " (" + table["columns"] + ")")
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
    log("info", "Created new Unique Device ID: " + udid + ".")

c.execute("SELECT * FROM `config` WHERE `option` = 'udid'")
if c.fetchone() == None:
    newUdid()

tala = talalib.Tala()

tala.clear()

def encode(data):
    data = json.dumps(data) #Json dump message
    return(data)
def decode(data):
    data = json.loads(data) #Load from json
    return(data)

while True:
    log("info", "Showing main menu")
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

        c.execute("SELECT * FROM `config` WHERE `option` = 'udid'")
        udid = c.fetchone()[0]

        message = {
                    "content": content,
                    "id": msg_id,
                    "timestamp": timestamp,
                    "sender": {
                        "name": "Jake Walker",
                        "udid": udid
                    }
                }

        log("info", "Sending Public Message: " + encode(message))

        tala.send(encode(message))
        time.sleep(1)
    elif choice == "Memo":
        c.execute("SELECT * FROM memos")
        memos = c.fetchall()
        if len(memos) > 0:
            log("info", "Showing memo menu.")
            memolist = ["New Memo", "Delete Memo"]
            for memo in memos:
                memolist.append(memo[0])
            choice = tala.menu(memolist)
            time.sleep(1)
        else:
            log("info", "No memos created, automatically choosing to create new memo.")
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
            log("info", "Created new memo with title '" + memo_name + "' and body '" + memo_data + "'")
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
            choice = tala.menu(["Change Pin", "Reset Device ID", "Clear Data", "Update Tala", "Exit Options"])
            if choice == "Change Pin":
                pin = tala.type_numbers()
                time.sleep(1)
                tala.message("Debug", "Changed PIN to " + str(pin))
                time.sleep(1)
            elif choice == "Reset Device ID":
                result = tala.yn("Are you sure")
                if result:
                    newUdid()
                    tala.message("Reset UDID", "Device ID regenerated!")
                    time.sleep(1)
                elif not result:
                    tala.message("Reset UDID", "No changes made.")
                    time.sleep(1)
            elif choice == "Clear Data":
                result = tala.yn("Are you sure")
                if result:
                    log("info", "Deleting database...")
                    os.remove("database.db")
                    tala.popup("Purging...", "Database purged!")
                    time.sleep(2)
                    tala.popup("Purging...", "Recreating Database...")
                    log("info", "Setting up database...")
                    setupDb()
                    tala.message("Purged", "Successfully cleared data.")
                    time.sleep(1)
                    log("info", "Database purge complete!")
                elif not result:
                    tala.message("Alert", "No changed made.")
                    time.sleep(1)
            elif choice == "Update Tala":
                result = tala.yn("Are you sure you'd like to update")
            elif choice == "Exit Options":
                break
    elif choice == "Power Off":
        choice = tala.menu(["Power Off", "Don't Power Off"])
        if choice == "Power Off":
            option = tala.yn("Power Off", "Are you sure you'd like to power off?")
            if option:
                log("warn", "=== POWERING OFF DEVICE ===")
                tala.popup(body="Device shutting down. Wait up to 10s before removing power.")
                tala.cleanup()
                call(["sudo", "halt"])
                break
