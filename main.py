import os
from pyrogram import Client
import config
import asyncio
from queue import Queue
from pyrogram.utils import ainput

async def save(name_acc, to_top, user_tag, text):
    file_name = f'{name_acc}/{user_tag}/log.txt'
    file_text = ''

    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='UTF-8') as file:
            file_text = file.read()

    with open(file_name, 'w', encoding='utf-8') as file:
        if to_top:
            file.write(f'{text}\n')
            file.write(file_text)

        else:
            file.write(file_text)
            file.write(f'{text}\n')

async def log(app, name_acc, to_top, user_tag, from_user, message, type, date):
    await app.download_media(message=message, file_name=f"{name_acc}/{user_tag}/{type}/{from_user} {date}.{'mp3' if type=='voice' else 'jpeg'}")
    
    await save(name_acc, to_top, user_tag, f'{from_user}: {message.text}, // Was send {type} look folder {type}// {date}')

async def write_msg(app, name_acc, user_tag, message, to_top=False):
    date = str(message.date).replace(':', '#')

    from_user_tag = message.from_user.username
    if from_user_tag == None:
        if str(message.from_user.id) == user_tag:
            from_user_tag = str(message.from_user.id)

        else:
            from_user_tag = message.from_user.first_name
    
    # Проверяем какие медиа файлы содержаться в сообщении
    if message.voice:
        await log(app, name_acc, to_top, user_tag, from_user_tag, message, 'voice', date)

    elif message.photo:
        await log(app, name_acc, to_top, user_tag, from_user_tag, message, 'screenshots', date)

    elif message.sticker:
        await save(name_acc, to_top, user_tag, f'{from_user_tag}: Sticker from {message.sticker.set_name}, {message.sticker.emoji} {date}\n')

    elif message.text:
        await save(name_acc, to_top, user_tag, f'{from_user_tag}: {message.text} {date}')
        
    elif message.location:
        await save(name_acc, to_top, user_tag, f"{from_user_tag}: {message.location.longitude}, {message.location.latitude} //Was send location// {date}")
                
    elif message.chat.dc_id == 2:
        await save(name_acc, to_top, user_tag, f'{from_user_tag}:  //There was a telephone conversation// {date}')

def check_dir(name_acc, user_tag):
    # Если нет папки с таким юзером, то создаём
    if not os.path.isdir(f"{name_acc}/{user_tag}"):
        try:
            os.mkdir(f"{name_acc}/{user_tag}")
            os.mkdir(f"{name_acc}/{user_tag}/voice")
            os.mkdir(f"{name_acc}/{user_tag}/screenshots")
        except:
            return True

    return False

# Основная функция
async def main(app, name_acc):
    # Пробегается по всем чатам которые есть у пользователя
    async for dialog in app.get_dialogs():
        # Проверяет личный это чат или нет
        if dialog.chat.first_name and not dialog.top_message.from_user.is_bot:
            name_user = dialog.chat.first_name or dialog.chat.title            

            # Узнаем тэг пользователя
            user_tag = dialog.chat.username
            if user_tag == None:
                user_tag = name_user

            #print(name_acc, name_user)

            if check_dir(name_acc, user_tag):
                user_tag = str(dialog.chat.id)

                check_dir(name_acc, user_tag)

            # Пробегаем по всем сообщениям в чате
            async for message in app.get_chat_history(chat_id=dialog.chat.id):
                await write_msg(app, name_acc, user_tag, message)

class VARS:
    tasks = Queue()
    proxies = []

async def account_task(name_acc, load_cach, proxy, loop):
    if not os.path.isdir(name_acc):
        os.mkdir(name_acc)

    print('Login', name_acc)
    app = Client(name_acc, config.api_id, config.api_hash, proxy=proxy)
    await app.start()
    loop.create_task(VARS.tasks.get())
    
    if load_cach:
        await main(app, name_acc)
        print(name_acc, 'Downloading done')

    @app.on_message()
    async def _(_, message):
        if message.chat.first_name and not message.from_user.is_bot:
            name_user = message.chat.first_name or message.chat.title

            # Узнаем тэг пользователя
            user_tag = message.chat.username
            if user_tag == None:
                user_tag = name_user

            if check_dir(name_acc, user_tag):
                user_tag = str(message.chat.id)

                check_dir(name_acc, user_tag)

            await write_msg(app, name_acc, user_tag, message, True)   

async def wait_new_user(loop):
    while True:
        cmd = await ainput()

        if cmd == 'new':
            if len(VARS.proxies) == 0:
                print('no proxies')
                continue

            loop.create_task(starter(loop))
            return

        else:
            print('Unknown cmd')

async def starter(loop):
    work = True
    while work:
        if len(VARS.proxies) == 0:
            break

        proxy_line = VARS.proxies.pop()

        if proxy_line == '-':
            proxy = None

        else:
            segs = proxy_line.split(':')

            proxy = {
                "scheme": segs[0],  # "socks4", "socks5" and "http" are supported
                "hostname": segs[1],
                "port": int(segs[2]),
                "username": segs[3],
                "password": segs[4]
            }

        for _ in range(config.count_accs_on_proxy):
            name_acc = await ainput('Acc name: ')

            if name_acc == 'exit':
                work = False
                break

            load_srt = await ainput('Download messages? (y/n): ')

            VARS.tasks.put(account_task(name_acc, load_srt=='y', proxy, loop))
        
    if work:    
        print('Proxies end')

    VARS.tasks.put(wait_new_user(loop))
    loop.create_task(VARS.tasks.get())


if __name__ == '__main__':
    with open('proxies.txt', 'r', encoding='UTF-8') as file:
        VARS.proxies = file.read().replace('\r', '').split('\n')
    
    loop = asyncio.new_event_loop()  
    loop.create_task(starter(loop))
    loop.run_forever()