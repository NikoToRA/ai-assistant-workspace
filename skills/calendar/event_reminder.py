#!/usr/bin/env python3
"""予定の10分前リマインダー。

5分ごとにcron/スケジューラーで実行し、
直近5〜10分以内に開始する予定があれば通知テキストを出力する。
出力がなければ通知不要。
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# config.local.json から設定を読み込み
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "lib"))
from config import get_notion_api_key, get_notion_db_id

# 設定
DB_ID = get_notion_db_id("todo")
DATE_PROPERTY = "日付"
TZ = ZoneInfo("Asia/Tokyo")
NOTION_VERSION = "2022-06-28"
NOTIFIED_FILE = Path(__file__).parent / ".notified_events.json"


def get_api_key() -> str:
    return get_notion_api_key()


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {get_api_key()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def query_today_events() -> list[dict]:
    """今日の予定を取得する。"""
    now = datetime.now(TZ)
    today = now.date()
    start_date = str(today - timedelta(days=1))
    end_date = str(today + timedelta(days=2))

    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
    body = {
        "filter": {
            "and": [
                {"property": DATE_PROPERTY, "date": {"on_or_after": start_date}},
                {"property": DATE_PROPERTY, "date": {"before": end_date}},
            ]
        },
        "sorts": [{"property": DATE_PROPERTY, "direction": "ascending"}],
    }

    r = requests.post(url, headers=get_headers(), json=body)
    r.raise_for_status()
    return r.json().get("results", [])


def parse_event(page: dict) -> dict | None:
    """時刻付き予定のみ抽出する。"""
    props = page.get("properties", {})

    # タイトル
    title_parts = props.get("Name", {}).get("title", [])
    title = "".join(t.get("plain_text", "") for t in title_parts) or "（タイトルなし）"

    # 日付
    date_prop = props.get(DATE_PROPERTY, {}).get("date", {}) or {}
    start_str = date_prop.get("start", "")

    if not start_str or "T" not in start_str:
        return None  # 終日予定はスキップ

    start_dt = datetime.fromisoformat(start_str).astimezone(TZ)
    return {"title": title, "start": start_dt, "page_id": page["id"]}


def load_notified() -> set:
    """今日通知済みのイベントIDを読み込む。"""
    if not NOTIFIED_FILE.exists():
        return set()
    data = json.loads(NOTIFIED_FILE.read_text())
    today = str(datetime.now(TZ).date())
    if data.get("date") != today:
        return set()
    return set(data.get("notified", []))


def save_notified(notified: set):
    """通知済みイベントIDを保存する。"""
    today = str(datetime.now(TZ).date())
    NOTIFIED_FILE.write_text(json.dumps({"date": today, "notified": list(notified)}))


def main():
    now = datetime.now(TZ)
    results = query_today_events()
    notified = load_notified()

    reminders = []
    for page in results:
        event = parse_event(page)
        if not event:
            continue

        # 今日の予定のみ
        if event["start"].date() != now.date():
            continue

        # 5〜15分後に開始する予定を検出（5分間隔実行を想定）
        diff = (event["start"] - now).total_seconds() / 60
        if 0 < diff <= 15 and event["page_id"] not in notified:
            minutes = int(diff)
            reminders.append(
                f"⏰ あと約{minutes}分で **{event['title']}** が始まります！"
                f"（{event['start'].strftime('%H:%M')}〜）"
            )
            notified.add(event["page_id"])

    if reminders:
        save_notified(notified)
        print("\n".join(reminders))
    # 出力がなければ通知不要


if __name__ == "__main__":
    main()
