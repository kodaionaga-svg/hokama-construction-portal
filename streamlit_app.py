import streamlit as st


st.set_page_config(
    page_title="株式会社ホカマ 建築部施工管理ポータルサイト",
    page_icon="🏗️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 680px;
            padding: 1.25rem 1rem 2.5rem;
        }
        h1 {
            font-size: clamp(1.65rem, 7vw, 2.25rem) !important;
            line-height: 1.32 !important;
            margin-bottom: 0.35rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
            margin-top: 0.25rem !important;
        }
        div[data-testid="stLinkButton"] > a {
            min-height: 4.25rem;
            padding: 1rem 1.1rem;
            border-radius: 0.85rem;
            font-size: 1.08rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            box-shadow: 0 2px 7px rgba(0, 0, 0, 0.12);
        }
        div[data-testid="stLinkButton"] {
            margin: 0.65rem 0;
        }
        hr {
            margin: 1.65rem 0 1rem;
        }
        [data-testid="stCaptionContainer"] {
            font-size: 0.93rem;
        }
        @media (max-width: 480px) {
            .block-container {
                padding: 1rem 0.85rem 2rem;
            }
            div[data-testid="stLinkButton"] > a {
                min-height: 4.6rem;
                font-size: 1.1rem;
                padding: 1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏗️ 株式会社ホカマ\n建築部施工管理ポータルサイト")
st.caption("現場で使うアプリを、下の大きなボタンから開けます。")


def app_link(label: str, url: str = "https://example.com") -> None:
    """公開済みの各アプリURLを指定してください。"""
    st.link_button(label, url, use_container_width=True)


st.divider()
st.header("💬 コミュニケーション")
app_link("⚠️ KY・安全管理", "https://hokama-ky-safety.streamlit.app/")
app_link("📢 お知らせ・連絡掲示板", "https://kodaionaga-svg.github.io/hokama-safety-patrol-app/notice-board/?v=e025f8af")
app_link("📅 工程・予定共有", "https://kodaionaga-svg.github.io/hokama-safety-patrol-app/schedule-share/?v=18595504")
app_link("📝 工事日報・作業報告", "https://hokama-60sec-daily-report.streamlit.app/")
app_link("📌 未対応事項", "https://hokama-issue-management.streamlit.app/")

st.divider()
st.header("🔍 品質・検査")
app_link("📚 公共建築工事標準仕様書検索", "https://hokama-spec-search.streamlit.app/")
app_link("📷 写真管理・検査記録")
app_link("📄 各種検査書類", "https://hokama-self-inspection.streamlit.app/")
app_link("🧱 施工確認アプリ", "https://hokama-construction-check.streamlit.app/")
app_link("🛠️ 是正事項", "https://hokama-corrective-actions.streamlit.app/")

st.divider()
st.header("🛠️ 施工管理支援ツール")
app_link("📏 測量計算ツール", "https://hokama-ts-sokuryou.streamlit.app/")
app_link("💾 測量計算ツール（端末保存版）", "https://github.com/kodaionaga-svg/hokama-ts-sokuryou/raw/main/ts_sokuryou_local.html")
app_link("🧮 数量・出来形計算")
app_link("📊 材料・数量集計")

st.divider()
st.caption("※ 各ボタンのURLは、公開済みアプリのURLへ書き換えてご利用ください。")
