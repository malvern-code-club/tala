import talalib
import sqlite3
import threading
import random
import string
import datetime
import json
import time
from subprocess import call

conn = sqlite3.connect("database.db")
c = conn.cursor()

def setupDb():
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
    		print("Creating table " + table["name"])
    		print("CREATE TABLE " + table["name"] + " (" + table["columns"] + ")")
    		c.execute("CREATE TABLE " +
    				  table["name"] + " (" + table["columns"] + ")")
        	conn.commit()

setupDb()

tala = talalib.Tala()

tala.clear()

def encode(data):
	data = json.dumps(data) #Json dump message
	return(data)
def decode(data):
	data = json.loads(data) #Load from json
	return(data)

while True:
	choice = tala.menu(["Public Message", "Memo", "Settings", "Power Off"])
	time.sleep(1)
	if choice == "Public Message":
		def recv_data(stop_event):
			while (not stop_event.is_set()):
				data = tala.receive()
				time.sleep(1)
				if data == "":
					pass
				else:
					tala.message("Message", data)

		t_stop = threading.Event()
		thread_recv_data = threading.Thread(target=recv_data, args=t_stop)
		thread_recv_data.start()

		content = tala.type()
		time.sleep(1)
		while True:
			choice = tala.menu(["Send a message", "Exit"])
			if choice == "Send a message":
				msg_id = ""
				i = 0
				while i != 5:
					msg_id += random.choice(string.ascii_lowercase)

				timestamp = datetime.datetime.now()

				message = {
								"content": content,
								"id": msg_id,
								"timestamp": timestamp,
								"sender": "",
								"recipient": ""
								}

				tala.send(encode(message))
				time.sleep(1)
			elif choice == "Exit":
				t_stop.set() # Kills the thread
				break
	elif choice == "Memo":
		c.execute("SELECT * FROM memos")
		memos = c.fetchall()
		if len(memos) > 0:
			memolist = ["New Memo", "Delete Memo"]
			for memo in memos:
				memolist.append(memo[0])
			choice = tala.menu(memolist)
			time.sleep(1)
		else:
			choice = "New Memo"
		if choice == "New Memo":
                        tala.message("Alert", "Input memo name")
			memo_name = tala.type()
			time.sleep(1)
			tala.message("Alert", "Input memo data")
			memo_data = tala.type()
			time.sleep(1)
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
			choice = tala.menu(["Change Pin", "Reset Device Key", "Clear Data", "Update Tala", "Exit Options"])
			if choice == "Change Pin":
				pin = tala.type_numbers()
				time.sleep(1)
				tala.message("Debug", "Changed PIN to " + str(pin))
				time.sleep(1)
			elif choice == "Reset Device Key":
				result = tala.yn("Are you sure")
				if result:
					tala.message("Alert", "Device Key reset")
					time.sleep(1)
					#No actual code for this yet
				elif not result:
					tala.message("Alert", "No changes made.")
					time.sleep(1)
			elif choice == "Clear Data":
				result = tala.yn("Are you sure")
				if result:
                    c.execute("DROP TABLE *;")
                    tala.popup(body="Database purged!")
                    time.sleep(2)
                    tala.popup(body="Recreating Database...")
                    setupDb()
                    tala.message("Cleared", "Successfully cleared data.")
                    time.sleep(1)
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
            tala.message("Alert", "Power Off")
            tala.cleanup()
            call(["sudo", "halt"])
            break
