# -*- coding: utf-8 -*-
"""
===================================================================
[Version Info]
- Current Version: v2.5.5 (최종 프롬프트/가변형 Q&A 동기화 매스터본)
- Last Updated: 2026. 07. 08
- Updates:
  1. 기존 UI 및 이중 프리셋 로더 가드(my_style.txt & doa_filter_prompt.txt) 완벽 유지
  2. TITLE_GENERATION_RULES 및 가변형 Q&A 규칙을 프롬프트 파일 지침에 완전 매핑
  3. 멀티모달 이미지 객체 인식 및 자연스러운 플레이스홀더 배치 로직 싱크 패치
  4. 모델 버전을 공식 레퍼런스 규격(gemini-3.5-flash)으로 최적화 교정
===================================================================
"""

import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image

# 1. 웹 페이지 기본 설정
st.set_page_config(page_title="DOA 여행 콘텐츠 생성기", layout="wide")
st.title("🏆 DOA 여행 콘텐츠 생성기")
st.caption("동행인, 무드, 이동수단과 현실 에피소드 디테일을 반영하여 AI 느낌을 완벽히 지운 '내돈내산' 스타일 글을 생성합니다.")

# ==========================================
# 📁 외부 txt 파일에서 내 말투(프리셋) 불러오기 함수
# ==========================================
def load_preset_style():
    file_path = "my_style.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# ==========================================
# 📁 외부 txt 파일에서 도아 필터 프롬프트 가이드 불러오기 함수
# ==========================================
def load_doa_filter_prompt():
    file_path = "doa_filter_prompt.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return "너는 네이버 여행 블로거야. 친근한 어조로 내돈내산 후기를 작성해줘."

MY_PRESET_STYLE = load_preset_style()

# ==========================================
# 🔒 [보안] 사이드바 입력 및 클라우드 Secrets 하이브리드 키 처리
# ==========================================
with st.sidebar:
    st.header("⚙️ API 인증")
    
    saved_key = ""
    if "GEMINI_API_KEY" in st.secrets:
        saved_key = st.secrets["GEMINI_API_KEY"]
    elif "GEMINI_API_KEY" in os.environ:
        saved_key = os.environ.get("GEMINI_API_KEY")
        
    if saved_key:
        api_key = st.text_input("Gemini API Key가 안전하게 연동되었습니다.", value=saved_key, type="password")
    else:
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
        
    st.markdown("[Google AI Studio](https://aistudio.google.com/)에서 무료 키를 발급받을 수 있습니다.")
    st.divider()
    st.markdown("🎯 **최종 버전 치트키 가동중**\n"
                "- 외부 가이드 파일(`doa_filter_prompt.txt`) 규칙에 맞춰 포스팅이 구성됩니다.\n"
                "- 4가지 후킹 제목 스타일 무작정 랜덤 다변화 선택 엔진 구축.\n"
                "- 고정 Q&A 탈피: 장소 카테고리와 데이터에 맞춰 유기적인 가변 질문 조립.\n"
                "- 이미지 입력 시 멀티모달 시각 분석 후 본문 맥락 일치 묘사 자동 싱크.")

