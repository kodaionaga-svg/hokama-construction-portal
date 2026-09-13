import streamlit as st
from streamlit.components.v2 import component

cloudflare_web_analytics = component(
    "cloudflare_web_analytics",
    js="""export default function() {
        if (document.querySelector('script[data-cf-analytics-token="b9aa05f3b763493dbc50ab8b373f3cd4"]')) return;
        const script = document.createElement("script");
        script.type = "module";
        script.src = "https://static.cloudflareinsights.com/beacon.min.js";
        script.dataset.cfBeacon = JSON.stringify({ token: "b9aa05f3b763493dbc50ab8b373f3cd4" });
        script.dataset.cfAnalyticsToken = "b9aa05f3b763493dbc50ab8b373f3cd4";
        document.head.appendChild(script);
    }""",
)
cloudflare_web_analytics()



st.set_page_config(
    page_title="建築施工管理ポータルサイト",
    page_icon="🏗️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp { background: #f4f7fa; }\n        header { visibility: hidden; height: 0; }\n        .block-container {
            max-width: 680px;
            padding: 1.5rem 1rem 3rem;\n            background: #ffffff;\n            border: 1px solid #d7e2eb;\n            border-radius: 1.1rem;\n            box-shadow: 0 3px 14px rgba(18, 55, 87, 0.10);\n            margin-top: 1rem;
        }
        h1 {
            font-size: clamp(2rem, 9vw, 2.8rem) !important;
            line-height: 1.32 !important;
            margin-bottom: 0.5rem !important;\n            color: #123757 !important;
        }
        h2 {
            font-size: 1.5rem !important;
            margin-top: 1.35rem !important;\n            padding: 0.7rem 0.85rem;\n            background: #e7f1f8;\n            border-left: 5px solid #1d6398;\n            border-radius: 0.55rem;\n            color: #123757 !important;
        }
        div[data-testid="stLinkButton"] > a {
            min-height: 5.25rem;
            padding: 1rem 1.1rem;
            border-radius: 0.85rem;
            font-size: 1.32rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            box-shadow: 0 3px 9px rgba(18, 55, 87, 0.16);\n            background: #1d6398 !important;\n            color: #ffffff !important;\n            border: 0 !important;
        }
        div[data-testid="stLinkButton"] {
            margin: 0.75rem 0;
        }
        hr {
            margin: 1.65rem 0 1rem;
        }
        [data-testid="stCaptionContainer"] {
            font-size: 1.05rem;
        }
        @media (max-width: 480px) {
            .block-container {
                padding: 1rem 0.85rem 2rem;
            }
            div[data-testid="stLinkButton"] > a {
                min-height: 5.5rem;
                font-size: 1.35rem;
                padding: 1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏗️ 建築施工管理ポータルサイト")
st.caption("現場で使うアプリを、下の大きなボタンから開けます。")


def app_link(label: str, url: str = "https://example.com") -> None:
    """公開済みの各アプリURLを指定してください。"""
    st.link_button(label, url, use_container_width=True)


st.divider()
st.header("💬 コミュニケーション")
app_link("⚠️ KY・安全管理", "https://onaga-ky-safety.streamlit.app/")
app_link("🦺 安全パトロール", "https://onaga-safety-patrol.streamlit.app/")
app_link("📢 お知らせ・連絡掲示板", "https://onaga-notice-board.streamlit.app/")
app_link("📅 工程・予定共有", "https://onaga-schedule-share.streamlit.app/")
app_link("📝 工事日報・作業報告", "https://onaga-60sec-daily-report.streamlit.app/")
app_link("📌 未対応事項", "https://onaga-issue-management.streamlit.app/")

st.divider()
st.header("🔍 品質・検査")
app_link("📚 公共建築工事標準仕様書検索", "https://construction-spec-search.kodaionaga.chatgpt.site")
app_link("📄 各種検査書類", "https://onaga-self-inspection.streamlit.app/")
app_link("🧱 コンクリート打設管理", "https://onaga-construction-check.streamlit.app/")
app_link("🛠️ 是正事項", "https://onaga-corrective-actions.streamlit.app/")

st.divider()
st.header("🛠️ 施工管理支援ツール")
app_link("📏 測量計算ツール", "https://onaga-ts-sokuryou.streamlit.app/")

st.divider()
st.caption("※ 各ボタンのURLは、公開済みアプリのURLへ書き換えてご利用ください。")

# Re-publish portal to refresh the safety patrol link.


st.divider()
st.header("🦺 安全パトロール")
st.caption("下のボタンから安全パトロールを直接開けます。")
st.link_button("🦺 安全パトロールを開く", "https://onaga-safety-patrol.streamlit.app/?from=portal", use_container_width=True)
