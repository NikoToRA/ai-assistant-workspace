---
name: site-patrol
description: お気に入りサイトのRSSフィードを巡回し、新着記事をカテゴリ別にまとめて報告するスキル。「サイト巡回して」「tech系チェックして」「巡回先追加して」で使用。
---

# サイト巡回スキル

お気に入りサイトを巡回し、新着記事をカテゴリ別にチェックして報告する。

## トリガー

「サイト巡回して」「サイトチェックして」「tech系のニュース見て」「巡回先を追加して」

## 手順（必ずこの順番で実行）

### Step 1: 巡回スクリプトを実行

```bash
cd skills/site-patrol && .venv/bin/python fetch_sites.py
```

カテゴリを絞りたい場合：
```bash
cd skills/site-patrol && .venv/bin/python fetch_sites.py --category tech
cd skills/site-patrol && .venv/bin/python fetch_sites.py --category ai
cd skills/site-patrol && .venv/bin/python fetch_sites.py --category medical
cd skills/site-patrol && .venv/bin/python fetch_sites.py --category gadget
```

記事数を変更したい場合：
```bash
cd skills/site-patrol && .venv/bin/python fetch_sites.py --max 3
```

### Step 2: 結果を整理して報告

スクリプトの出力をそのまま報告する。ユーザーが興味を持ちそうな記事には一言コメントを添える。

出力フォーマット：
```markdown
## サイト巡回レポート

### TECH（技術全般）
- 記事タイトル（日時）
  URL
  → 一言コメント（任意）

### AI・機械学習
...

### 医療・ヘルステック
...

### ガジェット・IoT
...
```

### Step 3: Notion保存（任意）

ユーザーが「Notionに保存して」と言った場合、`skills/notion-manager/SKILL.md` を参照してNotionにレポートを保存する。

## カテゴリ一覧

| カテゴリ | 説明 | キーワード |
|---------|------|-----------|
| tech | 技術全般 | 「tech系」「技術ニュース」 |
| ai | AI・機械学習 | 「AI」「機械学習」 |
| medical | 医療・ヘルステック | 「医療」「ヘルステック」 |
| gadget | ガジェット・IoT | 「ガジェット」「IoT」 |
| blog | 個人ブログ | 「ブログ」 |

## 巡回先の追加・編集

ユーザーから「巡回先に追加して」と言われたら、`sites.yaml` を編集する。

追加時のフォーマット：
```yaml
- name: "サイト名"
  url: "RSSフィードのURL"
  type: rss
  category: tech  # tech/ai/medical/gadget/blog
```

RSSフィードのURLがわからない場合は、WebSearchで探す。

## 使用例

```
サイト巡回して
tech系のサイトチェックして
AI関連のニュースだけ見せて
この巡回先を追加して: https://example.com/feed
巡回結果をNotionに保存して
```
