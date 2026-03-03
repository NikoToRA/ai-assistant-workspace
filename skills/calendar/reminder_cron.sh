#!/bin/bash
# 予定の10分前リマインダー（crontabで5分ごとに実行）
# 出力がある場合のみxangiのスケジュール経由で通知

SKILL_DIR="$(dirname "$(realpath "$0")")"
cd "$SKILL_DIR" || exit 1

OUTPUT=$(.venv/bin/python event_reminder.py 2>/dev/null)

if [ -n "$OUTPUT" ]; then
    echo "$OUTPUT"
fi
