import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image

# 1. 웹 페이지 기본 설정
st.set_page_config(page_title="네이버 여행 블로그 마스터", layout="wide")
st.title("🏆 네이버 여행 블로그 상위노출 & 홈판 최적화 프로그램 (최종형)")
st.caption("동행인, 무드, 이동수단 등 디테일한 요소를 선택하여 AI 느낌을 완벽히 지운 '내돈내산' 스타일 글을 생성합니다.")

# ==========================================
# 🔒 [보안 추가] 사이드바 입력 및 클라우드 Secrets 하이브리드 키 처리
# ==========================================
with st.sidebar:
    st.header("⚙️ API 인증")
    
    # 1. 먼저 Streamlit Cloud Secrets나 PC 시스템 환경 변수에 키가 숨겨져 있는지 체크합니다.
    saved_key = ""
    if "GEMINI_API_KEY" in st.secrets:
        saved_key = st.secrets["GEMINI_API_KEY"]
    elif "GEMINI_API_KEY" in os.environ:
        saved_key = os.environ.get("GEMINI_API_KEY")
        
    # 2. 시스템에 저장된 키가 있다면 화면에 연동 메시지를 띄우고 기본값으로 사용합니다.
    if saved_key:
        api_key = st.text_input("Gemini API Key가 안전하게 연동되었습니다.", value=saved_key, type="password")
    else:
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
        
    st.markdown("[Google AI Studio](https://aistudio.google.com/)에서 무료 키를 발급받을 수 있습니다.")
    st.divider()
    st.markdown("🎯 **최종 버전 치트키**\n"
                "- 카테고리와 동행자에 따라 AI가 본문 구성 및 추천 표(Table) 항목을 유연하게 변경합니다.\n"
                "- 방문 시기 및 솔직 평점 옵션이 본문 생동감을 극대화합니다.")

