import streamlit as st
from google import genai
from google.genai import types

# 1. 웹 페이지 기본 설정
st.set_page_config(page_title="인스타그램 캡션 마스터", layout="wide", initial_sidebar_state="expanded")

st.title("📸 인스타그램 맛집/카페/여행 콘텐츠 자동 생성기")
st.caption("장소, 메뉴, 간단한 특징만 입력하면 알고리즘이 좋아하는 가독성 높은 인스타 감성 캡션과 맞춤형 해시태그를 생성합니다.")

# 2. .streamlit/secrets.toml 로드 검증 (최우선 실행)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    MY_APP_PASSWORD = str(st.secrets["MY_APP_PASSWORD"])  # 문자열 대조를 위해 안전하게 형변환
except KeyError:
    st.error("❌ `.streamlit/secrets.toml` 파일에서 설정 값을 읽어오지 못했습니다.")
    st.info("💡 해당 폴더 안에 GEMINI_API_KEY와 MY_APP_PASSWORD가 올바르게 세팅되어 있는지 확인해 주세요.")
    st.stop()

# 3. 사이드바 비밀번호 입력 모듈
with st.sidebar:
    st.header("⚙️ 인증 및 설정")
    st.divider()
    password_input = st.text_input("프로그램 접속 비밀번호를 입력하세요", type="password")

# =========================================================================
# 4. 화면 레이아웃 구성 및 입력 폼
# =========================================================================

# 화면을 좌우 2단 레이아웃으로 분할 (입력 / 결과)
col1, col2 = st.columns([1, 1])

# --- 좌측 탭: 데이터 입력 공간 ---
with col1:
    st.subheader("📝 정보 입력")
    
    place_name = st.text_input("📍 장소명 및 위치", placeholder="예: 양주 레이크스토어")
    address_info = st.text_input("🗺️ 상세 주소 (생략 가능)", placeholder="예: 경기 양주시 백석읍 기산로 409")
    business_hours = st.text_input("⏰️ 영업시간 및 휴무 (생략 가능)", placeholder="예: 평일 12시-21시, 주말 11시~22시 (화 휴무)")
    menus = st.text_input("🍽️ 먹은 메뉴 / 경험", placeholder="예: 숯불에 구워먹는 셀프 바베큐, 고기, 야채")
    
    features = st.text_area(
        "✍️ 한 줄 특징 & 비하인드 에피소드", 
        placeholder="예: 텐트 치고 짐 챙기기 번거로울 때 몸만 가기 딱 좋음. 여행 온 기분 제대로 느낄 수 있고 힐링됨. 현장 구매 다 됨.",
        height=100
    )
    
    # 인스타그램 무드 및 톤앤매너 선택
    tone_mood = st.radio(
        "🎭 캡션 톤앤매너 선택",
        [
            "✨ 내돈내산 일상/공감형 (도아님 디폴트 말투: 담백하고 트렌디함)",
            "📌 정보/추천형 (저장 및 주말 데이트 코스 강력 유도 스타일)",
            "😎 미니멀/힙한형 (이모지와 극도로 짧은 문장 위주의 시크한 느낌)"
        ]
    )
    
    hashtag_count = st.slider("🏷️ 생성할 해시태그 개수", min_value=5, max_value=25, value=10, step=5)
    
    generate_btn = st.button("🚀 인스타그램 캡션 생성하기", use_container_width=True)

