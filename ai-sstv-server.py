# ai-sstv-server.py ver1.0.0(W) by Tuningradio & Microsoft Cpilot 2024.06.18
# 音声で送って欲しい画像プロンプトを話すと、SSTV信号で返す。
# 音声→google recognizerでテキスト化
# テキストデータを googletransで英訳(Stable Diffusionが日本語をほとんど理解できないため)
# 英訳したテキストをローカルのStable Diffusion APIに渡して画像生成する。
# 画像ファイルを サブスクリプトsstvtool.pyに渡してSSTV信号にする。(ストリーミングor音声ファイルセーブ可能)
# 起動パラメーター：
# -c はCOMポートのDTRコントロール。-c COM7 と付けると送信時にCOM7のDTRをONにする。つけないと何もしない。
# -t を付けると、SSTV信号処理のサブスクリプトsstvtool.pyをスキップする。googleやLM Studioとの通信試験時に使う。

import speech_recognition as sr
import pyaudio
import requests
import base64
import sys
import subprocess
import serial
import argparse
from datetime import datetime, timezone, timedelta
from googletrans import Translator  # googletransライブラリをインポート


# 音声デバイスの一覧表示と選択
def select_audio_device(device_type):
    p = pyaudio.PyAudio()
    print(f"\n\n{datetime.now(timezone(timedelta(hours=+9))).isoformat()} Available {device_type} devices:")
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if (device_type == 'input' and device_info['maxInputChannels'] > 0) or \
           (device_type == 'output' and device_info['maxOutputChannels'] > 0):
            print(i, device_info['name'])
    device = int(input(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} Please enter the number of the {device_type} device: "))
    return device

# 音声入力デバイスの選択
input_device_index = select_audio_device('input')

# 音声出力デバイスの選択
output_device_index = select_audio_device('output')

# コマンドライン引数の解析
parser = argparse.ArgumentParser(description="ai-sstv-server.py 1.0.0(W)")
parser.add_argument('-c', '--com', help='DTR制御をしたいCOMポート名')
parser.add_argument('-t', '--test', action='store_true', help='テストモード（SSTV信号変換を実行しない）')
args = parser.parse_args()

# COMポートの設定
com_port = args.com  # 起動パラメータでCOMポートを指定
if com_port:
    ser = serial.Serial(com_port)  # COMポートを開く
    ser.setDTR(False)  # DTRを強制OFFにする（初期化）
else:
    print("COMポートが指定されなかったので、DTR制御をしません。")

# 音声認識オブジェクトの作成
r = sr.Recognizer()


try:
    # マイクから音声を取得し、Ctrl+Cが押されるまでループ
    while True:
        with sr.Microphone(device_index=input_device_index) as source:
            print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} 音声を入力してください:")
            audio = r.listen(source)

            try:
                # Googleの音声認識APIを使用して音声をテキストに変換
                text = r.recognize_google(audio, language="ja-JP")
                print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} テキスト: ", text)

                # テキストを英語に翻訳
                translator = Translator()
                translated_text = translator.translate(text, dest='en').text
                print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} Translated text: ", translated_text)

                # 翻訳したテキストをprompt.txtに保存
                try:
                    with open('prompt.txt', 'w') as f:
                        f.write(translated_text)
                except IOError as e:
                    print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} ファイルオープンエラー: {e}")

##########
# Stable Diffusionにprompt.txtを渡す
                def read_prompt_file(file_path):
                    encodings = ['utf-8', 'shift_jis', 'utf-16le']
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                return f.read().strip()
                        except UnicodeDecodeError:
                            continue
                    raise ValueError(f"エラー: ファイル '{file_path}' はUTF-8、Shift-JIS、またはUTF-16 LEではありません。")

                # コマンドライン引数の解析
                # parser = argparse.ArgumentParser(description="画像生成とSSTV信号変換スクリプト")
                # parser.add_argument('-t', '--test', action='store_true', help='テストモード（SSTV信号変換を実行しない）')
                # args = parser.parse_args()

                # プロンプトをファイルから読み込む
                prompt_file = "prompt.txt"
                try:
                    prompt = read_prompt_file(prompt_file)
                except FileNotFoundError:
                    print(f"エラー: ファイル '{prompt_file}' が見つかりません。")
                    sys.exit(1)
                except IOError:
                    print(f"エラー: ファイル '{prompt_file}' を開くことができません。")
                    sys.exit(1)
                except ValueError as e:
                    print(str(e))
                    sys.exit(1)

                # APIエンドポイント
                url = "http://"your Stable Diffusion Server address":7860/sdapi/v1/txt2img"

                # リクエストペイロード
                payload = {
                    "prompt": prompt,
                    "steps": 20
                }

                # APIリクエストの送信
                response = requests.post(url, json=payload)

                # レスポンスの確認
                if response.status_code == 200:
                    response_data = response.json()
                    image_data = response_data.get('images', [None])[0]

                    if image_data is not None:
                        # Base64エンコードされた画像データをデコードして保存
                        try:
                            image_bytes = base64.b64decode(image_data)
                            with open("output.png", "wb") as f:
                                f.write(image_bytes)
                            print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} 画像を生成しました。")

# テストモードではない場合のみサブスクリプトを実行
##########
# sstvtool.pyにoutput.pngを渡す。もしCOMポートが指定されていたらDTRをONにする。
                            if not args.test:
                                # ここでDTRをONにする
                                if com_port:
                                    ser.setDTR(True)
                                # 絶対パスを指定
                                sstvtools_path = ".\\sstvtool101.py"
                                result = subprocess.run(["py", sstvtools_path, "-i", "output.png", "-p", "160x120", "-m", "Robot8BW", "-s", "-d", str(output_device_index) ], capture_output=True)
###str(output_device_index)
                                print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} SSTV処理終了")
                                # ここでDTRをOFFにする
                                if com_port:
                                    ser.setDTR(False)
                            else:
                                print("テストモードのため、SSTV信号変換は実行されませんでした。")

                        except Exception as e:
                            print("画像データのデコード中にエラーが発生しました:", str(e))
                    else:
                        print("画像データが含まれていません。")
                else:
                    print("エラーが発生しました:", response.status_code, response.text)

            except sr.UnknownValueError:
                print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} Google音声認識が音声を理解できませんでした")
            except sr.RequestError as e:
                print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} Google音声認識サービスから結果を要求できませんでした; {0}".format(e))
except KeyboardInterrupt:
    # Ctrl+Cが押されたときの処理
    print(f"{datetime.now(timezone(timedelta(hours=+9))).isoformat()} プログラムを終了します...")
    if com_port:
        ser.setDTR(False)  # DTRをOFFにする
        ser.close()  # COMポートを閉じる
