import csv, io, re
from datetime import date, datetime
from uuid import uuid4
import streamlit as st
from supabase import create_client
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

st.set_page_config(page_title="コンクリート打設管理", page_icon="🚚", layout="centered")
st.markdown("<style>.block-container{max-width:820px;padding:1rem 1rem 4rem}div.stButton>button,div[data-testid='stFormSubmitButton'] button{min-height:52px;font-weight:700}.stage{padding:.55rem .75rem;border-radius:.6rem;background:#eef5fa;color:#123757;font-weight:700}</style>", unsafe_allow_html=True)
for key, default in {"active_cast_site": ""}.items(): st.session_state.setdefault(key, default)

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M")
@st.cache_resource
def cloud():
    return create_client("https://schttjeinzdhjemgtdvi.supabase.co", "sb_publishable_7HgyHI9HKDD5lvyPnX3tSA_ptePV39_")

def require_cloud():
    client=cloud()
    return client

def site_list(client):
    return client.table("concrete_sites").select("id,name").order("name").execute().data

def data():
    rows=require_cloud().table("concrete_records").select("id,stage,payload,created_at").eq("site_id", st.session_state.active_cast_site).order("created_at", desc=True).execute().data
    result={"pre": [], "receipt": [], "progress": [], "curing": []}
    for row in rows:
        item=dict(row["payload"]); item["id"]=row["id"]; item["saved_at"]=row["created_at"]
        result[row["stage"]].append(item)
    return result

def save(stage, payload):
    require_cloud().table("concrete_records").insert({"site_id":st.session_state.active_cast_site,"stage":stage,"payload":payload}).execute()

def upload_photos(pour_id, files):
    client=require_cloud(); saved=[]
    for file in files:
        safe=re.sub(r"[^A-Za-z0-9._-]", "_", file.name)
        path=f"{st.session_state.active_cast_site}/{pour_id}/{uuid4()}_{safe}"
        client.storage.from_("concrete-photos").upload(path=path, file=io.BytesIO(file.getvalue()), file_options={"content-type":file.type, "upsert":"false"})
        saved.append({"name":file.name,"path":path})
    return saved
def pours(records): return {f"{x['date']}｜{x['area']}｜{x['id'][:6]}": x for x in records["pre"]}
def clean(row): return {k: (" / ".join(v) if isinstance(v, list) else v) for k, v in row.items() if k not in {"id", "pour_id", "photos"}}
def report_rows(records): return [{"段階": stage, **clean(row)} for stage, entries in records.items() for row in entries]
def csv_bytes(records):
    rows=report_rows(records); fields=sorted({k for r in rows for k in r}|{"段階"}); out=io.StringIO(); w=csv.DictWriter(out,fieldnames=fields); w.writeheader(); w.writerows(rows); return ("\ufeff"+out.getvalue()).encode()
def pdf_bytes(site, records):
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5")); out=io.BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=14*mm,rightMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm)
    ss=getSampleStyleSheet(); title=ss["Title"].clone("t",fontName="HeiseiKakuGo-W5",fontSize=18); body=ss["BodyText"].clone("b",fontName="HeiseiKakuGo-W5",fontSize=8.5,leading=12)
    story=[Paragraph("コンクリート打設管理記録",title),Paragraph(f"工事名：{site}　出力：{now()}",body),Spacer(1,5*mm)]
    labels={"pre":"打設前チェック","receipt":"受入検査","progress":"打設中の管理","curing":"養生・強度管理"}
    for stage,label in labels.items():
        story += [Paragraph(label,body),Spacer(1,2*mm)]
        entries=records[stage]
        if not entries: story += [Paragraph("記録なし",body),Spacer(1,4*mm)]; continue
        for entry in entries:
            lines=[[Paragraph(str(k),body),Paragraph(str(v).replace("\n","<br/>"),body)] for k,v in clean(entry).items()]
            table=Table(lines,colWidths=[43*mm,135*mm]); table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.35,colors.HexColor("#9fb4c5")),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#edf4f8")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)])); story += [table,Spacer(1,4*mm)]
    doc.build(story); return out.getvalue()