# --- 우측 탭: AI 생성 결과 출력 공간 ---
with col2:
    st.subheader("✨ 생성된 인스타그램 피드 미리보기")
    
    if not password_input:
        st.warning("🔒 프로그램 작동을 위해 사이드바에 비밀번호를 먼저 입력하세요.")
    elif str(password_input) != MY_APP_PASSWORD:
        st.error("❌ 비밀번호가 올바르지 않습니다. 다시 확인해 주세요.")
    else:
        if generate_btn:
            if not place_name or not menus:
                st.error("⚠ 장소명과 메뉴는 필수 입력 사항입니다.")
            else:
                with st.spinner("도아님 말투 이식 중... 🐨🐰"):
                    
                    # 도아님 스타일 가이드라인을 시스템 인스트럭션에 완전 주입
                    system_instruction = (
                        "당신은 트렌디한 개인 여행/맛집 인스타그램 계정을 운영하는 인플루언서 마케터입니다. "
                        "다음 '도아(DOA)'님만의 고유한 피드 작성 규칙을 절대적으로 준수하여 캡션을 작성하세요.\n\n"
                        "[도아님 말투 및 구조 가이드라인]\n"
                        "1. 호들갑 떨거나 유저를 부르는 멘트('여러분~', '심장 부여잡고~')는 절대로 하지 마세요.\n"
                        "2. 첫 줄(Hooking)은 '🐰🐨 [핵심 요약 한 줄] 내돈내산💕' 혹은 그와 결이 맞는 귀여운 이모지와 함께 아주 직관적이고 담백하게 시작하세요.\n"
                        "3. 호흡이 엄청나게 짧습니다. 문장이 조금만 길어져도 줄바꿈을 하세요. 2~3줄 적으면 무조건 문단을 나누어 공백 라인을 두세요. 모바일 화면 가독성이 최우선입니다.\n"
                        "4. 서술형 어미(~요, ~합니다) 남발 대신, 중간중간 명사나 구어체 단어(~바베큐🥩, ~힐링했던 날이에요✨)로 문장을 시크하게 종결하세요.\n"
                        "5. 오글거리는 감성 묘사(노을이 미쳤다, 나만 알고 싶다 등)는 전부 배제하고, 깔끔한 팩트와 경험 위주로 서술하세요.\n"
                        "6. 저장 및 친구 태그 유도 영역 위아래는 반드시 '〰️〰️〰️〰️〰️〰️' 기호로 명확히 감싸세요.\n"
                        "7. 최하단 장소 정보는 무조건 아래의 기호와 순서 포맷을 유지하여 요약하세요:\n"
                        "   📍[장소 이름]\n"
                        "   [상세 주소 (입력된 경우)]\n"
                        "   ⏰️ [영업 시간 (입력된 경우)]\n"
                        "   ✔️ [특징 요약 1]\n"
                        "   ✔️ [특징 요약 2]"
                    )
                    
                    prompt = f"""
                    다음 정보들을 기반으로 도아님 스타일 가이드를 완벽히 적용한 인스타그램 캡션과 해시태그 세트를 생성해줘.

                    [입력 정보]
                    - 장소/위치: {place_name}
                    - 상세 주소: {address_info if address_info else '포함 안 함'}
                    - 영업시간/휴무: {business_hours if business_hours else '포함 안 함'}
                    - 메뉴/경험: {menus}
                    - 특징/에피소드: {features}
                    - 선택한 무드: {tone_mood}
                    - 해시태그 수: {hashtag_count}개 내외

                    [출력 형식 가이드]
                    (첫 줄 제목 🐰🐨 ~ 내돈내산💕)
                    (공백)
                    (본문 내용 - 2~3줄마다 공백 라인 배치 필수)
                    (공백)
                    〰️〰️〰️〰️〰️〰️
                    친구 태그 및 저장 유도 구문
                    〰️〰️〰️〰️〰️〰️
                    (공백)
                    📍{place_name}
                    (주소 및 영업시간이 존재하면 입력)
                    ✔️특징 메세지들 나열
                    (공백)
                    #해시태그 {hashtag_count}개 나열

                    인스타그램 화면에 바로 복사해서 쓸 수 있도록 최종 텍스트만 출력해줘.
                    """
                    
                    try:
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.5, # 말투 재현도를 향상시키기 위해 온도를 조금 낮춤
                            )
                        )
                        
                        generated_text = response.text
                        
                        st.text_area("📋 복사용 텍스트 창 (전체 선택 후 복사하세요)", value=generated_text, height=450)
                        
                        st.markdown("---")
                        st.markdown("### 📱 피드 실제 렌더링 예시")
                        st.info(generated_text)
                        
                    except Exception as e:
                        st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        else:
            st.info("왼쪽 칸에 정보를 입력한 뒤 [인스타그램 캡션 생성하기] 버튼을 눌러주세요.")
