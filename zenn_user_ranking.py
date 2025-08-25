#!/usr/bin/env python3
"""
Zennユーザーのいいね数ランキング生成ツール（最適化版）

このスクリプトは、Zenn APIを使用して人気記事からユーザーを発見し、
ユーザーAPIから直接total_liked_countを取得してトップ100のランキングを生成します。
"""

import requests
import csv
import time
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class ZennUserDiscovery:
    """
    Zennの人気記事からユーザーを発見するクラス。
    """
    
    def __init__(self, max_pages: int = 50):
        """
        Args:
            max_pages (int): 取得する最大ページ数
        """
        self.max_pages = max_pages
        self.base_url = "https://zenn.dev/api/articles"
    
    def discover_users_from_popular_articles(self) -> Set[str]:
        """
        人気記事からユーザー名を収集する。
        
        Returns:
            Set[str]: 発見されたユーザー名のセット
        """
        discovered_users = set()
        page = 1
        
        print(f"人気記事からユーザーを発見中... (最大{self.max_pages}ページ)")
        
        while page <= self.max_pages:
            try:
                print(f"  ページ {page} を処理中...")
                response = requests.get(f"{self.base_url}?order=liked&page={page}")
                
                if not response.ok:
                    print(f"  エラー: ページ {page} の取得に失敗 (Status: {response.status_code})")
                    break
                
                data = response.json()
                articles = data.get("articles", [])
                
                if not articles:
                    print("  記事が見つかりません。検索を終了します。")
                    break
                
                # ユーザー名を抽出
                page_users = set()
                for article in articles:
                    username = article.get("user", {}).get("username")
                    if username:
                        discovered_users.add(username)
                        page_users.add(username)
                
                print(f"  {len(articles)} 記事から {len(page_users)} ユーザーを発見")
                
                # 次のページがあるかチェック
                next_page = data.get("next_page")
                if next_page is None:
                    print("  最終ページに到達しました。")
                    break
                    
                page = next_page
                time.sleep(0.3)  # API制限を考慮した待機時間
                
            except Exception as e:
                print(f"  エラー: ページ {page} の処理中にエラーが発生: {e}")
                break
        
        print(f"発見完了: 合計 {len(discovered_users)} 人のユーザーを発見")
        return discovered_users


class ZennUserStatsCollector:
    """
    ユーザーAPIから直接統計データを収集するクラス。
    """
    
    def __init__(self):
        self.base_url = "https://zenn.dev/api/users"
    
    def collect_user_stats(self, username: str) -> Tuple[str, int, int]:
        """
        指定されたユーザーの統計情報をAPIから直接取得する。
        
        Args:
            username (str): ユーザー名
            
        Returns:
            tuple: (ユーザー名, 総いいね数, 記事数)
        """
        try:
            response = requests.get(f"{self.base_url}/{username}")
            
            if not response.ok:
                print(f"  警告: ユーザー {username} のデータ取得に失敗 (Status: {response.status_code})")
                return username, 0, 0
            
            data = response.json()
            user = data.get("user", {})
            
            total_likes = user.get("total_liked_count", 0)
            article_count = user.get("articles_count", 0)
            
            return username, total_likes, article_count
            
        except Exception as e:
            print(f"  警告: ユーザー {username} のデータ取得中にエラー: {e}")
            return username, 0, 0
    
    def collect_all_user_stats(self, usernames: Set[str]) -> List[Tuple[str, int, int]]:
        """
        全ユーザーの統計データを収集する。
        
        Args:
            usernames (Set[str]): 収集対象のユーザー名セット
            
        Returns:
            List[Tuple]: (ユーザー名, 総いいね数, 記事数) のリスト
        """
        user_stats = []
        total_users = len(usernames)
        
        print(f"\n{total_users} 人のユーザー統計を収集中...")
        
        for i, username in enumerate(usernames, 1):
            print(f"  [{i:3d}/{total_users}] {username} を処理中...")
            
            username, total_likes, article_count = self.collect_user_stats(username)
            user_stats.append((username, total_likes, article_count))
            
            if i % 20 == 0:
                print(f"  進捗: {i}/{total_users} 完了")
            
            # APIレート制限を考慮した短い待機
            time.sleep(0.1)
        
        print("統計収集完了!")
        return user_stats


