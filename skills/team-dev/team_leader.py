#!/usr/bin/env python3
"""チーム開発リーダー — バックグラウンドで自律的に開発タスクを実行する

いずな（xangi）から起動され、claude CLIでサブエージェントを使って開発を進める。
判断が必要な時はreportsに質問を書き、いずな経由でDiscordに伝達する。

使い方:
  python team_leader.py                    # キューからタスクを取得して実行
  python team_leader.py --status           # 現在のタスク状態を表示
  python team_leader.py --answer "回答"    # ブロック中のタスクに回答を渡す
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).resolve().parent
WORKSPACE = SKILL_DIR.parent.parent
PROJECTS_DIR = WORKSPACE / "team-projects"  # チーム開発の作業ディレクトリ
QUEUE_FILE = SKILL_DIR / "task_queue.json"
REPORTS_FILE = SKILL_DIR / "reports.json"
LOG_FILE = SKILL_DIR / "leader.log"

# GitHub設定
GITHUB_ORG = "NikoToRA"  # GitHubユーザー/組織名

# サブエージェント実行のタイムアウト（秒）
SUBAGENT_TIMEOUT = 600  # 10分
# ユーザー回答待ちのポーリング間隔（秒）
POLL_INTERVAL = 30
# ユーザー回答待ちの最大時間（秒）
MAX_WAIT_FOR_ANSWER = 3600  # 1時間


def log(msg: str):
    """ログ出力（ファイル + stdout）"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_json(path: Path) -> dict | list:
    if not path.exists():
        return {} if path == REPORTS_FILE else []
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# === タスクキュー管理 ===

def get_queue() -> list:
    data = load_json(QUEUE_FILE)
    if isinstance(data, dict):
        return data.get("tasks", [])
    return data


def save_queue(tasks: list):
    save_json(QUEUE_FILE, {"tasks": tasks, "updated_at": datetime.now().isoformat()})


def get_next_task() -> Optional[dict]:
    """次の未処理タスクを取得"""
    tasks = get_queue()
    for task in tasks:
        if task.get("status") == "pending":
            return task
    return None


def update_task_status(task_id: str, status: str, result: str = None):
    """タスクのステータスを更新"""
    tasks = get_queue()
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
            if result:
                task["result"] = result
            break
    save_queue(tasks)


# === レポート管理 ===

def get_reports() -> dict:
    data = load_json(REPORTS_FILE)
    if not isinstance(data, dict):
        return {"messages": [], "questions": []}
    return data


def save_reports(data: dict):
    data["updated_at"] = datetime.now().isoformat()
    save_json(REPORTS_FILE, data)


def add_report(msg: str, report_type: str = "progress"):
    """進捗報告を追加"""
    reports = get_reports()
    if "messages" not in reports:
        reports["messages"] = []
    reports["messages"].append({
        "type": report_type,
        "message": msg,
        "timestamp": datetime.now().isoformat(),
        "delivered": False,
    })
    save_reports(reports)


def ask_user(question: str) -> Optional[str]:
    """ユーザーに質問し、回答を待つ"""
    reports = get_reports()
    if "questions" not in reports:
        reports["questions"] = []

    q_id = f"q_{int(time.time())}"
    reports["questions"].append({
        "id": q_id,
        "question": question,
        "timestamp": datetime.now().isoformat(),
        "answered": False,
        "answer": None,
    })
    save_reports(reports)
    log(f"質問を送信: {question}")

    # 回答を待つ
    waited = 0
    while waited < MAX_WAIT_FOR_ANSWER:
        time.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL

        reports = get_reports()
        for q in reports.get("questions", []):
            if q["id"] == q_id and q.get("answered"):
                log(f"回答を受信: {q['answer']}")
                return q["answer"]

    log("回答タイムアウト")
    return None


# === GitHub連携 ===

def create_github_repo(task: dict) -> Optional[str]:
    """タスク用のGitHubリポジトリを作成し、ローカルにcloneする。
    戻り値: リポジトリURL（失敗時None）"""
    task_id = task["id"]
    description = task["description"]

    # リポジトリ名を生成（task_idベース、安全な文字のみ）
    repo_name = f"team-{task_id}"
    local_dir = PROJECTS_DIR / repo_name

    # 既にローカルディレクトリがあればそのまま使う
    if local_dir.exists() and (local_dir / ".git").exists():
        log(f"既存リポジトリを使用: {local_dir}")
        repo_url = f"https://github.com/{GITHUB_ORG}/{repo_name}"
        return repo_url

    # team-projectsディレクトリ作成
    PROJECTS_DIR.mkdir(exist_ok=True)

    try:
        # GitHubにリポジトリ作成
        result = subprocess.run(
            ["gh", "repo", "create", repo_name, "--private", "--clone",
             "--description", description[:200]],
            capture_output=True, text=True, timeout=60,
            cwd=str(PROJECTS_DIR),
        )

        if result.returncode != 0:
            # 既にリモートにある場合はclone
            if "already exists" in result.stderr:
                log(f"リポジトリは既存、cloneします: {repo_name}")
                clone_result = subprocess.run(
                    ["gh", "repo", "clone", f"{GITHUB_ORG}/{repo_name}"],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(PROJECTS_DIR),
                )
                if clone_result.returncode != 0:
                    log(f"Clone失敗: {clone_result.stderr[:200]}")
                    return None
            else:
                log(f"リポジトリ作成失敗: {result.stderr[:200]}")
                return None

        repo_url = f"https://github.com/{GITHUB_ORG}/{repo_name}"

        # 初期README作成
        readme_path = local_dir / "README.md"
        if not readme_path.exists():
            readme_path.write_text(
                f"# {description}\n\nTask ID: `{task_id}`\n\n"
                f"Created: {datetime.now().isoformat()}\n\n"
                f"This repository was created by the team-dev autonomous development system.\n"
            )
            subprocess.run(
                ["git", "add", "-A"],
                cwd=str(local_dir), capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"Initial commit: {description[:50]}"],
                cwd=str(local_dir), capture_output=True
            )
            subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=str(local_dir), capture_output=True, timeout=30
            )

        log(f"リポジトリ作成完了: {repo_url}")
        return repo_url

    except Exception as e:
        log(f"GitHub連携エラー: {e}")
        return None