st.title("🚚 コンクリート打設管理")
st.caption("打設前から養生・帳票までを、現場ごとに管理します。")
if not st.session_state.active_cast_site:
    client=require_cloud(); sites=site_list(client); names={item["name"]:item["id"] for item in sites}
    st.subheader("現場を選択")
    st.write("最初に現場を選択してください。登録・写真・帳票は現場ごとに分かれます。")
    with st.form("gate"):
        selected=st.selectbox("登録済み現場",[""]+list(names),format_func=lambda x:"選択してください" if not x else x)
        new=st.text_input("新しい現場名",placeholder="例：○○建設工事")
        enter=st.form_submit_button("この現場を開く",use_container_width=True)
    if enter:
        name=new.strip() or selected
        if not name: st.warning("現場を選択するか、新しい現場名を入力してください。")
        else:
            if name not in names:
                created=client.table("concrete_sites").insert({"name":name}).execute().data[0]
                st.session_state.active_cast_site=created["id"]
            else: st.session_state.active_cast_site=names[name]
            st.rerun()
    st.stop()

client=require_cloud(); site=client.table("concrete_sites").select("name").eq("id",st.session_state.active_cast_site).single().execute().data["name"]; records=data()
c1,c2=st.columns([4,1]); c1.markdown(f"### 現場：{site}")
if c2.button("現場を切替",use_container_width=True): st.session_state.active_cast_site=""; st.rerun()
t1,t2,t3,t4,t5=st.tabs(["1. 打設前","2. 受入","3. 打設中","4. 養生・強度","5. 帳票"])

with t1:
    st.markdown('<p class="stage">打設前チェック</p>',unsafe_allow_html=True)
    with st.form("pre",clear_on_submit=True):
        a,b=st.columns(2); day=a.date_input("打設予定日",date.today()); area=b.text_input("打設区画",placeholder="例：1階 スラブ A工区")
        a,b=st.columns(2); mix=a.text_input("配合・呼び強度",placeholder="例：24-18-20N"); volume=b.number_input("予定数量 m³",0.0,step=.5)
        a,b=st.columns(2); people=a.text_input("人員・担当"); pump=b.text_input("ポンプ車・重機")
        weather=st.text_input("天候・気温予報"); checks=st.multiselect("事前確認",["配筋・型枠検査完了","打設順・打重ね計画","ポンプ車配置・動線","締固め機器・予備品","養生資材","試験・供試体採取"]); approval=st.selectbox("打設可否",["未判定","打設可","条件付き可","延期"]); memo=st.text_area("打設前メモ・注意事項")
        save=st.form_submit_button("打設前チェックを保存",use_container_width=True)
    if save:
        if not area: st.warning("打設区画を入力してください。")
        else: save("pre", {"date":str(day),"area":area,"mix":mix,"予定数量m3":volume,"人員":people,"ポンプ車":pump,"天候":weather,"事前確認":checks,"可否":approval,"メモ":memo,"保存":now()}); st.success("クラウドへ保存しました。"); st.rerun()
    st.dataframe([clean(x) for x in records["pre"][::-1]],use_container_width=True,hide_index=True)

with t2:
    st.markdown('<p class="stage">受入検査</p>',unsafe_allow_html=True); options=pours(records)
    if not options: st.info("先に「打設前」で打設区画を登録してください。")
    else:
        with st.form("receipt",clear_on_submit=True):
            pick=st.selectbox("対象打設",list(options)); a,b,c=st.columns(3); arrival=a.time_input("到着時刻"); truck=b.text_input("車番"); ticket=c.text_input("伝票番号")
            a,b,c=st.columns(3); slump=a.number_input("スランプ cm",0.0,step=.5); air=b.number_input("空気量 %",0.0,step=.1); temp=c.number_input("コンクリート温度 ℃",0.0,step=.1)
            a,b=st.columns(2); judge=a.selectbox("受入判定",["適合","条件付き受入","不適合・返却"]); sample=b.text_input("供試体・試験採取"); note=st.text_area("受入所見・対応"); save=st.form_submit_button("受入検査を保存",use_container_width=True)
        if save:
            p=options[pick]; save("receipt", {"pour_id":p["id"],"date":p["date"],"area":p["area"],"到着":arrival.strftime("%H:%M"),"車番":truck,"伝票":ticket,"スランプcm":slump,"空気量%":air,"温度℃":temp,"判定":judge,"供試体":sample,"所見":note,"保存":now()}); st.success("クラウドへ保存しました。"); st.rerun()
    st.dataframe([clean(x) for x in records["receipt"][::-1]],use_container_width=True,hide_index=True)

