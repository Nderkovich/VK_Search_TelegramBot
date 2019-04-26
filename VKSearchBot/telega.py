import telebot
import json
import threading
import re

import vk

TOKEN = "" #telegram token here
bot = telebot.TeleBot(TOKEN, threaded=False)

with open("Groups.json") as fw:
    try:
        data = json.load(fw)
    except:
        data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello use /help to get more info:)')
    with open("user.txt", "w") as user_info:
        user_info.write(str(message.chat.id))


# HELP
@bot.message_handler(commands=['help'])
def send_help_info(message):
    with open("user.txt", "w") as user_info:
        user_info.write(str(message.chat.id))
    bot.send_message(message.chat.id,
                     """Write /add_group to add new group to serach or /add_word to add a new search word""")


# ADD GROUP
@bot.message_handler(commands=['addgroup'])
def add_group(message):
    msg = bot.send_message(message.chat.id, "Paste the link to the group like: vk.com/***")
    bot.register_next_step_handler(msg, get_group)


# ADD WORD
@bot.message_handler(commands=['addword'])
def add_word(message):
    msg = bot.send_message(message.chat.id, "Enter word or phrase you'd like to search for")
    bot.register_next_step_handler(msg, get_word)


# VIEW INCLUDED GROUPS
@bot.message_handler(commands=['viewgroups'])
def view_groups(message):
    text = ''
    for group in data.keys():
        text += group + "\n"
    if text:
        bot.send_message(message.chat.id, "Your groups:\n" + text)
    else:
        bot.send_message(message.chat.id, "You have mo groups")


# VIEW INCLUDED WORDS/PHRASES
@bot.message_handler(commands=['viewwords'])
def view_words(message):
    text = ''
    with open('Words.txt', 'r') as wordsfile:
        for line in wordsfile:
            text += line
    if text:
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Your words list is empty")


# DELETE GROUP
@bot.message_handler(commands=['deletegroup'])
def delete_group(message):
    msg = bot.send_message(message.chat.id, "Enter group to delete")
    bot.register_next_step_handler(msg, group_del)


@bot.message_handler(commands=['deleteword'])
def delete_word(message):
    msg = bot.send_message(message.chat.id, "Enter word to delete")
    bot.register_next_step_handler(msg, word_del)


# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ADD GROUP TO FILE
def get_group(message):
    # look for group in message
    if re.search(r"vk.com/\w+\.\w+", message.text):
        group = re.search(r"vk.com/\w+\.\w+", message.text)
        # check if group already included
        with open('Groups.json', 'r') as groupsfile_read:
            if group[0] not in groupsfile_read:
                groupsfile_read.close()
                # adding group to file
                data[group[0]] = {"short_name": (group[0])[7:], "id": None, "last_post": None}
                vk_id = vk.get_id((data[group[0]])["short_name"])
                last_post = vk.get_last_post(vk_id)
                if vk_id and last_post:
                    ((data[group[0]])["id"]) = vk_id
                    ((data[group[0]])["last_post"]) = last_post
                    bot.send_message(message.chat.id, "Group has been successfully added")
                    with open("Groups.json", "w") as groupsfile_write:
                        json.dump(data, groupsfile_write, indent=4)
                else:
                    if not vk_id:
                        bot.send_message(message.chat.id, "Error when trying to get group id")
                    else:
                        bot.send_message(message.chat.id, "Error when trying to get group posts")
                    data.pop(group[0])
            else:
                bot.send_message(message.chat.id, "Group is already included")
    else:
        bot.send_message(message.chat.id, "Something went wrong check your link")


# ADD WORD/PHRASE TO FILE
def get_word(message):
    if message.text:
        with open('Words.txt', 'r') as wordsfile_read:
            data_in_file = wordsfile_read.read().replace('\n', ' ')
            if message.text not in data_in_file:
                with open('Words.txt', 'a') as wordsfile_write:
                    wordsfile_write.write(message.text + '\n')
                    bot.send_message(message.chat.id, "Word/phrase has been successfully added")
            else:
                bot.send_message(message.chat.id, "Word/phrase is already included")
    else:
        bot.send_message(message.chat.id, "Something went wrong:(")


# DELETE GROUP
def group_del(message):
    try:
        data.pop(message.text)
        with open("Groups.json", "w") as groupsfile_write:
            json.dump(data, groupsfile_write, indent=4)
        bot.send_message(message.chat.id, "Success")
    except:
        bot.send_message(message.chat.id, "Something went wrong")


def full_seacrh(data):
    threading.Timer(1800.0, full_seacrh, (data,)).start()
    print("started")
    with open("user.txt") as user:
        user_id = user.read()
    words = []
    with open('Words.txt', 'r') as wordsfile:
        for line in wordsfile:
            words.extend(line.split())
    if words and data:
        for word in words:
            for key in data.keys():
                result = vk.search((data[key])["last_post"], word, (data[key])["id"])
            if result:
                bot.send_message(int(user_id), result)
        for key in data.keys():
            (data[key])["last_post"] = vk.get_last_post((data[key])["id"])
            with open("Groups.json", "w") as groupsfile_write:
                json.dump(data, groupsfile_write, indent=4)
    else:
        pass


def word_del(message):
    try:
        words = []
        with open("Words.txt", "r") as wordsread:
            for word in wordsread:
                words.append(word.rstrip())
        words.remove(message.text)
        with open("Words.txt", "w") as wordswrite:
            for word in words:
                wordswrite.write(word + "\n")
        bot.send_message(message.chat.id, "Success")
    except:
        bot.send_message("Something went wrong")


# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

while True:
    full_seacrh(data)
    bot.polling()
