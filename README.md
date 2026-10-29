# 課題：SQLiteでECサイトのログを集計する

## 目的

ECサイトの操作ログをもとに、**リレーションを持つテーブルの作成**と、**SQLによる基本的な集計**を体験する。

## 手順

1. 配布されたzipを展開し、 **{学籍番号(先頭のsは不要)}-DSP-SATask3** という名前の**プライベートリポジトリ**として作成する。(パブリックでは他人から回答が見えてしまうため不可)

2. 作業用のブランチを作成し、そのブランチ上で作業する。`main` ブランチは編集しない。

3. main.pyのみを編集し、SQLを記述する。

4. main.pyを実行し、結果が正しく得られることを確認する。

5. 採点のためにSAをコラボレーターとして招待する。今回は学籍番号が偶数の人は橘(GitHub id: tacho-bana)を、奇数の人は竹本(GitHub id: bambooked)をコラボレーターとして招待すること。 

6. classroomで作成したリポジトリのurlを提出する。

## 配布ファイル・実行環境

- `main.py`：編集するPythonプログラム
- `ec.log`：架空のECサイトのログ（UTF-8、CSV形式）
- `readme.md`：この説明書

Python 3.9以上を使用する。追加ライブラリは不要。`sqlite3`、`csv`、`json`はPython標準ライブラリである。

`main.py`の **`SCHEMA_SQL` と `VIEWS_SQL` の2か所** にSQLを記述すればよい。ログの読み込みやJSON出力の部分は、あらかじめ実装してある。

## 1. ログ形式

`ec.log`は次の3種類のレコードを1ファイルにまとめたもの。フィールドはカンマで区切られる。

```text
USER,U001,east
PRODUCT,P001,books
EVENT,E0001,U001,P001,view,
EVENT,E0002,U001,P001,purchase,1500
```

| レコード | フィールドの順序 | 意味 |
|---|---|---|
| `USER` | `user_id, region` | ユーザーのID・地域 |
| `PRODUCT` | `product_id, category` | 商品のID・カテゴリ |
| `EVENT` | `event_id, user_id, product_id, event_type, amount` | 閲覧・購入イベント |

- `event_type`は`view`（閲覧）または`purchase`（購入）。
- `amount`は購入金額（整数・円）。`view`の場合は空欄で、DBには`NULL`として登録される。
- 1行が1イベント。同じユーザーが複数回購入する場合もある。

## 2. 課題1：テーブルを作成する

`main.py`の`SCHEMA_SQL`に、次の3テーブルを作成するSQLを記述する。

| テーブル | 列（列名と型） | 制約 |
|---|---|---|
| `users` | `user_id TEXT`, `region TEXT` | `user_id`を主キー |
| `products` | `product_id TEXT`, `category TEXT` | `product_id`を主キー |
| `events` | `event_id TEXT`, `user_id TEXT`, `product_id TEXT`, `event_type TEXT`, `amount INTEGER` | `event_id`を主キー。`user_id`は`users(user_id)`を、`product_id`は`products(product_id)`を外部キー参照する |

外部キーは**列名が一致するだけでは不可**。`REFERENCES`を使って制約として定義すること。次のどちらの書き方でもよい。

```sql
-- 書き方1：テーブル制約として末尾にまとめて書く
FOREIGN KEY (user_id) REFERENCES users(user_id)

-- 書き方2：列定義の中に直接書く
user_id TEXT REFERENCES users(user_id)
```

- 列名・型は上の表のとおりに記述すること（例：`INTEGER`を`INT`にしない）。列の順序も表のとおりとする。
- 表にない制約（`NOT NULL`、`CHECK`など）は付けなくてよい。付けても、配布データ・差し替えデータの読み込みが失敗しなければ減点しない。

`main.py`がCSV形式のログを読み込み、テーブルにレコードを挿入する部分は実装済み。

## 3. 課題2：SQLで集計する

`main.py`の`VIEWS_SQL`に、次の2つのVIEWを作成するSQLを記述する。Pythonで集計するのではなく、`SELECT`、`JOIN`、`WHERE`、`GROUP BY`などの**SQLで計算すること**。

### (A) `category_stats`

**購入イベントが1件以上ある商品カテゴリ**について、次の3列を出すVIEWを作成する。

| 列名 | 内容 |
|---|---|
| `category` | 商品カテゴリ |
| `purchase_count` | `purchase`イベントの件数 |
| `revenue` | そのカテゴリの`purchase`イベントの`amount`合計（円） |

同じカテゴリに属する複数の商品は、まとめて集計すること。閲覧（`view`）は件数にも金額にも含めない。

### (B) `region_stats`

**購入したユーザーが1人以上いる地域**について、次の2列を出すVIEWを作成する。

| 列名 | 内容 |
|---|---|
| `region` | ユーザーの地域 |
| `unique_buyers` | その地域で1回以上購入したユーザー数（重複なし） |

同じユーザーが何回購入しても、人数は**1人**と数えること。

## 4. 実行と出力

3ファイルを同じフォルダに置き、ターミナルから以下を実行する。

```bash
python main.py
```

正常終了すると、そのフォルダに`ec.db`が作成され、**標準出力にはJSONのみ**が表示される。形式は次のとおり（数値は例）。

```json
{
  "category_stats": [
    {"category": "books", "purchase_count": 12, "revenue": 36000},
    {"category": "food", "purchase_count": 20, "revenue": 25000}
  ],
  "region_stats": [
    {"region": "east", "unique_buyers": 8},
    {"region": "west", "unique_buyers": 6}
  ]
}
```

- JSONのキー名・列名を変更しないこと。
- カテゴリ・地域はそれぞれ**名前の昇順**で並べる（テンプレート側で対応済み）。
- 出力する統計量は整数にすること。
- 実行前に既存の`ec.db`があれば削除し、作り直す（テンプレート側で対応済み）。
- `print()`によるデバッグ出力は標準出力に残さないこと。

## 5. 提出物・採点

**提出するのは編集済みの`main.py`のみ**。配布された`ec.log`と本READMEの提出は不要。

**採点時には別の`ec.log`に差し替えて再実行する場合がある。** 配布データにしか対応しない数値の直接記入（ハードコード）は正解にならない。

生成AIの使用は認める。ただし、提出したプログラムの動作とSQLの意味は自分で確認すること。
