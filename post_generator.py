# post_generator.py
print("✅ post_generator.py 実行されました！")

import os
import random
import datetime
import time
import gspread
from google.oauth2.service_account import Credentials
import logging

import json
import os
from google.oauth2.service_account import Credentials

import os, json, base64

# Base64エンコードされたJSONをデコードしてdict化
encoded = os.environ['GOOGLE_SERVICE_ACCOUNT_JSON']
decoded = base64.b64decode(encoded).decode('utf-8')
service_account_info = json.loads(decoded)

credentials = Credentials.from_service_account_info(service_account_info)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("post_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Google Sheets APIの設定
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# 妖艶なお姉さんの投稿文テンプレート（40代男性向け）
POST_TEMPLATES = [
    "この体つき、見た瞬間頭が真っ白になった...",
    "こんなカラダ実在するの？特定して今夜眠れない...",
    "これを特定した俺の勝ち...溜まらずにはいられない",
    "この曲線美、罪深すぎる...特定したのでシェアします",
    "見つけた瞬間、股間が熱くなった...保存必須",
    "この極上ボディ、特定できた人だけの秘密...",
    "こんな完璧なカラダ見たことない...特定して震えた",
    "夜も眠れなくなる特定完了...これはヤバすぎる",
    "この官能的な姿を特定...一晩中見続けてしまった",
    "ついに見つけた極上の存在...思わず手が震える",
    "こんな完璧な女性を見つけてしまった...",
    "これは保存するしかない...特定完了",
    "こんな美しさ、実在していいのか...",
    "この極上ボディ、特定するのに徹夜した価値あり",
    "思わず息を呑む美しさ...特定できた人だけがわかる",
    "こんな曲線美を持つ女性を発見...保存不可避",
    "一度見たら忘れられない...特定してしまった",
    "この完璧すぎるスタイル、ついに見つけた",
    "特定完了...これは男なら保存必須",
    "こんな官能的な姿を見つけてしまった...シェア必須",
    "この完璧な女性、ついに見つけ出した...",
    "思わず見惚れてしまう...特定できた人だけの秘密",
    "これを見つけるのに3日かかった...保存必須",
    "こんな美しい女性が実在するなんて...特定完了",
    "特定するのに苦労したけど...これは価値あり",
    "この極上の姿を見つけてしまった...目が離せない",
    "これを特定できたのは運命...シェアします",
    "こんな完璧なカラダ、実在していいの？",
    "特定して震えが止まらない...これはヤバすぎる",
    "この美しすぎるスタイル、ついに見つけた..."
]

class XPostGenerator:
    """X投稿文を生成してスプレッドシートに記録するクラス"""
    
    def __init__(self, spreadsheet_id, credentials_file):
        """
        初期化
        
        Args:
            spreadsheet_id: GoogleスプレッドシートのID
            credentials_file: サービスアカウントの認証情報JSONファイルのパス
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self.gc = self._authenticate()
        
    def _authenticate(self):
        """Google APIに認証"""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES
            )
            return gspread.authorize(credentials)
        except Exception as e:
            logger.error(f"認証エラー: {e}")
            raise
    
    def generate_posts(self, count=10):
        """
        指定された数の投稿文を生成
        
        Args:
            count: 生成する投稿文の数
            
        Returns:
            生成された投稿文のリスト
        """
        # テンプレートからランダムに選択（重複なし）
        if count <= len(POST_TEMPLATES):
            return random.sample(POST_TEMPLATES, count)
        else:
            # もしテンプレートより多く必要な場合は、一部重複を許可
            posts = random.sample(POST_TEMPLATES, len(POST_TEMPLATES))
            additional_needed = count - len(POST_TEMPLATES)
            posts.extend(random.choices(POST_TEMPLATES, k=additional_needed))
            return posts
    
    def write_to_spreadsheet(self, count=10):
        """
        スプレッドシートに投稿文を書き込む
        
        Args:
            count: 生成する投稿文の数
        """
        try:
            # スプレッドシートを開く
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # 指定されたシートを開く
            try:
                worksheet = spreadsheet.worksheet("自動投稿ポスト一覧")
                logger.info("シート「自動投稿ポスト一覧」を開きました")
            except gspread.exceptions.WorksheetNotFound:
                # シートが存在しない場合は作成
                worksheet = spreadsheet.add_worksheet(title="自動投稿ポスト一覧", rows=1000, cols=1)
                logger.info("シート「自動投稿ポスト一覧」を新規作成しました")
            
            # 現在のA列の値を取得
            a_column = worksheet.col_values(1)
            logger.info(f"現在のA列のセル数: {len(a_column)}")
            
            # 投稿文を生成
            posts = self.generate_posts(count)
            logger.info(f"{count}個の投稿文を生成しました")
            
            # 空のセルから開始して書き込む
            start_row = len(a_column) + 1
            
            # 書き込み
            for i, post in enumerate(posts):
                worksheet.update_cell(start_row + i, 1, post)
                # APIレート制限を回避するための待機
                time.sleep(1)
            
            logger.info(f"{count}個の投稿文をA{start_row}:A{start_row+count-1}に書き込みました")
            return True
            
        except Exception as e:
            logger.error(f"スプレッドシートへの書き込みエラー: {e}")
            return False

def main():
    """メイン実行関数"""
    # 環境変数からスプレッドシートIDと認証情報のパスを取得
    # ここでハードコードするか、環境変数から読み込む
    spreadsheet_id = "1-CEFI2rEcyabviMUJsNBmX6r7V3hbsOVGxCaXbmsWe0"  # あなたのスプレッドシートID
    credentials_file = "phonic-sunbeam-456013-r1-1795127bd5f6.json"  # サービスアカウントのJSONファイルパス
    
    try:
        # 投稿生成器を初期化
        generator = XPostGenerator(spreadsheet_id, credentials_file)
        
        # スプレッドシートに投稿を追加
        success = generator.write_to_spreadsheet(count=10)
        
        if success:
            logger.info("投稿文の生成と書き込みが完了しました")
        else:
            logger.error("投稿文の生成と書き込みに失敗しました")
            
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()