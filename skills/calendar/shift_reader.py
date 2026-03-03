#!/usr/bin/env python3
"""
Google Sheets シフト表読み取り → Google Calendar 登録スクリプト

使い方:
  # シフト表を読み取って表示（ドライラン）
  python shift_reader.py

  # Google Calendar に登録
  python shift_reader.py --register

  # 特定の月だけ処理（デフォルトはシート上の全データ）
  python shift_reader.py --register --month 2026-03

  # カレンダーIDを指定
  python shift_reader.py --register --calendar-id your_calendar@gmail.com

  # 登録済みイベントを削除
  python shift_reader.py --delete --month 2026-03
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

# config.local.json から設定を読み込み
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "lib"))
from config import get_google_config, get_google_service_account_file, get_google_spreadsheet_id, get_google_calendar_id

# === 設定 ===
SPREADSHEET_ID = get_google_spreadsheet_id()
SERVICE_ACCOUNT_FILE = get_google_service_account_file()
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/calendar",
]

# Google Calendar IDs
CALENDAR_TOUJOKU = get_google_calendar_id("toujoku")  # 当直
CALENDAR_NIKKIN = get_google_calendar_id("nikkin")     # 日勤待機

# シフト種別 → カレンダー振り分け
# 準夜勤・夜勤 → 当直カレンダー、日勤・待機 → 日勤待機カレンダー
SHIFT_TO_CALENDAR = {
    "日勤": CALENDAR_NIKKIN,
    "準": CALENDAR_TOUJOKU,
    "夜": CALENDAR_TOUJOKU,
    "待": CALENDAR_NIKKIN,
}

# 平（ユーザー）の列インデックス（0-based、5週間ブロック）
USER_COLUMNS = [3, 14, 25, 36, 47]
# 日付列インデックス
DATE_COLUMNS = [2, 13, 24, 35, 46]

# シフト種別の行オフセットと時間マッピング
# 各曜日ブロックは6行: 早, A, P, 準, 夜, 待
# 早出は対象外。A/Pは「日勤」として統合（どちらかが色付きなら日勤）
SHIFT_ROWS = {
    "A": 1,
    "P": 2,
    "準": 3,
    "夜": 4,
    "待": 5,
}

# シフト時間帯（平日）
SHIFT_TIMES_WEEKDAY = {
    "日勤": ("09:00", "17:00"),
    "準": ("17:00", "23:00"),
    "夜": ("23:00", "09:00"),  # 翌日まで
    "待": ("17:00", "09:00"),  # 待機（オンコール）
}

# シフト時間帯（土日祝）
SHIFT_TIMES_WEEKEND = {
    "日勤": ("09:00", "19:00"),
    "準": ("19:00", "23:00"),
    "夜": ("19:00", "09:00"),  # 翌日まで
    "待": ("19:00", "09:00"),
}

# 勤務を示す背景色（RGB） — マゼンタのみが出勤
WORK_COLORS = [
    (1.0, 0.0, 1.0),      # マゼンタ
]
COLOR_THRESHOLD = 0.15  # 色マッチングの許容誤差


def is_work_color(bg_color: dict) -> bool:
    """セルの背景色が勤務色（ピンク or マゼンタ）かどうか判定"""
    if not bg_color:
        return False
    r = bg_color.get("red", 0)
    g = bg_color.get("green", 0)
    b = bg_color.get("blue", 0)
    for wr, wg, wb in WORK_COLORS:
        if (abs(r - wr) < COLOR_THRESHOLD and
            abs(g - wg) < COLOR_THRESHOLD and
            abs(b - wb) < COLOR_THRESHOLD):
            return True
    return False


def is_weekend_or_holiday(dt: datetime) -> bool:
    """土日かどうか判定（祝日は簡易判定のため省略）"""
    return dt.weekday() >= 5  # 5=Saturday, 6=Sunday


def get_shift_times(shift_type: str, date: datetime, is_holiday: bool = False) -> tuple:
    """シフト種別と日付から開始・終了時刻を返す"""
    if is_weekend_or_holiday(date) or is_holiday:
        times = SHIFT_TIMES_WEEKEND.get(shift_type)
    else:
        times = SHIFT_TIMES_WEEKDAY.get(shift_type)
    if not times:
        return None, None
    return times


def authenticate():
    """サービスアカウント認証"""
    creds = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE), scopes=SCOPES
    )
    return creds


def find_sheet_name(creds, year: int, month: int) -> str:
    """指定年月に対応するシート名を探す

    シート名パターン: "2026/3", "2026/3(作成途中)" など
    """
    sheets_service = build("sheets", "v4", credentials=creds)
    result = sheets_service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
    ).execute()

    target = f"{year}/{month}"
    for sheet in result.get("sheets", []):
        title = sheet["properties"]["title"]
        # "2026/3" or "2026/3(作成途中)" などにマッチ
        if title.startswith(target):
            return title

    return None


def read_shifts(creds, target_month: str = None) -> list:
    """Google Sheets からシフトデータを読み取る

    target_month: "YYYY-MM" 形式。指定すると対応するシートタブを自動選択。
                  未指定の場合は先頭シートを使用。

    シート構造:
    - Row 0: ヘッダー（平, 安, 山, ...）
    - Row 1-6: 月曜（早, A, P, 準, 夜, 待）
    - Row 7-12: 火曜
    - Row 13-18: 水曜
    - Row 19-24: 木曜
    - Row 25-30: 金曜
    - Row 31-36: 土曜
    - Row 37-42: 日曜
    - 5週分が横に並ぶ（列ブロック）
    - 日付は各曜日の先頭行（早の行）の日付列に記載
    """
    sheets_service = build("sheets", "v4", credentials=creds)

    # シートタブを特定
    sheet_name = None
    if target_month:
        year, month = map(int, target_month.split("-"))
        sheet_name = find_sheet_name(creds, year, month)
        if not sheet_name:
            print(f"⚠️  {target_month} に対応するシートが見つかりません")
            return []
        print(f"📄 シート: {sheet_name}")

    range_prefix = f"'{sheet_name}'!" if sheet_name else ""

    result = sheets_service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        ranges=[f"{range_prefix}A1:BF50"],
        includeGridData=True,
    ).execute()

    sheet_data = result["sheets"][0]["data"][0]
    rows = sheet_data.get("rowData", [])

    # 曜日ごとの開始行（0-based）
    DAY_START_ROWS = {
        0: 1,   # 月曜 → row 1
        1: 7,   # 火曜 → row 7
        2: 13,  # 水曜 → row 13
        3: 19,  # 木曜 → row 19
        4: 25,  # 金曜 → row 25
        5: 31,  # 土曜 → row 31
        6: 37,  # 日曜 → row 37
    }

    # シフト種別の行オフセット（曜日開始行からの相対位置）
    SHIFT_OFFSETS = {"早": 0, "A": 1, "P": 2, "準": 3, "夜": 4, "待": 5}

    shifts = []
    holiday_dates = set()

    # 各週ブロック × 各曜日を処理
    for week_idx in range(5):
        user_col = USER_COLUMNS[week_idx]
        date_col = DATE_COLUMNS[week_idx]

        for day_idx in range(7):  # 月〜日
            day_start = DAY_START_ROWS[day_idx]

            # 日付を取得（曜日の先頭行 = 早の行）
            date_str = None
            if day_start < len(rows):
                cells = rows[day_start].get("values", [])
                if date_col < len(cells):
                    date_str = cells[date_col].get("formattedValue", "")

            if not date_str:
                continue

            # 日付をパース
            try:
                clean = date_str.replace("日", "").strip()
                parts = clean.split("/")
                if len(parts) == 2:
                    month, day = int(parts[0]), int(parts[1])
                    now = datetime.now()
                    year = now.year
                    if month < now.month - 6:
                        year += 1
                    date_obj = datetime(year, month, day)
                else:
                    continue
            except (ValueError, IndexError):
                continue

            # 祝日チェック（日付列の近くに「(祝)」がある場合）
            for check_offset in range(6):
                check_r = day_start + check_offset
                if check_r < len(rows):
                    check_cells = rows[check_r].get("values", [])
                    if date_col < len(check_cells):
                        v = check_cells[date_col].get("formattedValue", "")
                        if "祝" in v:
                            holiday_dates.add(date_obj.strftime("%Y-%m-%d"))

            # 各シフト種別をチェック
            date_key = date_obj.strftime("%Y-%m-%d")
            is_holiday = date_key in holiday_dates

            # まず各シフト種別のマゼンタ有無を収集
            colored = set()
            for shift_name, offset in SHIFT_OFFSETS.items():
                check_row = day_start + offset
                if check_row >= len(rows):
                    continue
                cells = rows[check_row].get("values", [])
                if user_col >= len(cells):
                    continue
                cell = cells[user_col]
                bg_color = cell.get("effectiveFormat", {}).get(
                    "backgroundColor", {}
                )
                if is_work_color(bg_color):
                    colored.add(shift_name)

            if not colored:
                continue

            # 統合ルール:
            # - A/P → 「日勤」（重複なし）
            # - 準+夜 → 「夜勤」に統合（準夜勤の開始〜夜勤の終了）
            # - 準のみ → 「準夜勤」
            # - 夜のみ → 「夜勤」
            has_nikkin = bool(colored & {"A", "P"})
            has_jun = "準" in colored
            has_yoru = "夜" in colored
            has_taiki = "待" in colored

            weekday_names = ["月", "火", "水", "木", "金", "土", "日"]
            wd = weekday_names[date_obj.weekday()]

            if has_nikkin:
                start_time, end_time = get_shift_times("日勤", date_obj, is_holiday=is_holiday)
                if start_time:
                    shifts.append({
                        "date": date_key, "date_obj": date_obj,
                        "shift_type": "日勤", "start_time": start_time,
                        "end_time": end_time, "weekday": wd,
                        "is_holiday": is_holiday,
                    })

            if has_jun and has_yoru:
                # 準夜勤+夜勤 → 夜勤として統合（準の開始〜夜の終了）
                jun_start, _ = get_shift_times("準", date_obj, is_holiday=is_holiday)
                _, yoru_end = get_shift_times("夜", date_obj, is_holiday=is_holiday)
                if jun_start and yoru_end:
                    shifts.append({
                        "date": date_key, "date_obj": date_obj,
                        "shift_type": "夜", "start_time": jun_start,
                        "end_time": yoru_end, "weekday": wd,
                        "is_holiday": is_holiday,
                    })
            elif has_jun:
                start_time, end_time = get_shift_times("準", date_obj, is_holiday=is_holiday)
                if start_time:
                    shifts.append({
                        "date": date_key, "date_obj": date_obj,
                        "shift_type": "準", "start_time": start_time,
                        "end_time": end_time, "weekday": wd,
                        "is_holiday": is_holiday,
                    })
            elif has_yoru:
                start_time, end_time = get_shift_times("夜", date_obj, is_holiday=is_holiday)
                if start_time:
                    shifts.append({
                        "date": date_key, "date_obj": date_obj,
                        "shift_type": "夜", "start_time": start_time,
                        "end_time": end_time, "weekday": wd,
                        "is_holiday": is_holiday,
                    })

            if has_taiki:
                start_time, end_time = get_shift_times("待", date_obj, is_holiday=is_holiday)
                if start_time:
                    shifts.append({
                        "date": date_key, "date_obj": date_obj,
                        "shift_type": "待", "start_time": start_time,
                        "end_time": end_time, "weekday": wd,
                        "is_holiday": is_holiday,
                    })

    # 日付とシフト種別でソート
    shift_order = {"日勤": 0, "準": 1, "夜": 2, "待": 3}
    shifts.sort(key=lambda s: (s["date"], shift_order.get(s["shift_type"], 9)))

    return shifts


def get_existing_shifts(creds, month: str) -> set:
    """指定月の登録済みシフトイベントのキー（日付+種別）を取得"""
    cal_service = build("calendar", "v3", credentials=creds)

    year, mon = map(int, month.split("-"))
    time_min = datetime(year, mon, 1).strftime("%Y-%m-%dT00:00:00+09:00")
    if mon == 12:
        time_max = datetime(year + 1, 1, 1).strftime("%Y-%m-%dT00:00:00+09:00")
    else:
        time_max = datetime(year, mon + 1, 1).strftime("%Y-%m-%dT00:00:00+09:00")

    existing = set()
    for cal_id in [CALENDAR_TOUJOKU, CALENDAR_NIKKIN]:
        events_result = cal_service.events().list(
            calendarId=cal_id,
            timeMin=time_min,
            timeMax=time_max,
            q="勤務:",
            singleEvents=True,
        ).execute()

        for event in events_result.get("items", []):
            desc = event.get("description", "")
            if "シフト表から自動登録" not in desc:
                continue
            # descriptionから種別と日付を抽出してキーにする
            for line in desc.split("\n"):
                if line.startswith("種別:"):
                    shift_type = line.split(":")[1].strip()
                if line.startswith("日付:"):
                    date_str = line.split(":")[1].split("(")[0].strip()
            existing.add(f"{date_str}_{shift_type}")

    return existing


def register_to_calendar(creds, shifts: list, calendar_id: str = None):
    """Google Calendar にシフトを登録

    calendar_id を指定すると全てそのカレンダーに登録。
    指定しない場合は SHIFT_TO_CALENDAR に基づいて当直/日勤待機に振り分け。
    重複チェック: 同じ日付+種別のイベントが既に存在する場合はスキップ。
    """
    cal_service = build("calendar", "v3", credentials=creds)

    # 重複チェック用: 登録済みイベントのキーを取得
    if shifts:
        month_key = shifts[0]["date"][:7]
        existing = get_existing_shifts(creds, month_key)
        if existing:
            print(f"  📋 既存登録: {len(existing)}件")
    else:
        existing = set()

    shift_labels = {
        "日勤": "日勤",
        "準": "準夜勤",
        "夜": "夜勤",
        "待": "待機(オンコール)",
    }

    registered = 0
    skipped = 0
    for shift in shifts:
        date_obj = shift["date_obj"]
        start_time = shift["start_time"]
        end_time = shift["end_time"]
        shift_type = shift["shift_type"]

        # 開始・終了のdatetimeを構築
        sh, sm = map(int, start_time.split(":"))
        eh, em = map(int, end_time.split(":"))

        start_dt = date_obj.replace(hour=sh, minute=sm, second=0)

        # 夜勤・待機は翌日にまたがる
        if eh < sh:
            end_dt = (date_obj + timedelta(days=1)).replace(hour=eh, minute=em, second=0)
        else:
            end_dt = date_obj.replace(hour=eh, minute=em, second=0)

        # イベント名
        is_special = is_weekend_or_holiday(date_obj) or shift.get("is_holiday")
        weekend_mark = "🏥" if is_special else ""
        summary = f"{weekend_mark}勤務: {shift_labels.get(shift_type, shift_type)}"

        # 重複チェック
        shift_key = f"{shift['date']}_{shift_type}"
        if shift_key in existing:
            skipped += 1
            cal_name = "当直" if SHIFT_TO_CALENDAR.get(shift_type) == CALENDAR_TOUJOKU else "日勤待機"
            print(f"  - [{cal_name}] {shift['date']}({shift['weekday']}) "
                  f"{shift_labels.get(shift_type, shift_type)} → 登録済みのためスキップ")
            continue

        # カレンダー振り分け
        target_cal = calendar_id or SHIFT_TO_CALENDAR.get(shift_type, CALENDAR_NIKKIN)

        event = {
            "summary": summary,
            "start": {
                "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Asia/Tokyo",
            },
            "end": {
                "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Asia/Tokyo",
            },
            "description": f"シフト表から自動登録\n種別: {shift_type}\n日付: {shift['date']}({shift['weekday']})",
        }

        try:
            cal_service.events().insert(
                calendarId=target_cal, body=event
            ).execute()
            registered += 1
            cal_name = "当直" if target_cal == CALENDAR_TOUJOKU else "日勤待機"
            print(f"  ✓ [{cal_name}] {shift['date']}({shift['weekday']}) "
                  f"{shift_labels.get(shift_type, shift_type)} {start_time}-{end_time}")
        except Exception as e:
            print(f"  ✗ {shift['date']} {shift_type}: {e}")

    return registered, skipped


def delete_shifts(creds, month: str, calendar_id: str = None):
    """指定月のシフトイベントを削除（両カレンダーから）"""
    cal_service = build("calendar", "v3", credentials=creds)

    year, mon = map(int, month.split("-"))
    time_min = datetime(year, mon, 1).strftime("%Y-%m-%dT00:00:00+09:00")
    if mon == 12:
        time_max = datetime(year + 1, 1, 1).strftime("%Y-%m-%dT00:00:00+09:00")
    else:
        time_max = datetime(year, mon + 1, 1).strftime("%Y-%m-%dT00:00:00+09:00")

    calendars = [calendar_id] if calendar_id else [CALENDAR_TOUJOKU, CALENDAR_NIKKIN]
    cal_names = {CALENDAR_TOUJOKU: "当直", CALENDAR_NIKKIN: "日勤待機"}

    deleted = 0
    for cal_id in calendars:
        events_result = cal_service.events().list(
            calendarId=cal_id,
            timeMin=time_min,
            timeMax=time_max,
            q="勤務:",
            singleEvents=True,
        ).execute()

        events = events_result.get("items", [])
        for event in events:
            if "シフト表から自動登録" in event.get("description", ""):
                cal_service.events().delete(
                    calendarId=cal_id, eventId=event["id"]
                ).execute()
                deleted += 1
                name = cal_names.get(cal_id, cal_id)
                print(f"  削除: [{name}] {event['summary']} ({event['start'].get('dateTime', '')})")

    return deleted


def main():
    parser = argparse.ArgumentParser(description="シフト表読み取り・カレンダー登録")
    parser.add_argument("--register", action="store_true", help="Google Calendarに登録")
    parser.add_argument("--delete", action="store_true", help="登録済みシフトを削除")
    parser.add_argument("--month", type=str, help="対象月 (YYYY-MM)")
    parser.add_argument("--calendar-id", type=str, default=None,
                        help="Google Calendar ID (default: auto-route to 当直/日勤待機)")
    parser.add_argument("--json", action="store_true", help="JSON形式で出力")
    args = parser.parse_args()

    creds = authenticate()

    if args.delete:
        if not args.month:
            print("--delete には --month が必要です")
            sys.exit(1)
        print(f"📅 {args.month} のシフトイベントを削除中...")
        deleted = delete_shifts(creds, args.month, args.calendar_id)
        print(f"\n{deleted}件削除しました")
        return

    # シフト読み取り
    print("📋 シフト表を読み取り中...")
    shifts = read_shifts(creds, target_month=args.month)

    if not shifts:
        print("該当するシフトが見つかりませんでした")
        return

    if args.json:
        output = [{k: v for k, v in s.items() if k != "date_obj"} for s in shifts]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 表示
    print(f"\n{'='*50}")
    print(f"  シフト一覧 ({len(shifts)}件)")
    print(f"{'='*50}")
    current_date = None
    for s in shifts:
        if s["date"] != current_date:
            current_date = s["date"]
            is_special = is_weekend_or_holiday(s["date_obj"]) or s.get("is_holiday")
            marker = "🏥" if is_special else "  "
            holiday_tag = " (祝)" if s.get("is_holiday") and s["date_obj"].weekday() < 5 else ""
            print(f"\n{marker} {s['date']} ({s['weekday']}{holiday_tag})")

        shift_labels = {"日勤": "日勤", "準": "準夜勤", "夜": "夜勤", "待": "待機"}
        label = shift_labels.get(s["shift_type"], s["shift_type"])
        print(f"    {label}: {s['start_time']} - {s['end_time']}")

    if args.register:
        print(f"\n📅 Google Calendarに登録中...")
        registered, skipped = register_to_calendar(creds, shifts, args.calendar_id)
        msg = f"\n✅ {registered}件登録"
        if skipped:
            msg += f"、{skipped}件スキップ（重複）"
        msg += f"（全{len(shifts)}件中）"
        print(msg)
    else:
        print(f"\n💡 --register オプションでGoogle Calendarに登録できます")


if __name__ == "__main__":
    main()
