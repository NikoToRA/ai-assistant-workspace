---
name: wonder-drill-slides
description: Wonder Drill株式会社のブランドデザインでHTMLスライドを作成する基盤スキル。CSSテーマ・HTMLテンプレートを管理。補助金提案書・会社資料などの上位スキルから参照される。
---

# Wonder Drill スライドデザイン基盤

Wonder Drill 株式会社のブランドに統一されたHTMLスライドを作成するための基盤。
補助金提案書・一般会社資料など、すべての資料はこのテーマを使う。

**方式: 純粋なHTML/CSS（Marpは使わない）**

## ファイル構成

```
skills/wonder-drill-slides/
  SKILL.md       ← このファイル
  template.html  ← スターターテンプレート（新規資料作成時にコピー）
  theme.css      ← レガシー（Marp時代の残骸。参照不要）
  template.md    ← レガシー（Marp時代の残骸。参照不要）
```

## ブランドカラー

| 用途 | カラー |
|------|--------|
| メイン（紺） | `#002d80` |
| アクセント（青） | `#0055cc` |
| 明青 | `#007be8` |
| テキスト | `#1a2e4a` |

## CSSクラス一覧

### レイアウト
| クラス | 説明 |
|--------|------|
| `.body` | スライド本文エリアのラッパー（`h1`の下に置く） |
| `.g2` | 2カラムグリッド |
| `.g3` | 3カラムグリッド |
| `.g64` | 6:4比率の2カラムグリッド |
| `.ft` | フッター（ロゴ + メール表示。スライド末尾に置く） |

### カードボックス
| クラス | 色 | 用途 |
|--------|-----|------|
| `.bw` | 白 | 汎用ボックス、補足説明 |
| `.bb` | 青左ボーダー | 重要な根拠・説明 |
| `.bg` | 緑 | 達成・まとめ・ポジティブ |
| `.by` | 黄 | 推奨・注意事項 |
| `.br` | 赤 | 警告・リスク |

### テーブル行
| クラス | 説明 |
|--------|------|
| `.tt` | 合計行（紺背景・白文字） |
| `.ty` | 注目行（黄背景） |

### ステップUI
| クラス | 説明 |
|--------|------|
| `.sb` | 丸番号バッジ（`<div class="sb">1</div>`） |
| `.sr` | ステップ行（バッジ + テキストの横並び） |
| `.st` | ステップテキスト部分 |

### デコレーション
| クラス | 説明 |
|--------|------|
| `.al` | グラデーションアクセントライン（区切りに使用） |
| `.sep` | 薄い区切り線（ステップ間など） |

## HTML → PDF 変換コマンド

```bash
# Chromiumでheadless PDF生成（ワークスペースルートから実行）
chromium --headless --disable-gpu --no-sandbox \
  --print-to-pdf=notes/<ファイル名>.pdf \
  --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw \
  "file:///$(pwd)/notes/<ファイル名>.html"
```

## 新規資料を作成する手順

1. `skills/wonder-drill-slides/template.html` を `notes/<病院名>-proposal.html` にコピー
2. `{{年月}}` などのプレースホルダーを実際の値に置換
3. スライド内容を編集（CSSクラスを活用）
4. 上記コマンドでPDF生成
5. `MEDIA:notes/<病院名>-proposal.pdf` でDiscordに送信

## スライド構造

各スライドは `<section class="slide">` 要素：

```html
<!-- 表紙 -->
<section class="slide slide-cover">
  <!-- 左サイドバー（260px紺グラデ） + 右コンテンツ -->
</section>

<!-- 本文スライド -->
<section class="slide">
  <h1>スライドタイトル</h1>
  <div class="body">
    <!-- コンテンツ -->
  </div>
  <div class="ft">
    <img src="wonder-drill-logo.png">
    <span>support@wonder-drill.com</span>
  </div>
</section>
```

## ロゴ・アセット

| ファイル | 場所 |
|----------|------|
| Wonder Drillロゴ | `notes/wonder-drill-logo.png` |
| コエレクアプリ画像 | `notes/koereku-app.png` |
| コエレクデバイス画像 | `notes/coelec-device.png` |

スライドHTMLを `notes/` に置く場合、画像は相対パス（`wonder-drill-logo.png`）で参照できる。

## デザイン原則（余白・レイアウト）

### 構造
- **表紙**: 左サイドバー（260px、紺グラデ）＋ 右コンテンツエリア（`.slide-cover`）
- **本文スライド**: `h1`（ヘッダー帯）＋ `<div class="body">` ＋ `<div class="ft">` の3段構成
- **body内**: `flex:1; min-height:0` でスライド高さを使い切る

### 余白・間隔
- **グリッドの gap**: `10px`（カード間）
- **カードが縦に並ぶ場合**: `gap:6px`
- **重要ボックス（.bb）padding**: `16px 18px`
- **標準ボックス（.by/.bw）padding**: `14px 18px`

### フォントサイズ
- **本文**: `1.05em`
- **h2 見出し**: `1.1〜1.2em`
- **補足・キャプション**: `0.82〜0.88em`
- **大数字（ハイライト）**: `2.2em; font-weight:900`

### フッター
- **高さ**: 36px（`position: absolute; bottom: 0`）
- `.body` の `padding-bottom: 46px` でフッターと重ならないよう確保
