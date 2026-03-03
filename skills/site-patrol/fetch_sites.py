#!/usr/bin/env python3
"""サイト巡回スクリプト: sites.yaml のRSSフィードを取得し、カテゴリ別に新着記事を出力する。"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml

CATEGORY_LABELS = {
    "tech": "TECH（技術全般）",
    "ai": "AI・機械学習",
    "medical": "医療・ヘルステック",
    "gadget": "ガジェット・IoT",
    "blog": "ブログ",
    "news": "ニュース",
}

JST = timezone(timedelta(hours=9))


def load_sites(yaml_path: Path, category_filter: str | None = None) -> list[dict]:
    """sites.yaml を読み込み、オプションでカテゴリフィルタする。"""
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    sites = data.get("sites", [])
    if category_filter:
        sites = [s for s in sites if s.get("category") == category_filter]
    return sites


def fetch_feed(url: str, max_entries: int = 5) -> list[dict]:
    """RSSフィードを取得し、エントリのリストを返す。"""
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries[:max_entries]:
        published = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                published = dt.astimezone(JST).strftime("%m/%d %H:%M")
            except (ValueError, TypeError):
                pass

        entries.append({
            "title": entry.get("title", "(タイトルなし)"),
            "link": entry.get("link", ""),
            "published": published,
        })
    return entries


def patrol(yaml_path: Path, category_filter: str | None = None, max_entries: int = 5) -> str:
    """巡回を実行し、マークダウン形式の結果を返す。"""
    sites = load_sites(yaml_path, category_filter)
    if not sites:
        return "巡回先が見つかりませんでした。sites.yaml を確認してください。"

    # カテゴリ別にグループ化
    by_category: dict[str, list[dict]] = {}
    for site in sites:
        cat = site.get("category", "other")
        by_category.setdefault(cat, []).append(site)

    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    lines = [f"# サイト巡回レポート（{now}）\n"]

    total_articles = 0

    for cat, cat_sites in by_category.items():
        label = CATEGORY_LABELS.get(cat, cat.upper())
        cat_lines = []
        cat_count = 0

        for site in cat_sites:
            try:
                entries = fetch_feed(site["url"], max_entries)
            except Exception as e:
                cat_lines.append(f"### {site['name']}\n")
                cat_lines.append(f"- ⚠ 取得失敗: {e}\n")
                continue

            if not entries:
                continue

            cat_lines.append(f"### {site['name']}\n")
            for entry in entries:
                ts = f" ({entry['published']})" if entry["published"] else ""
                cat_lines.append(f"- {entry['title']}{ts}")
                cat_lines.append(f"  {entry['link']}\n")
                cat_count += 1

        if cat_lines:
            lines.append(f"## {label}（{cat_count}件）\n")
            lines.extend(cat_lines)
            total_articles += cat_count

    lines.insert(1, f"\n合計 {total_articles} 件の記事を取得しました。\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="サイト巡回スクリプト")
    parser.add_argument("--category", "-c", help="カテゴリでフィルタ (tech/ai/medical/gadget/blog)")
    parser.add_argument("--max", "-m", type=int, default=5, help="サイトあたりの最大記事数 (デフォルト: 5)")
    parser.add_argument("--sites", "-s", default=None, help="sites.yaml のパス")
    args = parser.parse_args()

    yaml_path = Path(args.sites) if args.sites else Path(__file__).parent / "sites.yaml"
    if not yaml_path.exists():
        print(f"エラー: {yaml_path} が見つかりません", file=sys.stderr)
        sys.exit(1)

    result = patrol(yaml_path, args.category, args.max)
    print(result)


if __name__ == "__main__":
    main()
