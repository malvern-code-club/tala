import talalib

tala = talalib.Tala()

tala.clear()

while True:
    choice = tala.menu(["Public Message", "Private Message", "Snake", "Distress Beacon", "Power Off"])
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
    elif choice == "Power Off":
        tala.message("Alert", "Power Off")]
        break
