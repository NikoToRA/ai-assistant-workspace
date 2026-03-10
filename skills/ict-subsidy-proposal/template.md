---
marp: true
theme: wonder-drill
paginate: false
html: true
---

<!-- _style: "section:first-of-type { flex-direction: row !important; background: linear-gradient(160deg, #f2f8ff 0%, #ddeeff 100%) !important; }" -->

<!-- ==================== SLIDE 1: 表紙 ==================== -->

<!-- 左：ブルーサイドバー（縦カラム） -->
<div style="width:260px; min-width:260px; background:linear-gradient(180deg,#001f6b,#0044bb,#0066dd); display:flex; flex-direction:column; align-items:center; justify-content:center; padding:40px 24px; box-sizing:border-box;">
  <img src="wonder-drill-logo.png" style="width:160px; height:auto; filter:brightness(0) invert(1);">
</div>

<!-- 右：コンテンツエリア -->
<div style="flex:1; display:flex; flex-direction:column; padding:56px 80px 44px; box-sizing:border-box;">

  <div style="flex:1;"></div>

  <div>
    <div style="font-size:12px; color:#0055cc; font-weight:bold; letter-spacing:6px; margin-bottom:16px;">PROPOSAL</div>
    <div style="font-size:80px; font-weight:900; color:#0055cc; line-height:1; margin-bottom:16px;">提案資料</div>
    <div style="height:3px; background:linear-gradient(90deg,#0033aa 0%,#0088ee 50%,#00ccff 80%,transparent 100%); border-radius:2px; margin:0 0 24px 0;"></div>
    <div style="font-size:18px; color:#555; letter-spacing:1px; margin-bottom:14px; font-weight:bold; line-height:1.7;">厚生労働省 令和8年度<br>業務効率化ICT補助金 活用のご提案</div>
    <div style="font-size:24px; font-weight:900; color:#1a2e4a; line-height:1.6;">コエレク導入および<br>研修プログラムについて</div>
  </div>

  <div style="flex:2; display:flex; flex-direction:column; justify-content:flex-end;">
    <div style="height:1px; background:rgba(0,80,200,0.2); margin-bottom:14px;"></div>
    <div style="font-size:14px; color:#444; font-weight:bold;">Wonder Drill 株式会社</div>
    <div style="font-size:13px; color:#888; margin-top:5px;">{{年月}}</div>
  </div>

</div>

---

<!-- ==================== SLIDE 2: 補助金 × コエレク ==================== -->

# 補助金 × コエレクで業務効率化を実現する

<div class="body">

<div class="g2" style="flex:1; align-items:stretch; min-height:0;">

<div style="display:flex; flex-direction:column; gap:10px;">
  <h2 style="font-size:1.2em;">補助金の申請構造</h2>
  <div class="bb" style="padding:16px 18px;">
    <p style="font-weight:bold; color:#002d80; font-size:1.1em; margin-bottom:8px;">厚生労働省の要件（令和8年度）</p>
    <p style="font-size:1.05em; line-height:1.7;">補助対象は <strong style="color:#cc0000;">「ICT機器の導入」と「それに附随する訓練（研修）」のセット</strong> に限られます。研修単体・ICT機器のみでは申請不可。</p>
    <small>出典：医政発0213第22号（令和8年2月13日）</small>
  </div>
  <div class="by" style="padding:14px 18px; font-size:1.05em;">
    <strong>コエレク（ICT機器）+ 現地研修 = 補助金対象</strong><br>
    <span style="font-size:0.88em;">生成AIを活用した「文書自動作成支援」として明確に対象費用に含まれます</span>
  </div>
  <div class="bw" style="margin-top:auto;">
    <div style="display:flex; gap:0; text-align:center;">
      <div style="flex:1; border-right:1px solid rgba(0,80,200,0.15); padding-right:14px;">
        <div style="font-size:2em; font-weight:900; color:#0033aa;">8,000万</div>
        <div style="font-size:0.74em; color:#444;">円　補助上限額/施設</div>
      </div>
      <div style="flex:1; padding-left:14px;">
        <div style="font-size:2em; font-weight:900; color:#cc0000;">80%</div>
        <div style="font-size:0.74em; color:#444;">補助率（費用の5分の4）</div>
      </div>
    </div>
  </div>
