#!/bin/bash
cd /home/aibot/ai-assistant-workspace

# 変更があるか確認
if git status --porcelain | grep -q .; then
    git add -A
    git commit -m "daily: $(date '+%Y-%m-%d') 自動コミット"
    git push origin main
    echo "[$(date)] push完了" >> /tmp/daily-push.log
else
    echo "[$(date)] 変更なし、スキップ" >> /tmp/daily-push.log
fi
