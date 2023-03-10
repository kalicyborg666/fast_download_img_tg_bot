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
            bot.send_message(
                message.chat.id, "Hello, this bot help you download more images\n/download - Download image")

        query_bot = {}

        @bot.message_handler(commands=["download"])
        def download(message):
            msg = bot.send_message(
                message.chat.id, "Select photo size: small, regular, full")
            bot.register_next_step_handler(msg, download_size)

        def download_size(message):
            query_bot['size_img'] = message.text.lower()
            msg = bot.send_message(
                message.chat.id, "What are we looking for? (Enter your query in English for best match)")
            bot.register_next_step_handler(msg, download_search)

        def download_search(message):
            query_bot['search_word'] = message.text
            msg = bot.send_message(
                message.chat.id, "Number of photos: (Enter quantity in multiples of 10. Min.value=10)")
            bot.register_next_step_handler(msg, download_count)

        def download_count(message):
            query_bot['search_count'] = int(message.text)
            time_download, count_files_text, lst_url_img, count_files, download_img_in_server = image_down_and_search.main(
                query_bot['search_word'], query_bot['search_count'], query_bot['size_img'])
            send_img_group_from_url(
                count_files, lst_url_img, message, download_img_in_server)
            bot.send_message(message.chat.id, time_download)
            bot.send_message(message.chat.id, count_files_text)
        bot.polling()
    except telebot.apihelper.ApiTelegramException as ex:
        @bot.message_handler()
        def outputerror(message):
            bot.send_message(message.chat.id, 'Try again later.')


if __name__ == '__main__':
    telegram_bot(token)