</div>

<div style="display:flex; flex-direction:column; gap:10px;">
  <h2 style="font-size:1.2em;">コエレクとは</h2>
  <div class="bw" style="text-align:center; padding:12px;">
    <div style="display:flex; align-items:center; gap:0; justify-content:center;">
      <div style="flex:1; background:#002d80; color:white; border-radius:6px; padding:10px 6px; font-size:0.9em; font-weight:bold;">音声入力</div>
      <div style="color:#0055cc; font-size:1.6em; padding:0 8px;">→</div>
      <div style="flex:1; background:#002d80; color:white; border-radius:6px; padding:10px 6px; font-size:0.9em; font-weight:bold;">AI解析</div>
      <div style="color:#0055cc; font-size:1.6em; padding:0 8px;">→</div>
      <div style="flex:1; background:#002d80; color:white; border-radius:6px; padding:10px 6px; font-size:0.9em; font-weight:bold;">カルテ生成</div>
    </div>
    <div style="font-size:0.82em; color:#555; margin-top:8px;">「声で記録、デジタルで解決。」</div>
  </div>
  <div class="bw">
    <ul>
      <li>SOAP形式のカルテを<strong>自動生成</strong>（音声入力のみ）</li>
      <li>院内のカルテ記載ルールに<strong>カスタマイズ対応</strong></li>
      <li>iPhoneからすぐに利用開始可能</li>
      <li>電子カルテとの連携対応</li>
      <li>修正が必要なのは<strong>全体の10%以下</strong></li>
    </ul>
  </div>
  <div style="flex:1; display:flex; align-items:center; justify-content:center; min-height:0;">
    <img src="koereku-app.png" style="max-width:100%; max-height:100%; object-fit:contain; border-radius:8px;">
  </div>
</div>

</div>

</div>
<div class="ft"><img src="wonder-drill-logo.png"><span>support@wonder-drill.com</span></div>

---

<!-- ==================== SLIDE 3: 料金表 ==================== -->

# 料金表（1アカウント・税別）

<div class="body">

<div class="g2" style="flex:1; align-items:stretch; min-height:0;">

<div style="display:flex; flex-direction:column; gap:6px;">
  <h2 style="font-size:1.1em; margin-bottom:2px;">コエレク導入パッケージ（初年度）</h2>
  <table style="font-size:0.95em;">
    <thead><tr><th>項目</th><th>金額</th></tr></thead>
    <tbody>
      <tr><td>アカウント年間使用料</td><td>180,000円</td></tr>
      <tr><td>初期登録料</td><td>30,000円</td></tr>
      <tr><td>おまとめBox（周辺機器一式）</td><td>99,800円</td></tr>
      <tr><td>初期登録料（サービス割引）</td><td style="color:#cc0000;">−10,000円</td></tr>
    </tbody>
    <tfoot><tr class="tt"><td>初年度 コエレク小計</td><td>299,800円</td></tr></tfoot>
  </table>
  <div class="bw" style="font-size:0.95em; padding:8px 12px;">
    <strong>コエレクおまとめBoxに含まれるもの</strong><br>
    QRリーダー、ワイヤレス充電機、iPhoneSE3、セットアップサポート一式
  </div>
  <div style="flex:1; display:flex; align-items:flex-start; justify-content:center; min-height:0; overflow:hidden;">
    <img src="coelec-device.png" style="max-width:100%; max-height:100%; object-fit:contain; border-radius:8px;">
  </div>
</div>

