import discord
import re 
import subprocess
import sqlite3
import encode

connect = sqlite3.connect('db.sqlite3')
cursor  = connect.cursor()

cursor.execute("SELECT token from token")
TOKEN=str(cursor.fetchall()[0][0])
client = discord.Client()

def dbUpdate(column, state):
    """
    データベースの内容を更新する

    Parameters
    ----------
    column : str
        変更するカラム
    state : int or str
        セットする値
    """
    if column == 'light':
        cursor.execute("UPDATE user_data SET light = ?", (state,))
    elif column == 'aircon_temp':
        cursor.execute("UPDATE user_data SET aircon_temp = ?", (state,))
    elif column == 'aircon_mode':
        cursor.execute("UPDATE user_data SET aircon_mode = ?", (state,))

    connect.commit()

def getState():
    """
    エアコンの運転モードと設定温度を取得する

    Returns
    ----------
    state : list[str, int]
        エアコンの運転モードと設定温度
    """
    cursor.execute("SELECT aircon_mode, aircon_temp FROM user_data")
    return list(cursor.fetchall()[0])

def lightON():
    proc = subprocess.run(["python3", "./irrp.py", "-p", "-g17", "-f", "./codes", "light:on"])

def lightOFF():
    proc = subprocess.run(["python3", "./irrp.py", "-p", "-g17", "-f", "./codes", "light:off"])

def airconOP(state):
    encode.encode(state[0], state[1])
    proc = subprocess.run(["python3", "./irrp.py", "-p", "-g17", "-f", "./aircon", "aircon:op"])

@client.event
async def on_message(message):
    message.content = str(message.content).replace(' ', '')

    if not re.match(r'$', message.content) is None:
        pass
    elif not re.search(r'電気\S*つけて', message.content) is None:
        lightON()
        dbUpdate('light', 1)
    elif not re.search(r'電気\S*消して', message.content) is None:
        lightOFF()
        dbUpdate('light', 0)
    elif not re.search(r'エアコン\S*つけて', message.content) is None:
        airconOP(['off', 27])
        state = getState()
        airconOP(state)
        dbUpdate('aircon_mode', state[0])
    elif not re.search(r'エアコン\S*消して', message.content) is None:
        temp = getState()[1]
        airconOP(['off', temp])
        dbUpdate('aircon_mode', 'off')
    elif not re.search(r'エアコン\S*冷房', message.content) is None:
        airconOP(['cool', 27])
        dbUpdate('aircon_mode', 'cool')
        dbUpdate('aircon_temp', 27)
    elif not re.search(r'エアコン\S*暖房', message.content) is None:
        airconOP(['warm', 20])
        dbUpdate('aircon_mode', 'warm')
        dbUpdate('aircon_temp', 20)
    elif not re.search(r'温度\S*下げて', message.content) is None:
        state = getState()
        state[1] -= 1
        airconOP(state)
        dbUpdate('aircon_temp', state[1])
    elif not re.search(r'温度\S*上げて', message.content) is None:
        state = getState()
        state[1] += 1
        airconOP(state)
        dbUpdate('aircon_temp', state[1])
    elif not re.match(r'now', message.content) is None:
        cursor.execute("SELECT * FROM user_data")
        await message.channel.send(str(cursor.fetchall()))

client.run(TOKEN)
