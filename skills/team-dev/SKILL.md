---
name: team-dev
description: チーム開発スキル。いずなの指揮下でチームリーダー＋サブエージェントが自律的に開発タスクを実行する。「開発して」「チームに任せて」「チーム状況」で使用。
---

# team-dev スキル

いずながチームリーダーを起動し、リーダーがサブエージェント（claude CLI）を使って自律的に開発する。
判断が必要な時はいずな経由でDiscordですぐるさんに質問する。

## アーキテクチャ

```
すぐるさん ←→ いずな（Discord窓口）←→ チームリーダー ←→ サブエージェント
                  伝達・報告              自律開発            並列作業
```

## トリガー

- 「○○を開発して」「チームに任せて」「チーム開発で○○」
- 「チーム状況」「開発進捗」→ ステータス表示
- 「チーム回答: ○○」→ リーダーからの質問に回答

## いずなの操作手順

### 1. タスク投入

ユーザーから開発依頼を受けたら、タスクキューにタスクを追加する：

```python
import json
from datetime import datetime
from pathlib import Path

queue_file = Path("[SKILL_DIR]/task_queue.json")
data = json.loads(queue_file.read_text()) if queue_file.exists() else {"tasks": []}

task = {
    "id": f"task_{int(datetime.now().timestamp())}",
    "description": "タスクの説明",
    "details": "詳細な要件（あれば）",
    "status": "pending",
    "created_at": datetime.now().isoformat(),
}
data["tasks"].append(task)
data["updated_at"] = datetime.now().isoformat()
queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
```

### 2. リーダー起動

```bash
cd skills/team-dev && bash run_leader.sh start
```

※ nohupでバックグラウンド実行されるのでタイムアウトしない

### 3. レポート確認（定期実行）

```bash
cd skills/team-dev && python3 check_reports.py
```

出力があればDiscordに転送する。スケジューラーで5分ごとに自動チェック。

### 4. ユーザー回答の伝達

ユーザーが「チーム回答: ○○」と言ったら：

```bash
cd skills/team-dev && python3 team_leader.py --answer "ユーザーの回答内容"
```

### 5. ステータス確認

```bash
cd skills/team-dev && bash run_leader.sh status
```

### 6. 停止

```bash
cd skills/team-dev && bash run_leader.sh stop
```

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `team_leader.py` | チームリーダー本体（バックグラウンド実行） |
| `run_leader.sh` | 起動・停止・ステータス管理 |
| `check_reports.py` | レポート監視（いずなのスケジューラーから実行） |
| `task_queue.json` | タスクキュー（いずな → リーダー） |
| `reports.json` | 報告・質問（リーダー → いずな） |
| `leader.log` | リーダーのログ |

## GitHub連携

タスクごとに専用のGitHubリポジトリが自動作成される。

- リポジトリ名: `team-{task_id}`（privateリポジトリ）
- 作業ディレクトリ: `team-projects/team-{task_id}/`（メインリポジトリの.gitignoreに含まれる）
- サブエージェントはこのディレクトリ内で開発を行う
- タスク完了時に自動でcommit & push
- 完了レポートにはGitHubリポジトリのURLが含まれる

## 制約

- サブエージェントは逐次実行（Maxプランのレートリミット対策）
- サブエージェントのモデルは `sonnet`（Opusより速く、レートリミットに余裕あり）
- 1タスクの最大実行時間: サブエージェント1回あたり10分 × 複数ステップ
- ユーザー回答待ちの最大時間: 1時間
