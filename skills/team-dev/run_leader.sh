#!/bin/bash
# チームリーダーをバックグラウンドで起動する
# nohupで実行するのでxangiのタイムアウトに影響されない

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/leader.log"
PID_FILE="$SCRIPT_DIR/leader.pid"

case "${1:-start}" in
  start)
    # 既に実行中かチェック
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "チームリーダーは既に実行中です (PID: $(cat "$PID_FILE"))"
      exit 0
    fi

    echo "チームリーダーを起動中..."
    # CLAUDECODE環境変数を外してネスト制限を回避
    unset CLAUDECODE
    nohup python3 "$SCRIPT_DIR/team_leader.py" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "起動完了 (PID: $!)"
    echo "ログ: $LOG_FILE"
    ;;

  stop)
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "チームリーダーを停止しました (PID: $PID)"
      else
        echo "プロセスは既に終了しています"
      fi
      rm -f "$PID_FILE"
    else
      echo "PIDファイルが見つかりません"
    fi
    ;;

  status)
    python3 "$SCRIPT_DIR/team_leader.py" --status
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo -e "\nリーダープロセス: 実行中 (PID: $(cat "$PID_FILE"))"
    else
      echo -e "\nリーダープロセス: 停止中"
    fi
    ;;

  log)
    tail -50 "$LOG_FILE" 2>/dev/null || echo "ログファイルがありません"
    ;;

  *)
    echo "Usage: $0 {start|stop|status|log}"
    ;;
esac
