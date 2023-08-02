### Торговый бот

```shell
Цель проекта: создать бота, который будет торговать зависимости от объема и ATR, а так же уведомлять о крупных объемах зависимости от времени.
```

==========================================================================

## Установка
1) Самый простой способ:
```shell
git clone https://github.com/s9515411757/todo.git
```

2) Или через PyCharm:
- нажмите на кнопку **Get from VCS**:
![alt text]([https://raw.githubusercontent.com/WISEPLAT/imgs_for_repos/master/get_from_vcs.jpg ](https://github.com/s9515411757/trading_bot.git))

Вот ссылка на этот проект:
```shell
https://github.com/s9515411757/kline.git
```
3) В PyCharm по умолчанию создается виртуальное окружение, если оно у вас не создалось, то следует воспользоваться командой для Windows:
```shell
python3 -m venv venv
или
python -m venv venv 
```
Если вы хотите использовать в работе определённую версию Python, добавьте к команде создания виртуального окружения номер этой версии. Пример:
```shell
python3.8 -m venv venv
```
4) Запускаем виртуальное окружение. Если venv вашего проекта деактивировано, активируйте его, введите команду:
```shell
# Для Windows:
source venv/Scripts/activate
или
venv/Scripts/activate

# Для Linux и macOS:
source venv/bin/activate 
```

5) Устанавливаем библиотеки, перед установкой следует обновить PIP:
```shell
python.exe -m pip install --upgrade pip

pip install -r requirements.txt
```
==========================================================================

## Python версия 3.7-3.9
Библиотеки:
```shell
requests==2.31.0
websocket-client==1.6.1
websockets==11.0.3
```
==========================================================================

## Настройка ботом происходит через терминал
![alt text](https://github.com/s9515411757/trading_bot/blob/main/1.png)

## Уведомления ATR
![alt text](https://github.com/s9515411757/trading_bot/blob/main/2.png)
