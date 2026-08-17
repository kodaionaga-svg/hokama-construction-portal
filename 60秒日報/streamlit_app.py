"""60秒日報（端末保存プロトタイプ）"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st


st.set_page_config(page_title="60秒日報", page_icon="📝", layout="centered")

DATA_FILE = Path(__file__).with_name("daily_reports.json")


def load_reports() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_reports(reports: list[dict]) -> None:
    temp_file = DATA_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_file.replace(DATA_FILE)


st.markdown(
    """
    <style>
    .block-container {max-width: 680px; padding: 1rem 1rem 5rem;}
    h1 {font-size: 1.75rem; margin-bottom: .15rem;}
    .lead {color: #5d6b78; margin-bottom: 1rem;}
    div[data-testid="stForm"] {border: 1px solid #d8e0e8; border-radius: 16px; padding: 1rem; background: #fff;}
    div[data-testid="stFormSubmitButton"] button {min-height: 58px; font-size: 1.15rem; font-weight: 700;}
    div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button {min-height: 48px; font-weight: 650;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📝 60秒日報")
st.markdown("<p class='lead'>現場で「今日・気になったこと・明日」を短く残す端末保存版です。黄色い入力欄を埋める感覚で、まずは1分以内を目指します。</p>", unsafe_allow_html=True)
st.warning("公開試用版です。この画面の保存データはクラウド再起動時に消えることがあります。重要な日報はCSVをダウンロードして保管してください。")

with st.form("daily_report", clear_on_submit=True):
    date = st.date_input("日付", value=datetime.now().date())
    site = st.text_input("現場名", placeholder="例：○○作業所")
    weather = st.selectbox("天候", ["晴れ", "くもり", "雨", "雪", "その他"])
    workers = st.number_input("作業人数", min_value=0, max_value=999, value=0, step=1)
    work = st.text_area("今日の作業", placeholder="例：1階柱配筋、型枠建込み", height=78)
    progress = st.selectbox("進捗", ["予定どおり", "やや遅れ", "遅れ", "中止・変更"])
    concern = st.text_area("気になったこと・違和感", placeholder="例：開口まわりの配筋が込み合っており、納まり確認が必要", height=78)
    tomorrow = st.text_area("明日の予定・引継ぎ", placeholder="例：配筋検査前に開口補強を再確認", height=70)
    submitted = st.form_submit_button("✅ 日報を保存する", use_container_width=True)

if submitted:
    if not site.strip() or not work.strip():
        st.error("「現場名」と「今日の作業」は入力してください。")
    else:
        reports = load_reports()
        reports.append(
            {
                "id": str(uuid4()),
                "日付": str(date),
                "現場名": site.strip(),
                "天候": weather,
                "作業人数": int(workers),
                "今日の作業": work.strip(),
                "進捗": progress,
                "気になったこと・違和感": concern.strip(),
                "明日の予定・引継ぎ": tomorrow.strip(),
                "登録日時": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )
        save_reports(reports)
        st.success("保存しました。気になることは、後で是正事項アプリへ登録できます。")

reports = load_reports()
st.divider()
st.subheader("📚 保存済み日報")

if not reports:
    st.info("まだ日報はありません。上のフォームから1件目を登録してください。")
else:
    columns = ["日付", "現場名", "天候", "作業人数", "今日の作業", "進捗", "気になったこと・違和感", "明日の予定・引継ぎ", "登録日時"]
    rows = [{column: report.get(column, "") for column in columns} for report in reversed(reports)]
    st.caption(f"このアプリに {len(rows)} 件を一時保存しています。")
    st.dataframe(rows, use_container_width=True, hide_index=True)
    csv_lines = [",".join(columns)]
    for row in rows:
        csv_lines.append(",".join('"' + str(row[column]).replace('"', '""') + '"' for column in columns))
    st.download_button(
        "📥 日報をCSVで保存",
        data="\ufeff" + "\n".join(csv_lines),
        file_name="60秒日報.csv",
        mime="text/csv",
        use_container_width=True,
    )
    with st.expander("端末内の日報をすべて削除する"):
        confirm = st.checkbox("削除内容を確認しました")
        if st.button("🗑️ 全件削除", type="secondary", use_container_width=True, disabled=not confirm):
            save_reports([])
            st.rerun()

st.caption("プロトタイプ版：公開クラウドでは保存領域が恒久的ではありません。共同利用版にする場合は、現場ごとのクラウド保存・写真添付・是正事項アプリ連携を追加します。")

