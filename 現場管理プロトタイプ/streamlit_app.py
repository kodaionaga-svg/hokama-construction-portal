import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="施工確認アプリ", page_icon="🏗️", layout="centered")
st.markdown("""<style>.block-container{max-width:720px;padding:1rem 1rem 4rem}div.stButton>button,div[data-testid='stFormSubmitButton'] button{min-height:52px;font-weight:700}</style>""",unsafe_allow_html=True)
for key in ("rc","cast","plan","correct"):
    st.session_state.setdefault(key,[])

st.title("🏗️ 施工確認アプリ")
st.caption("RC施工チェック・打設管理・3日先確認・是正事項分析を、現場の流れで確認する試作版です。")
site=st.text_input("工事名",placeholder="例：○○建設工事")
tab1,tab2,tab3,tab4=st.tabs(["🧱 RC施工","🚚 打設","📅 3日先","📊 是正分析"])

with tab1:
    st.subheader("RC施工チェック")
    part=st.selectbox("部位",["柱","梁","壁","スラブ"])
    items={"柱":["主筋径・本数","帯筋ピッチ","定着・かぶり","開口補強"],"梁":["主筋・あばら筋","定着・継手","かぶり","設備開口"],"壁":["縦横筋","開口補強","かぶり","セパレーター"],"スラブ":["上端・下端筋","かぶり","開口補強","配管干渉"]}[part]
    with st.form("rc_form",clear_on_submit=True):
        checks={item:st.selectbox(item,["未確認","OK","要是正"],key=f"{part}_{item}") for item in items}
        memo=st.text_area("確認メモ")
        save=st.form_submit_button("✅ チェックを保存",use_container_width=True)
    if save:
        st.session_state.rc.append({"工事":site,"部位":part,"結果":" / ".join(f"{k}:{v}" for k,v in checks.items()),"メモ":memo});st.success("保存しました")
    st.dataframe(st.session_state.rc[::-1],use_container_width=True,hide_index=True)

with tab2:
    st.subheader("コンクリート打設管理")
    with st.form("cast_form",clear_on_submit=True):
        area=st.text_input("打設区画")
        truck=st.text_input("車番")
        c1,c2,c3=st.columns(3); slump=c1.number_input("スランプ cm",0.0); air=c2.number_input("空気量 %",0.0); temp=c3.number_input("コンクリート温度 ℃",0.0)
        note=st.text_area("受入・締固め・養生メモ")
        save=st.form_submit_button("✅ 打設記録を保存",use_container_width=True)
    if save and area:
        st.session_state.cast.append({"工事":site,"区画":area,"車番":truck,"Slump":slump,"Air":air,"温度":temp,"メモ":note});st.success("保存しました")
    st.dataframe(st.session_state.cast[::-1],use_container_width=True,hide_index=True)

with tab3:
    st.subheader("今日から3日先の確認")
    for offset in range(3):
        day=date.today()+timedelta(days=offset)
        with st.expander(day.strftime("%m/%d")+(" 今日" if offset==0 else ""),expanded=offset==0):
            with st.form(f"plan_{offset}",clear_on_submit=True):
                task=st.text_input("作業・職種",key=f"task{offset}"); need=st.text_input("資材・重機・検査予定",key=f"need{offset}"); issue=st.text_input("懸念・確認事項",key=f"issue{offset}")
                if st.form_submit_button("保存",use_container_width=True) and task:
                    st.session_state.plan.append({"日付":str(day),"工事":site,"作業":task,"予定":need,"懸念":issue});st.rerun()
    st.dataframe(st.session_state.plan[::-1],use_container_width=True,hide_index=True)

with tab4:
    st.subheader("是正事項の傾向")
    with st.form("correct_form",clear_on_submit=True):
        category=st.selectbox("分類",["品質","安全","工程","納まり","設備干渉","その他"]); location=st.text_input("部位・場所"); cause=st.text_input("原因・違和感"); status=st.selectbox("状態",["未対応","対応中","完了"])
        save=st.form_submit_button("➕ 是正事項を登録",use_container_width=True)
    if save and location and cause:
        st.session_state.correct.append({"工事":site,"分類":category,"部位":location,"原因":cause,"状態":status});st.success("登録しました")
    rows=st.session_state.correct
    if rows:
        st.metric("未対応件数",sum(1 for row in rows if row["状態"]!="完了"))
        st.dataframe(rows[::-1],use_container_width=True,hide_index=True)
    else: st.info("是正事項を登録すると、繰り返す傾向を確認できます。")

st.caption("試作版：画面構成と入力項目を確認するための一時保存版です。次の段階で、工事別クラウド保存・写真・帳票出力・既存是正事項アプリとの連携を追加します。")

