"""60秒日報（全員共通・工事別クラウド保存版）"""
from __future__ import annotations
import json
from datetime import date, time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import streamlit as st

st.set_page_config(page_title="60秒日報", page_icon="📝", layout="centered")
SUPABASE_URL = "https://schttjeinzdhjemgtdvi.supabase.co"
SUPABASE_KEY = "sb_publishable_7HgyHI9HKDD5lvyPnX3tSA_ptePV39_"
DEFAULT_LABOR_TYPES = ["特殊作業員", "普通作業員", "軽作業員", "とび工", "鉄筋工", "鉄骨工", "溶接工", "型枠工", "大工", "左官工", "はつり工", "ガラス工", "建具工", "運転（特殊）", "建築ブロック", "タイル工", "内装工", "塗装工", "防水板金工", "屋根葺工", "鳶工", "ブロック工", "運転（一般）", "電工", "設備機械工", "ダクト工", "保温工", "配管工", "造園工", "削岩工", "石工"]

def api(table, method="GET", params=None, body=None, prefer="return=representation"):
    query = urlencode(params or {}, doseq=True)
    url = f"{SUPABASE_URL}/rest/v1/{table}" + (f"?{query}" if query else "")
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": prefer}
    request = Request(url, data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"), headers=headers, method=method)
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else []
    except HTTPError as error:
        raise RuntimeError(f"保存先との通信に失敗しました（{error.code}）：{error.read().decode('utf-8', errors='replace')}") from error
    except URLError as error:
        raise RuntimeError("保存先に接続できません。通信状況を確認してください。") from error

def labor_total(entries): return sum(float(entry.get("count") or 0) for entry in entries)
def display_number(value): return str(int(value)) if float(value).is_integer() else f"{value:.1f}"

st.markdown("""<style>.block-container{max-width:720px;padding:1rem 1rem 5rem}h1{font-size:1.7rem}.lead{color:#5d6b78}div[data-testid="stForm"]{border:1px solid #d8e0e8;border-radius:16px;padding:1rem;background:#fff}div[data-testid="stFormSubmitButton"] button,div[data-testid="stButton"] button{min-height:52px;font-size:1.02rem;font-weight:700}div[data-testid="stMetric"]{background:#f4f8fb;border-radius:12px;padding:.45rem}</style>""", unsafe_allow_html=True)
st.title("📝 60秒日報")
st.markdown("<p class='lead'>工事ごとに、職種別の出面と施工内容を全員で共有・累計する日報です。</p>", unsafe_allow_html=True)
st.info("共同利用版：URLを知る利用者は、すべての工事の日報・職種設定を閲覧、追加、編集、削除できます。")

try:
    projects = api("daily_report_projects", params={"select":"*", "order":"name.asc"})
except RuntimeError as error:
    st.error(str(error)); st.stop()

with st.expander("⚙️ 工事名・職種を管理する", expanded=not projects):
    with st.form("new_project", clear_on_submit=True):
        new_project_name = st.text_input("新しい工事名", placeholder="例：○○建設工事")
        create_project = st.form_submit_button("➕ 工事を追加", use_container_width=True)
    if create_project:
        if not new_project_name.strip(): st.error("工事名を入力してください。")
        else:
            try:
                api("daily_report_projects", "POST", body={"name":new_project_name.strip(), "labor_types":DEFAULT_LABOR_TYPES})
                st.success("工事を追加しました。"); st.rerun()
            except RuntimeError as error: st.error(str(error))
if not projects:
    st.warning("最初に「工事を追加」から工事名を登録してください。"); st.stop()

project_names = [project["name"] for project in projects]
selected_project_name = st.selectbox("🏗️ 工事名を切り替える", project_names)
project = next(item for item in projects if item["name"] == selected_project_name)
labor_types = project.get("labor_types") or DEFAULT_LABOR_TYPES
with st.expander("職種の追加・削除", expanded=False):
    st.caption("この変更は、選択中の工事だけに反映されます。")
    with st.form(f"labor_types_{project['id']}"):
        edited_types = st.text_area("職種（1行に1職種）", value="\n".join(labor_types), height=260, help="参考Excelの職種を初期登録しています。不要な職種は行ごと削除し、自由に追加できます。")
        save_types = st.form_submit_button("💾 職種設定を保存", use_container_width=True)
    if save_types:
        cleaned_types = list(dict.fromkeys(line.strip() for line in edited_types.splitlines() if line.strip()))
        if not cleaned_types: st.error("職種を1つ以上残してください。")
        else:
            try:
                api("daily_report_projects", "PATCH", {"id":f"eq.{project['id']}"}, {"labor_types":cleaned_types})
                st.success("職種設定を保存しました。"); st.rerun()
            except RuntimeError as error: st.error(str(error))

report_date = st.date_input("日付", value=date.today())
try: reports = api("daily_reports", params={"select":"*", "project_id":f"eq.{project['id']}", "order":"report_date.desc"})
except RuntimeError as error: st.error(str(error)); st.stop()
existing_report = next((item for item in reports if item["report_date"] == str(report_date)), None)
existing_entries = (existing_report or {}).get("labor_entries") or []
context = f"{project['id']}_{report_date}"
count_key = f"labor_row_count_{context}"
if count_key not in st.session_state: st.session_state[count_key] = max(1, len(existing_entries))
previous_total = sum(labor_total(item.get("labor_entries") or []) for item in reports if item["report_date"] < str(report_date))
today_total = labor_total(existing_entries)
grand_total = sum(labor_total(item.get("labor_entries") or []) for item in reports)
st.subheader("👷 現場全体の出面")
m1,m2,m3=st.columns(3); m1.metric("前日まで", f"{display_number(previous_total)} 人"); m2.metric("本日", f"{display_number(today_total)} 人"); m3.metric("累計", f"{display_number(grand_total)} 人")
st.caption("本日・累計は保存済みの値です。入力後に「日報を保存」で更新されます。")
if st.button("➕ 職種の入力行を追加", use_container_width=True): st.session_state[count_key] += 1; st.rerun()

defaults = existing_entries + [{}] * max(0, st.session_state[count_key] - len(existing_entries))
with st.form(f"daily_report_{context}"):
    agent_name = st.text_input("代理人名", value=(existing_report or {}).get("agent_name", ""), placeholder="例：現場 太郎")
    weather_options = ["晴れ", "くもり", "雨", "雪", "その他"]
    saved_weather = (existing_report or {}).get("weather", "晴れ")
    weather = st.selectbox("天候", weather_options, index=weather_options.index(saved_weather) if saved_weather in weather_options else 0)
    start_col,end_col=st.columns(2)
    work_start = start_col.time_input("作業開始", value=time.fromisoformat((existing_report or {}).get("work_start") or "08:00:00"))
    work_end = end_col.time_input("作業終了", value=time.fromisoformat((existing_report or {}).get("work_end") or "17:00:00"))
    st.markdown("#### 職種別の出面・施工内容")
    current_entries=[]
    for index, default in enumerate(defaults[:st.session_state[count_key]]):
        st.markdown(f"**{index+1}行目**")
        saved_role=default.get("labor_type", labor_types[0]); role_index=labor_types.index(saved_role) if saved_role in labor_types else 0
        labor_type=st.selectbox("職種", labor_types, index=role_index, key=f"role_{context}_{index}")
        count=st.number_input("出面（人）", min_value=0.0, max_value=999.0, value=float(default.get("count") or 0), step=0.5, key=f"count_{context}_{index}")
        content=st.text_area("この職種の施工内容", value=default.get("content", ""), placeholder="例：1階柱配筋・梁主筋組立", height=70, key=f"content_{context}_{index}")
        if count>0 or content.strip(): current_entries.append({"labor_type":labor_type,"count":count,"content":content.strip()})
        st.divider()
    concern=st.text_area("気になったこと・違和感", value=(existing_report or {}).get("concern", ""), height=75)
    tomorrow=st.text_area("明日の予定・引継ぎ", value=(existing_report or {}).get("tomorrow", ""), height=75)
    save_report=st.form_submit_button("✅ 日報を保存・更新する", use_container_width=True)
if save_report:
    if not agent_name.strip(): st.error("代理人名を入力してください。")
    elif not current_entries: st.error("職種別の出面または施工内容を1件以上入力してください。")
    else:
        payload={"project_id":project["id"],"report_date":str(report_date),"agent_name":agent_name.strip(),"weather":weather,"work_start":work_start.isoformat(),"work_end":work_end.isoformat(),"labor_entries":current_entries,"concern":concern.strip(),"tomorrow":tomorrow.strip()}
        try:
            api("daily_reports", "POST", {"on_conflict":"project_id,report_date"}, payload, "resolution=merge-duplicates,return=representation")
            st.success("日報を保存しました。出面累計を更新しました。"); st.rerun()
        except RuntimeError as error: st.error(str(error))

st.divider(); st.subheader("📊 職種別の出面累計")
totals={}
for report in reports:
    for entry in report.get("labor_entries") or []:
        role=entry.get("labor_type", "未分類"); totals[role]=totals.get(role,0)+float(entry.get("count") or 0)
if totals: st.dataframe([{"職種":role,"出面累計（人）":display_number(total)} for role,total in sorted(totals.items())], use_container_width=True, hide_index=True)
else: st.info("保存済みの出面はまだありません。")
st.subheader("📚 保存済み日報")
if reports:
    rows=[]
    for report in reports:
        summaries=" / ".join(f"{entry.get('labor_type')} {display_number(float(entry.get('count') or 0))}人" for entry in report.get("labor_entries") or [])
        rows.append({"日付":report["report_date"],"代理人名":report.get("agent_name",""),"出面":summaries,"本日合計":display_number(labor_total(report.get("labor_entries") or [])),"天候":report.get("weather","")})
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if existing_report:
        with st.expander("選択日のこの日報を削除する"):
            confirm_delete=st.checkbox("削除内容を確認しました", key=f"delete_{context}")
            if st.button("🗑️ 日報を削除", use_container_width=True, disabled=not confirm_delete):
                try: api("daily_reports", "DELETE", {"id":f"eq.{existing_report['id']}"}, prefer="return=minimal"); st.success("日報を削除しました。"); st.rerun()
                except RuntimeError as error: st.error(str(error))
else: st.info("この工事の日報はまだありません。")
st.caption("参考Excelの職種を初期設定しています。職種設定は工事ごとに編集でき、出面・施工内容・代理人名・作業時間は工事別にクラウド保存されます。")