# ==========================================
# 📍 3. 메인 화면 레이아웃 및 입력 폼
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 1. 여행 기본 정보")
    location = st.text_input("여행지 및 핵심 장소명", placeholder="예: 강화도 덕오리주물럭 본점, 인천 강화군 길상면 마니산로 121")
    
    content = st.text_area(
        "솔직한 특징 및 느낀점 (메모하듯 편하게 나열)", 
        placeholder="예: 숯불 초벌구이로 잡내 하나도 없음. 주물럭보단 로스구이가 단연 담백하고 풍미 깊음. 밑반찬 깔끔하고 쌈채소 셀프 리필 편함.",
        height=100
    )
    
    # 💡 스토리텔링을 위한 인간미 치트키 인풋 항목
    st.subheader("💡 2. 스토리텔링 치트키 (현실 정보 및 에피소드)")
    
    c_episode = st.text_area(
        "현실 에피소드 / 비하인드 스토리",
        placeholder="AI가 모르는 인간적인 맥락을 입력해 주세요.\n예: 남자친구랑 식단 관리 중이라 담백한 로스구이를 시킴, 밑반찬 중 맛탕이 너무 오랜만이라 맛있어서 한 접시 더 리필해 먹음, 정신없이 먹느라 마지막 볶음밥 사진은 깜빡함.",
        height=90
    )
    
    c_bad_point = st.text_area(
        "아쉬웠던 점 / 주의 사항 / 주차 디테일",
        placeholder="독자들을 위한 진정성 있는 솔직 경고성 팁.\n예: 매장 앞 주차장은 넓은데 옆길 오르막에서 확 꺾어 들어와야 해서 초보운전에겐 살짝 빡셈. 시골 한적한 곳이라 대중교통은 힘들고 무조건 자차 드라이브 추천. 밤엔 가로등 없어서 운전 조심해야 함.",
        height=90
    )
    
    c_info = st.text_area(
        "장소 상세 정보 (영업시간 / 가격 등 팩트)",
        placeholder="하단 총정리에 들어갈 정보.\n예: 화-금 11시~20시30분 / 토-일 11시~21시 (매주 월요일 휴무)\n메뉴: 오리주물럭 1인 2만 원, 오리로스 1인 2만 원",
        height=70
    )

    # 📸 [모바일 호환성 패치 및 붙여넣기 가이드 추가]
    uploaded_files = st.file_uploader(
        "직접 찍은 사진 업로드 / 복사-붙여넣기(Ctrl+V) / 드래그 가능", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        help="모바일 환경 호환을 위해 파일 확장자 가드를 최적화했습니다. 사진첩이나 파일 앱에서 선택해 주세요."
    )

with col2:
    st.subheader("✈️ 3. 리얼 디테일 옵션")
    c_category = st.selectbox("장소 카테고리", ["맛집", "카페", "숙소", "명소(풍경/구경)", "액티비티(놀거리/체험)"])
    c_companion = st.selectbox("누구와 함께 갔나요?", ["연인(데이트)", "친구와", "아이와 함께", "부모님(가족)과", "혼자(혼여행)"])
    c_mood = st.selectbox("공간의 분위기/감성", ["조용하고 고즈넉한(힐링)", "인스타 핫플(힙하고 세련된)", "레트로/노포 감성", "럭셔리/깔끔하고 고급진", "자연 친화적(초록초록/오션뷰)"])
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        c_time = st.selectbox("방문 시기", ["주말 저녁", "평일 오전", "평일 오후", "주말 낮", "비/눈 오는 날", "노을 질 무렵", "늦은 야경 타임"])
    with sub_col2:
        c_transport = st.selectbox("이동 수단", ["자차 운전", "대중교통/뚜벅이"])
        
    # 🐛 [오류 패치]: 별점 순서가 뒤죽박죽이던 것을 1점부터 5점까지 순차 정렬 완료
    c_rating = st.select_slider(
        "내돈내산 솔직 평점", 
        options=[
            "★☆☆☆☆ (실망)", 
            "★★☆☆☆ (아쉬움)", 
            "★★★☆☆ (무난함)", 
            "★★★★☆ (추천!)", 
            "★★★★★ (인생스팟)"
        ],
        value="★★★★☆ (추천!)" # 기본 선택값 세팅
    )

    st.subheader("🎨 4. 블로그 발행 스타일")
    tone = st.selectbox(
        "기본 말투 선택 (샘플 글이 없을 때 적용)",
        ["① 친근한 이웃체 (~해요, ~했답니다)", 
         "② 감성 브이로그체 (~했다, ~함)", 
         "③ 정보 전달 전문 에디터체 (~습니다, ~입니다)", 
         "④ 2030 텐션 업 체 (~대박, 존맛 ㅠㅠ)"]
    )
    length = st.selectbox(
        "목표 분량 선택",
        ["1000자 내외", "1500자 내외", "2000자 내외", "2500자 내외", "3000자 내외"]
    )
    
    layout_style = "PC 최적화형 (문단 구분이 깔끔한 긴 줄글 스타일)" if st.radio("가독성 최적화 옵션", ["모바일 최적화 (잦은 줄바꿈 형태)", "PC 최적화 (줄글 형태)"]) == "PC 최적화 (줄글 형태)" else "모바일 최적화형 (1~2줄마다 엔터, 호혹이 짧아 스크롤에 최적화된 스마트에디터 스타일)"
    
    use_preset = st.checkbox("🌟 사전 저장된 내 말투 가져오기 (my_style.txt 연동)", value=True)
    
    if not use_preset:
        sample_text = st.text_area(
            "[선택] 내 블로그 샘플 글 (말투 완벽 복사용)", 
            placeholder="기존에 직접 작성하셨던 정성 글을 붙여넣으면 본인 특유의 톤앤매너, 자주 쓰는 어미, 이모티콘 습관을 AI가 최우선으로 복사합니다.",
            height=130
        )
    else:
        if MY_PRESET_STYLE.strip():
            st.info("⚙️ `my_style.txt` 파일에서 내 말투 프리셋을 성공적으로 로드했습니다.")
            sample_text = MY_PRESET_STYLE
        else:
            st.warning("⚠️ `my_style.txt` 파일이 비어있거나 존재하지 않습니다. 폴더 내 파일을 생성해 주세요.")
            sample_text = ""

