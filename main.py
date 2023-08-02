import json
import hmac
import logging
import requests
import time
import datetime as dt
import websocket
import threading
import datetime as dat
import settings

from datetime import datetime

CHAT_ID = settings.CHAT_ID
BYBIT_API_KEY = settings.BYBIT_API_KEY
BYBIT_API_SECRET = settings.BYBIT_API_SECRET


logging.basicConfig(filename='logfile_wrapper.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

TORGI = {
    'Цена покупки': 0,
    'Цена продажи': 0,
    'Сделка на покупку': False,
    'Кол-во акций': 0,
    'Плечо': 0.1,
    'Депозит': 1000,
    'Процент сделки': 10,
    'Мы в сделке': False,
    'Сколько раз проиграли': 0,
    'Сколько раз выиграли': 0,
    'Сколько процентов вышли': 3,
    'Процент стоп-лост': 1,
    'Логика игры': 0
}

TORGI_ATR = {
    'Цена покупки': 0,
    'Цена продажи': 0,
    'Сделка на покупку': False,
    'Кол-во акций': 0,
    'Плечо': 0.1,
    'Депозит': 1000,
    'Мы в сделке': False,
    'Сколько раз проиграли': 0,
    'Сколько раз выиграли': 0,
    'Процент сделки': 75,
    'ATR на покупку': 0,
    'ATR на продажу': 0,
    'ATR': 0
}


usdt = str(input('Введи валюту на примере MAGICUSDT: '))
flag_allert_value = int(input('0 - Нет, 1 - Да. Уведомлять по объему?: '))
if flag_allert_value == 1:
    trigger = float(input('Введи объем от которого будет уведомление: '))
else:
    trigger = 100

flag_allert = int(input('0 - Нет, 1 - Да. Уведомление на каждый час по суммарному объему: '))
flag_allert_atr = int(input('0 - Нет, 1 - Да. Включаем АТР: '))
if flag_allert_atr == 1:
    day = int(input('Введи сколько дней отсчитываем ATR: '))
else:
    day = 1
flag_bot = int(input('0 - Нет, 1 - Да. Включаем торговлю ботом по объемам?: '))
if flag_bot == 1:
    TORGI['Логика игры'] = int(input('0 - Прошла крупная заявка и мы идём вместе с ней, 1 - Прошла крупная заявка и мы идём против неё. Какую торговую логику выбираем?: '))
    trigger_bot = float(input('Введи объем от которого торгует бот: '))
    TORGI['Плечо'] = float(input('Введи какое плечо (0.1 - это 10%): '))
    TORGI['Депозит'] = float(input('Введи какой деползит (Например 1000 - это 1000$): '))
else:
    trigger_bot = 100

flag_bot_atr = int(input('0 - Нет, 1 - Да. Включаем торговлю ботом по ATR?: '))
if flag_bot_atr == 1:
    TORGI_ATR['Логика игры'] = int(input('0 - Если ATR  внизу, то покупаем, 1 - Если ATR  внизу, то продаём?: '))
    TORGI_ATR['Процент сделки'] = int(input('На какой процент ATR покупаем/продаем? (Пример  75): '))
    day_bot = int(input('Введи сколько дней отсчитываем ATR для торговли: '))
    TORGI_ATR['Плечо'] = float(input('Введи какое плечо (0.1 - это 10%): '))
    TORGI_ATR['Депозит'] = float(input('Введи какой деползит (Например 1000 - это 1000$): '))
else:
    trigger_bot_atr = 100


topic = f"publicTrade.{usdt}"


expires = int((time.time() + 1) * 1000)

signature = str(hmac.new(
    bytes(BYBIT_API_SECRET, "utf-8"),
    bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256"
).hexdigest())

param = "api_key={api_key}&expires={expires}&signature={signature}".format(
    api_key=BYBIT_API_KEY,
    expires=expires,
    signature=signature
)


def push(text):
    print(f'Уведомление в тг: {text}')
    request = requests.post(
        url='https://api.telegram.org/bot5176992957:AAE6oX7SdfJxGULiO9MS1uEpbviTmLyXxvg/sendmessage',
        data={'chat_id': CHAT_ID, 'text': str(text)}
    )
    if request.status_code != 200:
        print('Error: %s' % request.status_code)


c = True
INFO = {
    'покупка': 0,
    'продажа': 0,
    'день покупка': 0,
    'день продажа': 0,
}


# S Покупка/продажа
# s Валюта
# v объем
# p Цена
def kline_bot():
    #нтервал Клайна. 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, M, W
    end_ds = int(time.time()*1000)
    start_ds = end_ds - 86400000 * (day_bot + 1)

    url = 'https://api.bybit.com'
    path = '/v5/market/kline'
    URL = url + path
    r = []
    params = {
        'category': 'linear',
        'symbol': usdt,
        'interval': 'D',
        'start': start_ds,
        'end': end_ds,
    }
    f = requests.get(URL, params=params).json().get('result').get('list')
    count = 0
    open_price = 0
    for i in f:
        if count != 0:
            r.append([i[1], i[4]])
        else:
            open_price = float(i[1])
        count += 1

    _list = []
    for i in r:
        result = float(i[0]) - float(i[1])
        if result > 0:
            _list.append(result)
        else:
            _list.append(result * (-1))

    sred = sum(_list) / len(_list)
    new = []
    new1 = []
    for i in _list:
        if i >= sred * 2 or i <= sred / 3:
            new.append(i)
        else:
            new1.append(i)
    if new:
        new_sred = sum(new) / len(new)
    else:
        new_sred = sum(new1) / len(new1)

    TORGI_ATR['ATR на покупку'] = round(open_price + new_sred, 7)
    TORGI_ATR['ATR на продажу'] = round(open_price - new_sred, 7)
    TORGI_ATR['ATR'] = round(new_sred, 7)
    TORGI_ATR['ATR открытая свеча'] = open_price
    push(f'ATR для бота: {str(round(new_sred, 7))}, монеты: {usdt}, дни: {str(day)} \n\nМаксимальный ATR: {str(round(open_price + new_sred, 7))}\nМинимальный ATR: {str(round(open_price - new_sred, 7))}')


def kline():
    #нтервал Клайна. 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, M, W
    end_ds = int(time.time()*1000)
    start_ds = end_ds - 86400000 * (day + 1)

    url = 'https://api.bybit.com'
    path = '/v5/market/kline'
    URL = url + path
    r = []
    params = {
        'category': 'linear',
        'symbol': usdt,
        'interval': 'D',
        'start': start_ds,
        'end': end_ds,
    }
    f = requests.get(URL, params=params).json().get('result').get('list')
    count = 0
    open_price = 0
    for i in f:
        if count != 0:
            r.append([i[1], i[4]])
        else:
            open_price = float(i[1])
        count += 1
    _list = []
    for i in r:
        result = float(i[0]) - float(i[1])
        if result > 0:
            _list.append(result)
        else:
            _list.append(result * (-1))

    sred = sum(_list) / len(_list)
    new = []
    new1 = []
    for i in _list:
        if i >= sred * 2 or i <= sred / 3:
            new.append(i)
        else:
            new1.append(i)
    if new:
        new_sred = sum(new) / len(new)
    else:
        new_sred = sum(new1) / len(new1)
    push(f'ATR: {str(round(new_sred, 7))}, монеты: {usdt}, дни: {str(day)} \n\nМаксимальный ATR: {str(round(open_price + new_sred, 7))}\nМинимальный ATR: {str(round(open_price - new_sred, 7))}')


def torgi(S, p, v):
    if TORGI['Мы в сделке']:
        if TORGI['Сделка на покупку']:
            if float(p) >= TORGI['Цена покупки'] + (TORGI['Цена покупки'] * (TORGI['Сколько процентов вышли'] / 100)):
                TORGI['Сколько раз выиграли'] += 1
                TORGI['Цена продажи'] = float(p)
                PRIBL = (TORGI['Цена продажи'] - TORGI['Цена покупки']) * TORGI['Кол-во акций']
                TORGI['Депозит'] += PRIBL
                push(f"✅ Прибыль: {PRIBL} Депозит: {TORGI['Депозит']}\nСделка в выирыше, мы зашли по цене {TORGI['Цена покупки']}\nцена продажи: {TORGI['Цена продажи']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}")
                TORGI['Цена продажи'] = 0
                TORGI['Цена покупки'] = 0
                TORGI['Кол-во акций'] = 0
                TORGI['Сделка на покупку'] = False
                TORGI['Мы в сделке'] = False
            if float(p) <= TORGI['Цена покупки'] - (TORGI['Цена покупки'] * (TORGI['Процент стоп-лост']/100)):
                TORGI['Сколько раз проиграли'] += 1
                TORGI['Цена продажи'] = float(p)
                PRIBL = (TORGI['Цена продажи'] - TORGI['Цена покупки']) * TORGI['Кол-во акций']
                TORGI['Депозит'] += PRIBL
                push(f"❌ Проигрыш: {PRIBL} Депозит: {TORGI['Депозит']}\nцена покупки: {TORGI['Цена покупки']}\nцена продажи: {TORGI['Цена продажи']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}")
                TORGI['Цена продажи'] = 0
                TORGI['Цена покупки'] = 0
                TORGI['Кол-во акций'] = 0
                TORGI['Сделка на покупку'] = False
                TORGI['Мы в сделке'] = False
        else:
            if float(p) <= TORGI['Цена продажи'] - ( TORGI['Цена продажи'] * (TORGI['Сколько процентов вышли']/100)):
                TORGI['Сколько раз выиграли'] += 1
                TORGI['Цена покупки'] = float(p)
                PRIBL = (TORGI['Цена продажи']-TORGI['Цена покупки']) * TORGI['Кол-во акций']
                TORGI['Депозит'] += PRIBL
                push(
                    f"✅ Прибыль: {PRIBL}\nДепозит: {TORGI['Депозит']}\nСделка в выирыше, мы зашли по цене {TORGI['Цена покупки']}\nцена продажи: {TORGI['Цена продажи']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}")
                TORGI['Цена продажи'] = 0
                TORGI['Цена покупки'] = 0
                TORGI['Кол-во акций'] = 0
                TORGI['Мы в сделке'] = False
            if float(p) >= TORGI['Цена продажи'] + ( TORGI['Цена продажи'] * (TORGI['Процент стоп-лост']/100)) and TORGI['Цена продажи'] != 0:
                TORGI['Сколько раз проиграли'] += 1
                TORGI['Цена покупки'] = float(p)
                PRIBL = (TORGI['Цена покупки'] - TORGI['Цена продажи']) * TORGI['Кол-во акций']
                TORGI['Депозит'] -= PRIBL
                push(
                    f"❌ Проигрыш: {PRIBL}\nДепозит: {TORGI['Депозит']}\nцена покупки: {TORGI['Цена покупки']}\nцена продажи: {TORGI['Цена продажи']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}")
                TORGI['Цена продажи'] = 0
                TORGI['Цена покупки'] = 0
                TORGI['Кол-во акций'] = 0
                TORGI['Мы в сделке'] = False

    else:
        if TORGI['Логика игры'] == 0:
            if float(v) >= trigger_bot:
                if S == '✅ Покупка':
                    TORGI['Мы в сделке'] = True
                    TORGI['Сделка на покупку'] = True
                    TORGI['Цена покупки'] = float(p)
                    TORGI['Кол-во акций'] = float((TORGI['Депозит'] / TORGI['Цена покупки']) * TORGI['Плечо'])*10
                    OPEN = TORGI['Цена покупки'] + (TORGI['Цена покупки'] * (TORGI['Сколько процентов вышли'] / 100))
                    CLOSE = TORGI['Цена покупки'] - (TORGI['Цена покупки'] * (TORGI['Процент стоп-лост']/100))
                    push(
                        f"⬆️ Депозит: {TORGI['Депозит']}\nСделка зашли по цене {TORGI['Цена покупки']}\nцена продажи: {TORGI['Цена продажи']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}\n{OPEN} = {CLOSE}")
                else:
                    TORGI['Мы в сделке'] = True
                    TORGI['Цена продажи'] = float(p)
                    TORGI['Кол-во акций'] = float((TORGI['Депозит'] / TORGI['Цена продажи']) * TORGI['Плечо'])*10
                    OPEN = TORGI['Цена продажи'] - ( TORGI['Цена продажи'] * (TORGI['Сколько процентов вышли']/100))
                    CLOSE = TORGI['Цена продажи'] + ( TORGI['Цена продажи'] * (TORGI['Процент стоп-лост']/100))
                    push(
                        f"⬇️ Депозит: {TORGI['Депозит']}\nСделка зашли на продажу по цене {TORGI['Цена покупки']}\nцена продажи: {TORGI['Цена продажи']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}\n{OPEN} = {CLOSE}")
        else:
            if float(v) >= trigger_bot:
                if S == '❌ Продажа':
                    TORGI['Мы в сделке'] = True
                    TORGI['Сделка на покупку'] = True
                    TORGI['Цена покупки'] = float(p)
                    TORGI['Кол-во акций'] = float((TORGI['Депозит'] / TORGI['Цена покупки']) * TORGI['Плечо']) * 10
                    OPEN = TORGI['Цена покупки'] + (TORGI['Цена покупки'] * (TORGI['Сколько процентов вышли'] / 100))
                    CLOSE = TORGI['Цена покупки'] - (TORGI['Цена покупки'] * (TORGI['Процент стоп-лост']/100))
                    push(
                        f"⬆️ Депозит: {TORGI['Депозит']}\nСделка зашли по цене {TORGI['Цена покупки']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}\n{OPEN} = {CLOSE}")
                else:
                    TORGI['Мы в сделке'] = True
                    TORGI['Цена продажи'] = float(p)
                    TORGI['Кол-во акций'] = float((TORGI['Депозит'] / TORGI['Цена продажи']) * TORGI['Плечо']) * 10
                    OPEN = TORGI['Цена продажи'] - ( TORGI['Цена продажи'] * (TORGI['Сколько процентов вышли']/100))
                    CLOSE = TORGI['Цена продажи'] + ( TORGI['Цена продажи'] * (TORGI['Процент стоп-лост']/100))
                    push(
                        f"⬇️️ Депозит: {TORGI['Депозит']}\nСделка цена продажи: {TORGI['Цена продажи']}\nвалюта: {usdt}\nКол-во акций: {TORGI['Кол-во акций']}\nПлечо: {TORGI['Плечо']}\n{OPEN} = {CLOSE}")


def torgi_ATR(p):
    if TORGI_ATR['Мы в сделке']:
        if TORGI_ATR['Сделка на покупку']:
            if float(p) >= (TORGI_ATR['ATR открытая свеча'] + ((TORGI_ATR['ATR'] * TORGI_ATR['Процент сделки']) / 100)):
                TORGI_ATR['Сколько раз выиграли'] += 1
                TORGI_ATR['Цена продажи'] = float(p)
                PRIBL = (TORGI_ATR['Цена продажи'] - TORGI_ATR['Цена покупки']) * TORGI_ATR['Кол-во акций']
                TORGI_ATR['Депозит'] += PRIBL
                push(f"✅ Прибыль: {PRIBL} Депозит: {TORGI_ATR['Депозит']} | Сделка в выирыше, мы зашли по цене {TORGI_ATR['Цена покупки']}, цена продажи: {TORGI_ATR['Цена продажи']}, валюта: {usdt}, Кол-во акций: {TORGI_ATR['Кол-во акций']}, Плечо: {TORGI_ATR['Плечо']} {TORGI_ATR['Сколько раз выиграли']} = {TORGI_ATR['Сколько раз проиграли']}")
                TORGI_ATR['Цена продажи'] = 0
                TORGI_ATR['Цена покупки'] = 0
                TORGI_ATR['Кол-во акций'] = 0
                TORGI_ATR['Сделка на покупку'] = False
                TORGI_ATR['Мы в сделке'] = False

            if float(p) <= TORGI_ATR['ATR на покупку']:
                TORGI_ATR['Сколько раз проиграли'] += 1
                TORGI_ATR['Цена продажи'] = float(p)
                PRIBL = (TORGI_ATR['Цена продажи'] - TORGI_ATR['Цена покупки']) * TORGI_ATR['Кол-во акций']
                TORGI_ATR['Депозит'] += PRIBL
                push(f"❌ Проигрыш: {PRIBL} Депозит: {TORGI_ATR['Депозит']} | цена покупки: {TORGI_ATR['Цена покупки']}, цена продажи: {TORGI_ATR['Цена продажи']}, валюта: {usdt}, Кол-во акций: {TORGI_ATR['Кол-во акций']}, Плечо: {TORGI_ATR['Плечо']} {TORGI_ATR['Сколько раз выиграли']} = {TORGI_ATR['Сколько раз проиграли']}")
                TORGI_ATR['Цена продажи'] = 0
                TORGI_ATR['Цена покупки'] = 0
                TORGI_ATR['Кол-во акций'] = 0
                TORGI_ATR['Сделка на покупку'] = False
                TORGI_ATR['Мы в сделке'] = False
        else:
            if float(p) <= (TORGI_ATR['ATR открытая свеча'] - ((TORGI_ATR['ATR'] * TORGI_ATR['Процент сделки']) / 100)):
                TORGI_ATR['Сколько раз выиграли'] += 1
                TORGI_ATR['Цена покупки'] = float(p)
                PRIBL = (TORGI_ATR['Цена продажи']-TORGI_ATR['Цена покупки']) * TORGI_ATR['Кол-во акций']
                TORGI_ATR['Депозит'] += PRIBL
                push(
                    f"✅ Прибыль: {PRIBL} Депозит: {TORGI_ATR['Депозит']} | Сделка в выирыше, мы зашли по цене {TORGI_ATR['Цена покупки']}, цена продажи: {TORGI_ATR['Цена продажи']}, валюта: {usdt}, Кол-во акций: {TORGI_ATR['Кол-во акций']}, Плечо: {TORGI_ATR['Плечо']} {TORGI_ATR['Сколько раз выиграли']} = {TORGI_ATR['Сколько раз проиграли']}")
                TORGI_ATR['Цена продажи'] = 0
                TORGI_ATR['Цена покупки'] = 0
                TORGI_ATR['Кол-во акций'] = 0
                TORGI_ATR['Мы в сделке'] = False

            if float(p) >= TORGI_ATR['ATR на продажу']:
                TORGI_ATR['Сколько раз проиграли'] += 1
                TORGI_ATR['Цена покупки'] = float(p)
                PRIBL = (TORGI_ATR['Цена покупки'] - TORGI_ATR['Цена продажи']) * TORGI_ATR['Кол-во акций']
                TORGI_ATR['Депозит'] -= PRIBL
                push(
                    f"❌ Проигрыш: {PRIBL} Депозит: {TORGI_ATR['Депозит']} | цена покупки: {TORGI_ATR['Цена покупки']}, цена продажи: {TORGI_ATR['Цена продажи']}, валюта: {usdt}, Кол-во акций: {TORGI_ATR['Кол-во акций']}, Плечо: {TORGI_ATR['Плечо']} {TORGI_ATR['Сколько раз выиграли']} = {TORGI_ATR['Сколько раз проиграли']}")
                TORGI_ATR['Цена продажи'] = 0
                TORGI_ATR['Цена покупки'] = 0
                TORGI_ATR['Кол-во акций'] = 0
                TORGI_ATR['Мы в сделке'] = False

    else:
        if float(p) <= (TORGI_ATR['ATR открытая свеча'] - ((TORGI_ATR['ATR'] * TORGI_ATR['Процент сделки']) / 100)):
            TORGI_ATR['Мы в сделке'] = True
            TORGI_ATR['Сделка на покупку'] = True
            TORGI_ATR['Цена покупки'] = float(p)
            TORGI_ATR['Кол-во акций'] = float((TORGI_ATR['Депозит'] / TORGI_ATR['Цена покупки']) * TORGI_ATR['Плечо']) * 10
            push(
                f"⬆️ Депозит: {TORGI_ATR['Депозит']} | Сделка зашли по цене {TORGI_ATR['Цена покупки']}, валюта: {usdt}, Кол-во акций: {TORGI_ATR['Кол-во акций']}, Плечо: {TORGI_ATR['Плечо']} {TORGI_ATR['Сколько раз выиграли']} = {TORGI_ATR['Сколько раз проиграли']}")
        if float(p) >= (((TORGI_ATR['ATR'] * TORGI_ATR['Процент сделки']) / 100) + TORGI_ATR['ATR открытая свеча']):
            TORGI_ATR['Мы в сделке'] = True
            TORGI_ATR['Цена продажи'] = float(p)
            TORGI_ATR['Кол-во акций'] = float((TORGI_ATR['Депозит'] / TORGI_ATR['Цена продажи']) * TORGI_ATR['Плечо']) * 10
            push(
                f"⬇️️ Депозит: {TORGI_ATR['Депозит']} | Сделка цена продажи: {TORGI_ATR['Цена продажи']}, валюта: {usdt}, Кол-во акций: {TORGI_ATR['Кол-во акций']} {TORGI_ATR['Сколько раз выиграли']} = {TORGI_ATR['Сколько раз проиграли']}")


def on_message(ws, message):
    global c
    if c:
        push(f'Запущен. Настройки: Валюта - {usdt} | Объем - {trigger}')
        c = False
    message = json.loads(message)
    data = message.get('data')
    if data:
        for i in message['data']:
            T = dt.datetime.fromtimestamp(i['T'] / 1000.0)#Время
            S = i['S']#Покупка/продажа
            s = i['s']#Валюта
            v = i['v']#объем
            p = i['p']#Цена

            if S == 'Buy':
                S = '✅ Покупка'
                if flag_allert_value == 1:
                    INFO['покупка'] += float(v)
                    INFO['день покупка'] += float(v)
            else:
                S = '❌ Продажа'
                if flag_allert_value == 1:
                    INFO['покупка'] += float(v)
                    INFO['день покупка'] += float(v)

            if float(v) >= trigger and flag_allert_value == 1:
                push(f'{T}, {S}, {s}, {v}, {p}  \n')
            if flag_bot == 1:
                torgi(S, p, v)
            if flag_bot_atr == 1:
                torgi_ATR(p)


def on_error(*error):
    print(error)


def on_close(*ws):
    print("### собираюсь закрываться, пожалуйста, не закрывайте ###")


def on_open(ws):
    print('открытый')
    ws.send(json.dumps({"op": "subscribe", "args": [topic]}))


def on_pong(ws, *data):
    print('понг получен')


def on_ping(ws, *data):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("дата и время =", dt_string)
    print('получен пинг')


def info_orders():
    while True:
        s = dat.datetime.now()
        if s.minute == 59 and s.second in (10, 11, 12, 13, 14, 15) and flag_allert_atr == 1:
            push(f"За час на валюте {usdt}: ✅ {str(INFO['покупка'])} | ❌ {str(INFO['продажа'])}")
            INFO['покупка'] = 0
            INFO['продажа'] = 0
            time.sleep(60)
        if s.hour == 23 and s.minute == 10  and s.second in (10, 11, 12, 13, 14, 15):
            push(f"За сутки на валюте {usdt}: ✅ {str(INFO['день покупка'])} | ❌ {str(INFO['день продажа'])}")
            INFO['день покупка'] = 0
            INFO['день продажа'] = 0
            time.sleep(60)
        time.sleep(30)


def connWS():
    ws = websocket.WebSocketApp(
        "wss://stream.bybit.com/v5/public/linear" + "?" + param,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_ping=on_ping,
        on_pong=on_pong,
        on_open=on_open
    )

    ws.run_forever(
        ping_interval=20,
        ping_timeout=10
    )


if __name__ == "__main__":
    # while True:
    #     try:
    #         t1 = threading.Thread(target=info_orders)
    #         t1.start()
    #         if flag_allert_atr == 1:
    #             t2 = threading.Thread(target=kline)
    #             t2.start()
    #         if flag_bot_atr == 1:
    #             t3 = threading.Thread(target=kline_bot)
    #             t3.start()
    #         connWS()
    #     except Exception as ex:
    #         print(ex)
    #     finally:
    #         print(f'💊 перезапуск монеты {usdt}')
    t1 = threading.Thread(target=info_orders)
    t1.start()
    if flag_allert_atr == 1:
        t2 = threading.Thread(target=kline)
        t2.start()
    if flag_bot_atr == 1:
        t3 = threading.Thread(target=kline_bot)
        t3.start()
    connWS()