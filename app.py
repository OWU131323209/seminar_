import os
import sys

# 文字コードをUTF-8に統一
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"] = "C.UTF-8"
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="SNS誤読・早とちり防止チェッカー", layout="wide")
st.title("SNS誤読・早とちり防止チェッカー")
st.caption("読者が『最初の1文しか読まない』前提で、投稿前のリスク診断とリライトを行います。")

# キーの取得と前後の空白除去
raw_key = st.secrets.get("GEMINI_API_KEY", "")
api_key = str(raw_key).strip().replace("\u3000", "")  # 全角空白も排除

if not api_key:
    st.error(".streamlit/secrets.toml に GEMINI_API_KEY を設定してください。")
    st.stop()

# クライアント初期化
client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
あなたはSNSの炎上防止・リスク管理・情報伝達の専門家です。
読者は「最初の1文しか読まない」「長文を精読しない」「最悪の文脈で曲解・早とちりする」という認知バイアスを持っている前提で、以下のフォーマットに沿って分析してください。

### 1. 🚨 早とちり・曲解リスク診断
- 救済情報や最も重要な結論が後回し（文末など）になっていないか
- 1文目だけ切り取られたときに、ネガティブな印象や誤認を与えるリスク
- 主語や制約条件の抜け落ちによる最悪の解釈可能性

### 2. 👿 悪魔の代弁者（最悪の誤読シミュレーション）
- 「悪意を持った読者や反射的に怒る読者が、どう曲解して批判するか」を1〜2行で具体的に提示

### 3. ✍️ 改善リライト案（推奨フォーマット）
- 1行目に結論・救済策・一番伝えたいポジティブ要素を配置
- 補足条件や日時は箇条書きにし、スマホ1画面で流し読みできる構成にする
"""

user_text = st.text_area(
    "投稿予定の文章を入力してください",
    height=140,
    placeholder="例：完売のため本日の販売は終了いたしました。次回入荷につきましては、明日10時よりオンラインストアにて再販を予定しております。"
)

if st.button("リスク分析＆リライト", type="primary"):
    if not user_text.strip():
        st.warning("文章を入力してください。")
    else:
        with st.spinner("早とちりリスクを解析中..."):
            try:
                # ユーザー入力を明示的にUTF-8の文字列として渡す
                cleaned_input = user_text.strip()
                prompt_content = f"以下の投稿文を分析し、リライト案を作成してください。\n\n【投稿予定の文章】\n{cleaned_input}"
                
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt_content,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.2,
                    ),
                )
                
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                # 詳細なトレースバックを表示して特定しやすくする
                import traceback
                st.error(f"エラーが発生しました: {e}")
                with st.expander("詳細エラーログ"):
                    st.code(traceback.format_exc())
