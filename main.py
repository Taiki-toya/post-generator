import os
import time
import json
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account
import tweepy
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = "1-CEFI2rEcyabviMUJsNBmX6r7V3hbsOVGxCaXbmsWe0"
SHEET_NAME = "自動投稿ポスト一覧2"

def setup_twitter_api():
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
        )
        print("✅ Twitter API認証成功")
        return client
    except Exception as e:
        print(f"❌ Twitter API認証エラー: {e}")
        return None

def setup_google_sheets():
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        # Base64文字列から読み込む（Renderの環境変数から）
        b64_creds = os.getenv("GOOGLE_CREDENTIALS_BASE64")
        creds_dict = json.loads(base64.b64decode(b64_creds))
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

        service = build('sheets', 'v4', credentials=creds)
        print("✅ Google Sheets API認証成功")
        return service
    except Exception as e:
        print(f"❌ Google Sheets API認証エラー: {e}")
        return None

def get_next_post_row(service):
    try:
        range_name = f"{SHEET_NAME}!A:D"
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        rows = result.get('values', [])
        if not rows:
            print("データが見つかりませんでした")
            return None, None

        for i in range(1, len(rows)):
            row = rows[i] + [''] * (4 - len(rows[i]))
            if row[3].upper() != "TRUE":
                print(f"未投稿の行が見つかりました: 行 {i+1}")
                return i+1, row
        print("すべての行が投稿済みです")
        return None, None
    except Exception as e:
        print(f"❌ データ取得エラー: {e}")
        return None, None

def post_tweet_with_reply(client, post_text, video_url, affiliate_link):
    try:
        main_text = f"{post_text}\n{video_url}"
        response = client.create_tweet(text=main_text)
        tweet_id = response.data['id']
        print(f"✅ メインツイート投稿成功！ツイートID: {tweet_id}")
        time.sleep(20)
        reply_text = f"これですね👇\n{affiliate_link}"
        reply = client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
        print(f"✅ 返信投稿成功！返信ID: {reply.data['id']}")
        return True
    except Exception as e:
        print(f"❌ 投稿エラー: {e}")
        return False

def update_spreadsheet_status(service, row_number):
    try:
        range_name = f"{SHEET_NAME}!D{row_number}"
        body = {'values': [['TRUE']]}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        print(f"✅ 行{row_number}を更新しました")
        return True
    except Exception as e:
        print(f"❌ スプレッドシート更新エラー: {e}")
        return False

# Flask側の /run エンドポイントで呼び出すためのメイン処理
def main():
    print("🚀 自動投稿スクリプト開始")
    client = setup_twitter_api()
    if not client:
        return
    service = setup_google_sheets()
    if not service:
        return
    row_number, row_data = get_next_post_row(service)
    if not row_number:
        return
    post_text = row_data[0]
    video_url = row_data[1]
    affiliate_link = row_data[2]
    success = post_tweet_with_reply(client, post_text, video_url, affiliate_link)
    if success:
        update_spreadsheet_status(service, row_number)
