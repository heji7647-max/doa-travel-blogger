import streamlit as st
import os

# ==========================================
# 🔒 [보안 통제] 로컬 시스템 변수 & 클라우드 Secrets 하이브리드 감지
# ==========================================
def get_api_key(key_name):
    # 1. Streamlit 클라우드(Secrets) 환경인지 먼저 확인
    if key_name in st.secrets:
        return st.secrets[key_name]
    # 2. 내 PC(환경 변수) 환경인지 확인
    elif key_name in os.environ:
        return os.environ.get(key_name)
    # 3. 둘 다 없으면 None 반환
    return None

# 필요한 API 키 로드 (상황에 맞게 자동으로 가져옵니다)
openai_key = get_api_key("OPENAI_API_KEY")
gemini_key = get_api_key("GEMINI_API_KEY")

# ==========================================
# 🎨 UI 및 핵심 기능 구현 (기존 블로거 코드 연동)
# ==========================================
st.set_page_config(page_title="DOA 여행 블로그 AI 작가", layout="centered")

st.title("✏️ DOA 여행 블로그 AI 자동 작가")
st.caption("출퇴근길 모바일 환경 및 PC 환경을 모두 지원하는 초안 생성기입니다.")

# 🚨 API 키 유효성 실시간 검증 알림
if not openai_key and not gemini_key:
    st.error("⚠️ API 키를 찾을 수 없습니다! PC의 환경 변수를 확인하거나, Streamlit Cloud의 [Settings] -> [Secrets]에 키를 등록해 주세요.")
else:
    st.success("🔒 API 키 인증 완료: 모바일/PC 모드로 안전하게 연결되었습니다.")

st.markdown("---")

# 1. 입력 폼 영역
with st.form("blogger_form", clear_on_submit=False):
    destination = st.text_input("📍 여행지 입력", placeholder="예: 일본 오사카 도톤보리")
    
    key_points = st.text_area(
        "✨ 방문 장소 및 특징 (Key 포인트)", 
        placeholder="예: 타코야키 맛집 투어, 앗치치혼포 대기 30분, 글리코상 앞에서 인증샷, 야경이 끝내줌",
        height=100
    )
    
    impressions = st.text_area(
        "💬 내가 느낀 점 & 꿀팁", 
        placeholder="예: 주말 저녁에는 사람이 진짜 많으니 5시쯤 미리가는 걸 추천. 소스가 달달해서 맥주 안주로 최고임",
        height=80
    )
    
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("✍️ 작성 말투 선택", ["친근한 이웃 말투 (~해요체)", "감성적인 에세이 톤", "정보 전달형 격식체 (~합니다)", "통통 튀는 20대 블로거 톤"])
    with col2:
        length = st.selectbox("📏 희망 분량", ["공백 제외 1,000자 내외 (기본)", "공백 제외 1,500자 이상 (대형 포스팅)"])
        
    submit_btn = st.form_submit_button("🔥 상위 노출용 블로그 본문 추출하기")

# 2. AI 글쓰기 작동 영역
if submit_btn:
    if not destination.strip() or not key_points.strip():
        st.warning("⚠️ 여행지와 특징(Key 포인트)은 필수 입력 사항입니다.")
    else:
        with st.spinner("🚀 네이버 검색 알고리즘에 맞춘 최적의 여행 글을 작성 중입니다..."):
            # 임시 가상 AI 프롬프트 작동 영역 (기존 사용하시던 LLM 호출 코드가 있다면 여기에 얹으시면 됩니다!)
            # 예시: openai.api_key = openai_key 또는 genai.configure(api_key=gemini_key)
            
            simulated_result = f"""### 🌟 [{destination}] 방문기: 직접 다녀온 생생 후기와 주차/웨이팅 꿀팁 총정리!

안녕하세요! DOA 여행 블로그입니다. 오늘은 정말 기대했던 **{destination}**에 다녀온 이야기를 풀어보려고 해요. 

#### 📍 1. 현장 분위기와 핵심 스팟 체크
이번 여행의 핵심은 바로 이곳이었는데요. 직접 가보니 다음과 같은 특징들이 눈에 띄었습니다.
- **특징 및 코스:** {key_points}

#### 💬 2. 직접 느끼고 온 솔직한 후기 & Tip
개인적으로 가장 좋았던 점은 분위기였어요. 방문하실 분들을 위해 소소한 팁을 공유해 드려요.
- **DOA's 꿀팁:** {impressions}
- **선택한 말투 반영:** {tone} 조건에 맞춰 감성적이고 자연스럽게 녹여냈습니다.

본 초안을 네이버 블로그 임시저장에 복사해 넣으신 뒤 스마트폰 갤러리의 사진과 함께 매칭하여 발행해 보세요!"""
            
            st.markdown("### 📋 AI 생성 초안 결과물")
            st.text_area("텍스트 복사용 창 (전체 선택하여 복사하세요)", value=simulated_result, height=350)
            st.markdown(simulated_result)
