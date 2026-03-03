"""ワークスペース共通設定ローダー

config.local.json から機密情報を読み込む。
リポジトリルートに config.local.json を配置すること（gitignore済み）。
テンプレートは config.example.json を参照。
"""

import json
from pathlib import Path

_config = None
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_FILE = _WORKSPACE_ROOT / "config.local.json"


def load_config() -> dict:
    """設定ファイルを読み込む（キャッシュあり）"""
    global _config
    if _config is not None:
        return _config

    if not _CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"設定ファイルが見つかりません: {_CONFIG_FILE}\n"
            f"config.example.json をコピーして config.local.json を作成してください"
        )

    with open(_CONFIG_FILE) as f:
        _config = json.load(f)
    return _config


def get_notion_config() -> dict:
    """Notion関連の設定を取得"""
    return load_config()["notion"]


def get_google_config() -> dict:
    """Google関連の設定を取得"""
    return load_config()["google"]


def get_notion_db_id(name: str) -> str:
    """Notion DB IDを取得（例: 'todo', 'memory'）"""
    return get_notion_config()["databases"][name]


def get_notion_api_key() -> str:
    """Notion APIキーを取得"""
    api_key_file = Path(get_notion_config()["api_key_file"]).expanduser()
    return api_key_file.read_text().strip()


def get_google_calendar_id(name: str) -> str:
    """Google Calendar IDを取得（例: 'toujoku', 'nikkin'）"""
    return get_google_config()["calendars"][name]


def get_google_spreadsheet_id() -> str:
    """Google Spreadsheet IDを取得"""
    return get_google_config()["spreadsheet_id"]


def get_google_service_account_file() -> Path:
    """Googleサービスアカウントファイルのパスを取得"""
    return Path(get_google_config()["service_account_file"]).expanduser()
