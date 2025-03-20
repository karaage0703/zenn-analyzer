import requests
import csv


def parse_json_and_calculate(url):
    """
    指定されたURLからJSONデータを取得し、記事数とliked_countの合計を計算する。

    Args:
        url (str): Zenn APIのエンドポイントURL。

    Returns:
        tuple: (パブリケーション名/ユーザー名, 記事数, liked_countの合計)
    """
    page = 1
    article_count = 0
    total_liked_count = 0

    while True:
        # 不要なクォートを削除
        response = requests.get(f"{url}&page={page}")
        if response.ok:
            json_data = response.json()

            articles = json_data["articles"]
            article_count += len(articles)
            total_liked_count += sum(article["liked_count"] for article in articles)

            if json_data["next_page"] is None:
                try:
                    user_name = articles[0]["publication"]["display_name"]
                except Exception as e:
                    user_name = articles[0]["user"]["username"]
                    print(e)

                return user_name, article_count, total_liked_count
            else:
                page = json_data["next_page"]


# CSVファイルのパスを指定
file_path = "url_list.csv"

# URLを格納するためのリストを初期化
url_list = []

# CSVファイルを開き、内容をリストに格納
with open(file_path, mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        url_list.append(row[0])  # 仮定として、URLは各行の最初の列にあるとします


# データ収集
user_names = []
article_counts = []
total_liked_counts = []

for url in url_list:
    user_name, article_count, total_liked_count = parse_json_and_calculate(url)
    user_names.append(user_name)
    article_counts.append(article_count)
    total_liked_counts.append(total_liked_count)

# 結果の表示
print(list(zip(user_names, article_counts, total_liked_counts)))
