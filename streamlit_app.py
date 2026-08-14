import streamlit as st


st.set_page_config(
    page_title="株式会社ホカマ 建築部施工管理ポータルサイト",
    page_icon="🏗️",
    layout="centered",
)

st.title("🏗️ 株式会社ホカマ 建築部施工管理ポータルサイト")
st.caption("各施工管理アプリへ、下のボタンからアクセスできます。")


def app_link(label: str, url: str = "https://example.com") -> None:
    """公開済みの各アプリURLを指定してください。"""
    st.link_button(label, url, use_container_width=True)


st.divider()
st.header("💬 コミュニケーション")
app_link("📢 お知らせ・連絡掲示板")
app_link("📅 工程・予定共有")
app_link("📝 日報・作業報告")

st.divider()
st.header("🔍 品質・検査")
app_link("✅ 品質管理チェックリスト")
app_link("📷 写真管理・検査記録")
app_link("📄 各種検査書類", "https://hokama-self-inspection.streamlit.app/")

st.divider()
st.header("📐 測量・計算")
app_link("📏 測量計算ツール", "https://hokama-ts-sokuryou.streamlit.app/")
app_link("🧮 数量・出来形計算")
app_link("📊 材料・数量集計")

st.divider()
st.caption("※ 各ボタンのURLは、公開済みアプリのURLへ書き換えてご利用ください。")
