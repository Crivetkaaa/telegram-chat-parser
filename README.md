# telegram-chat-parser
Парсер всех сообщений из телеграма
Нужен user-bot, который парсит все переписки в лс [игнорируя группы/чаты] и создает отдельную папку с каждым человеком с его логом переписки.
Пример лога
@user1 - Hello 23:43 24.02.2023
@user2[user-bot] - Здравствуйте 23:43 24.02.2023

Формат лога: Лог должен быть в формате log.txt

Пример сохранения:  создаётся отдельная папка с именем @user [ тег пользователя, на которого стоит бот] внутри папки с логами название папки переписки  @user[с кем переписка].

Дополнение к тз
Ещё нужно, чтобы он скачивал скриншоты и голосовые сообщения и сохранял их в отдельных папках в папке переписки с отдельными подпапками от кого с указанием @user. 


Screnshoots @user1 - скриншоты
Voice @user1 - голосовые сообщения

Screnshoots @user2 - скриншоты
Voice @user2 - голосовые сообщения


Проект перенесён из репозитория организации поэтому всего 1 коммит