# ==========================================
# 📍 3. 메인 화면 레이아웃 및 입력 폼 (기존 도아님 코드 100% 일치)
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 1. 여행 기본 정보")
    location = st.text_input("여행지 및 핵심 장소명", placeholder="예: 경주 황리단길 감성숙소 00펜션, 애월 오션뷰 카페 XX")
    
    content = st.text_area(
        "솔직한 특징 및 느낀점 (메모하듯 편하게 나열)", 
        placeholder="예: 뷰는 정말 최고였음. 인테리어가 우드톤이라 이쁨. 다만 생각보다 골목 깊숙이 있어서 초보 운전은 진입할 때 힘들 듯. 시그니처 메뉴 꼭 드세요.",
        height=120
    )
    
    uploaded_files = st.file_uploader("직접 찍은 사진 업로드 (멀티모달 매칭용)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    st.subheader("✈️ 2. 리얼 디테일 세팅 (사람 느낌 극대화)")
    c_category = st.selectbox("장소 카테고리", ["맛집", "카페", "숙소", "명소(풍경/구경)", "액티비티(놀거리/체험)"])
    c_companion = st.selectbox("누구와 함께 갔나요?", ["연인(데이트)", "친구와", "아이와 함께", "부모님(가족)과", "혼자(혼여행)"])
    c_mood = st.selectbox("공간의 분위기/감성", ["인스타 핫플(힙하고 세련된)", "조용하고 고즈넉한(힐링)", "레트로/노포 감성", "럭셔리/깔끔하고 고급진", "자연 친화적(초록초록/오션뷰)"])
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        c_time = st.selectbox("방문 시기", ["평일 오전", "평일 오후", "주말 낮", "주말 저녁", "비/눈 오는 날", "노을 질 무렵", "늦은 야경 타임"])
    with sub_col2:
        c_transport = st.selectbox("이동 수단", ["자차 운전", "대중교통/뚜벅이"])
        
    c_rating = st.select_slider("내돈내산 솔직 평점", options=["★☆☆☆☆ (실망)", "★★☆☆☆ (아쉬움)", "★★★☆☆ (무난함)", "★★★★☆ (추천!)", "★★★★★ (인생스팟)"])

with col2:
    st.subheader("🎨 3. 블로그 발행 스타일")
    
    tone = st.selectbox(
        "기본 말투 선택 (샘플 글이 없을 때 적용)",
        ["① 친근한 이웃체 (~해요, ~했답니다)", 
         "② 감성 브이로그체 (~했다, ~함)", 
         "③ 정보 전달 전문 에디터체 (~습니다, ~입니다)", 
         "④ 2030 텐션 업 체 (~대박, 존맛 ㅠㅠ)"]
    )
    
    length = st.selectbox(
        "목표 분량 선택",
        ["500자 내외", "800자 내외", "1000자 내외", "1500자 내외"]
    )
    
    layout_style = "PC 최적화형 (문단 구분이 깔끔한 긴 줄글 스타일)" if st.radio("가독성 최적화 옵션", ["PC 최적화 (줄글 형태)", "모바일 최적화 (잦은 줄바꿈 형태)"]) == "PC 최적화 (줄글 형태)" else "모바일 최적화형 (1~2줄마다 엔터, 호흡이 짧아 스크롤에 최적화된 스마트에디터 스타일)"
    
    sample_text = st.text_area(
        "[선택] 내 블로그 샘플 글 (말투 완벽 복사용)", 
        placeholder="기존에 직접 작성하셨던 정성 글을 붙여넣으면 본인 특유의 톤앤매너, 자주 쓰는 어미, 이모티콘 습관을 AI가 최우선으로 복사합니다.",
        height=220
    )

st.divider()

# 4. 글 생성 로직 구동 버튼
if st.button("🔥 상위 노출 & 홈판 저격 포스팅 생성하기", type="primary"):
    if not api_key:
        st.error("⚠️ 왼쪽 사이드바에 Gemini API Key를 입력해 주세요.")
    elif not location or not content:
        st.error("⚠️ 여행지와 특징/느낀점은 필수 입력 사항입니다.")
    else:
        with st.spinner("네이버 스마트블록 구조화 및 인간미 디테일 주입 중... ✨"):
            try:
                client = genai.Client(api_key=api_key)
                
                images = []
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        img = Image.open(uploaded_file)
                        images.append(img)
                
                # 디테일 메타 데이터를 프롬프트에 융합
                prompt_content = f"""
                너는 네이버 블로그 검색 상위 노출(C-Rank, DIA+ 알고리즘) 및 모바일 홈판 픽업을 겨냥하는 최고의 여행 전문 인플루언서이자 에디터야.
                단순히 정보를 복사하는 AI 느낌을 완전히 배제하고, 실제 사람이 직접 돈을 지불하고 다녀온 '초리얼 생생 후기' 형태로 포스팅을 작성해줘.
                
                [세부 여행 메타 데이터]
                - 여행지/장소: {location}
                - 장소 성격(카테고리): {c_category}
                - 동행자: {c_companion}
                - 분위기/무드: {c_mood}
                - 방문 시기: {c_time}
                - 이동 수단: {c_transport}
                - 사용자의 솔직 평점: {c_rating}
                - 메모된 솔직 특징 및 느낀점: {content}
                
                [스타일 지침]
                - 분량 타겟: {length}
                - 가독성 레이아웃 스타일: {layout_style}
                
                [핵심 반영 규칙 (인간미 주입)]
                1. 동행자가 '{c_companion}'인 점과 이동 수단이 '{c_transport}'인 점을 고려하여 본문과 FAQ에 실용적인 꿀팁을 주입해라. (예: 아이와 함께+자차면 주차장 및 케어 키즈존 여부, 연인과 함께+뚜벅이면 걷기 좋은 데이트 코스 및 접근성 위주 묘사)
                2. 방문 시기인 '{c_time}'를 본문 도입부에 자연스럽게 언급하여 현장감을 살려라. (예: 지난 주말 노을 질 무렵에 방문했더니~)
                3. 사용자의 솔직 평점인 '{c_rating}'에 걸맞게 글 전체의 텐션을 조절하고, 장점뿐만 아니라 메모에 적힌 아쉬운 점(단점)도 '솔직 담백한 내돈내산 팁'으로 포장하여 신뢰도를 높여라.
                
                [출력 구조 명령]
                
                1. 🚀 [네이버 검색 최적화 제목 후보 (3~5개)]
                   - 타겟 스마트블록 키워드를 스스로 예측하여 맨 앞 대괄호 안에 전진 배치할 것.
                   - 동행인, 카테고리, 무드를 반영해 홈판 에디터가 클릭할 법한 감성 문장형으로 뽑을 것.
                   - 구조 예시: [스마트블록 키워드] 감성을 자극하는 문장형 제목
                
                2. 🔍 [SEO 핵심 키워드 & 해시태그 정리]
                   - 본문에 녹인 메인/서브 키워드와 태그 리스트업.
                
                3. 📝 [네이버 AI 및 홈판 에디터 저격 본문]
                   반드시 아래의 4단계 구조로 섹션을 완벽히 분리하여 마크다운 양식으로 작성해라.
                   
                   - [도입부]: 체류시간 확보를 위해 '{c_companion}'와 가기 좋은 곳을 찾는 독자층을 명확히 타겟팅하며 오픈할 것. 방문 시기인 '{c_time}'의 무드를 묘사할 것.
                   
                   - [소제목 1]: '1. 직접 다녀온 {location} 핵심 코스 및 {c_mood} 분위기'
                     * 업로드된 사진이 있다면 시각 정보와 본문 묘사를 완벽히 일치시킬 것(멀티모달 일치).
                     * 가독성 스타일 지침을 엄격히 반영할 것 (모바일 최적화 선택 시 문단을 2~3문장 이내로 짧게 치고 엔터 빈번히 입력).
                     * 본문 흐름상 자연스러운 곳에 `[여기쯤 사진 1 삽입]`, `[여기쯤 사진 2 삽입]` 플레이스홀더를 명시할 것. (단, 첫 사진은 글자 없는 감성 뷰 사진 유도하도록 배치)
                   
                   - [소제목 2]: '2. 한눈에 보는 일정 및 {c_category} 상세 정보 요약'
                     * 네이버 AI 스니펫 노출을 위해 반드시 '마크다운 표(Table)'를 자동 생성할 것.
                     * 카테고리가 맛집/카페면 [메뉴/장소 | 가격 및 요금 | 주차/웨이팅 팁 | {c_companion} 추천 포인트] 구조로 표를 짜고, 숙소/명소면 [장소/룸타입 | 소요 시간 | 이용 팁 | 추천 포인트] 구조로 임의 최적화하여 채울 것.
                   
                   - [소제목 3]: '3. 방문 전 꼭 알아야 할 꿀팁 & FAQ'
                     * 이동 수단({c_transport})과 장단점을 고려해 유저들이 가장 궁금해할 실용적 질문과 답변을 `Q.`, `A.` 형태로 2개 이상 상세히 작성할 것.
                     * 마지막에 `[여기쯤 네이버 플레이스 지도 태그 삽입]` 가이드를 넣을 것.
                
                [말투 및 톤앤매너 지침]
                """
                
                if sample_text.strip():
                    prompt_content += f"""
                    - 최우선 지시: 사용자가 기존에 작성한 아래 [사용자 샘플 글]의 어조, 자주 쓰는 종결어미, 문장 호흡, 이모티콘 활용 패턴을 철저히 분석하여 이 사람의 '영혼을 복사한 듯한' 말투로 본문을 작성해라.
                    - [사용자 샘플 글]: {sample_text}
                    """
                else:
                    prompt_content += f"""
                    - 지정된 기본 말투 서체인 '{tone}'를 100% 구현하여 자연스럽고 신뢰감 있게 작성해라.
                    """
                
                contents = [prompt_content] + images
                
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=contents
                )
                
                st.success("🎉 최신 네이버 알고리즘 및 휴먼 감성 최적화 포스팅이 완성되었습니다!")
                st.text_area("📋 최종 고도화 결과물 (드래그하여 네이버 스마트에디터에 붙여넣으세요)", value=response.text, height=650)
                
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {e}")