st.divider()

# 5. 글 생성 로직 구동 버튼
if st.button("🔥 상위 노출 & 홈판 저격 포스팅 생성하기", type="primary"):
    if not api_key:
        st.error("⚠️ 왼쪽 사이드바에 Gemini API Key를 입력해 주세요.")
    elif not location or not content:
        st.error("⚠️ 여행지와 특징/느낀점은 필수 입력 사항입니다.")
    else:
        with st.spinner("네이버 스마트블록 구조화 및 인간미 디테일 주입 중... ✨"):
            try:
                actual_key = api_key
                if hasattr(actual_key, "to_dict"):
                    actual_key = saved_key if saved_key else ""
                
                client = genai.Client(api_key=actual_key)
                
                images = []
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        img = Image.open(uploaded_file)
                        images.append(img)
                
                # 외부 파일에서 도아 필터 핵심 프롬프트 가이드라인 로드
                system_instruction = load_doa_filter_prompt()
                
                # 유저 인풋 메타 데이터를 통합 가공 (가변형 Q&A 제어용 메타 요소 완벽 포함)
                user_context_prompt = f"""
                [세부 여행 메타 데이터]
                - 여행지/장소: {location}
                - 장소 성격(카테고리): {c_category}
                - 동행자: {c_companion}
                - 분위기/무드: {c_mood}
                - 방문 시기: {c_time}
                - 이동 수단: {c_transport}
                - 사용자의 솔직 평점: {c_rating}
                - 메모된 특징 및 느낀점: {content}
                
                [사용자 제공 현실 스토리 소스]
                - 현실 에피소드/비하인드: {c_episode}
                - 아쉬운 점/주의 사항/주차 팁: {c_bad_point}
                - 장소 팩트 정보(영업시간/가격 등): {c_info}
                
                [스타일 지침]
                - 분량 타겟: {length}
                - 가독성 레이아웃 스타일: {layout_style}
                - 제공된 사진 데이터 개수: {len(images)}개
                """
                
                if sample_text.strip():
                    user_context_prompt += f"""
                    - 말투 복사 요구사항: 아래 제공된 [사용자 샘플 글]의 어조, 종결어미 습관, 이모티콘 사용빈도를 흉내 내어 똑같이 복사할 것.
                    - [사용자 샘플 글]: {sample_text}
                    """
                else:
                    user_context_prompt += f"""
                    - 기본 말투 서체 지침: '{tone}'를 기반으로 어조를 유지할 것.
                    """
                
                contents = [user_context_prompt] + images
                
                # 제미나이 호출 시 외부에서 가져온 유연한 수익화 프롬프트를 system_instruction으로 완전 전송
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.75,
                        top_p=0.9
                    )
                )
                
                st.success("🎉 최신 네이버 알고리즘 및 휴먼 감성 최적화 포스팅이 완성되었습니다!")
                st.text_area("📋 최종 고도화 결과물 (드래그하여 네이버 스마트에디터에 붙여넣으세요)", value=response.text, height=650)
                
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {e}")
