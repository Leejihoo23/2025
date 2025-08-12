import streamlit as st
import pandas as pd
from textwrap import dedent

st.set_page_config(page_title="진로탐색 — 진로의 MBTI 직업 추천", page_icon="🧭", layout="wide")

# --- Custom CSS ---
st.markdown(
    """
    <style>
    :root{--bg:#0f172a;--card:#0b1220;--accent:#7c3aed}
    .header{display:flex;align-items:center;gap:16px}
    .brand{font-size:28px;font-weight:800}
    .subtitle{color:#94a3b8}
    .hero{background:linear-gradient(90deg,#0f172a 0%, #071129 100%);padding:18px;border-radius:12px}
    .card{background:linear-gradient(180deg, #ffffff, #f8fafc);border-radius:12px;padding:14px;margin-bottom:12px;box-shadow:0 6px 20px rgba(12,16,50,0.06)}
    .job-card{border-radius:10px;padding:12px;margin:8px 0;border:1px solid #eef2ff}
    .tag{display:inline-block;background:#eef2ff;color:#3730a3;padding:6px 10px;border-radius:999px;font-weight:600;margin-right:6px}
    .skill{display:inline-block;background:#f1f5f9;padding:6px 8px;border-radius:8px;margin-right:6px;font-size:13px}
    .small{font-size:13px;color:#64748b}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sample DB ---
JOBS = [
    {"mbti": "INTJ", "title": "연구원 / 데이터 과학자", "desc": "복잡한 시스템을 설계하고 분석하는 걸 즐깁니다.", "skills": ["데이터분석", "통계", "파이썬"], "icon": "🧪"},
    {"mbti": "INTJ", "title": "전략 기획", "desc": "장기적 계획 수립과 문제 해결에 강합니다.", "skills": ["전략수립", "문제해결", "리더십"], "icon": "📈"},
    {"mbti": "ENFP", "title": "콘텐츠 마케터", "desc": "아이디어를 현실로 만드는 것을 좋아합니다.", "skills": ["스토리텔링", "콘텐츠제작", "커뮤니케이션"], "icon": "✍️"},
    {"mbti": "ISFP", "title": "그래픽 디자이너", "desc": "감각적 표현과 세부조정에 능합니다.", "skills": ["포토샵", "디자인감각", "포트폴리오"], "icon": "🎨"},
    {"mbti": "ESTJ", "title": "운영 관리자", "desc": "프로세스와 팀 운영에 강합니다.", "skills": ["운영관리", "성과관리", "조직운영"], "icon": "⚙️"},
    {"mbti": "INFJ", "title": "상담사 / 임상 심리사", "desc": "사람의 내면을 이해하고 돕는 업무에 적합합니다.", "skills": ["심리학", "상담스킬", "공감능력"], "icon": "🫂"},
    # ... 필요시 더 추가
]

MBTI_LIST = sorted(list({j['mbti'] for j in JOBS}))

# --- Layout: Hero ---
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='hero'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='header'>
              <div class='brand'>🧭 진오의 MBTI 진로 가이드</div>
              <div class='subtitle'>교육용 데모 — MBTI 성향에 맞춘 직업 추천과 진로 팁을 제공합니다.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='text-align:right'><span class='small'>교육용 • 비상업적</span></div>", unsafe_allow_html=True)

# --- Sidebar: inputs ---
st.sidebar.header("입력 — MBTI 선택")
mode = st.sidebar.radio("입력 방식:", ("직접선택", "간단퀵체크"))

if mode == "직접선택":
    mbti = st.sidebar.selectbox("MBTI 유형 선택", options=sorted(MBTI_LIST))
else:
    st.sidebar.write("간단 퀵체크: 예를 더 많이 선택하면 해당 항목이 선택됩니다.")
    e = st.sidebar.radio("에너지", ("E", "I"))
    s = st.sidebar.radio("인식", ("S", "N"))
    t = st.sidebar.radio("판단", ("T", "F"))
    j = st.sidebar.radio("생활", ("J", "P"))
    mbti = f"{e}{s}{t}{j}"

# Filters
st.sidebar.markdown("---")
st.sidebar.subheader("필터")
keyword = st.sidebar.text_input("키워드 검색 (직업명/스킬)")
skill_filter = st.sidebar.multiselect("스킬 필터", options=sorted({s for j in JOBS for s in j['skills']}))

# --- Main: show selection ---
st.markdown(f"### 선택된 MBTI: **{mbti}**")

# Search & filter
def match_job(job):
    if job['mbti'] != mbti:
        return False
    if keyword:
        k = keyword.lower()
        if k not in job['title'].lower() and k not in job['desc'].lower() and not any(k in s.lower() for s in job['skills']):
            return False
    if skill_filter:
        if not set(skill_filter).issubset(set(job['skills'])):
            return False
    return True

results = [j for j in JOBS if match_job(j)]

# Layout: results cards + detail panel
left, right = st.columns([2, 1])
with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("추천 직업")
    if results:
        for idx, job in enumerate(results):
            st.markdown("<div class='job-card'>", unsafe_allow_html=True)
            col_a, col_b = st.columns([8, 2])
            with col_a:
                st.markdown(f"**{job['icon']} {job['title']}**")
                st.markdown(f"<div class='small'>{job['desc']}</div>", unsafe_allow_html=True)
                st.markdown('<div style="margin-top:8px">', unsafe_allow_html=True)
                for s in job['skills']:
                    st.markdown(f"<span class='skill'>{s}</span>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col_b:
                if st.button("자세히 보기", key=f"detail_{idx}"):
                    st.session_state['selected_job'] = idx
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("추천 결과가 없습니다. 필터를 조정하거나 키워드를 지워보세요.")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("직업 상세 / 진로 팁")
    sel = st.session_state.get('selected_job', None)
    if sel is not None and sel < len(results):
        job = results[sel]
        st.markdown(f"### {job['icon']} {job['title']}")
        st.write(job['desc'])
        st.write("**필요 스킬:**", ", ".join(job['skills']))
        st.write("**시작하는 법(초급 단계)**")
        st.write(dedent("""
        1. 기본 관련 도서/온라인 강의 수강
        2. 작게 포트폴리오/프로젝트 진행
        3. 현업 멘토 혹은 스터디 참여
        """))
        st.write("**중장기 학습 로드맵(샘플)**")
        st.progress(30)
    else:
        st.info("직업 카드에서 '자세히 보기'를 눌러 상세 정보를 확인하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# --- Export ---
if results:
    df = pd.DataFrame([{"직업": r['title'], "설명": r['desc'], "스킬": ", ".join(r['skills']), "MBTI": r['mbti']} for r in results])
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("추천 직업 CSV로 다운로드", data=csv, file_name=f"{mbti}_career_suggestions.csv", mime='text/csv')

# --- Helpful tips ---
with st.expander("MBTI와 진로 선택에 대한 팁 (열기)"):
    st.write(dedent("""
    - MBTI는 성향을 이해하는 도구입니다. 능력이나 적성의 절대적 척도가 아닙니다.
    - 추천 결과는 출발점으로 삼고, 직접 경험(인턴/프로젝트/자원봉사 등)으로 확인하세요.
    - 직업 선택 시에는 가치관, 생활리듬, 성장 가능성, 수입/안정성 등을 함께 고려하세요.
    - 학교/기관용으로 사용하실 경우, 직업 데이터베이스를 외부(구글시트/Airtable)와 연동하면 관리가 편합니다.
    """))

st.markdown("---")
st.markdown("**원하시면 다음을 추가해 드릴게요:** 로고/컬러 적용, 직업별 이미지·아이콘, 정식 MBTI 검사(문항), Google Sheets 연동, 또는 학교별 맞춤 데이터.")