class RankingGenerator:
    """
    ユーザー統計からランキングを生成・出力するクラス。
    """
    
    @staticmethod
    def generate_top_ranking(user_stats: List[Tuple[str, int, int]], top_n: int = 100) -> List[Tuple[int, str, int, int]]:
        """
        ユーザー統計からトップランキングを生成する。
        
        Args:
            user_stats (List[Tuple]): (ユーザー名, 総いいね数, 記事数) のリスト
            top_n (int): 取得する上位N位
            
        Returns:
            List[Tuple]: (順位, ユーザー名, 総いいね数, 記事数) のリスト
        """
        # いいね数でソート（降順）、同率の場合は記事数でソート
        sorted_users = sorted(user_stats, key=lambda x: (x[1], x[2]), reverse=True)
        
        # 上位N位を取得し、順位を追加
        ranking = []
        for i, (username, total_likes, article_count) in enumerate(sorted_users[:top_n], 1):
            ranking.append((i, username, total_likes, article_count))
        
        return ranking
    
    @staticmethod
    def export_to_csv(ranking: List[Tuple[int, str, int, int]], output_path: str) -> None:
        """
        ランキングデータをCSVファイルに出力する。
        
        Args:
            ranking (List[Tuple]): (順位, ユーザー名, 総いいね数, 記事数) のリスト
            output_path (str): 出力ファイルパス
        """
        with open(output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["順位", "ユーザー名", "総いいね数", "記事数", "ユーザーページ"])
            
            for rank, username, total_likes, article_count in ranking:
                user_page = f"https://zenn.dev/{username}"
                writer.writerow([rank, username, total_likes, article_count, user_page])
        
        print(f"ランキングデータを {output_path} に出力しました")
    
    @staticmethod
    def print_top_ranking(ranking: List[Tuple[int, str, int, int]], top_n: int = 30) -> None:
        """
        トップランキングをコンソールに表示する。
        
        Args:
            ranking (List[Tuple]): (順位, ユーザー名, 総いいね数, 記事数) のリスト  
            top_n (int): 表示する上位N位
        """
        print(f"\n=== Zennユーザー いいね数ランキング TOP {top_n} ===")
        print("順位 | ユーザー名             | 総いいね数 | 記事数 | 平均いいね/記事")
        print("-" * 75)
        
        for rank, username, total_likes, article_count in ranking[:top_n]:
            avg_likes = round(total_likes / max(article_count, 1), 1)
            print(f"{rank:3d} | {username:22s} | {total_likes:8d} | {article_count:5d} | {avg_likes:13.1f}")


class ZennRankingOrchestrator:
    """
    ランキング生成プロセス全体を統括するクラス。
    """
    
    def __init__(self, discovery_pages: int = 50, top_ranking: int = 100):
        """
        Args:
            discovery_pages (int): ユーザー発見用に取得する人気記事のページ数
            top_ranking (int): 生成するランキングの上位N位
        """
        self.discovery_pages = discovery_pages
        self.top_ranking = top_ranking
        
        self.discovery = ZennUserDiscovery(max_pages=discovery_pages)
        self.collector = ZennUserStatsCollector()
        self.generator = RankingGenerator()
    
    def execute_ranking_pipeline(self) -> None:
        """
        ランキング生成パイプラインを実行する。
        """
        print("=== Zennユーザー いいね数ランキング生成開始 (最適化版) ===\n")
        
        # Step 1: ユーザー発見
        discovered_users = self.discovery.discover_users_from_popular_articles()
        
        if not discovered_users:
            print("エラー: ユーザーが発見されませんでした。")
            return
        
        # Step 2: ユーザー統計収集（最適化版：ユーザーAPIから直接取得）
        user_stats = self.collector.collect_all_user_stats(discovered_users)
        
        if not user_stats:
            print("エラー: ユーザー統計が収集されませんでした。")
            return
        
        # Step 3: ランキング生成
        ranking = self.generator.generate_top_ranking(user_stats, self.top_ranking)
        
        # Step 4: 結果出力
        output_file = "zenn_user_likes_ranking_top100.csv"
        self.generator.export_to_csv(ranking, output_file)
        self.generator.print_top_ranking(ranking, 30)
        
        # Step 5: 統計サマリー
        total_likes = sum(likes for _, likes, _ in user_stats)
        total_articles = sum(articles for _, _, articles in user_stats)
        
        print(f"\n=== 完了 ===")
        print(f"発見ユーザー数: {len(discovered_users)}")
        print(f"データ収集ユーザー数: {len(user_stats)}")
        print(f"全体総いいね数: {total_likes:,}")
        print(f"全体総記事数: {total_articles:,}")
        print(f"ランキング出力: TOP {len(ranking)}")
        print(f"出力ファイル: {output_file}")


def main() -> None:
    """
    メイン実行関数。
    """
    # より多くのユーザーを発見するため、人気記事のページ数を増やす
    orchestrator = ZennRankingOrchestrator(discovery_pages=50, top_ranking=100)
    orchestrator.execute_ranking_pipeline()


if __name__ == "__main__":
    main()