#!/usr/bin/env python3
"""Notionデータベースからカレンダー予定を取得するスクリプト。

使い方:
  python notion_calendar.py              # 今日
  python notion_calendar.py today        # 今日
  python notion_calendar.py tomorrow     # 明日
  python notion_calendar.py week         # 今後7日間
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


def get_api_key() -> str:
    return get_notion_api_key()


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {get_api_key()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def query_events(start_date: str, end_date: str) -> list[dict]:
    """Notion DBから指定期間の予定を取得する。

    Notionの日時はUTCで格納されているため、JSTとの時差を考慮して
    前後1日広めに取得し、後からJSTベースでフィルタする。
    """
    # UTC/JST時差を考慮して前後1日広く取得
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    wide_start = str(start_dt - timedelta(days=1))
    wide_end = str(end_dt + timedelta(days=1))

    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
    body = {
        "filter": {
            "and": [
                {
                    "property": DATE_PROPERTY,
                    "date": {"on_or_after": wide_start}
                },
                {
                    "property": DATE_PROPERTY,
                    "date": {"before": wide_end}
                },
            ]
        },
        "sorts": [
            {"property": DATE_PROPERTY, "direction": "ascending"}
        ],
    }

    r = requests.post(url, headers=get_headers(), json=body)
    r.raise_for_status()
    results = r.json().get("results", [])

    # JSTベースで日付フィルタ
    filtered = []
    for page in results:
        date_prop = page.get("properties", {}).get(DATE_PROPERTY, {}).get("date", {}) or {}
        start_str = date_prop.get("start", "")
        if not start_str:
            continue
        if "T" in start_str:
            event_date = str(datetime.fromisoformat(start_str).astimezone(TZ).date())
        else:
            event_date = start_str[:10]
        if start_date <= event_date < end_date:
            filtered.append(page)

    return filtered


def parse_event(page: dict) -> dict:
    """Notionページから予定情報を抽出する。"""
    props = page.get("properties", {})

    # タイトル
    name_prop = props.get("Name", {})
    title_parts = name_prop.get("title", [])
    title = "".join(t.get("plain_text", "") for t in title_parts) or "（タイトルなし）"

    # 日付
    date_prop = props.get(DATE_PROPERTY, {}).get("date", {}) or {}
    start_str = date_prop.get("start", "")
    end_str = date_prop.get("end", "")

    # ステータス
    status_prop = props.get("status", {}).get("status", {}) or {}
    status = status_prop.get("name", "")

    # 優先度
    priority_prop = props.get("priority", {}).get("select", {}) or {}
    priority = priority_prop.get("name", "")

    # タグ
    tags_prop = props.get("タグ", {}).get("multi_select", []) or []
    tags = [t.get("name", "") for t in tags_prop]

    return {
        "title": title,
        "start": start_str,
        "end": end_str,
        "status": status,
        "priority": priority,
        "tags": tags,
        "url": page.get("url", ""),
    }


def to_jst(dt_str: str) -> datetime | None:
    """日時文字列をJSTのdatetimeに変換する。"""
    if not dt_str or "T" not in dt_str:
        return None
    dt = datetime.fromisoformat(dt_str)
    return dt.astimezone(TZ)


def format_time(dt_str: str) -> str:
    """日時文字列から時刻部分を取得。"""
    if not dt_str:
        return ""
    dt = to_jst(dt_str)
    if dt:
        return dt.strftime("%H:%M")
    return "終日"


def format_event(event: dict) -> str:
    """予定を表示用にフォーマット。"""
    start_time = format_time(event["start"])
    end_time = format_time(event["end"])

    if start_time == "終日":
        time_str = "終日"
    elif end_time and end_time != "終日":
        time_str = f"{start_time}-{end_time}"
    elif start_time:
        time_str = start_time
    else:
        time_str = ""

    status = f" [{event['status']}]" if event["status"] else ""
    priority = f" !{event['priority']}" if event["priority"] else ""
    tags = f" ({', '.join(event['tags'])})" if event["tags"] else ""

    return f"{time_str} {event['title']}{status}{priority}{tags}"


def parse_args(args: list[str]) -> tuple[str, str, str]:
    """引数をパースして (start_date, end_date, title) を返す。"""
    now = datetime.now(TZ)
    today = now.date()

    if not args or args[0].lower() == "today":
        start = today
        end = today + timedelta(days=1)
        title = f"今日の予定 ({start})"
    elif args[0].lower() == "tomorrow":
        start = today + timedelta(days=1)
        end = today + timedelta(days=2)
        title = f"明日の予定 ({start})"
    elif args[0].lower() == "week":
        start = today
        end = today + timedelta(days=7)
        title = f"今後7日間の予定 ({start} 〜 {end - timedelta(days=1)})"
    else:
        try:
            offset = int(args[0])
            start = today + timedelta(days=offset)
            end = start + timedelta(days=1)
            title = f"{start} の予定"
        except ValueError:
            start = today
            end = today + timedelta(days=1)
            title = f"今日の予定 ({start})"

    return str(start), str(end), title


def main():
    args = sys.argv[1:]
    start_date, end_date, title = parse_args(args)

    try:
        results = query_events(start_date, end_date)
    except Exception as e:
        print(f"エラー: Notion APIの呼び出しに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    events = [parse_event(page) for page in results]

    print(f"📅 {title}")
    print()

    if not events:
        print("予定はありません")
    else:
        current_date = None
        for event in events:
            # 複数日表示の場合、日付ヘッダーを付ける
            jst_dt = to_jst(event["start"])
            event_date = str(jst_dt.date()) if jst_dt else (event["start"][:10] if event["start"] else "")
            if start_date != str(datetime.now(TZ).date()) or end_date != str(datetime.now(TZ).date() + timedelta(days=1)):
                if event_date != current_date:
                    if current_date is not None:
                        print()
                    weekday = ["月", "火", "水", "木", "金", "土", "日"]
                    try:
                        d = datetime.strptime(event_date, "%Y-%m-%d")
                        wd = weekday[d.weekday()]
                        print(f"**{event_date} ({wd})**")
                    except ValueError:
                        pass
                    current_date = event_date

            print(f"  {format_event(event)}")

    print(f"\n合計: {len(events)}件")


if __name__ == "__main__":
    main()
