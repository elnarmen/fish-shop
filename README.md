# fish-shop
# Телеграм бот, работающий по API CMS от Elastic Path. 
Это MVP версия продукта для демонстрации заказчику. Бот реализован до шага получения заказа и контактов покупателя.
Бот интегрирован с CMS от Moltin (Elastic Path).

![gif](https://dvmn.org/filer/canonical/1569215892/326/)

[Ссылка на работающий бот](https://t.me/elnar_fish_store_bot)

Скачайте код:
```sh
git clone https://github.com/elnarmen/fish-shop.git
```

Перейдите в каталог проекта:
```sh
cd fish-shop
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Рекомендую установить версию Python не ниже 3.10

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`.
Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.

## Установка виртуального окружения и настройка зависимостей
В каталоге `fish-shop/` создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`


Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```
Для работы магазина убедитесь, что у вас пройдены следующие шаги:

1. Получена учетная запись Elastic Path, создан store, если необходимо.
2. Созданы товары и заполнены все обязательные поля.
3. Загружены картинки для товаров и они связаны с товарами.
4. Товары и цены из Price Book связаны через каталог

## Переменные окружения
В каталоге `fish-shop/` создайте файл `.env` для хранения переменных окружения.

Внутри вашего файла `.env` нужно указать следующие настройки:
* `CLIENT_ID`=клиент id от Elastic Path
* `CLIENT_SECRET`=Секретный ключ от Elastic Path
* `TG_TOKEN` - Ваш токен для бота в телеграме
* `REDIS_HOST` - Адрес хоста вашего сервера базы данных Redis
* `REDIS_PORT` - Номер порта сервера базы данных Redis
* `REDIS_PASSWORD` - Пароль для подключения к базе данных Redis

#### CLIENT_ID и CLIENT_SECRET
Секретный ключ и ID клиента можно найти в разделе SYSTEM/Application Keys/Legacy Key

#### TG_TOKEN

* Через поиск телеграм найдите бот @BotFather. 
* Отправьте /start для получения списока всех его команд.
* Выберите команду /newbot - бот попросит придумать имя вашему новому боту. 
* Сохраните полученный токен в переменной `TG_TOKEN`в файле `.env`:

```
TG_TOKEN=<Токен для основного бота>

```

#### REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
Для хранения данных пользователя бот использует базу данных Redis. Для подключения к ней нужно получить адрес базы данных, ее порт и пароль.
Самый легкий способ это сделать - зарегистрировать бесплатную версию на облачной платформе [Redis](https://redis.com/)

Порт часто пишется прямо в адресе, через двоеточие: `redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com:16635`


## Запуск
### Команды для запуска ботов
Телеграм:
```
python tg_bot.py
```

