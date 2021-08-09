import os 
import json

base = "4a75c358a76f907f80ff00b748ef10fd02de21"
modeNum = {"off": 18, "auto" : 25, "cool" : 26, "dry" : 27, "clean" : 28, "warm" : 29}
pulse = [[400, 400], [400, 1200]]

def conv_temp_to_hexcode(T):
    """
    設定温度を16進制御コードに変換する

    Parameters
    ----------
    T : int
        エアコンの設定温度

    Returns
    -------
    (signal1, signal2) : tuple(str,str)
        設定温度の16進制御コード
        singal2 は singal1 の補ビット
    """
    bincode = str(bin(32 - T)) # bincode = "0bxxxx"

    # 4bitに整形
    while len(bincode) < 6:
        bincode = bincode[:2] + '0' + bincode[2:]

    signal_1 = bincode[2:6] # bit部だけ取り出す
    signal_1 = (signal_1)[::-1] # reverse
    signal_2 = signal_1.translate(str.maketrans({'0': '1', '1':'0'})) # bit 反転
    signal_1 = format(int(signal_1, 2), 'x')
    signal_2 = format(int(signal_2, 2), 'x')

    return signal_1, signal_2

def conv_mode_to_hexcode(mode):
    """
    エアコンの運転モード(冷房,暖房 etc.)を16進制御コードに変換する

    Parameters
    ----------
    mode : string
        エアコンの運転モード

    Returns
    -------
    signal : str
        運転モードの16進制御コード
    """
    global modeNum
    signal = conv_temp_to_hexcode(modeNum[mode])
    return signal

def gen_code(mode, T):
    """
    エアコンの16進制御コード全体を生成する

    Parameters
    ----------
    mode : string
        エアコンの運転モード
    T : int
        エアコンの設定温度

    Returns
    -------
    hexCode : str
        エアコンの16進制御コード
    """
    global base

    # mode部を書き換え
    tmp = conv_mode_to_hexcode(mode)
    print("mode: " + tmp[0] + "f" + tmp[1] + "0")
    base = base[:10] + tmp[0] + base[11:] # 10文字目をtmp[0]でreplace
    base = base[:12] + tmp[1] + base[13:]

    # 温度部を書き換え
    tmp = conv_temp_to_hexcode(T)
    print("temp: " + tmp[0] + "f" + tmp[1] + "0")
    base = base[:14] + tmp[0] + base[15:]
    base = base[:16] + tmp[1] + base[17:]

    hexCode = base
    print("hexCode: " + hexCode)
    return hexCode

def encode(mode, T):
    """
    エアコンの16進制御コードを赤外線LEDの点灯間隔に変換する

    Parameters
    ----------
    mode : string
        エアコンの運転モード
    T : int
        エアコンの設定温度

    Returns
    -------
    None

    Note 
    -------
    赤外線LEDの点灯間隔は同ディレクトリのairconに書き込まれる
    """
    global pulse

    hexcode = gen_code(mode, T)
    signal = [3200, 1600]

    # 2進変換
    bincode = ""
    for hx in hexcode:
        code = str(bin(int(hx, 16)))
        while len(code) < 6:
            code = code[:2] + '0' + code[2:]
        code = code[2:6]
        bincode += code
    
    # 2進 -> 点灯間隔
    sig = [pulse[int(bit)][i] for bit in bincode for i in range(0,2)]
    signal.extend(sig)
    signal.append(400)
    #print(signal)

    # ファイルがない場合 空のjsonファイルを作成
    if not os.path.isfile("aircon"): 
        with open("aircon", "w") as s:
            s.write("{}")
    # ファイルが空の場合 空のjsonファイルを作成
    with open("aircon", "r") as s:
        if len(s.read()) == 0:
            s.write("{}")
    # -s で指定されたファイルに書き込み
    with open("aircon", "r") as s:
        Recode = json.load(s)
    with open("aircon", "w") as s:
        Recode["aircon:op"] = signal
        s.write(json.dumps(Recode))

if __name__ == '__main__':
    mode = input()
    T    = int(input())

    encode(mode, T)
