import streamlit as st
from pathlib import Path
import tempfile
from server_core import process_audio

st.set_page_config(page_title="会議議事録アプリ", layout="centered")

st.title("🎙 会議議事録メーカー (Whisper + GPT)")
st.write("iPhoneやPCの音声ファイルをアップロードして、議事録を自動生成します。")

uploaded_file = st.file_uploader("音声ファイルを選択 (.m4a / .mp3 / .wav)", type=["m4a", "mp3", "wav"])

prompt_key = st.selectbox(
    "生成スタイルを選択",
    options=["default", "decision_focus", "todo_focus"],
    format_func=lambda x: {
        "default": "標準議事録",
        "decision_focus": "決定事項重視",
        "todo_focus": "ToDoリスト重視",
    }[x],
)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/m4a")

    if st.button("🎧 議事録を生成"):
        with st.spinner("文字起こしと要約を処理中...（数分かかります）"):
            temp_dir = Path(tempfile.mkdtemp())
            audio_path = temp_dir / uploaded_file.name
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            result = process_audio(audio_path, prompt_key)
            st.success("✅ 議事録を生成しました！")

            st.subheader("📝 要約結果")
            st.markdown(result["summary"])

            with st.expander("🗒️ 文字起こし（抜粋）"):
                st.text(result["transcript"])

            st.download_button(
                label="📥 議事録（Markdown）をダウンロード",
                data=result["summary"],
                file_name=f"{uploaded_file.name}.minutes.md",
                mime="text/markdown",
            )
