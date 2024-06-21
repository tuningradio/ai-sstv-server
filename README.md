# ai-sstv-server.py ver1.0.0(W) by Tuningradio & Microsoft Copilot 2024.06.18

 音声で送って欲しい画像プロンプトを話すと、SSTV信号で返す。

 処理ステップ：  
 1)オーディオ入出力デバイスの指定(表示されるデバイス名の先頭の番号を入力して決定する)  
 2)音声入力→google recognizerでテキスト化する。  
 3)テキストデータを googletransで英訳(Stable Diffusionが日本語をほとんど理解できないため)  
 4)英訳したテキストをローカルのStable Diffusion APIに渡して画像生成する。  
 5)生成された画像ファイルを サブスクリプトsstvtool.pyに渡してSSTV信号にする。(このサブスクリプトのパラメーター指定でストリーミング(-s) or 音声ファイルセーブ(-o) の選択可能)  
 
 起動パラメーター：  
 1)-c はCOMポートのDTRコントロール。-c COM7 と付けると送信時にCOM7のDTRをONにする。つけないと何もしない。  
 2)-t を付けると、SSTV信号処理のサブスクリプトsstvtool.pyの実行をスキップする。各google serviceやStable Diffusionとの通信試験時に使う。  
 3)-h でusageを表示する。  

