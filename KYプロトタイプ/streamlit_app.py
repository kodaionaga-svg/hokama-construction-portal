import streamlit as st

st.set_page_config(page_title="KY・安全管理プロトタイプ", page_icon="⚠️", layout="centered")
st.markdown("""<style>.block-container{max-width:680px;padding:1rem 1rem 4rem}div[data-testid='stFormSubmitButton'] button{min-height:56px;font-weight:700}</style>""",unsafe_allow_html=True)
st.session_state.setdefault("ky_records",[])
st.title("⚠️ KY・安全管理プロトタイプ")
st.caption("朝礼前に、作業・危険・対策・周知を短時間で揃える試作版です。")
with st.form("ky",clear_on_submit=True):
    site=st.text_input("工事名")
    work=st.text_area("本日の作業・作業場所")
    risk=st.text_area("危険ポイント・気になる違和感")
    action=st.text_area("対策・作業員への周知内容")
    leader=st.text_input("確認者")
    confirmed=st.checkbox("朝礼・KYで周知した")
    save=st.form_submit_button("✅ KYを記録",use_container_width=True)
if save:
    if not(site.strip() and work.strip() and risk.strip() and action.strip()): st.error("工事名・作業・危険ポイント・対策を入力してください。")
    else:
        st.session_state.ky_records.append({"工事":site,"作業":work,"危険":risk,"対策":action,"確認者":leader,"周知":"済" if confirmed else "未"})
        st.success("KYを記録しました。")
st.subheader("記録一覧")
st.dataframe(st.session_state.ky_records[::-1],use_container_width=True,hide_index=True)
st.caption("試作版：次の段階で、工事別クラウド保存、職長確認、写真、危険予知の傾向分析を追加します。")