<div style="display:flex; flex-direction:column; gap:10px;">
  <h2 style="font-size:1.2em;">研修メニュー（各回 現地実施）</h2>
  <table style="flex:0; font-size:1em;">
    <thead><tr><th>研修名</th><th>内容</th><th>金額</th></tr></thead>
    <tbody>
      <tr><td><strong>コエレク導入研修</strong></td><td>操作・設定・カスタマイズ</td><td>150,000円</td></tr>
      <tr><td><strong>AI基本研修</strong></td><td>AI活用の基礎・実践</td><td>150,000円</td></tr>
      <tr><td><strong>DX研修</strong></td><td>院内DX推進・計画策定</td><td>150,000円</td></tr>
    </tbody>
    <tfoot><tr class="tt"><td colspan="2">研修3本 合計</td><td>450,000円</td></tr></tfoot>
  </table>
  <div class="by" style="font-size:1.05em;">
    <strong>補助金申請には全3本の受講を推奨。</strong><br>「ICT機器導入に附随する訓練」として研修費用も補助対象です。
  </div>
  <div class="bw" style="flex:1; font-size:1.05em;">
    <strong>各研修の実施形式</strong>
    <ul style="margin-top:6px;">
      <li>貴院への<strong>現地訪問</strong>で実施（オンライン対応も可）</li>
      <li>スタッフ全員参加可能、人数制限なし</li>
      <li>研修後のフォローアップ相談付き</li>
    </ul>
  </div>
</div>

</div>

</div>
<div class="ft"><img src="wonder-drill-logo.png"><span>support@wonder-drill.com</span></div>

---

<!-- ==================== SLIDE 4: 3年間全体像 ==================== -->

# 3ヵ年サポートプラン 全体像（1アカウント・税別）

<div class="body">

<table style="font-size:0.9em; flex-shrink:0;">
  <thead>
    <tr><th>項目</th><th>初年度</th><th>2年目</th><th>3年目</th><th>3年合計</th></tr>
  </thead>
  <tbody>
    <tr><td>アカウント年間使用料</td><td>180,000</td><td>180,000</td><td>180,000</td><td>540,000円</td></tr>
    <tr><td>初期登録料（正味）</td><td>20,000</td><td>—</td><td>—</td><td>20,000円</td></tr>
    <tr><td>おまとめBox（周辺機器一式）</td><td>99,800</td><td>—</td><td>—</td><td>99,800円</td></tr>
    <tr><td>コエレク導入研修（現地・初年度のみ）</td><td>150,000</td><td>—</td><td>—</td><td>150,000円</td></tr>
    <tr><td>AI基本研修（現地・年1回）</td><td>150,000</td><td>150,000</td><td>150,000</td><td>450,000円</td></tr>
    <tr><td>DX研修（現地・年1回）</td><td>150,000</td><td>150,000</td><td>150,000</td><td>450,000円</td></tr>
  </tbody>
  <tfoot>
    <tr class="ty"><td>推奨オプション：年間レポート・評価表作成サポート</td><td>100,000</td><td>100,000</td><td>100,000</td><td>300,000円</td></tr>
    <tr class="tt"><td>3年間 合計（税別）</td><td>849,800円</td><td>580,000円</td><td>580,000円</td><td>2,009,800円</td></tr>
  </tfoot>
</table>

<div class="al" style="flex-shrink:0;"></div>

<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; flex-shrink:0;">
  <div class="bw" style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
    <div style="font-size:2.2em; font-weight:900; color:#0033aa; line-height:1;">2,009,800</div>
    <div style="font-size:0.75em; color:#333; margin-top:5px; font-weight:bold;">円　3年間の総コスト（税別）</div>
  </div>
  <div class="bw" style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; border:2px solid rgba(200,150,0,0.35);">
    <div style="font-size:2.2em; font-weight:900; color:#cc8800; line-height:1;">80<span style="font-size:0.5em;">%</span></div>
    <div style="font-size:0.75em; color:#333; margin-top:5px; font-weight:bold;">補助率（費用の5分の4）</div>
    <div style="font-size:0.7em; color:#888; margin-top:2px;">厚生労働省 令和8年度</div>
  </div>
  <div class="bw" style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; border:2px solid rgba(200,0,0,0.25);">
    <div style="font-size:2.2em; font-weight:900; color:#cc0000; line-height:1;">約40万<span style="font-size:0.5em;">円</span></div>
    <div style="font-size:0.75em; color:#333; margin-top:5px; font-weight:bold;">実質ご負担（補助後）</div>
    <div style="font-size:0.7em; color:#888; margin-top:2px;">3年間・1アカウント</div>
  </div>
