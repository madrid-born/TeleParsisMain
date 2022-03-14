import telebot
from flask import Flask, request
import pandas as pd
import os
import psycopg2
from sqlalchemy import create_engine

API_KEY = '5131929422:AAGZhRuzw-FEiMtEyLmVCaGd0Tz1eGCZDrM'
conn_string = 'postgresql://rouzfxqtgpxzvf:7186fe89ce7cf7a0268fac5955dae9b8a612b61daa7167d91d6651cfebf0e97a@ec2-3-209-61-239.compute-1.amazonaws.com:5432/d4bfe3vvb81eoe'
bot = telebot.TeleBot(API_KEY)
server = Flask(__name__)

channel = -1001600009203
group = -1001712280383
MB = 315703198

Swears = []


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام به بات آژانس پارسیس خوش آمدید")


@bot.message_handler(commands=['main'])
def am(message):
    bot.send_message(message.chat.id, str(db_reader()))


@bot.message_handler(commands=['check'])
def check(message):
    if message.chat.type == "private":
        result = bot.get_chat_member(group, message.chat.id)
        if result.status == "left":
            bot.send_message(message.chat.id, "لطفا در گروه عضو شوید")
        else:
            add = reader(message.chat.id)
            bot.send_message(message.chat.id, "شما تعداد " + str(add) + " نفر را اضافه کردید")


@bot.message_handler(content_types='new_chat_members')
def new_participant(message):
    adding(message.json["from"]["id"])
    adder(message.json["new_chat_member"]["id"])
    delete(message)


@bot.message_handler(content_types='left_chat_member')
def left_participant(message):
    delete(message)


@bot.message_handler(content_types='text')
def police(message):
    string = message.text
    for word in string.split():
        if word in Swears:
            ban(message.chat.id)


def db_reader():
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    sql1 = '''select * from data;'''
    cursor.execute(sql1)
    df = pd.DataFrame(cursor.fetchall())
    conn.close()
    return df


def db_replace(df):
    db = create_engine(conn_string)
    conn = db.connect()
    df.to_sql('data', con=conn, if_exists='replace', index=False)
    conn.close()


def reader(user_id):
    file = db_reader()
    i = 0
    a = []
    while i != -1:
        try:
            a.append(file[0][i])
            i += 1
        except:
            i = -1
    num = a.index(user_id)
    return file[1][num]


def adder(user_id):
    file = db_reader()
    i = 0
    a = []
    while i != -1:
        try:
            a.append(file[0][i])
            i += 1
        except:
            i = -1
    df2 = pd.DataFrame({0: [user_id], 1: [0]})
    db_replace(pd.concat([file, df2], ignore_index=True))


def adding(user_id):
    file = db_reader()
    i = 0
    a = []
    while i != -1:
        try:
            a.append(file[0][i])
            i += 1
        except:
            i = -1
    user_tag = a.index(user_id)
    num = file[1][user_tag]
    add = int(num) + 1
    file[1][user_tag] = add
    file = file[[0, 1]]
    db_replace(file)


def ban(user_id):
    bot.restrict_chat_member(group, user_id, 86400, False, False, False, False, False, False, True, False)


def delete(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@server.route('/'+ API_KEY, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telparsis.herokuapp.com/' + API_KEY)
    return "!", 200


def main():
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


if __name__ == '__main__':
    main()