from auth_data import TOKEN as token  # file with API
import telebot
import image_down_and_search
from math import ceil
import time


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    def send_img_group_from_url(count_files: int, lst_url_img: list, message,  download_img_in_server: bool):
        n1, n2, wait = 0, 10, 10
        for i in range(ceil(count_files/10)):
            if wait == 40:
                time.sleep(14)  # Telegram bot API max 30 req/sec
                wait = 0
            if not i == ceil(count_files/10):
                if download_img_in_server:
                    bot.send_media_group(message.chat.id, [telebot.types.InputMediaDocument(
                        open(link, 'rb')) for link in lst_url_img[n1:n2]])
                else:
                    bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(
                        link) for link in lst_url_img[n1:n2]])
                    time.sleep(0.5)
            else:
                if download_img_in_server:
                    bot.send_media_group(message.chat.id, [
                        telebot.types.InputMediaDocument(open(link, 'rb')) for link in lst_url_img[n2:]])
                else:
                    bot.send_media_group(message.chat.id, [
                        telebot.types.InputMediaPhoto(link) for link in lst_url_img[n2:]])
                    time.sleep(0.5)
            n1 += 10
            n2 += 10
            wait += 10
    try:
        @bot.message_handler(commands=["start"])
        def start_message(message):
            lst_menu = ('/download',)
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            [markup.add(telebot.types.KeyboardButton(word)) for word in lst_menu]
            bot.send_message(
                message.chat.id, "Hello, this bot help you download more images", reply_markup=markup)
            
        query_bot = {}

        @bot.message_handler(commands=["download"])
        def download(message):
            lst_names_size = ('Small', 'Medium', 'Full')
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            [markup.add(telebot.types.KeyboardButton(word)) for word in lst_names_size]
            msg = bot.send_message(
                message.chat.id, "Select photo size: Small, Medium, Full", reply_markup=markup)
            bot.register_next_step_handler(msg, download_size)

        def download_size(message):
            match message.text:
                case "Small":
                    query_bot['size_img'] = "small"
                case "Medium":
                    query_bot['size_img'] = "regular"
                case "Full":
                    query_bot['size_img'] = "full"
            markup = telebot.types.ReplyKeyboardRemove()
            msg = bot.send_message(
                message.chat.id, "What are we looking for? (Enter your query in English for best match)", reply_markup=markup)
            bot.register_next_step_handler(msg, download_search)

        def download_search(message):
            query_bot['search_word'] = message.text
            lst_count_img = (10,20,30,40,50,100)
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            [markup.add(telebot.types.KeyboardButton(num)) for num in lst_count_img]
            msg = bot.send_message(
                message.chat.id, "Choise or enter number: (Enter quantity in multiples of 10. Min.value=10)", reply_markup=markup)
            bot.register_next_step_handler(msg, download_count)

        def download_count(message):
            query_bot['search_count'] = int(message.text)
            time_download, count_files_text, lst_url_img, count_files, download_img_in_server = image_down_and_search.main(
                query_bot['search_word'], query_bot['search_count'], query_bot['size_img'])
            send_img_group_from_url(
                count_files, lst_url_img, message, download_img_in_server)
            bot.send_message(message.chat.id, time_download)
            bot.send_message(message.chat.id, count_files_text, reply_markup=telebot.types.ReplyKeyboardRemove())
        
    except telebot.apihelper.ApiTelegramException as ex:
        @bot.message_handler()
        def outputerror(message):
            bot.send_message(message.chat.id, 'Try again later.')
    bot.polling()

if __name__ == '__main__':
    telegram_bot(token)
