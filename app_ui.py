import streamlit as st
from pathlib import Path
import tempfile
from server_core import process_audio

# ==============================================
# 🌐 MTGMAP - Meeting Minutes Generator
# ==============================================
st.set_page_config(
    page_title="MTGMAP - Meeting Minutes Generator",
    page_icon="🗺️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ======= ヘッダー部分 =======
st.markdown(
    """
    <style>
        .title {
            font-size: 2.2em;
            font-weight: 700;
            color: #FF7F50;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: gray;
            font-size: 1.1em;
        }
        .stButton>button {
            background-color: #FF7F50;
            color: white;
            border-radius: 8px;
            height: 3em;
            width: 100%;
            font-weight: 600;
        }
        .stDownloadButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 6px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="title">🗺️ MTGMAP</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-powered Meeting Minutes Generator (Whisper + GPT)</p>', unsafe_allow_html=True)
st.write("---")

# ======= ファイルアップロード部分 =======
st.write("🎙 音声ファイルをアップロードして議事録を自動生成します。")
uploaded_file = st.file_uploader(
    "対応形式: .m4a / .mp3 / .wav",
    type=["m4a", "mp3", "wav"]
)

# ======= モード選択 =======
st.subheader("🧭 生成スタイルを選択")
prompt_key = st.selectbox(
    "用途に合わせて出力形式を選べます。",
    options=["default", "decision_focus", "todo_focus"],
    format_func=lambda x: {
        "default": "標準議事録",
        "decision_focus": "決定事項重視",
        "todo_focus": "ToDoリスト重視",
    }[x],
)

# ======= 音声再生プレビュー =======
if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/m4a")
    st.info(f"ファイル名: **{uploaded_file.name}**")
    st.write("---")

    # ======= 議事録生成ボタン =======
    if st.button("🎧 議事録を生成する"):
        with st.spinner("⏳ Whisperで文字起こし中... その後、GPTが要約を作成します（数分かかる場合があります）"):
            temp_dir = Path(tempfile.mkdtemp())
            audio_path = temp_dir / uploaded_file.name
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            try:
                result = process_audio(audio_path, prompt_key)
                st.success("✅ 議事録の生成が完了しました！")

                # ======= 結果表示 =======
                st.subheader("📝 要約結果")
                st.markdown(result["summary"])

                with st.expander("🗒️ 文字起こしテキスト（抜粋）を表示"):
                    st.text(result["transcript"])

                st.download_button(
                    label="📥 議事録（Markdown）をダウンロード",
                    data=result["summary"],
                    file_name=f"{uploaded_file.name}.minutes.md",
                    mime="text/markdown",
                )

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}")

else:
    st.info("⬆️ まずは音声ファイルをアップロードしてください。")

# ======= フッター =======
st.write("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.9em;">
        © 2025 MTGMAP - Powered by Whisper & GPT
    </div>
    """,
    unsafe_allow_html=True
)
