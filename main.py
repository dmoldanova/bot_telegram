from flask import Flask, request
from flask_sslify import SSLify
import telebot
import requests
import json
import config

app = Flask(__name__)
sslify = SSLify(app)

bot = telebot.TeleBot(config.TOKEN)

#text_lower = '79215662404'
#url = 'https://api.bmi.io/voip/v1/call?login={}&password={}&from={}&to={}'.format(config.login, config.pw, config.domen, text_lower)
#print(url)

# список user
users = {}
URL = 'https://api.telegram.org/bot{}'.format(config.TOKEN)

# список привествий
greeating = ['привет','добрый день','добрый вчер','здравствуйте']
num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# доплнительные функции!!
def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return

def check_number_phone(text):
    text_len = len(text)
    #print(text_len, ', ', text)
    if text_len != 11:
        return False
    else:
        i = 0
        sum = 0
        while i != text_len:
            #print(text[i])
            #print(str(text[i]) in num)
            if (str(text[i]) in num) == False:
                return False
            i += 1
        return True


# /start
def handler_start(id):
    text = 'Привет. Начнем наше общение!\nДля начала давай поприветствуем друг друг.'
    bot.send_message(id, text)

    if not (id == users):
        users[id] = {'number_mobile': 'no', 'level': '0'}
    users[id]['number_mobile'] = 'no'
    users[id]['level'] = '0'

    return


# /help
def handler_help(id):
    text = 'Функций у меня пока мало.\nДавай просто начнем общение:) Ты можешь оставить свой номер телефона\n и оператор ' \
           'с тобой в ближайшее время\nс тобой свяжется'
    bot.send_message(id, text)

    return

# обработчик вопросов
def handler_question(id, text):
    text_lower = str(text).lower()

    print('handler_question()')

    if users[id]['level'] == '0':
        if (text_lower in greeating) == False:
            text = 'Для начала давай поприветствуем друг друга!'
            bot.send_message(id, text)
            users[id]['level'] = '0'
        else:
            text = 'Привет! Данный бот предназначен для сбора контактной информации.\nОставь свой номер телефона ' \
                   'и в ближайшее время наш оператор с Вами свяжется!\n' \
                   'Основные правила ввода номера телефона:\n' \
                   '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                   '\n3. В номере телефона должны быть только цифры.'
            bot.send_message(id, text)
            users[id]['level'] = '1'
    elif users[id]['level'] == '1' or users[id]['level'] == '2':
        if text[0] != 8 and len(text) == 10:
            text = 'Номер телефона должен начинаться с 8! Еще раз скажу правила ввода номера:\n' \
                   '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                   '\n3. В номере телефона должны быть только цифры.'
            bot.send_message(id, text)
        elif len(text_lower) != 11:
            text = 'Данный бот предназначен для сбора контактной информации.\nПомощь в написании номера телефона:\n1. ' \
                   'Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                   '\n3. В номере телефона должны быть только цифры.'
            bot.send_message(id, text)
        else:
            if text_lower[0] != '7':
                text = 'Номер телефона должен начинаться с 7! Еще раз скажу правила ввода номера:\n' \
                       '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                       '\n3. В номере телефона должны быть только цифры.'
                bot.send_message(id, text)
            elif check_number_phone(text_lower) == False:
                text = 'В номере должны присутствовать только цифры. Еще раз скажу правила ввода номера:\n' \
                       '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 7.' \
                       '\n3. В номере телефона должны быть только цифры.'
                bot.send_message(id, text)
            else:
                if users[id]['number_mobile'] == 'no':
                    users[id]['number_mobile'] = text_lower
                    text = 'Ваш номер {} попал в базу. Ждите звонка от нашего оператора!'.format(text)
                    bot.send_message(id, text)
                    users[id]['level'] = '2'
                    url = 'https://api.sip7.net/cm/v2/quickcall?login={}&password={}&from={}&to={}'.format(config.login, config.pw, config.domen, text_lower)
                    #r = requests.post(url)
                    #print(r)
                else:
                    text = 'Ваш номер телефона поменялся на - {}'.format(text_lower)
                    users[id]['number_mobile'] = text_lower
                    bot.send_message(id, text)
                    users[id]['level'] = '2'
                    url = 'https://api.sip7.net/cm/v2/quickcall?login={}&password={}&from={}&to={}'.format(config.login, config.pw, config.domen, text_lower)
                    #r = requests.post(url)
                    #print(r)
    return


# обработчик всех функций
def handler_funk(r):
    text = r['message']['text']
    id = r['message']['chat']['id']

    if text == '/start':
        handler_start(id)
    elif text == '/help':
        handler_help(id)
    else:
        handler_question(id, text)

    return

@app.route('/', methods=['POST','GET'])
def index():
    print(request.method, ':')
    if request.method == 'POST':
        r = request.get_json()
        config.num += 1
        print('--- to (', config.num, ') ---')
        print('chat_id: ', r['message']['chat']['id'])
        print('text: ', r['message']['text'])
        print('-------------------------')
        handler_funk(r)
        write_json(r)
    return '<h1> Bot welcomes you! </h1>'

def main():
    pass

if __name__ == '__main__':
    app.run()
