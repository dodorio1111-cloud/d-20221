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

# 사용자가 분석할 영화를 선택하는 드롭다운 메뉴
selected_movie = st.selectbox("영화를 선택하세요:", movie_order)

# 선택한 영화의 데이터만 필터링합니다.
filtered_df = df[df["영화명"] == selected_movie]

# -------------------------------------------------------------------
# [4. 첫 번째 그래프: 개별 영화 일별 관객 수 선그래프]
# -------------------------------------------------------------------
st.divider()  # 구분선 추가
st.header(f"📌 1. {selected_movie} - 일별 관객 수 추이")

# Plotly 선그래프 생성
fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객 수 변화",
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 화면 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 문구
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 선택한 영화({selected_movie})의 상영 기간 동안 날짜별 관객 수 증감 추이를 확인할 수 있습니다."
)

# -------------------------------------------------------------------
# [5. 두 번째 그래프: 개별 영화 누적관객수 영역차트]
# -------------------------------------------------------------------
st.divider()  # 구분선 추가
st.header(f"📌 2. {selected_movie} - 누적 관객 수 성장 추이")

# Plotly 영역차트(area chart) 생성
fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}'의 기준일자별 누적 관객 수 추이",
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 화면 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 설명 문구
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 선택한 영화({selected_movie})의 관객 수가 시간에 따라 어떻게 누적되며 성장했는지를 한눈에 확인할 수 있습니다."
)

# -------------------------------------------------------------------
# [6. 세 번째 그래프: 조건부 흥행 TOP 5 영화 누적관객수 비교 다중 선그래프]
# -------------------------------------------------------------------
st.divider()  # 구분선 추가
st.header("📌 3. 장기 흥행(20일 이상) TOP 5 영화 누적 관객 수 비교")

# 1) 영화별 데이터 등장 일수(TOP10 차트 등재 일수) 계산
movie_days = df.groupby("영화명")["기준일자"].count()

# 2) 20일 이상 등장한 영화들만 필터링
movies_over_20days = movie_days[movie_days >= 20].index

# 3) 20일 이상 등장한 영화 중 최대 누적관객수 기준 상위 5개 추출
top5_long_run_movies = (
    df[df["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# 4) 조건에 맞는 TOP 5 영화의 데이터만 추출
top5_df = df[df["영화명"].isin(top5_long_run_movies)]

# 5) color="영화명" 옵션을 통해 영화별 색상 및 범례 적용
fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="20일 이상 차트 등재 영화 중 상위 5개작의 누적 관객 수 비교",
)

# 그래프 화면 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 설명 문구
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** TOP 10에 20일 이상 머무른 장기 흥행작 중 관객 수가 가장 많은 상위 5개 영화({', '.join(top5_long_run_movies)})의 누적 관객 수 성장 속도를 서로 비교할 수 있습니다."
)
