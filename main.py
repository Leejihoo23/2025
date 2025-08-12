import streamlit as st
import pandas as pd
from textwrap import dedent

st.set_page_config(page_title="진로탐색 — 진오의 MBTI 직업 추천", page_icon="🧭", layout="wide")

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

# --- 16 MBTI 유형별 추천 직업 DB ---
JOBS = [
    {"mbti": "INTJ", "title": "연구원 / 데이터 과학자", "desc": "복잡한 시스템을 설계하고 분석하는 걸 즐깁니다.", "skills": ["데이터분석", "통계", "파이썬"], "icon": "🧪"},
    {"mbti": "INTJ", "title": "전략 기획", "desc": "장기적 계획 수립과 문제 해결에 강합니다.", "skills": ["전략수립", "문제해결", "리더십"], "icon": "📈"},
    {"mbti": "INTP", "title": "연구개발(R&D)", "desc": "이론적 탐구와 실험에 몰입합니다.", "skills": ["실험설계", "분석", "창의성"], "icon": "🔬"},
    {"mbti": "INTP", "title": "데이터 분석가", "desc": "패턴을 찾아내고 모델링하는 것을 좋아합니다.", "skills": ["SQL", "Python", "통계"], "icon": "📊"},
    {"mbti": "ENTJ", "title": "CEO / 경영자", "desc": "리더십과 전략적 추진력이 강합니다.", "skills": ["경영", "의사결정", "전략"], "icon": "🏢"},
    {"mbti": "ENTJ", "title": "프로젝트 매니저", "desc": "목표 달성과 자원 배분에 능합니다.", "skills": ["PM", "조직관리", "문제해결"], "icon": "📋"},
    {"mbti": "ENTP", "title": "스타트업 창업자", "desc": "새로운 아이디어와 기회를 추구합니다.", "skills": ["창업", "네트워킹", "실험정신"], "icon": "🚀"},
    {"mbti": "ENTP", "title": "마케팅 기획자", "desc": "창의적 캠페인 설계에 능합니다.", "skills": ["마케팅", "스토리텔링", "데이터분석"], "icon": "📢"},
    {"mbti": "INFJ", "title": "상담사 / 임상 심리사", "desc": "사람의 내면을 이해하고 돕는 업무에 적합합니다.", "skills": ["심리학", "상담", "공감능력"], "icon": "🫂"},
    {"mbti": "INFJ", "title": "교육자", "desc": "깊이 있는 코칭과 멘토링을 잘합니다.", "skills": ["교육", "멘토링", "기획"], "icon": "🎓"},
    {"mbti": "INFP", "title": "작가 / 에디터", "desc": "창의적 표현과 의미 찾기를 즐깁니다.", "skills": ["글쓰기", "편집", "창의성"], "icon": "✍️"},
    {"mbti": "INFP", "title": "디자이너", "desc": "심미적 감각과 메시지 전달에 능합니다.", "skills": ["디자인", "시각화", "브랜딩"], "icon": "🎨"},
    {"mbti": "ENFJ", "title": "교육/HR 전문가", "desc": "사람을 이끌고 성장시키는 역할에 적합합니다.", "skills": ["교육", "조직개발", "리더십"], "icon": "🧑‍🏫"},
    {"mbti": "ENFJ", "title": "커뮤니케이션 디렉터", "desc": "조직 내외의 협업을 촉진합니다.", "skills": ["홍보", "소통", "브랜딩"], "icon": "📡"},
    {"mbti": "ENFP", "title": "콘텐츠 마케터", "desc": "아이디어를 현실로 만드는 것을 좋아합니다.", "skills": ["콘텐츠제작", "SNS", "마케팅"], "icon": "💡"},
    {"mbti": "ENFP", "title": "브랜드 전략가", "desc": "스토리텔링과 창의적 비전을 가집니다.", "skills": ["브랜딩", "전략", "기획"], "icon": "🏷️"},
    {"mbti": "ISTJ", "title": "회계사 / 감사인", "desc": "정확함과 책임감을 요구하는 역할에 적합합니다.", "skills": ["회계", "세무", "규정"], "icon": "💼"},
    {"mbti": "ISTJ", "title": "공무원", "desc": "절차와 규칙을 준수하며 안정적으로 일합니다.", "skills": ["행정", "정책", "법규"], "icon": "🏛️"},
    {"mbti": "ISFJ", "title": "간호사", "desc": "타인을 돌보는 세심한 역할에 적합합니다.", "skills": ["간호", "응급처치", "공감"], "icon": "🩺"},
    {"mbti": "ISFJ", "title": "교무행정", "desc": "지원과 안정성을 제공하는 업무를 잘합니다.", "skills": ["행정", "조직", "문서작성"], "icon": "📚"},
    {"mbti": "ESTJ", "title": "운영 관리자", "desc": "프로세스와 팀 운영에 강합니다.", "skills": ["운영", "관리", "리더십"], "icon": "⚙️"},
    {"mbti": "ESTJ", "title": "법무 / 규정 준수", "desc": "규칙을 적용하고 집행하는 역할에 적합합니다.", "skills": ["법률", "규정", "관리"], "icon": "📜"},
    {"mbti": "ESFJ", "title": "이벤트 플래너", "desc": "사람과 경험을 조직하는 것을 즐깁니다.", "skills": ["기획", "이벤트", "운영"], "icon": "🎉"},
    {"mbti": "ESFJ", "title": "고객 성공 매니저", "desc": "관계 관리에 강합니다.", "skills": ["고객관리", "소통", "서비스"], "icon": "🤝"},
    {"mbti": "ISTP", "title": "기계공 / 엔지니어", "desc": "실무 중심의 문제 해결을 잘합니다.", "skills": ["기계", "수리", "문제해결"], "icon": "🔧"},
    {"mbti": "ISTP", "title": "응급 구조원", "desc": "현장에서 빠르게 대응합니다.", "skills": ["응급처치", "체력", "신속성"], "icon": "🚑"},
    {"mbti": "ISFP", "title": "그래픽 디자이너", "desc": "감각적 표현과 세부조정에 능합니다.", "skills": ["디자인", "포토샵", "창의성"], "icon": "🎨"},
    {"mbti": "ISFP", "title": "사진작가", "desc": "순간과 감정을 시각화합니다.", "skills": ["사진", "편집", "예술감각"], "icon": "📷"},
    {"mbti": "ESTP", "title": "영업 / 세일즈", "desc": "즉각적 교섭과 상황 적응이 탁월합니다.", "skills": ["영업", "협상", "설득"], "icon": "💬"},
    {"mbti": "ESTP", "title": "퍼포먼스 마케터", "desc": "실험하고 빠르게 최적화합니다.", "skills": ["마케팅", "데이터분석", "실험"], "icon": "📈"},
    {"mbti": "ESFP", "title": "연예 / 퍼포머", "desc": "무대와 사람 앞에서 에너지를 발휘합니다.", "skills": ["연기", "공연", "대중소통"], "icon": "🎤"},
    {"mbti": "ESFP", "title": "행사 호스트", "desc": "사교적 상황을 즐깁니다.", "skills": ["사회", "기획", "서비스"], "icon": "🎙️"},
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
              <div class='subtitle'>MBTI 성향에 맞춘 직업 추천과 진로 팁을 제공합니다.</div>
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

if results:
    df = pd.DataFrame([{"직업": r['title'], "설명": r['desc'], "스킬": ", ".join(r['skills']), "MBTI": r['mbti']} for r in results])
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("추천 직업 CSV로 다운로드", data=csv, file_name=f"{mbti}_career_suggestions.csv", mime='text/csv')

with st.expander("MBTI와 진로 선택에 대한 팁 (열기)"):
    st.write(dedent("""
    - MBTI는 성향을 이해하는 도구입니다. 능력이나 적성의 절대적 척도가 아닙니다.
    - 추천 결과는 출발점으로 삼고, 직접 경험(인턴/프로젝트/자원봉사 등)으로 확인하세요.
    - 직업 선택 시에는 가치관, 생활리듬, 성장 가능성, 수입/안정성 등을 함께 고려하세요.
    """))

st.markdown("---")
st.markdown("**추가 가능 기능:** 로고/컬러 테마, 이미지·아이콘 자동, 정식 MBTI 검사, Google Sheets 연동.")