def push_to_github(local_dir: Path, message: str) -> bool:
    """ローカルの変更をコミット＆プッシュ"""
    try:
        # 変更があるかチェック
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(local_dir)
        )
        if not status.stdout.strip():
            log("変更なし、pushスキップ")
            return True

        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(local_dir), capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=str(local_dir), capture_output=True
        )
        result = subprocess.run(
            ["git", "push"],
            cwd=str(local_dir), capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            log(f"Push失敗: {result.stderr[:200]}")
            return False
        log(f"Push成功: {message[:50]}")
        return True
    except Exception as e:
        log(f"Push エラー: {e}")
        return False


# === サブエージェント実行 ===

def run_subagent(prompt: str, session_id: str = None, work_dir: Path = None) -> dict:
    """claude CLIでサブエージェントを実行"""
    args = [
        "claude", "-p",
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--model", "sonnet",
    ]

    if session_id:
        args.extend(["--resume", session_id])

    args.append(prompt)

    cwd = str(work_dir) if work_dir and work_dir.exists() else str(WORKSPACE)
    log(f"サブエージェント実行 (cwd={cwd}): {prompt[:80]}...")

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=SUBAGENT_TIMEOUT,
            cwd=cwd,
            env={**dict(__import__('os').environ), "CLAUDECODE": ""},  # ネスト防止を回避
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr[:500],
                "session_id": None,
            }

        try:
            response = json.loads(result.stdout.strip())
            return {
                "success": not response.get("is_error", False),
                "result": response.get("result", ""),
                "session_id": response.get("session_id", ""),
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "result": result.stdout[:2000],
                "session_id": None,
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"サブエージェントがタイムアウト（{SUBAGENT_TIMEOUT}秒）",
            "session_id": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_id": None,
        }


# === メインロジック ===

