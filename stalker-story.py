# stalker-text.py

# Obtain player name
guide = "Guide: "
quote = "''"
space = " "
divider = "__________________________________________________________________________________________________________________________________________________________"
print(guide, quote,"Hello STALKER, I'll be your guide to getting started here, though, I must ask, what should I call you?",quote, space)
playerName = input ("My name's... ")
print(" ")
print(guide, quote,"Pleasure to meet you", playerName,quote, space)
# Interaction
speech1 = ("1) Nice to meet you as well.  2) Lets just get going.   3) Enough pleasantry, I don't need the chit-chat.   4) ... ")
print(divider)
print("Respond:")
print(speech1)
print(divider)
print(space)
respond1 = input ("Your Reply: ")
print(divider)
print(space)
# Set response as a print based off the players reply
response1 = ""
if respond1 == "1":
    response1 = print(guide, quote,"Alright then, we'd best get a move on.",quote)
elif respond1 == "2":
    response1 = print(guide, quote,"Alright, fair enough I guess, we do need to get going.",quote)
if respond1 == "3":
    response1 = print(guide, quote,"Damn, well screw you I guess, now lets get going.",quote)
if respond1 == "4":
    response1 = print(guide, quote,"Not a talker stalker huh, well, we better get going.",quote)

print(divider)
print(space)
print(divider)
print(space)
print(guide, quote,"Hey, there is an old weapons crate here, why don't you open it up and see what is in there!",quote)
print(divider)
print(space)
print(" 1) Open")
print(space)
openInput1 = input ("- ")
print(space)
print(divider)
print(space)
openeningInput1 = ""
if openInput1 == "1":
    openingInput1 = print("+1 Makarov PM")
print(divider)
print(space)
