from django.http import HttpResponse
from django.shortcuts import render
import requests
from django.core.exceptions import ObjectDoesNotExist
from .models import BotUsers
from django.views.decorators.csrf import csrf_exempt
import json
from .credetials import URL, BOT_API
from googletrans import Translator
# Create your views here.
from django.views.decorators.http import require_http_methods

translator = Translator()
LANGUAGES = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',

    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
}


def index(request):
    return HttpResponse("index is working")


def translate(message=None, user=None, text=None):
    lang = ''
    if user:
        if user.user_lang == 'uz':
            lang = user.user_lang
        elif user.user_lang == 'en':
            lang = user.user_lang
    elif message:
        user_id = message['from']['id']
        user = BotUsers.objects.get(user_id=user_id)
        if user.user_lang == 'uz':
            lang = user.user_lang
        elif user.user_lang == 'en':
            lang = user.user_lang
    else:
        return text

    if lang == 'uz':
        words = {
            "choose language": "tilni tanlang",
            "please enter your name": 'iltimos ismizni kiriting',
            'qaysi tildan tarjima qilmoqchisiz': 'qaysi tildan tarjima qilmoqchisiz',
            'qaysi tilga tarjima qilmoqchisiz': 'qaysi tilga tarjima qilmoqchisiz',
        }
        if text in words.keys():
            return words[text]
        else:
            return text


    elif lang == 'en':
        words = {
            "tarjima tilini kiritish": "enter translating languages",
            'setting': 'setting',
            'biz haqimizda': 'about us',
            "tilni tanlang": "choose language",
            'qaysi tildan tarjima qilmoqchisiz': 'Which language you are translating from',
            'qaysi tilga tarjima qilmoqchisiz': 'Which language you are translating to',
        }
        if text in words.keys():
            return words[text]
        else:
            return text


@csrf_exempt
def getpost(request):
    global message
    if request.method == 'POST':

        telegram_message = json.loads(request.body)
        if "callback_query" in telegram_message.keys():
            message = telegram_message['callback_query']
            print(message)
        if "message" in telegram_message.keys():
            message = telegram_message['message']

        try:

            user = BotUsers.objects.get(user_id=message['from']['id'])

            if 'text' in message.keys():
                messageHandler(message, user)
            elif "data" in message.keys():
                callbackHandler(message, user=user)

        except ObjectDoesNotExist:
            if message['text'] == translate(text="register"):
                print(message)
                user = BotUsers.objects.create(user_id=message['from']['id'], user_step='get_lang')
                user.fullname = message['from']['first_name']
                user.save()
                stepHandler(user, message)

            else:
                bot_request("sendMessage", {
                    'chat_id': message['from']['id'],
                    'text': "Botimizni ishlatish uchun registratsiyadan oting/ In order to use our bot please register!",
                    "reply_markup": json.dumps({
                        "keyboard": [[
                            'register',
                        ]],
                        'resize_keyboard': True
                    })
                })

    return HttpResponse("getpost")


@require_http_methods(["GET", "POST"])
def setwebhook(request):
    response = requests.post(BOT_API + "setWebhook?url=" + URL).json()
    return HttpResponse(f"{response}")


def bot_request(method, data):
    return requests.post(BOT_API + method, data)


def callbackHandler(message, user=None):

    if message['data'] == 'bot_lang':
        delete_message(message)

        user.user_step = 'get_lang'
        user.save()
        stepHandler(user)
    elif message['data'] == 'translate_lang':
        delete_message(message)

        user.user_step = 'get_t_from_lang'
        user.save()
        stepHandler(user)
    elif user.user_step:
        delete_message(message)
        setHandler(message, user)
    print('callback ni ichidaman')
    print(message['data'])


def messageHandler(message, user):
    # print(message)
    user = BotUsers.objects.get(user_id=message['from']['id'])
    if user.user_step:
        setHandler(message, user)

    elif message['text'] == translate(message=message, text="tarjimani boshlash"):
        user.user_step = 'get_text'
        user.save()
        bot_request("sendMessage", {
            'chat_id': message['from']['id'],
            'text': translate(message=message, text="texni kiriting")
        })
    elif message['text'] == translate(message=message, text='biz haqimizda'):
        bot_request("sendMessage", {
            'chat_id': user.user_id,
            'parse_mode': 'HTML',
            'text': translate(user=user, text="biz haqimizda")
        })
        redirectToHomePage(message)
    elif message['text'] == translate(message=message, text='setting'):
        settingHandler(message, user)
    elif message['text'] == translate(message=message, text='biz haqimizda'):
        pass

    else:
        redirectToHomePage(message)


