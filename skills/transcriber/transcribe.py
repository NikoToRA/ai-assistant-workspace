#!/usr/bin/env python3
"""音声文字起こしスクリプト: faster-whisperを使って音声ファイルをテキストに変換する。"""

import argparse
import sys
import time
from pathlib import Path


def transcribe(audio_path: str, model_size: str = "base", output_path: str | None = None) -> str:
    """音声ファイルを文字起こしする。"""
    from faster_whisper import WhisperModel

    audio = Path(audio_path)
    if not audio.exists():
        print(f"エラー: ファイルが見つかりません: {audio_path}", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        output_path = str(audio.with_suffix(".txt"))

    print(f"モデル: {model_size}")
    print(f"入力: {audio_path}")
    print(f"出力: {output_path}")
    print("読み込み中...")

    start = time.time()
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print("文字起こし中...")
    segments, info = model.transcribe(str(audio), language="ja", beam_size=5)

    print(f"検出言語: {info.language} (確率: {info.language_probability:.2f})")

    texts = []
    for segment in segments:
        ts = f"[{_fmt_time(segment.start)} - {_fmt_time(segment.end)}]"
        texts.append(f"{ts} {segment.text.strip()}")
        # 進捗表示
        print(f"  {ts} {segment.text.strip()[:60]}...")

    result = "\n".join(texts)

    Path(output_path).write_text(result, encoding="utf-8")

    elapsed = time.time() - start
    char_count = len(result.replace("\n", "").replace(" ", ""))

    print(f"\n完了！")
    print(f"  処理時間: {elapsed:.1f}秒")
    print(f"  文字数: 約{char_count}文字")
    print(f"  出力先: {output_path}")

    return result


def _fmt_time(seconds: float) -> str:
    """秒数を MM:SS 形式に変換。"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description="音声文字起こし（faster-whisper）")
    parser.add_argument("audio", help="音声ファイルのパス")
    parser.add_argument("--model-size", "-m", default="base",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Whisperモデルサイズ (デフォルト: base)")
    parser.add_argument("--output", "-o", default=None, help="出力テキストファイルのパス")
    args = parser.parse_args()

    transcribe(args.audio, args.model_size, args.output)


if __name__ == "__main__":
    main()
