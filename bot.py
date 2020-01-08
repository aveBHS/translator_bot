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

def translate(text, lang):
    args = {'key': config.translator_token, 'text': text, 'lang': lang}
    response = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate', params=args)
    if(response.status_code == 200):
        return response.json()['text'][0]
    else:
        print(response)
        print(response.url)

for event in longpoll.listen():
    if(event.type == VkBotEventType.MESSAGE_NEW):
        text = event.object.text
        if(len(text) < 500):
            lang = detect_language(text)
            if(lang != 'ru'):
                if(len(text) < 101):
                    translated_text = translate(text, 'ru')
                    write_msg(f'В сообщении обнаружен иностранный текст ({lang}). Перевод на русский:\n{translated_text}', event.object.peer_id)
                else:
                    write_msg(f'В сообщении обнаружен иностранный текст ({lang}), начинаю переводить...', event.object.peer_id)
                    translated_text = translate(text, 'ru')
                    write_msg(f'Перевод успешно завершен:\n{translated_text}', event.object.peer_id)
