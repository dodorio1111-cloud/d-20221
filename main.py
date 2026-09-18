import pandas as pd
import plotly.express as px
import streamlit as st


# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 데이터를 캐싱합니다.
# 앱이 재실행되어도 매번 CSV를 새로 다운로드하지 않아 속도가 빨라집니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    data = pd.read_csv(url)

    # [2. 날짜 및 데이터 전처리]
    # 결측치가 포함된 행을 삭제합니다.
    data = data.dropna()

    # '기준일자' 컬럼을 datetime 형식으로 변환합니다.
    data["기준일자"] = pd.to_datetime(data["기준일자"])

    # 전체 데이터를 기준일자 순서대로 오름차순 정렬합니다.
    data = data.sort_values(by="기준일자")

    return data


# 앱 제목 설정
st.title("🎬 박스오피스 데이터 분석 앱")

# 데이터 로드
df = load_data()

# [3. 영화 선택 기능]
# 영화별 최대 누적관객수를 기준으로 내림차순 정렬하여 중복 없는 영화 목록을 만듭니다.
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바 또는 메인 화면에서 영화를 선택할 수 있는 드롭다운 메뉴를 생성합니다.
selected_movie = st.selectbox("영화를 선택하세요:", movie_order)

# 선택한 영화의 데이터만 필터링합니다.
filtered_df = df[df["영화명"] == selected_movie]

# [5. 구역 나누기 - 세션 1]
st.divider()  # 구분선 추가
st.header(f"📌 1. {selected_movie} - 일별 관객 수 추이")

# [4. 선그래프 그리기]
# Plotly를 사용해 기준일자별 해당일관객수 변화를 나타내는 선 그래프를 그립니다.
fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객 수 변화",
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 화면 출력
st.plotly_chart(fig1, use_container_width=True)

# [5. 그래프 설명 문구 자리]
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 선택한 영화({selected_movie})의 상영 기간 동안 날짜별 관객 수 증감 추이를 확인할 수 있습니다."
)

# [5. 추후 그래프 추가를 위한 구역 예시]
st.divider()
st.header("📌 2. 추가 분석 그래프 (예정 구역)")
st.info("이 구역에 추후 새로운 분석 그래프를 추가할 수 있습니다.")
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 추후 추가될 그래프에 대한 설명이 들어갈 자리입니다."
)
