import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 데이터 전처리: '|' 구분자로 나눈 후 첫 번째 장르만 추출
    df["genre"] = df["genre"].fillna("미상").astype(str)
    df["genre"] = df["genre"].apply(lambda x: x.split("|")[0].strip())

    return df


df = load_data()

# ---------------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 비율 (도넛 차트)
# ---------------------------------------------------------
st.subheader("1. 장르별 영화 편수 비율")

# 장르별 영화 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화 편수"]

# Plotly 도넛 차트 생성
fig_donut = px.pie(
    genre_counts,
    values="영화 편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 편수 분포",
)

# 마우스오버(툴팁) 시 편수와 비율 표기 설정
fig_donut.update_traces(
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}"
)

# 그래프 출력
st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 설명 구역
st.divider()
st.markdown("💡 **이 그래프로 알 수 있는 것**")
st.info(
    "박스오피스 상위권 영화 중 특정 장르가 차지하는 비중을 한눈에 파악할 수 있으며, 가장 비중이 높은 주력 장르를 확인해 볼 수 있습니다."
)

st.write("")
st.write("")

# ---------------------------------------------------------
# 두 번째 그래프: 장르 및 영화별 총 관객 수 (트리맵)
# ---------------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객 수 분포")

# Plotly 트리맵 생성 (path: 장르 -> 영화명, values: 총 관객 수)
fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 영화"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 (칸 크기 = 총 관객 수)",
    color="genre",  # 장르별 색상 구분
)

# 마우스오버(툴팁) 시 영화명과 총 관객 수 표기 설정
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명"
)

# 그래프 출력
st.plotly_chart(fig_treemap, use_container_width=True)

# 그래프 설명 구역
st.divider()
st.markdown("💡 **이 그래프로 알 수 있는 것**")
st.info(
    "전체 관객 수 대비 각 장르가 차지하는 규모와, 그 장르 안에서 흥행을 견인한 대표 영화가 무엇인지 상대적인 면적으로 직관적으로 알 수 있습니다."
)

st.write("")
st.write("")

# ---------------------------------------------------------
# 세 번째 그래프: 총 관객 수 분포 (히스토그램)
# ---------------------------------------------------------
st.subheader("3. 총 관객 수 분포")

# 히스토그램 생성
fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="총 관객 수 구간별 영화 수 분포",
    labels={"total_audi": "총 관객 수"},
)

# 툴팁 설정
fig_hist.update_traces(
    hovertemplate="관객 수 구간: %{x}<br>영화 수: %{y}편"
)

# 그래프 출력
st.plotly_chart(fig_hist, use_container_width=True)

# 최다 관객 영화 정보 동적 추출
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

# 그래프 설명 구역
st.divider()
st.markdown("💡 **이 그래프로 알 수 있는 것**")
st.info(
    f"대부분의 영화는 총 관객 수 **500만 명 이하(주로 100만~300만 명대)** 구간에 밀집해 있는 오른쪽 꼬리가 긴 분포를 보이며, "
    f"가장 많은 관객 수를 기록한 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,.0f}명)입니다."
)
