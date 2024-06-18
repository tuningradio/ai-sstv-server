# ai-sstv-server.py ver1.0.0(W) by Tuningradio & Microsoft Cpilot 2024.06.18

# 音声で送って欲しい画像プロンプトを話すと、SSTV信号で返す。

# 音声→google recognizerでテキスト化

# テキストデータを googletransで英訳(Stable Diffusionが日本語をほとんど理解できないため)

# 英訳したテキストをローカルのStable Diffusion APIに渡して画像生成する。

# 画像ファイルを サブスクリプトsstvtool.pyに渡してSSTV信号にする。(ストリーミングor音声ファイルセーブ可能)

# 起動パラメーター：
# -c はCOMポートのDTRコントロール。-c COM7 と付けると送信時にCOM7のDTRをONにする。つけないと何もしない。

# -t を付けると、SSTV信号処理のサブスクリプトsstvtool.pyをスキップする。googleやLM Studioとの通信試験時に使う。

