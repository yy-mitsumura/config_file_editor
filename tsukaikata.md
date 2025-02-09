# 使い方
## 概要
ちょっとだけ使い方の補足

## 自動生成されるもの
### config.json
- カレントディレクトリに`config.json`がない時に生成される。
- `config.json`は`Label`「Jw_win.exeのインストール先フォルダ」(`指定フォルダを変更する`ボタンで選ばれるディレクトリ)の隣にある、黄色背景の`Label`に記載のパスを保存している。また、`config.json`は`Jw_win.jwfの更新時にソートを行う(切り替えるとJw_win.jwfの再読み込みもします)`ボタンのチェック状態も保存している。
### backup manual auto 各ディレクトリ
- 1度でもバックアップが行われたら以下の3つのディレクトリが生成される
    - `backup\`
    - `backup\manual\`
    - `backup\auto\`
### JWC_TEMP.TXT
- **本ソフトによる自動生成で作られる訳ではない** が、記述する。
- `jw_win.exe`から外部変形として`config_file_editor.bat`を実行すると、生成される。

## バックアップ
手動と自動がある
- 手動
    - `現時点のJw_win.jwfをバックアップする`ボタンをおしたときにバックアップ
    - バックアップ先: `backup\manual\`
- 自動
    - `Jw_win.jwf`に変更があるときにバックアップ(変更直前の状態をバックアップ)
    - バックアップ先: `backup\auto\`


## ソート
- `Jw_win.jwfの更新時にソートを行う(切り替えるとJw_win.jwfの再読み込みもします)`ボタンにチェックが入っている場合は、`Jw_win.jwf`更新時に自動でソートを行う。同ボタンクリック時はソートを行わない。
- `直ちにソートを行う`ボタンを押した時もソートを行う。
- ソート以下のように行う。GCOM行やKEY行前後の行にコメント行がある場合は注意。
```
無関係な行
GCOM行
アルファベットのキー行(KEY_Aなど)
ファンクションキーのキー行(KEYF2など)
スペースキー行
KEY76行
END
```
## GCOM行のツリー
### 編集
- 編集は後述通りコンテキストメニューから行う
- 編集時に、編集後のコマンド名に、使用できない文字`*?"<>|,`のいずれかが含まれている場合、その部分を`_`で置き換えるかどうかアラートする
### コンテキストメニュー
- 行を左クリックで選んだあと右クリックでコンテキストメニューを表示する。コンテキストメニューから編集や割り当てを変更できる。
### 非表示行
- GCOM行内に`*?"<>|`のいずれか、または`,`が規定数より多い場合、その行は非表示となる。
- 非表示になった行はGCOM行ツリーの下(KEY行ツリーの上)の辺りに非表示の旨が表示される。
- 非表示になった行の編集は **ファイルを直接編集** して、適切な状態にする。GUIからは行えない。
## KEY行のツリー
### コンテキストメニュー
- 行を左クリックで選んだあと右クリックでコンテキストメニューを表示する。コンテキストメニューから割り当てを変更できる。
### ソート機能
- `キー`列のラベル`キー`を押すと、同列を独自のソートする
     - 独自のソートとは`_`を英数字より前に持ってくるソートを指す
- `通常`及び`shift時`列もラベルクリックでそれぞれの列を一般的なソートをする
