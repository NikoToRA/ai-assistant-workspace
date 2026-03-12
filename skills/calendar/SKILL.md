---
name: calendar
description: カレンダー予定を確認・追加するスキル。ICS（Googleカレンダー等）と手動追加（画像読み取り）を統合。「今日の予定」「明日の予定」「カレンダー画像送って」「スケジュール確認」「〇〇を予定に入れて」で使用。`/calendar` で発動。
---

# calendar スキル

ICSカレンダー（Googleカレンダー等）＋ 手動追加の予定（画像読み取り等）を統合して予定を確認する。

## 予定の追加（Googleカレンダー API）

「〇〇をカレンダーに入れて」「予定を登録して」と言われたら **Googleカレンダー（main）に直接登録する**。
manual_events.jsonやNotionではなく、Google Calendar APIを使うこと。

```python
# skills/calendar/ で uv run python - として実行
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "lib"))
from config import get_google_service_account_file, get_google_calendar_id
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = get_google_service_account_file()
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = get_google_calendar_id("main")  # super206cc@gmail.com

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build("calendar", "v3", credentials=creds)

event = {
    "summary": "イベント名",
    "description": "メモ",
    "start": {"dateTime": "2026-03-13T21:00:00+09:00", "timeZone": "Asia/Tokyo"},
    "end":   {"dateTime": "2026-03-13T22:00:00+09:00", "timeZone": "Asia/Tokyo"},
}
result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
print(f"✅ 登録完了: {result.get('htmlLink')}")
```

終了時刻が不明な場合は開始から1時間後をデフォルトとする。

## セットアップ

`[SKILL_DIR]/calendar_urls.json` にICS URLを登録する：

```json
{
  "calendars": [
    {
      "name": "main",
      "url": "https://calendar.google.com/calendar/ical/xxxxx/basic.ics"
    },
    {
      "name": "family",
      "label": "家族",
      "url": "https://calendar.google.com/calendar/ical/yyyyy/basic.ics"
    }
  ]
}
```

- `name`: カレンダー識別名（必須）
- `url`: ICSのURL（必須）。Googleカレンダーの場合「設定 → カレンダーの統合 → iCal形式の非公開URL」
- `label`: 表示ラベル（任意）。設定すると予定に `[家族]` のようなタグが付く。共有カレンダーなど、自分の予定とは限らないものに付けると便利

## コマンド

### Notionカレンダー（メイン）

```bash
cd skills/calendar && .venv/bin/python notion_calendar.py [引数]
```

- `today` / 引数なし → 今日
- `tomorrow` → 明日
- `week` → 今後7日間

Notion DB ID: `config.local.json` の `notion.databases.todo` を参照

### ICSカレンダー（補助）

```bash
cd skills/calendar && .venv/bin/python calendar_check.py [引数]
```

- `today` / 引数なし → 今日
- `tomorrow` → 明日
- `week` → 今後7日間
- `0 7` → 今日から7日間（範囲指定）
- `-7 0` → 過去7日間

## 画像からの予定追加

カレンダーのスクリーンショットが送られたら：

### Step 1: 画像を読み取る

添付画像を Read ツールで確認する。

### Step 2: 予定を抽出

画像から以下の情報を読み取る：
- 日付、開始時刻、終了時刻、予定名
- 終日予定かどうか

### Step 3: manual_events.json に保存

`[SKILL_DIR]/manual_events.json` に保存。既存の予定と**マージ**する（同じ日付の予定は上書き）。

```json
{
  "events": [
    {
      "date": "2026-03-01",
      "time_start": "09:00",
      "time_end": "10:00",
      "summary": "ミーティング",
      "all_day": false
    },
    {
      "date": "2026-03-01",
      "summary": "有給休暇",
      "all_day": true
    }
  ],
  "updated_at": "2026-03-01T12:00:00+09:00"
}
```

### 保存ルール

- 同じ日付の予定は**上書き**（最新の画像が正）
- `updated_at` を更新時刻に設定
- 過去の予定は放置OK（表示時にフィルタされる）

### Step 4: 再確認

保存後、`calendar_check.py` を再実行して反映を確認。

## シフト表 → Google Calendar 登録

Google Sheetsのシフト表からセル背景色（マゼンタ）を読み取り、Google Calendarに自動登録する。

### トリガー

- 「シフト登録して」「来月のシフト入れて」「シフト表読み取って」
- 月末3日前に自動実行（スケジュールID: `sch_shift_register`）

### コマンド

```bash
cd skills/calendar

# 来月のシフトを確認（ドライラン）
.venv/bin/python shift_reader.py --month YYYY-MM

# Google Calendarに登録（重複チェック付き）
.venv/bin/python shift_reader.py --month YYYY-MM --register

# 登録済みシフトを削除
.venv/bin/python shift_reader.py --delete --month YYYY-MM
```

### 自動実行時の動作

1. 翌月の `YYYY-MM` を算出
2. `--register` で登録（重複は自動スキップ）
3. 結果をチャンネルに報告

### 仕様

- **データソース**: Google Sheets（IDは `config.local.json` の `google.spreadsheet_id`）
- **判定色**: マゼンタ RGB(1,0,1) のみ（ピンクは勤務ではない）
- **シフト種別と統合ルール**:
  - A/P → 「日勤」に統合（平日 9-17、土日祝 9-19）
  - 準夜勤 + 夜勤 → 「夜勤」に統合（準の開始〜夜の終了）
  - 準夜勤のみ → そのまま「準夜勤」
  - 待機 → 「待機(オンコール)」
- **カレンダー振り分け**:
  - 当直カレンダー: 準夜勤、夜勤
  - 日勤待機カレンダー: 日勤、待機
- **重複防止**: description内の種別・日付で既存イベントと照合、登録済みはスキップ
- **タブ自動選択**: シート名 `YYYY/M` パターンで対応タブを自動検出

## 飛行機予定の移動時間ルール

飛行機の予定を登録する際は、前後に **「移動」** イベントを自動で追加する。

- **出発前**: フライト出発の前に「移動（空港へ）」を登録
- **到着後**: フライト到着後に「移動（空港から）」を登録
- 飛行機だと判断できるキーワード: 「フライト」「飛行機」「航空」「空港」「ANA」「JAL」「便」など
- 移動イベントの登録先カレンダー: フライト本体と同じカレンダー

### 移動時間の判定

| 空港 | 移動時間 |
|------|----------|
| **新千歳空港**（CTS / 千歳 / 新千歳） | **2時間** |
| **それ以外の空港** | **1時間半** |

出発地・到着地のどちらかが新千歳なら、その区間の移動を2時間にする。不明な場合はデフォルト1時間半。

### 例

羽田→新千歳 10:00〜11:30 の場合
- 08:30〜10:00 移動（空港へ）← 羽田なので1.5時間
- 11:30〜13:30 移動（空港から）← 新千歳なので2時間

新千歳→羽田 14:00〜15:30 の場合
- 12:00〜14:00 移動（空港へ）← 新千歳なので2時間
- 15:30〜17:00 移動（空港から）← 羽田なので1.5時間

## チェックリスト（実行時に必ず確認）

- [ ] `calendar_urls.json` が存在するか（初回はセットアップを案内）
- [ ] 画像から予定を追加した場合、保存後に再実行して確認したか
- [ ] **🚨 共有カレンダーの予定を「あなたの予定」と断定しない**（labelで区別する）
