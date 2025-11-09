from __future__ import annotations
import os
from pathlib import Path
from faster_whisper import WhisperModel
from openai import OpenAI
from dotenv import load_dotenv

# ==========================================
# ✅ 環境変数の読み込み
# ==========================================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # gpt-5-mini は未対応の環境あり

# OpenAI クライアント初期化
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY が設定されていません。Streamlit Cloud の Secrets に設定してください。")
client = OpenAI(api_key=OPENAI_API_KEY)


# ==========================================
# 🎙 Whisper による音声文字起こし
# ==========================================
def transcribe_audio(audio_path: Path) -> str:
    """音声ファイルを文字起こししてテキストとして返す"""
    model = WhisperModel("medium", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), language="ja")

    text = "".join([seg.text for seg in segments])

    # テキストファイルとして保存（任意）
    txt_path = audio_path.with_suffix(".txt")
    txt_path.write_text(text, encoding="utf-8")

    return text


# ==========================================
# 🧠 GPT による議事録要約
# ==========================================
def summarize_with_llm(text: str, prompt_key: str = "default") -> str:
    """ChatGPT (OpenAI API) で自然な議事録を生成"""
    prompts = {
        "default": (
            "あなたは日本語の議事録作成アシスタントです。"
            "以下の会議内容をもとに、自然で読みやすく要点をまとめた議事録をMarkdown形式で出力してください。"
            "『会議名』『日時』『参加者』『決定事項』『ToDo』『議論サマリ』の構成でお願いします。"
        ),
        "decision_focus": (
            "以下の内容から、決定事項とその根拠・影響・次のアクションを中心にMarkdownでまとめてください。"
        ),
        "todo_focus": (
            "以下の内容から、担当者・期限・内容に注目したToDoリスト形式でMarkdownを生成してください。"
        ),
    }

    system_prompt = prompts.get(prompt_key, prompts["default"])

    # ✅ 新SDK（v1.x系）では responses ではなく chat.completions を使う！
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.4,
    )

    summary = response.choices[0].message.content
    return summary


# ==========================================
# ⚙️ メイン処理（音声→文字起こし→要約→保存）
# ==========================================
def process_audio(audio_file: Path, prompt_key: str = "default") -> dict:
    """音声ファイルを処理し、文字起こし＋要約結果を返す"""
    text = transcribe_audio(audio_file)
    summary = summarize_with_llm(text, prompt_key)

    # 保存先を作成
    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / f"{audio_file.stem}.minutes.md"
    md_path.write_text(summary, encoding="utf-8")

    return {
        "transcript": text[:800] + "..." if len(text) > 800 else text,
        "summary": summary,
        "md_path": str(md_path),
    }
