import json
import os
import argparse

# オプション引数の定義
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="Filename", required=True)
parser.add_argument("-s", "--save", help="saveFilename", type=str)

# オプション引数の取り出し
args = parser.parse_args()

# 指定されたファイルをjson形式で読み込み
with open(args.file, "r") as f:
    rowRecodes = json.load(f)

# ファイルに保存されている全ての信号を16進数に変換する
for key in rowRecodes.keys():
    interval = rowRecodes[key]

    # 信号間隔を読み取って2進数に変換(AEHAフォーマット)
    t = 0.0
    binCode = []
    for i in range(0, len(interval)-1, 2):
        if t * 7.0 < interval[i]:
            t = (interval[i] + interval[i+1]) / 12.0
            binCode.append("")
        elif interval[i+1] < t * 2.0:
            binCode[-1] += "0"
        elif interval[i+1] < t * 6.0:
            binCode[-1] += "1"
    
    # 16進数に変換
    hexCode = ""
    for c in binCode:
        hexCode += format(int(c, 2), "x")
        
    print(key + " : " + hexCode)
    # ファイルがない場合 空のjsonファイルを作成
    if not os.path.isfile(args.save): 
        with open(args.save, "w") as s:
            s.write("{}")

    # ファイルが空の場合 空のjsonファイルを作成
    with open(args.save, "r") as s:
        if len(s.read()) == 0:
            s.write("{}")

    # -s で指定されたファイルに書き込み
    with open(args.save, "r") as s:
        hexRecodes = json.load(s)
    with open(args.save, "w") as s:
        hexRecodes[key] = hexCode
        s.write(json.dumps(hexRecodes))