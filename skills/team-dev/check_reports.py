#!/usr/bin/env python3
"""レポートチェッカー — いずなのスケジューラーから定期実行される

未配信のメッセージや未回答の質問があれば、Discordに送信するテキストを出力する。
出力がなければ何もなし。
"""

import json
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
REPORTS_FILE = SKILL_DIR / "reports.json"


def check():
    if not REPORTS_FILE.exists():
        return

    with open(REPORTS_FILE) as f:
        reports = json.load(f)

    output = []

    # 未配信メッセージ
    for msg in reports.get("messages", []):
        if not msg.get("delivered"):
            icon = {"start": "🚀", "progress": "📝", "complete": "✅", "error": "❌", "info": "ℹ️"}.get(msg["type"], "📌")
            output.append(f"{icon} {msg['message']}")
            msg["delivered"] = True

    # 未回答の質問
    for q in reports.get("questions", []):
        if not q.get("answered"):
            output.append(f"❓ チームリーダーからの質問:\n{q['question']}\n\n回答するには「チーム回答: ○○」と返信してください。")

    if output:
        # レポートファイルを更新（delivered フラグ）
        reports["updated_at"] = datetime.now().isoformat()
        with open(REPORTS_FILE, "w") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

        # 出力
        print("\n".join(output))


if __name__ == "__main__":
    check()
