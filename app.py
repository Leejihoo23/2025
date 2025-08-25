# Emotion Recording & Analysis App (Streamlit)
# Save this file as `app.py` and run: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import os
from fpdf import FPDF

# ----------------------
# Configuration
# ----------------------
DATA_FILE = "emotions.csv"
EMOTIONS = [
    "very_happy",
    "happy",
    "neutral",
    "tired",
    "sad",
    "angry",
    "anxious",
    "stressed",
]
EMO_LABELS = {
    "very_happy": "😊 매우 좋음",
    "happy": "🙂 좋음",
    "neutral": "😐 보통",
    "tired": "😴 피곤",
    "sad": "😢 우울",
    "angry": "😠 화남",
    "anxious": "😬 불안",
    "stressed": "😣 스트레스",
}

# Map emotions to feedback
FEEDBACK = {
    "very_happy": ("좋아요! 오늘 좋은 일을 축하해요.", "친구에게 감사 인사 보내기나 기분을 기록해보세요."),
    "happy": ("기분이 좋군요!", "짧은 산책이나 좋아하는 음악을 들으며 더 즐거운 시간을 보내보세요."),
    "neutral": ("보통인 하루네요.", "가벼운 스트레칭이나 5분 명상으로 기분을 끌어올려볼까요."),
    "tired": ("피곤하군요.", "짧은 낮잠(15~20분)이나 휴식 시간을 추천합니다."),
    "sad": ("힘든 날이군요.", "가까운 사람에게 이야기해보거나, 따뜻한 차 한 잔을 추천합니다."),
    "angry": ("화가 난 상태네요.", "심호흡 4-4-4(숨 들이쉬기 4, 참기 4, 내쉬기 4)를 1분 해보세요."),
    "anxious": ("불안하네요.", "주의를 환기시키는 짧은 산책이나 5분 호흡 명상이 도움이 됩니다."),
    "stressed": ("스트레스가 많아 보입니다.", "해야 할 일을 작은 단위로 쪼개고, 한 번에 하나씩 처리해보세요."),
}

# ----------------------
# Utility functions
# ----------------------

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"]) 
        return df
    else:
        return pd.DataFrame(columns=["timestamp", "date", "time", "emotion", "note"]) 


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def add_entry(emotion, note, when=None):
    df = load_data()
    if when is None:
        now = datetime.now()
    else:
        now = when
    entry = {
        "timestamp": now,
        "date": now.date().isoformat(),
        "time": now.time().strftime("%H:%M:%S"),
        "emotion": emotion,
        "note": note,
    }
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    save_data(df)
    return df


def get_week_range(ref_date=None):
    if ref_date is None:
        ref = datetime.now().date()
    else:
        ref = ref_date
    start = ref - timedelta(days=ref.weekday())  # Monday
    end = start + timedelta(days=6)
    return start, end


def weekly_counts(df, ref_date=None):
    start, end = get_week_range(ref_date)
    mask = (pd.to_datetime(df["date"]).dt.date >= start) & (pd.to_datetime(df["date"]).dt.date <= end)
    week = df.loc[mask].copy()
    # Count by emotion
    counts = week["emotion"].value_counts().reindex(EMOTIONS, fill_value=0)
    return counts, week


def emotion_calendar(df, ref_date=None):
    start, end = get_week_range(ref_date)
    dates = [start + timedelta(days=i) for i in range(7)]
    day_emotion = {}
    for d in dates:
        mask = pd.to_datetime(df["date"]).dt.date == d
        day = df.loc[mask]
        if len(day) == 0:
            day_emotion[d] = None
        else:
            # choose the most recent entry of the day
            last = day.sort_values("timestamp").iloc[-1]
            day_emotion[d] = last["emotion"]
    return day_emotion


def create_week_plot(counts):
    fig, ax = plt.subplots()
    idx = [EMO_LABELS[e] for e in counts.index]
    ax.bar(idx, counts.values)
    ax.set_title("이번 주 감정 분포")
    ax.set_ylabel("기록 수")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf


def create_calendar_plot(day_emotion):
    # convert to numeric scores for simple color map
    score_map = {
        "very_happy": 4,
        "happy": 3,
        "neutral": 2,
        "tired": 1,
        "sad": 0,
        "angry": 0,
        "anxious": 0,
        "stressed": 0,
    }
    dates = list(day_emotion.keys())
    scores = [score_map[e] if e is not None else np.nan for e in day_emotion.values()]
    fig, ax = plt.subplots()
    ax.plot(dates, scores, marker="o")
    ax.set_ylim(-0.5, 4.5)
    ax.set_yticks([0,1,2,3,4])
    ax.set_yticklabels(["neg","tired","neutral","happy","very\nhappy"])
    ax.set_title("주간 감정 캘린더 (최근 기록 기준)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf


def generate_pdf_report(summary_text, week_plot_buf, calendar_buf, filename="weekly_report.pdf"):
    # Using fpdf to create a simple PDF with images
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "주간 감정 리포트", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    for line in summary_text.split("\n"):
        pdf.multi_cell(0, 6, line)
    pdf.ln(4)
    # week plot
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "이번 주 감정 분포", ln=True)
    pdf.image(week_plot_buf, x=15, w=180)
    pdf.ln(4)
    pdf.cell(0, 6, "주간 감정 캘린더", ln=True)
    pdf.image(calendar_buf, x=15, w=180)
    out = io.BytesIO()
    pdf.output(out)
    out.seek(0)
    return out

