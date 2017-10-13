import talalib
from subprocess import call

tala = talalib.Tala()

tala.clear()

while True:
    choice = tala.menu(["Public Message", "Private Message", "Snake", "Distress Beacon", "Settings", "Power Off"])
    if choice == "Public Message":
        message = tala.type()
        tala.message("Debug", message) #Replace this with code for sending message
        
    elif choice == "Private Message":
         message = tala.type()
         tala.message("Debug", message) #Replace this with code for sending message
        
    elif choice == "Snake":
        tala.message("Alert", "[game code here]")
    elif choice == "Distress Beacon":
        tala.message("Alert", "[distress beacon code here]")
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
        choice = tala.menu(["Power Off", "Don't Power Off"])
        if choice == "Power Off":
            tala.message("Alert", "Power Off")]
            tala.cleanup()
            call(["sudo", "halt"])
            break
