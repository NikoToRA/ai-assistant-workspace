---
name: arxiv
description: arXiv論文の検索・トレンド発見・詳細分析を行う統合スキル。「論文調べて」「最新AI論文」「arXiv検索」で使用。Pythonのarxivライブラリで論文検索・要約を日本語で提供。
---

# arXiv論文調査スキル

arXiv論文の検索とトレンド把握を行う。

## セットアップ（初回のみ）
pip3 install arxiv

## 実行方法（Pythonで直接）
import arxiv
client = arxiv.Client()
search = arxiv.Search(query="LLM agents", max_results=10, sort_by=arxiv.SortCriterion.SubmittedDate)
for r in client.results(search):
    print(f"- {r.title} ({r.published.date()})")
    print(f"  {r.summary[:200]}")

## 出力
- タイトル・著者・日付・要約（日本語訳）を提示
- 重要論文はnotes/にmarkdownで保存
- カテゴリ: cs.AI / cs.LG / cs.CL / cs.CV / cs.MA