# ----------------------
# Streamlit UI
# ----------------------

st.set_page_config(page_title="감정 기록 & 분석", layout="wide")
st.title("🌈 감정 기록 & 분석 앱")

# Sidebar: User meta
with st.sidebar:
    st.header("설정")
    name = st.text_input("이름 (선택)", "학생")
    selected_date = st.date_input("기록 날짜 선택 (기본: 오늘)")
    st.markdown("---")
    st.subheader("주간 챌린지")
    weekly_goal = st.number_input("이번 주 긍정 기록 목표 (횟수)", min_value=0, value=3)
    if st.button("챌린지 목표 초기화"):
        st.session_state.pop("challenge_awarded", None)

# Main: 기록 입력
st.subheader("새 감정 기록")
col1, col2 = st.columns([2,3])
with col1:
    emotion = st.selectbox("오늘의 감정 선택", options=EMOTIONS, format_func=lambda x: EMO_LABELS[x])
    note = st.text_area("메모 (선택)", "", max_chars=300, height=80)
    if st.button("기록 저장"):
        # use selected_date + current time
        now = datetime.combine(selected_date, datetime.now().time())
        df = add_entry(emotion, note, when=now)
        st.success("기록이 저장되었습니다! 📥")
        st.experimental_rerun()

with col2:
    st.markdown("**맞춤 피드백**")
    title, suggestion = FEEDBACK.get(emotion, ("감정 인식", "작은 활동을 시도해보세요"))
    st.info(title)
    st.write(suggestion)
    st.markdown("---")
    st.markdown("**짧은 호흡 가이드 (4-4-4)**")
    st.write("1) 코로 4초 들이마시기. 2) 4초 멈추기. 3) 4초 천천히 내쉬기. 1분 수행 권장.")

# Load data and show table
st.subheader("기록 내역")
df = load_data()
if df.empty:
    st.info("아직 기록이 없습니다. 위에서 기록을 추가해보세요.")
else:
    st.dataframe(df.sort_values("timestamp", ascending=False))

# Weekly analysis
st.subheader("주간 분석")
week_counts, week_df = weekly_counts(df, ref_date=selected_date)
col3, col4 = st.columns(2)
with col3:
    st.markdown("**이번 주 감정 분포 (막대그래프)**")
    buf = create_week_plot(week_counts)
    st.image(buf)
    # show numeric
    st.write(week_counts.rename(index=EMO_LABELS))

with col4:
    st.markdown("**주간 감정 캘린더**")
    day_em = emotion_calendar(df, ref_date=selected_date)
    cal_buf = create_calendar_plot(day_em)
    st.image(cal_buf)
    # show icons / labels
    cols = st.columns(7)
    for i,(d,emo) in enumerate(day_em.items()):
        with cols[i]:
            st.write(d.strftime("%a %m/%d"))
            if emo is None:
                st.write("-")
            else:
                st.write(EMO_LABELS[emo])

# Challenge tracking
st.subheader("챌린지 진행 상황")
positive_count = week_df[week_df["emotion"].isin(["very_happy","happy"])].shape[0]
st.write(f"이번 주 긍정 기록 수: **{positive_count}** / 목표 **{weekly_goal}**")
if positive_count >= weekly_goal and not st.session_state.get("challenge_awarded", False):
    st.balloons()
    st.success("축하합니다! 챌린지를 달성했어요 🎉")
    st.session_state["challenge_awarded"] = True
elif st.session_state.get("challenge_awarded", False):
    st.info("이미 이번 주 챌린지를 달성했습니다 ✅")

# Generate PDF report & download
st.subheader("주간 리포트 다운로드 (PDF)")
if df.empty:
    st.info("기록이 없어서 리포트를 만들 수 없습니다.")
else:
    # create a summary
    avg_emotion = week_counts.idxmax() if week_counts.sum() > 0 else None
    summary_lines = [
        f"사용자: {name}",
        f"주간( {get_week_range(selected_date)[0]} ~ {get_week_range(selected_date)[1]} ) 요약:",
    ]
    summary_lines.append(f"- 총 기록 수: {len(week_df)}")
    summary_lines.append(f"- 가장 많이 기록된 감정: {EMO_LABELS[avg_emotion] if avg_emotion else '기록 없음'}")
    summary_lines.append("")
    summary_lines.append("추천 활동:")
    # include top emotion feedback
    if avg_emotion:
        summary_lines.append(f"- {FEEDBACK[avg_emotion][0]}: {FEEDBACK[avg_emotion][1]}")
    summary_text = "\n".join(summary_lines)

    week_plot_buf = create_week_plot(week_counts)
    calendar_buf = create_calendar_plot(day_em)
    pdf_bytes = generate_pdf_report(summary_text, week_plot_buf, calendar_buf)
    st.download_button("PDF 리포트 다운로드", data=pdf_bytes, file_name="weekly_emotion_report.pdf", mime="application/pdf")

# Export CSV
st.subheader("데이터 내보내기")
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("CSV 다운로드", data=csv, file_name="emotions.csv", mime="text/csv")

st.markdown("---")
st.caption("제작: Streamlit 기반 감정 기록 & 분석 앱 — 수행평가용 예시")
