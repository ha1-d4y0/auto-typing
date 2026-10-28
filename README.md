# benesse AutoTyping project
[benesse typing](https://manabi-gakushu.benesse.ne.jp/gakushu/typing/nihongonyuryoku.html)用のOCR、またはDOM要素からテキストを取得し、自動でタイピングするスクリプトです。

## 確認動作環境

* Windows 11
* Python 3.14.x 以降
* ([Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki))

## 構成ファイル

* `benesseDOM.py` : Windows用のメイン処理スクリプト
* `benesseWin.py` : 古い方式のWindows用のメイン処理スクリプト
* `requirementsDOM.txt` : benesseDOM.py用の依存するPythonライブラリの一覧
* `requirementsWin.txt` : benesseWin.py用の依存するPythonライブラリの一覧
* `setupDOM.bat` : benesseDOM.py用の環境構築および実行用バッチファイル
* `setupWin.bat` : benesseWin.py用の環境構築および実行用バッチファイル
* `README.md` : 本ファイル

## セットアップと実行手順

1. 環境に合わせたバッチファイル、またはシェルスクリプトを右クリックし、管理者として実行する。
2. 自動で以下が処理されます：
   * `python`の確認
   * `pip`の更新
   * `pip`による依存ライブラリの一覧インストール
   * (`setupWin.bat`の場合、`winget`によるTesseractOCRのインストール)
3. インストール完了後、画面の案内に従って`Y`を入力すると、自動でPythonファイルが実行されます。
