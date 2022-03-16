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

group = -1001313147690
MB = 315703198

Swears = []


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "با سلام به بات آژانس مسافرتی پارسیس خوش آمدید\n\nبرای اتصال به بخش فروش روی "
                                      "گزینه /tour کلیک کنید\n و برای اطلاع از تعداد افراد اضافه شده توسط شما بر روی "
                                      "/check کلیک کنید")


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
    state1 = search(message.json["new_chat_member"]["id"])
    state2 = search(message.json["from"]["id"])
    if state1:
        adder(message.json["new_chat_member"]["id"])
    if state2:
        adder(message.json["from"]["id"])
    if state1:
        adding(message.json["from"]["id"])
    delete(message)


@bot.message_handler(commands='ban')
def banning(message):
    try:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.json["from"]["id"], 86400)
    except:
        pass


@bot.message_handler(commands='tour')
def new_tour(message):
    tour(message)


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


def search(user_id):
    file = db_reader()
    i = 0
    a = []
    while i != -1:
        try:
            a.append(file[0][i])
            i += 1
        except:
            i = -1
    if user_id in a:
        return False
    else:
        return True


def adder(user_id):
    file = db_reader()
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


def tour(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("تور خارجی", url='t.me/omidhappy'))
    keyboard.add(telebot.types.InlineKeyboardButton("تور داخلی", url='t.me/omidhappy'))
    keyboard.add(telebot.types.InlineKeyboardButton("تور کیش", url='t.me/omidhappy'))
    bot.send_message(message.chat.id, "برای خرید تور و بلیط بر روی دکمه موردنظر خود کلیک کنید",
                     reply_markup=keyboard)


def ban(user_id):
    bot.restrict_chat_member(group, user_id, 86400, False, False, False, False, False, False, True, False)


def delete(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@server.route('/' + API_KEY, methods=['POST'])
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
