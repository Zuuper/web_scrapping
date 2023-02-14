import telebot

uid_token = "5833760214:AAEs27YOC63HOprbO53j-jup7fMT2iMTZzk"
user_id = '1566553232'
user_id_2 = "676516449"
user_id_luka = '927606900'
bot = telebot.TeleBot(uid_token)

updates = bot.get_updates()
# chat_ids = []
#
# for update in updates:
#     chat_id = update.message.chat.id
#     print(chat_id)
#     print(update)


def bot_send_message(text):
    bot.send_message(chat_id=user_id_luka, text=text)