def execute_task(task: dict):
    """タスクを実行する"""
    task_id = task["id"]
    description = task["description"]
    details = task.get("details", "")

    log(f"=== タスク開始: {description} ===")
    update_task_status(task_id, "running")
    add_report(f"タスク開始: {description}", "start")

    # Step 0: GitHubリポジトリ作成
    repo_url = create_github_repo(task)
    repo_name = f"team-{task_id}"
    work_dir = PROJECTS_DIR / repo_name

    if repo_url:
        add_report(f"リポジトリ作成: {repo_url}", "progress")
        task["repo_url"] = repo_url
        update_task_status(task_id, "running")
    else:
        # リポジトリ作成失敗でもローカルで続行
        log("GitHubリポジトリ作成失敗、ローカルで続行")
        work_dir = PROJECTS_DIR / repo_name
        work_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=str(work_dir), capture_output=True)

    # Step 1: プラン立案
    plan_prompt = f"""以下の開発タスクのプランを立ててください。
具体的なステップに分解し、各ステップで何をするか明確にしてください。
JSON形式で出力: {{"steps": [{{"step": 1, "description": "...", "details": "..."}}]}}

タスク: {description}
{f'詳細: {details}' if details else ''}
作業ディレクトリ: {work_dir}"""

    plan_result = run_subagent(plan_prompt, work_dir=work_dir)

    if not plan_result["success"]:
        log(f"プラン立案失敗: {plan_result.get('error', 'unknown')}")
        answer = ask_user(f"タスク「{description}」のプラン立案に失敗しました。\nエラー: {plan_result.get('error', 'unknown')[:200]}\nどう進めますか？")
        if not answer:
            update_task_status(task_id, "failed", "プラン立案失敗・回答タイムアウト")
            add_report(f"タスク失敗: {description}（プラン立案失敗）", "error")
            return
        plan_prompt += f"\n\nユーザーからの指示: {answer}"
        plan_result = run_subagent(plan_prompt, work_dir=work_dir)
        if not plan_result["success"]:
            update_task_status(task_id, "failed", "プラン立案再失敗")
            add_report(f"タスク失敗: {description}", "error")
            return

    add_report(f"プラン完了。実装を開始します。", "progress")

    # Step 2: プランに基づいて実装
    session_id = None
    steps_done = 0

    implement_prompt = f"""以下のタスクを実装してください。プランに従って段階的に進めてください。
各ステップが完了したら次に進んでください。全て完了したら「全ステップ完了」と報告してください。

重要: 全てのファイルはこのディレクトリ内に作成してください: {work_dir}

タスク: {description}
{f'詳細: {details}' if details else ''}

プラン:
{plan_result.get('result', '')}

実装を開始してください。"""

    impl_result = run_subagent(implement_prompt, session_id=session_id, work_dir=work_dir)
    session_id = impl_result.get("session_id")
    steps_done += 1

    if impl_result["success"]:
        result_text = impl_result.get("result", "")

        # 追加の実装が必要かチェック
        if "全ステップ完了" not in result_text and steps_done < 5:
            continue_prompt = "続きを実装してください。完了したら「全ステップ完了」と報告してください。"
            cont_result = run_subagent(continue_prompt, session_id=session_id, work_dir=work_dir)
            session_id = cont_result.get("session_id") or session_id
            if cont_result["success"]:
                result_text = cont_result.get("result", "")

        # 成果物をGitHubにpush
        push_msg = f"Complete: {description[:50]}"
        pushed = push_to_github(work_dir, push_msg)

        repo_info = f"\nリポジトリ: {repo_url}" if repo_url else ""
        push_status = "（GitHubにpush済み）" if pushed else "（pushに失敗、ローカルのみ）"

        update_task_status(task_id, "completed", result_text[:1000])
        add_report(
            f"タスク完了: {description}{push_status}\n\n結果:\n{result_text[:400]}{repo_info}",
            "complete"
        )
        log(f"=== タスク完了: {description} ===")
    else:
        error_msg = impl_result.get("error", "unknown")
        answer = ask_user(f"タスク「{description}」の実装中にエラーが発生しました。\nエラー: {error_msg[:200]}\nどう対処しますか？")
        if answer:
            retry_prompt = f"以下のエラーが発生しました。ユーザーの指示に従って対処してください。\nエラー: {error_msg}\nユーザー指示: {answer}"
            retry_result = run_subagent(retry_prompt, session_id=session_id, work_dir=work_dir)
            if retry_result["success"]:
                push_to_github(work_dir, f"Fix and complete: {description[:40]}")
                repo_info = f"\nリポジトリ: {repo_url}" if repo_url else ""
                update_task_status(task_id, "completed", retry_result.get("result", "")[:1000])
                add_report(f"タスク完了（リトライ成功）: {description}{repo_info}", "complete")
                return

        update_task_status(task_id, "failed", error_msg[:500])
        add_report(f"タスク失敗: {description}\nエラー: {error_msg[:200]}", "error")
        log(f"=== タスク失敗: {description} ===")


def show_status():
    """現在のタスク状態を表示"""
    tasks = get_queue()
    reports = get_reports()

    if not tasks:
        print("タスクキューは空です")
        return

    print("=== タスク一覧 ===")
    for t in tasks:
        status_icon = {"pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌", "blocked": "🔒"}.get(t["status"], "?")
        print(f"  {status_icon} [{t['id']}] {t['description']} ({t['status']})")

    # 未回答の質問
    questions = [q for q in reports.get("questions", []) if not q.get("answered")]
    if questions:
        print("\n=== 未回答の質問 ===")
        for q in questions:
            print(f"  ❓ [{q['id']}] {q['question']}")

    # 未配信のメッセージ
    messages = [m for m in reports.get("messages", []) if not m.get("delivered")]
    if messages:
        print(f"\n=== 未配信レポート: {len(messages)}件 ===")


def deliver_answer(answer: str):
    """最新の未回答質問に回答する"""
    reports = get_reports()
    for q in reversed(reports.get("questions", [])):
        if not q.get("answered"):
            q["answered"] = True
            q["answer"] = answer
            q["answered_at"] = datetime.now().isoformat()
            save_reports(reports)
            log(f"回答を配信: {q['id']} -> {answer[:50]}")
            print(f"回答を配信しました: {q['question'][:50]}... -> {answer[:50]}")
            return
    print("未回答の質問がありません")


def main():
    parser = argparse.ArgumentParser(description="チーム開発リーダー")
    parser.add_argument("--status", action="store_true", help="タスク状態を表示")
    parser.add_argument("--answer", type=str, help="ブロック中のタスクに回答")
    parser.add_argument("--run-once", action="store_true", help="1タスクだけ実行して終了")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.answer:
        deliver_answer(args.answer)
        return

    # メインループ
    log("チームリーダー起動")

    task = get_next_task()
    if not task:
        log("実行待ちタスクなし")
        add_report("実行待ちタスクがありません。", "info")
        return

    execute_task(task)

    if not args.run_once:
        # 次のタスクがあれば続行
        next_task = get_next_task()
        while next_task:
            execute_task(next_task)
            next_task = get_next_task()

    log("チームリーダー終了")


if __name__ == "__main__":
    main()
