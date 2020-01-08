import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randint
import requests
import config

bot = vk_api.VkApi(token=config.token)
longpoll = VkBotLongPoll(bot, group_id=config.group_id, wait=99999)

def write_msg(message, peer_id):
    bot.method('messages.send', {'peer_id': peer_id, 'message': message, "random_id": randint(-2147483648, 2147483648)})

def detect_language(text):
    args = {'key': config.translator_token, 'text': text}
    response = requests.get('https://translate.yandex.net/api/v1.5/tr.json/detect', params=args)
    if(response.status_code == 200):
        return response.json()['lang']
    else:
        print(response)
        print(response.url)

def language_name(ui):
    args = {'key': config.translator_token, 'ui': ui}
    response = requests.get('https://translate.yandex.net/api/v1.5/tr.json/getLangs', params=args)
    if(response.status_code == 200):
        return response.json()['langs'][ui]
    else:
        print(response)
        print(response.url)

def translate(text, lang):
    args = {'key': config.translator_token, 'text': text, 'lang': lang}
    response = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate', params=args)
    if(response.status_code == 200):
        return response.json()['text'][0]
    elif(response.status_code == 400):
        return -1
    else:
        print(response)
        print(response.url)

for event in longpoll.listen():
    if(event.type == VkBotEventType.MESSAGE_NEW):
        text = event.object.text
        words = event.object.text.lower().split(' ')
        if(words[0] == '/language' or words[0] == '/lang' or words[0] == '/язык' or words[0] == '/определи'):
            lang = detect_language(text)
            lang_name = language_name(lang)
            write_msg(f'Язык определен, как: {lang_name}\nКод языка: {lang}', event.object.peer_id)
        elif(words[0] == '/trans' or words[0] == '/translate' or words[0] == '/перевод' or words[0] == '/переведи'):
            if(len(words) < 3):
                write_msg(f'Используйте команду в виде: {words[0]} [код языка] [текст]\nПример: {words[0]} en Привет!', event.object.peer_id)
                continue
            text_to_translate = ''
            i = 0
            for word in words:
                if(i < 2):
                    i += 1
                else:
                    text_to_translate += word + ' '
            translated_text = translate(text_to_translate, words[1])
            if(translated_text == -1):
                if(detect_language(text_to_translate) == 'ru'):
                    translated_text = translate(text_to_translate, 'en')
                    write_msg(f'Вы ввели неверный код языка или не ввели его вовсе!\nМы перевели текст на английский:\n{translated_text}', event.object.peer_id)
                else:
                    translated_text = translate(text_to_translate, 'ru')
                    write_msg(f'Вы ввели неверный код языка или не ввели его вовсе!\nМы перевели текст на русский:\n{translated_text}', event.object.peer_id)
                continue
            else: 
                write_msg(f'Перевод успешно завершен:\n{translated_text}', event.object.peer_id)
        else:
            lang = detect_language(text)
            print(lang)
            if(len(text) < 500):
                if(lang == ''):
                    continue
                if(lang != 'ru'):
                    if(len(text) < 101):
                        translated_text = translate(text, 'ru')
                        write_msg(f'В сообщении обнаружен иностранный текст ({lang}).\nПеревод на русский:\n{translated_text}', event.object.peer_id)
                    else:
                        write_msg(f'В сообщении обнаружен иностранный текст ({lang}), начинаю переводить...', event.object.peer_id)
                        translated_text = translate(text, 'ru')
                        write_msg(f'Перевод успешно завершен:\n{translated_text}', event.object.peer_id)
