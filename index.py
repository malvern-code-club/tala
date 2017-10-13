import talalib
import sqlite3
import threading
import random
import string
import datetime
import json

conn = sqlite3.connect("student_database.db")
c = conn.cursor()

tables = [
    {
        "name": "memos",
        "columns": "memo_name TEXT, memo_data TEXT"
    },
    {
        "name": "config",
        "columns": "pin TEXT"
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


tala = talalib.Tala()

tala.clear()

def encode(data):
    data = json.dumps(data) #Json dump message
    return(data) 
def decode(data):
    data = json.loads(data) #Load from json
    return(data)


while True:
    choice = tala.menu(["Public Message", "Private Message", "Snake", "Memo", "Settings", "Power Off"])
    if choice == "Public Message":
        def recv_data():
            print("Thread has run")

        thread_recv_data = threading.Thread(target=recv_data):
        thread_recv_data.start()

        content = tala.type()
    
        msg_id = ""
        i = 0
        while i != 5:
            msg_id += random.choice(string.ascii_lowercase)
    
        timestamp = datetime.datetime.now()        
                
        message = { "content": content,
                    "id": msg_id, 
                    "timestamp": timestamp, 
                    "sender": "", 
                    "recipient": ""
                    }
            
        tala.send(encode(message))
	    
    elif choice == "Private Message":
         message = tala.type()
         tala.message("Debug", message) #Replace this with code for sending message
    elif choice == "Snake":
        tala.message("Alert", "[game code here]")
	elif choice == "Memo":
		c.execute("SELECT * FROM memos")
		memos = c.fetchall()
		choice = tala.menu(["New Memo"], memos)
		if choice == "New Memo":
			memo_data = tala.type()
			tala.message("Alert", "Input memo name")
			memo_name = tala.type()
			c.execute("INSERT INTO memos (memo_name, memo_data) values (?, ?)", [memo_name, memo_data])
		else:
			c.execute("SELECT memo_data FROM memos WHERE memo_name = ?", [choice])
			memo_data = c.fetchall()
			tala.message(choice, memo_data[0])
    elif choice == "Settings":
        while True:
            choice = tala.menu(["Change Pin", "Reset Device Key", "Exit Options"])
            if choice == "Change Pin":
                pin = tala.type_numbers()
                tala.message("Debug", "Changed PIN to " + str(pin))
            elif choice == "Reset Device Key":
                tala.message("Warning!", "Are you sure?(0/1)")
                while True:
                    choice = tala.singlebutton()
                    if choice == "1":
                        tala.message("Alert", "Device Key reset")
                        #No actual code for this yet
                    elif choice == "0":
                        tala.message("Alert", "Did not reset Device Key")
                    else:
                        tala.message("Error", "Invalid input")
            elif choice == "Exit Options":
                break
    elif choice == "Power Off":
        tala.message("Alert", "Power Off")]
        tala.cleanup()
        break
