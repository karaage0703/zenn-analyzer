#!/usr/bin/env python3
"""
Zenn記事情報収集ツール

このスクリプトは、CSVファイルからZenn APIのエンドポイントURLを読み込み、
各URLに対してAPIリクエストを行い、記事情報（記事タイトル、Publication、投稿したユーザー名、いいね数）
を取得します。取得した結果はCSVファイルに出力されます。
"""

import requests
import csv


class ZennAPIClient:
    """
    Zenn APIとの通信を管理するクラス。

    Attributes:
        base_url (str): APIのベースURL（今回は各URLにフルエンドポイントが含まれている前提のため空文字）。
    """

    def __init__(self, base_url: str):
        """
        Args:
            base_url (str): APIのベースURL。
        """
        self.base_url = base_url

    def fetch_articles(self, url: str) -> list:
        """
        指定されたURLから記事情報を取得する。

        各記事について、記事タイトル、Publication、投稿したユーザー名、いいね数を抽出する。
        Publicationは、article内にpublicationが存在すればそのdisplay_name、存在しなければ空文字とする。
        投稿したユーザー名は、常にarticle内のuser.usernameから取得する。

        Args:
            url (str): APIのエンドポイントURL。

        Returns:
            list of tuple: 各タプルは (記事タイトル, Publication, 投稿したユーザー名, いいね数) を表す。
        """
        articles_data = []
        page = 1

        while True:
            response = requests.get(f"{url}&page={page}")
            if response.ok:
                json_data = response.json()
                articles = json_data.get("articles", [])
                for article in articles:
                    title = article.get("title", "")
                    publication_name = ""
                    if article.get("publication"):
                        publication_name = article.get("publication").get("display_name", "")
                    user_name = article.get("user", {}).get("username", "")
                    liked_count = article.get("liked_count", 0)
                    articles_data.append((title, publication_name, user_name, liked_count))
                if json_data.get("next_page") is None:
                    break
                else:
                    page = json_data.get("next_page")
            else:
                break

        return articles_data


class CSVReader:
    """
    CSVファイルを読み込み、URLリストを作成するクラス。
    """

    @staticmethod
    def read_csv(file_path: str) -> list:
        """
        CSVファイルを読み込み、各行の先頭列をURLリストとして抽出する。

        Args:
            file_path (str): 読み込み対象のCSVファイルパス。

        Returns:
            list: URLのリスト。
        """
        url_list = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    url_list.append(row[0])
        return url_list


def write_to_csv(data: list, output_path: str) -> None:
    """
    取得した記事情報をCSVファイルに書き出す。

    CSVファイルのヘッダーは「記事名」「Publication」「投稿したユーザー名」「いいね数」とする。

    Args:
        data (list): (記事タイトル, Publication, 投稿したユーザー名, いいね数) のタプルのリスト。
        output_path (str): 出力先のCSVファイルパス。
    """
    with open(output_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["記事名", "Publication", "投稿したユーザー名", "いいね数"])
        writer.writerows(data)


class MainProcessor:
    """
    CSVファイルからURLリストを読み込み、各URLから記事情報を取得し、CSV出力を行うクラス。
    """

    def __init__(self, csv_file: str, output_csv: str):
        """
        Args:
            csv_file (str): 入力CSVファイルパス（URLリスト）。
            output_csv (str): 出力CSVファイルパス。
        """
        self.csv_file = csv_file
        self.output_csv = output_csv
        self.client = ZennAPIClient(base_url="")

    def process(self) -> None:
        """
        URLリストを読み込み、各URLから記事情報を取得し、結果をCSVファイルに出力する。
        """
        url_list = CSVReader.read_csv(self.csv_file)
        all_articles = []
        for url in url_list:
            articles = self.client.fetch_articles(url)
            all_articles.extend(articles)
        write_to_csv(all_articles, self.output_csv)
        print(f"CSVファイルに記事情報を出力しました: {self.output_csv}")


def main() -> None:
    """
    メイン処理関数。
    """
    input_csv = "url_list.csv"
    output_csv = "zenn_articles.csv"
    processor = MainProcessor(input_csv, output_csv)
    processor.process()


if __name__ == "__main__":
    main()
