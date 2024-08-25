#!/usr/bin/env python3


# Telegram bot for Craiyon Image generator
# Github : https://github.com/Kourva/CraiyonBot


# Imports
import requests
import telebot
import base64
import json
import os


# Config
with open("token.env", "r") as config:
    Token = config.read().strip().split("=")[1]


# Client
bot = telebot.TeleBot(Token)


# User class: which creates a member with needed stuff.
class User:
    def __init__(self, message) -> None:
        # takes user info from message
        self.fname = message.from_user.first_name
        self.lname = message.from_user.last_name
        self.uname = message.from_user.username
        self.usrid = message.from_user.id


# Craiyon class: which creates images using craiyon
class Craiyon:
    def __init__(self, prompt):
        self.prompt = prompt

    # generates and saves the images
    def generate(self):
        craiyon = "https://backend.craiyon.com/generate"
        payload = {
            "prompt": self.prompt,
        }
        try:
            response = requests.post(url=craiyon, json=payload, timeout=160)
            result = response.json()["images"]

            for index, image in enumerate(result, start=1):
                with open(f"generated/{self.prompt}_{index}.webp", "wb") as file:
                    file.write(base64.decodebytes(image.encode("utf-8")))

        except Exception as ex:
            return False


## LOCKER
status = False


def lock():
    global status
    status = True


def unlock():
    global status
    status = False


# Start command: will be executed when /start pressed.
@bot.message_handler(commands=["start"])
def start_command(message):
    # Gets user information
    user = User(message)
    name = user.fname if user.fname is not None else f"Unknown User"

    # Send hello message
    bot.reply_to(message, "Hi. Use 'ai your text' to generate images")


# Craiyon image generator
@bot.message_handler(func=lambda message: message.text.startswith("ai"))
def craiyon_generator(message):
    if status == False:
        lock()
        
        # Gets user information
        user = User(message)
        name = user.fname if user.fname is not None else f"Unknown User"

        # Sends waiting prompt
        temp = bot.reply_to(message, "Please wait. It can up to 3 minutes")

        # Sets variables
        images = []
        usrmsg = message.text.split("ai")[1]

        # Deletes old images (if any)
        path = os.listdir("generated")
        if len(path) >= 1:
            for item in path:
                os.remove(f"generated/{item}")
            print("old images deleted")

        # Gets images from result
        result = Craiyon(usrmsg).generate()
        if result == False:
            bot.edit_message_text(
                "Can't get images right now. Try again", message.chat.id, temp.message_id
            )
        else:
            path = os.listdir("generated")
            print("new images downloaded.")
            for item in path:
                with open(f"generated/{item}", "rb") as file:
                    bot.send_photo(message.chat.id, file, item.split(".webp")[0])
            print(f"sent images to User '{name}' ({user.usrid})")

        unlock()

    else:
        bot.reply_to(message, "Another user is using this feature. wait...")


# Runs the bot in infinity mode
if __name__ == "__main__":
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Exit requested by user.")
        sys.exit()
