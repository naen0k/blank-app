# streamlit_app.py
# ---------------------------------------------------
# "이름 궁합 보기 ♥"
# - 두 이름을 교차 결합
# - 각 글자의 획수를 바로 아래에 표시
# - 인접합(모듈로 10) 반복 계산 후 최종 % 출력
# ---------------------------------------------------

import streamlit as st

st.set_page_config(page_title="이름 궁합 보기 ♥", page_icon="❤️", layout="centered")

# ====== 획수 표 (사주 이름풀이용) ======
CONSONANT_STROKES = {
    "ㄱ": 2, "ㄲ": 4, "ㄴ": 2, "ㄷ": 3, "ㄸ": 6, "ㄹ": 5, "ㅁ": 4, "ㅂ": 4, "ㅃ": 8,
    "ㅅ": 2, "ㅆ": 4, "ㅇ": 1, "ㅈ": 3, "ㅉ": 6, "ㅊ": 4, "ㅋ": 3, "ㅌ": 4, "ㅍ": 4, "ㅎ": 3
}
VOWEL_STROKES = {
    "ㅏ": 2, "ㅐ": 3, "ㅑ": 3, "ㅒ": 4, "ㅓ": 2, "ㅔ": 3, "ㅕ": 3, "ㅖ": 4,
    "ㅗ": 2, "ㅘ": 4, "ㅙ": 5, "ㅚ": 3, "ㅛ": 3, "ㅜ": 2, "ㅝ": 4, "ㅞ": 5, "ㅟ": 3,
    "ㅠ": 3, "ㅡ": 1, "ㅢ": 2, "ㅣ": 1
}

CHOSEONG_LIST = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JUNGSEONG_LIST = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONGSEONG_LIST = [
    '', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ',
    'ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]

def strokes_for_jong_cluster(cluster: str) -> int:
    return sum(CONSONANT_STROKES.get(ch, 0) for ch in cluster)

def strokes_for_hangul_char(ch: str) -> int:
    """한글 한 글자의 획수 합."""
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        base = code - 0xAC00
        cho_idx = base // 588
        jung_idx = (base % 588) // 28
        jong_idx = base % 28
        cho = CHOSEONG_LIST[cho_idx]
        jung = JUNGSEONG_LIST[jung_idx]
        jong = JONGSEONG_LIST[jong_idx]
        s = CONSONANT_STROKES.get(cho, 0)
        s += VOWEL_STROKES.get(jung, 0)
        s += strokes_for_jong_cluster(jong)
        return s
    return 0

def interleave_names(name1: str, name2: str) -> str:
    """이름을 교차 결합. (장하은, 김운학 → 장김하운은학)"""
    merged = []
    max_len = max(len(name1), len(name2))
    for i in range(max_len):
        if i < len(name1):
            merged.append(name1[i])
        if i < len(name2):
            merged.append(name2[i])
    return "".join(merged)

def reduce_adjacent_sums_mod10(values):
    steps = [values]
    cur = values
    while len(cur) > 1:
        nxt = [(cur[i] + cur[i+1]) % 10 for i in range(len(cur) - 1)]
        steps.append(nxt)
        cur = nxt
    return steps

# ====== UI ======
st.title("이름 궁합 보기 ♥")

with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        name_a = st.text_input("이름 A", value="", placeholder="예: 장하은")
    with col2:
        name_b = st.text_input("이름 B", value="", placeholder="예: 김운학")
    submitted = st.form_submit_button("궁합 보기")

if "results" not in st.session_state:
    st.session_state.results = None

if submitted:
    merged_name = interleave_names(name_a.strip(), name_b.strip())
    strokes = [strokes_for_hangul_char(ch) for ch in merged_name]
    if len(strokes) < 2:
        st.warning("두 이름에서 최소 2글자 이상의 한글이 필요합니다.")
        st.session_state.results = None
    else:
        steps = reduce_adjacent_sums_mod10(strokes)
        st.session_state.results = {
            "merged_name": merged_name,
            "strokes": strokes,
            "steps": steps,
            "final": steps[-1][0]
        }

if st.session_state.results:
    r = st.session_state.results
    st.subheader("1) 글자별 시작 획수")
    st.markdown(
        f"<div style='font-size:20px; text-align:center;'>{r['merged_name']}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size:20px; text-align:center;'>{'  '.join(str(x) for x in r['strokes'])}</div>",
        unsafe_allow_html=True
    )

    st.subheader("2) 계산 과정")
    for i, row in enumerate(r["steps"], start=1):
        st.text(f"{i}단계: {row}")

    st.subheader("3) 최종 궁합 ♥")
    st.markdown(
        f"""
        <div style="font-size:48px;text-align:center;">
            ❤️ {r["final"]} %
        </div>
        """,
        unsafe_allow_html=True
    )

st.caption("※ 본 앱은 재미로 즐기는 간단 계산입니다. 실제 궁합과 무관합니다.")