def delete_message(message):
    bot_request("deleteMessage", {
        'chat_id': message['from']['id'],
        'message_id': message['message']['message_id']
    })


def settingHandler(message, user):
    bot_request('sendMessage', {
        'chat_id': user.user_id,
        'text': translate(user=user, text="sozlamalar"),
        "reply_markup": json.dumps({
            "inline_keyboard": [[{
                'text': translate(user=user, text="botni tilini o'zgartiring"),
                'callback_data': "bot_lang"
            },
                {
                    'text': translate(user=user, text="tarjima qilish tillarini o'zgartiring"),
                    'callback_data': "translate_lang"
                }
            ]],
            'resize_keyboard': True
        })
    })


def translate_the_text(text, user=None):
    text = translator.translate(text, dest=user.translate_to_lang).text
    return text


def setHandler(message, user, setting=None):
    if setting is not None:
        if user.user_step == "get_lang":
            user.user_lang = message['text']
            user.user_step = ''
            user.save()
            stepHandler(user, message)
    elif user.user_step:
        print('sethandlerdaman', user.user_step)
        if user.user_step == "get_lang":
            user.user_lang = message['text']
            if user.translate_from_lang:
                user.user_step = ''
            else:
                user.user_step = 'get_t_from_lang'
            user.save()
            stepHandler(user, message)

        elif user.user_step == "get_t_from_lang":
            user.translate_from_lang = message['data']
            user.user_step = 'get_t_to_lang'
            user.save()
            stepHandler(user, message)

        elif user.user_step == "get_t_to_lang":
            user.translate_to_lang = message['data']
            user.user_step = ''
            user.save()
            stepHandler(user, message)

        elif user.user_step == "get_text":
            user.text = message['text']
            stepHandler(user, message)
            user.user_step = ''
            user.save()
            redirectToHomePage(message)


def stepHandler(user, message=None):
    print('stephandlerdaman', user.user_step)
    if user.user_step == "get_lang":
        bot_request("sendMessage", {
            "chat_id": user.user_id,
            'text': "Botni tililni tanlang / Choose the default language",
            "reply_markup": json.dumps({
                "keyboard": [['uz'], ['en']],
                'remove_keyboard': True
            })
        })
    elif user.user_step == "get_t_from_lang":
        menus = call_dynamic_menu(LANGUAGES)

        bot_request("sendMessage", {
            "chat_id": user.user_id,
            'text': translate(text='qaysi tildan tarjima qilmoqchisiz', user=user),
            "reply_markup": json.dumps({
                "inline_keyboard": menus,
                'resize_keyboard': True
            })
        })
    elif user.user_step == "get_t_to_lang":
        print('get_t_to_lang ni ichidaman')
        menus = call_dynamic_menu(LANGUAGES)
        bot_request("sendMessage", {
            "chat_id": user.user_id,
            'text': translate(text='qaysi tilga tarjima qilmoqchisiz', user=user),
            "reply_markup": json.dumps({
                "inline_keyboard": menus,
                'resize_keyboard': True
            })
        })
    elif user.user_step == 'get_text':
        text = translate_the_text(user.text, user=user)
        bot_request("sendMessage", {
            "chat_id": user.user_id,
            'text': text,
        })
    else:
        if message:
            redirectToHomePage(message)


def call_dynamic_menu(data, user=None):
    tem_data = []
    single_line = []
    num = len(data)
    menu = []
    if num % 2 != 0:
        num -= 1
        lang = data.popitem()
        one = {'text': lang[1], 'callback_data': lang[0]}
        tem_data.append([one])

    for key, value in data.items():
        one = {'text': value, 'callback_data': key}
        if len(single_line) < 1:
            single_line.append(one)
        else:
            single_line.append(one)
            tem_data.append(single_line)
            single_line = []
    return tem_data


def redirectToHomePage(message):
    user_id = message['from']['id']
    bot_request("sendMessage", {
        "chat_id": user_id,
        'text': translate(message=message, text="quyidagilardan birini tanleng"),
        "reply_markup": json.dumps({
            "keyboard": [
                [
                    translate(message=message, text="tarjimani boshlash"),
                    translate(message=message, text='setting')
                ], [
                    translate(message=message, text='biz haqimizda')
                ]
            ],
            'resize_keyboard': True
        })
    })
