import talalib
import time

tala = talalib.Tala()

tala.message("Controls", "Hi There! Press 8 to scroll down and 2 to scroll back up. Then when you are finished press 5 to dismiss this message.")

time.sleep(0.25)

tala.message("Question", "What is your name? (Press 5 to continue)")

time.sleep(0.25)

name = tala.type()

tala.message("Hey", "Hello " + name + "! Press 5 to continue.")

time.sleep(0.25)

tala.message("Question", "So, do you like Ice Cream, " + name + "? (Press 5 to continue)")

time.sleep(0.25)

opt = tala.menu(["Yes", "No", "I don't know"])

if opt == "Yes":
    tala.message("Awesome", "I love Ice Cream too! I think we are going to get along well " + name + "!")
elif opt == "I don't know":
    tala.message("?", "You don't know? That's a pathetic answer " + name + "!")
else:
    tala.message("Grrrr", "I'm not your friend " + name + "!")

tala.clear()
tala.cleanup()
