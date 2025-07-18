import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

st.set_page_config(page_title="공부 성취도 기록", layout="centered")

# 방학 기간 설정
start_date = datetime.date(2025, 7, 18)
end_date = start_date + datetime.timedelta(days=30)

st.title("📚 방학 공부 성취도 트래커")

# CSV 파일 경로
CSV_PATH = "data.csv"

# CSV 불러오기 (없으면 빈 데이터프레임)
if os.path.exists(CSV_PATH):
    df_all = pd.read_csv(CSV_PATH)
    if "날짜" in df_all.columns:
        df_all["날짜"] = pd.to_datetime(df_all["날짜"], errors='coerce')
    else:
        df_all["날짜"] = pd.NaT
else:
    df_all = pd.DataFrame(columns=["날짜", "매3비", "매3문", "영어", "수학1", "총점", "성취도"])

# 날짜 선택
today = st.date_input("날짜 선택", value=datetime.date.today(), min_value=start_date, max_value=end_date)

# 오늘 이미 기록했는지 확인
if not df_all.empty and pd.api.types.is_datetime64_any_dtype(df_all["날짜"]):
    already_saved = today in df_all["날짜"].dt.date.values
else:
    already_saved = False

# 점수 입력
st.subheader("✅ 오늘 점수 입력")

# 📕 매3비
st.markdown("### 📕 매3비")
m3bi_passage = st.slider("푼 지문 수", 0, 3, 0, key="m3bi")
m3bi_score = m3bi_passage * 3
if m3bi_passage > 0 and st.checkbox("정답률 80% 이상", key="m3bi_correct"):
    m3bi_score += 1
m3bi_score = min(m3bi_score, 10)
st.write(f"→ 점수: **{m3bi_score}/10**")

# 📗 매3문
st.markdown("### 📗 매3문")
m3mun_passage = st.slider("푼 지문 수", 0, 3, 0, key="m3mun")
m3mun_score = m3mun_passage * 3
if m3mun_passage > 0 and st.checkbox("정답률 80% 이상", key="m3mun_correct"):
    m3mun_score += 1
m3mun_score = min(m3mun_score, 10)
st.write(f"→ 점수: **{m3mun_score}/10**")

# 📘 영어
st.markdown("### 📘 영어 단어 테스트")
eng_percent = st.slider("정답률 (%)", 0, 100, step=5)
if eng_percent == 0:
    eng_score = 0
else:
    eng_score = round((eng_percent / 100) * 10)
    eng_score = max(1, eng_score)
st.write(f"→ 점수: **{eng_score}/10**")

# 📐 수학1
st.markdown("### 📐 수학1")
math_percent = st.slider("진도율 (%)", 0, 100, step=10)
math_score = round(math_percent / 10)
if math_percent > 0 and st.checkbox("오답 정리함", key="math_review"):
    math_score += 1
math_score = min(math_score, 10)
st.write(f"→ 점수: **{math_score}/10**")

# 총점 계산
total_score = m3bi_score + m3mun_score + eng_score + math_score

def get_achievement(score):
    if score >= 36:
        return "🌟 매우 우수"
    elif score >= 30:
        return "🔵 우수"
    elif score >= 20:
        return "🟡 보통"
    elif score >= 10:
        return "🔺 미흡"
    else:
        return "❌ 부족"

achievement = get_achievement(total_score)

# 총점 및 성취도 출력
st.markdown("### 🎯 총점 및 성취도")
st.write(f"총점: **{total_score}/40**")
st.write(f"성취도: **{achievement}**")

# 저장 버튼
if st.button("💾 저장"):
    if already_saved:
        st.warning("⚠️ 이미 이 날짜에 저장된 기록이 있습니다.")
    else:
        new_row = pd.DataFrame([{
            "날짜": pd.to_datetime(today),
            "매3비": m3bi_score,
            "매3문": m3mun_score,
            "영어": eng_score,
            "수학1": math_score,
            "총점": total_score,
            "성취도": achievement
        }])
        df_all = pd.concat([df_all, new_row], ignore_index=True)
        df_all.to_csv(CSV_PATH, index=False)
        st.success("✅ 저장 완료!")

# 그래프 표시
if not df_all.empty:
    st.subheader("📊 성취도 그래프")
    df_all = df_all.sort_values("날짜")

    for subject in ["매3비", "매3문", "영어", "수학1"]:
        fig = px.scatter(df_all, x="날짜", y=subject, title=f"{subject} 점수 추이",
                         range_y=[-0.5, 10.5], height=350)
        fig.update_layout(xaxis_tickangle=0, margin=dict(t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    fig_total = px.scatter(df_all, x="날짜", y="총점", title="🧮 총점 추이",
                           range_y=[-1, 41], height=350)
    fig_total.update_layout(xaxis_tickangle=0, margin=dict(t=40, b=40))
    st.plotly_chart(fig_total, use_container_width=True)

    st.markdown("### 🌟 성취도 기록")
    st.dataframe(df_all[["날짜", "총점", "성취도"]].set_index("날짜"))
else:
    st.info("아직 저장된 기록이 없습니다.")
