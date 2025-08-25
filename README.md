# Zenn Analyzer

このリポジトリは、Zenn APIを用いて記事情報を収集・分析するツール群を含みます。

## 機能概要

本リポジトリには3種類のツールが含まれます。

1. **zenn_analyzer.py**  
   - URLリスト（`url_list.csv`）からZenn APIのエンドポイントを取得し、記事数と「いいね」数の合計を算出するツール。  
   - 結果はコンソールに出力されます。

2. **zenn_article_analyzer.py**  
   - URLリスト（`url_list.csv`）から各記事の詳細情報（記事タイトル、Publication、投稿したユーザー名、いいね数）を取得し、CSVファイル（`zenn_articles.csv`）に書き出すツール。

3. **zenn_user_ranking.py**  
   - Zennの人気記事からユーザーを自動発見し、各ユーザーの総いいね数をランキング形式で集計するツール。  
   - 上位100位のランキングをCSVファイルに出力します。

## Setup

以下のコマンドでリポジトリをクローンしてください。

```sh
$ cd && git clone https://github.com/karaage0703/zenn-analyzer
$ cd zenn-analyzer
$ docker build -t zenn-analyzer .
```

必要に応じて `url_list.csv` を編集してください。

## Usage

- **zenn_analyzer.py** を実行する場合:
  ```sh
  $ python zenn_analyzer.py
  ```
  コンソールに集計結果が表示されます。

- **zenn_article_analyzer.py** を実行する場合:
  ```sh
  $ python zenn_article_analyzer.py
  ```
  結果は `zenn_articles.csv` に出力されます。

- **zenn_user_ranking.py** を実行する場合:
  ```sh
  $ uv run python3 zenn_user_ranking.py
  ```
  または
  ```sh
  $ python zenn_user_ranking.py
  ```
  Zennユーザーの総いいね数ランキングTOP100をCSVファイルに出力します。

- **run.sh の利用 (Docker を使用)**  
  リポジトリ直下にある `run.sh` を利用することで、Docker コンテナ内で `zenn_analyzer.py` を実行できます。  
  ```sh
  $ ./run.sh
  ```
  このコマンドは以下の内容を実行します:
  ```
  docker run -it --rm -v $(pwd):/root zenn-analyzer python3 zenn_analyzer.py
  ```

## 注意事項

- Python 3.x が必要です。
- 必要なライブラリ: `requests` と `csv`
