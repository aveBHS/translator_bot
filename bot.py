import vkbee
import requests
import config
import asyncio
from vkbee import oldlong

async def write_msg(message, peer_id):
    bot = vkbee.VkApi(
        config.token,
        loop=loop
     )
    await vkbee.VkApi.call(bot,'messages.send', {'peer_id': peer_id, 'message': message, "random_id": 0})

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
        
async def main(loop):
     bot = oldlong.VkApi(
        config.token,
        loop=loop
     )
     vk_polluse = oldlong.BotLongpoll(bot, config.group_id,10)
     async for event in vk_polluse.events():
        if event['type'] == 'message_new':
            text = event['object']['message']['text']
            words = text.lower().split(' ')
            if(words[0] == '/language' or words[0] == '/lang' or words[0] == '/язык' or words[0] == '/определи'):
                lang = detect_language(text)
                lang_name = language_name(lang)
                await write_msg(f'Язык определен, как: {lang_name}\nКод языка: {lang}', event['object']['message']['peer_id'])
            elif(words[0] == '/trans' or words[0] == '/translate' or words[0] == 'перевод' or words[0] == 'переведи'):
                if(len(words) < 3):
                    await write_msg(f'Используйте команду в виде: {words[0]} [код языка] [текст]\nПример: {words[0]} en Привет!', event['object']['message']['peer_id'])
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
                        await write_msg(f'Вы ввели неверный код языка или не ввели его вовсе!\nМы перевели текст на английский:\n{translated_text}', event['object']['message']['peer_id'])
                    else:
                        translated_text = translate(text_to_translate, 'ru')
                        await write_msg(f'Вы ввели неверный код языка или не ввели его вовсе!\nМы перевели текст на русский:\n{translated_text}', event['object']['message']['peer_id'])
                    continue
                else: 
                    await write_msg(f'Перевод успешно завершен:\n{translated_text}', event['object']['message']['peer_id'])
            elif(text == '' or text[0] == '/'):
                continue
            else:
                lang = detect_language(text)
                print(lang)
                if(len(text) < 500):
                    if(lang == '' or lang == None):
                        continue
                    if(lang != 'ru'):
                        if(len(text) < 101):
                            translated_text = translate(text, 'ru')
                            await write_msg(f'В сообщении обнаружен иностранный текст ({lang}).\nПеревод на русский:\n{translated_text}', event['object']['message']['peer_id'])
                        else:
                            await write_msg(f'В сообщении обнаружен иностранный текст ({lang}), начинаю переводить...', event['object']['message']['peer_id'])
                            translated_text = translate(text, 'ru')
                            await write_msg(f'Перевод успешно завершен:\n{translated_text}', event['object']['message']['peer_id'])
                            
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))                   