</div>

<div class="by" style="flex-shrink:0; font-size:0.85em; margin-top:4px;">
  <strong>【年間レポート・評価表作成サポートについて】</strong>
  毎年1回、コエレク活用状況・業務効率化の進捗をレポートにまとめ都道府県への報告資料として提出。初年度は評価指標・目標値を設定し、最終年は評価表・報告書を作成。補助金の返還リスクを最小化します。
</div>

</div>
<div class="ft"><img src="wonder-drill-logo.png"><span>support@wonder-drill.com</span></div>

---

<!-- ==================== SLIDE 5: 研修内容 ==================== -->

# 研修プログラム 詳細

<div class="body">

<div class="g3" style="flex:1; align-items:stretch; min-height:0;">

<div style="display:flex; flex-direction:column; gap:10px;">
  <h2 style="font-size:1.1em;">コエレク導入研修</h2>
  <div class="bb" style="font-size:0.82em; flex-shrink:0;">初年度のみ・現地実施　<strong>150,000円</strong></div>
  <div class="bw" style="flex:1;">
    <div class="sr"><div class="sb" style="font-size:0.8em;">1</div><div class="st"><strong>基本操作・音声入力</strong><br><span style="font-size:0.85em; color:#555;">コエレクの起動から音声入力の流れ、iPhoneとの連携方法</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">2</div><div class="st"><strong>SOAP自動変換の確認</strong><br><span style="font-size:0.85em; color:#555;">音声からカルテが生成される流れを実際のケースで体験</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">3</div><div class="st"><strong>院内ルールへのカスタマイズ</strong><br><span style="font-size:0.85em; color:#555;">記載ルール・略語・診療科ごとの設定調整</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">4</div><div class="st"><strong>導入後サポート確認</strong><br><span style="font-size:0.85em; color:#555;">よくある質問・修正対応・問合せ方法の説明</span></div></div>
  </div>
</div>

<div style="display:flex; flex-direction:column; gap:10px;">
  <h2 style="font-size:1.1em;">AI基本研修</h2>
  <div class="bb" style="font-size:0.82em; flex-shrink:0;">年1回・現地実施　<strong>150,000円</strong></div>
  <div class="bw" style="flex:1;">
    <div class="sr"><div class="sb" style="font-size:0.8em;">1</div><div class="st"><strong>生成AIの基礎知識</strong><br><span style="font-size:0.85em; color:#555;">仕組み・できること・限界を医療現場の視点で解説</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">2</div><div class="st"><strong>医療現場での活用事例</strong><br><span style="font-size:0.85em; color:#555;">カルテ記録・患者説明文・院内文書への応用</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">3</div><div class="st"><strong>プロンプト設計の基本</strong><br><span style="font-size:0.85em; color:#555;">指示の出し方・精度を上げるコツを実習形式で習得</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">4</div><div class="st"><strong>セキュリティ・個人情報対応</strong><br><span style="font-size:0.85em; color:#555;">AIツール利用時の注意点・院内ルール策定</span></div></div>
  </div>
</div>