with t3:
    st.markdown('<p class="stage">打設中の管理</p>',unsafe_allow_html=True); options=pours(records)
    if not options: st.info("先に「打設前」を登録してください。")
    else:
        with st.form("progress",clear_on_submit=True):
            pick=st.selectbox("対象打設",list(options),key="progress_pick"); a,b,c=st.columns(3); start=a.time_input("打設開始"); end=b.time_input("打設終了"); volume=c.number_input("今回数量 m³",0.0,step=.5)
            a,b=st.columns(2); layer=a.text_input("打設位置・打重ね"); vibrator=b.text_input("締固め担当・方法"); total=st.number_input("累計数量 m³",0.0,step=.5); issue=st.text_area("進捗・品質・安全上の記録"); files=st.file_uploader("施工写真（複数可）",type=["jpg","jpeg","png"],accept_multiple_files=True); save=st.form_submit_button("打設中の記録を保存",use_container_width=True)
        if save:
            p=options[pick]; saved_photos=upload_photos(p["id"], files); save("progress", {"pour_id":p["id"],"date":p["date"],"area":p["area"],"開始":start.strftime("%H:%M"),"終了":end.strftime("%H:%M"),"今回数量m3":volume,"累計数量m3":total,"打重ね":layer,"締固め":vibrator,"記録":issue,"photos":saved_photos,"写真数":len(saved_photos),"保存":now()}); st.success("写真を含めクラウドへ保存しました。"); st.rerun()
    st.dataframe([clean(x) for x in records["progress"][::-1]],use_container_width=True,hide_index=True)

with t4:
    st.markdown('<p class="stage">養生・強度管理</p>',unsafe_allow_html=True); options=pours(records)
    if not options: st.info("先に「打設前」を登録してください。")
    else:
        with st.form("curing",clear_on_submit=True):
            pick=st.selectbox("対象打設",list(options),key="curing_pick"); a,b=st.columns(2); begin_day=a.date_input("養生開始日",date.today()); begin_time=b.time_input("養生開始時刻",datetime.now().time().replace(second=0,microsecond=0)); a,b=st.columns(2); finish_day=a.date_input("養生終了予定日",date.today()); finish_time=b.time_input("養生終了予定時刻",datetime.now().time().replace(second=0,microsecond=0))
            a,b,c=st.columns(3); method=a.selectbox("養生方法",["散水","湿潤シート","被膜養生","保温養生","その他"]); temp=b.number_input("養生温度 ℃",0.0,step=.1); specimen=c.text_input("供試体番号")
            a,b=st.columns(2); test=a.date_input("強度試験予定日",date.today()); strength=b.number_input("圧縮強度 N/mm²",0.0,step=.1); judge=st.selectbox("強度判定",["未試験","適合","要確認","不適合"]); memo=st.text_area("養生・試験メモ"); save=st.form_submit_button("養生・強度記録を保存",use_container_width=True)
        if save:
            p=options[pick]; save("curing", {"pour_id":p["id"],"date":p["date"],"area":p["area"],"養生開始":f"{begin_day} {begin_time}","養生終了予定":f"{finish_day} {finish_time}","方法":method,"養生温度℃":temp,"供試体":specimen,"試験予定":str(test),"圧縮強度N/mm2":strength,"判定":judge,"メモ":memo,"保存":now()}); st.success("クラウドへ保存しました。"); st.rerun()
    st.dataframe([clean(x) for x in records["curing"][::-1]],use_container_width=True,hide_index=True)

with t5:
    st.markdown('<p class="stage">写真・帳票出力</p>',unsafe_allow_html=True); a,b=st.columns(2); a.metric("登録打設区画",len(records["pre"])); b.metric("施工写真",sum(x.get("写真数",0) for x in records["progress"]))
    for row in records["progress"][::-1]:
        if row.get("photos"):
            with st.expander(f"{row['date']}｜{row['area']}｜写真 {row['写真数']} 枚"):
                images=[require_cloud().storage.from_("concrete-photos").download(x["path"]) for x in row["photos"]]
                st.image(images,caption=[x["name"] for x in row["photos"]],width=180)
    st.download_button("CSV帳票をダウンロード",csv_bytes(records),f"{site}_コンクリート打設管理.csv","text/csv",use_container_width=True)
    st.download_button("PDF帳票をダウンロード",pdf_bytes(site,records),f"{site}_コンクリート打設管理.pdf","application/pdf",use_container_width=True)
    st.caption("現在選択している現場の記録だけを出力します。写真は画面で確認でき、帳票には写真の登録枚数を記録します。")

