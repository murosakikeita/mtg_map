from __future__ import annotations
import os
from pathlib import Path
from faster_whisper import WhisperModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

def transcribe_audio(audio_path: Path) -> str:
    """Whisperで音声を文字起こし"""
    model = WhisperModel("medium", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), language="ja")
    text = "".join([seg.text for seg in segments])
    txt_path = audio_path.with_suffix(".txt")
    txt_path.write_text(text, encoding="utf-8")
    return text

def summarize_with_llm(text: str, prompt_key: str = "default") -> str:
    """OpenAI APIで自然な議事録生成"""
    prompts = {
        "default": "あなたは日本語の議事録作成アシスタントです。以下の会話内容から自然で要点をまとめた議事録をMarkdownで出力してください。"
                   "『会議名』『日時』『参加者』『決定事項』『ToDo』『議論サマリ』の構成にしてください。",
        "decision_focus": "決定事項とその根拠、影響、次アクションを重点的にMarkdownでまとめてください。",
        "todo_focus": "担当者、期限、内容に注目してToDoリスト形式でMarkdownを生成してください。"
    }

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": prompts.get(prompt_key, prompts["default"])},
            {"role": "user", "content": text}
        ]
    )
    summary = resp.output_text
    return summary

def process_audio(audio_file: Path, prompt_key: str = "default") -> dict:
    """一連の処理: 文字起こし→要約→保存"""
    text = transcribe_audio(audio_file)
    summary = summarize_with_llm(text, prompt_key)

    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{audio_file.stem}.minutes.md"
    md_path.write_text(summary, encoding="utf-8")

    return {
        "transcript": text[:500] + "...",
        "summary": summary,
        "md_path": str(md_path)
    }