<div style="display:flex; flex-direction:column; gap:10px;">
  <h2 style="font-size:1.1em;">DX研修</h2>
  <div class="bb" style="font-size:0.82em; flex-shrink:0;">年1回・現地実施　<strong>150,000円</strong></div>
  <div class="bw" style="flex:1;">
    <div class="sr"><div class="sb" style="font-size:0.8em;">1</div><div class="st"><strong>院内DX現状分析</strong><br><span style="font-size:0.85em; color:#555;">業務フロー・課題の洗い出しとデジタル化の優先順位整理</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">2</div><div class="st"><strong>業務効率化計画の策定</strong><br><span style="font-size:0.85em; color:#555;">補助金申請に必要なKPI・目標値・スケジュールの立案</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">3</div><div class="st"><strong>効果測定・進捗管理</strong><br><span style="font-size:0.85em; color:#555;">記録時間削減率など数値で把握する方法と記録のルール化</span></div></div>
    <div class="sep"></div>
    <div class="sr"><div class="sb" style="font-size:0.8em;">4</div><div class="st"><strong>継続改善のフレームワーク</strong><br><span style="font-size:0.85em; color:#555;">PDCAサイクルを院内に定着させる体制づくり</span></div></div>
  </div>
</div>

</div>

</div>
<div class="ft"><img src="wonder-drill-logo.png"><span>support@wonder-drill.com</span></div>

---

<!-- ==================== SLIDE 6: CTA ==================== -->

# {{病院名}}さまへ　はじめの一歩

<div class="body">
<div style="display:flex; flex-direction:column; flex:1;">
<div style="flex:1;"></div>
<div style="display:grid; grid-template-columns:1fr auto 1fr auto 1fr; align-items:stretch; gap:0;">
<div class="bb" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:20px 18px; gap:10px;">
<div style="width:36px; height:36px; border-radius:50%; background:#0033aa; color:white; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px; flex-shrink:0;">1</div>
<div style="font-size:1.1em; font-weight:900; color:#001f6b; line-height:1.3;">Webミーティングにて<br>詳細を詰めましょう</div>
<div style="font-size:0.85em; color:#333; line-height:1.7;">カルテ記載の流れ・スタッフ人数・補助金申請の準備状況など、まずオンラインでお聞かせください。</div>
</div>
<div style="display:flex; align-items:center; padding:0 8px; margin-top:20px;"><div style="font-size:2em; color:#0055cc; font-weight:900;">→</div></div>
<div class="bb" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:20px 18px; gap:10px;">
<div style="width:36px; height:36px; border-radius:50%; background:#0033aa; color:white; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px; flex-shrink:0;">2</div>
<div style="font-size:1.1em; font-weight:900; color:#001f6b; line-height:1.3;">メールアドレス一つで<br>開始可能です</div>
<div style="font-size:0.85em; color:#333; line-height:1.7;">QRコードリーダーが必要になります。<br>（こちらもミーティングでご相談いただけます）</div>
</div>
<div style="display:flex; align-items:center; padding:0 8px; margin-top:20px;"><div style="font-size:2em; color:#0055cc; font-weight:900;">→</div></div>
<div class="bb" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:20px 18px; gap:10px;">
<div style="width:36px; height:36px; border-radius:50%; background:#0033aa; color:white; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px; flex-shrink:0;">3</div>
<div style="font-size:1.1em; font-weight:900; color:#001f6b; line-height:1.3;">研修・補助金申請を<br>具体的に相談</div>
<div style="font-size:0.85em; color:#333; line-height:1.7;">3本の研修内容・実施日程・補助金申請書類の作成まで、Wonder Drill が{{病院名}}さまに合わせてフルサポートします。</div>
</div>
</div>
<div style="flex:1;"></div>
<div class="by" style="text-align:center; padding:16px 40px;">
<div style="font-size:13px; color:#7a4a00; margin-bottom:6px; font-weight:bold;">連絡先</div>
<div style="font-size:26px; font-weight:900; color:#002080;">s-hirayama@wonder-drill.com</div>
<div style="font-size:13px; color:#555; margin-top:6px;">Wonder Drill 株式会社　代表取締役 平山 傑　— 本プランは{{病院名}}さまの状況に合わせてカスタマイズ可能です</div>
</div>
</div>
</div>
<div class="ft"><img src="wonder-drill-logo.png"><span>support@wonder-drill.com</span></div>
