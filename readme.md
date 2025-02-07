# config_file_editor

## 概要
`Jw_win.jwf`を良い感じに編集する

## 必要なもの
- python3.12.3以降(3.12.3にて検証済み)
- `jw_win`が必要(通常はないパターンではあるが、`jw_win`そのものはなくても`jw_win.exe`という名前のファイルがあれば動く)

## 使い方
細かいことは[tsukaikata.md](tsukaikata.md)に記載
- `config_file_editor.py`をダブルクリックする。
- `C:\JWW`に既存の`Jw_win.jwf`がある場合、何も設定しなくてもしなくても`Jw_win.jwf`が本ソフトに読み込まれる。
    - インストール先が異なる場合は`指定フォルダを変更する`ボタンを押して変更する。
    - `Jw_win.jwf`がない場合は、`jw_win.exe`の機能で環境設定ファイルを書き出すか、本ソフト`空のJw_win.jwf`ボタンで作成するなどする。
- ボタンとか表を右クリックとかすると各種機能が動いたりする。

## 機能
- GUIによる`Jw_win.jwf`の編集(外部変形コマンド行の追加・キー行の追加・キーマップ変更)
- `Jw_win.jwf`のコマンド行の重複チェック(関連する行のみ)
- `Jw_win.jwf`の行のソート(関連する行のみ)
- など

## config_file_editor.bat
config_file_editor.py自身を登録するためだけの外部変形ファイル

## 注意
- 本ソフトによって`Jw_win.jwf`が書き換えられるたびに`backup\auto\`に書き換えられる前の`Jw_win.jwf`がコピーされる。コピーは、コピー数や期間の制限なく増えるため、 **適宜手動削除** する(莫大な容量になるほど`Jw_win.jwf`を書き換えることもないと判断している)。
- パスにおける大文字小文字の扱いは以下を参照 [learn.microsoft.com「大文字と小文字の区別を調整する」](https://learn.microsoft.com/ja-jp/windows/wsl/case-sensitivity)
- 外部変形の登録の基本については`Jw_win`本体の同梱サンプルや各種解説ウェブページ、または拙ページを参照 [外部変形をショートカット登録するやり方のメモ](https://github.com/yy-mitsumura/yy-mitsumura.github.io/blob/main/gaihen_syotoka.md)

## リンク
jw_cad本家様: [jw_cad](https://www.jwcad.net/index.htm)
