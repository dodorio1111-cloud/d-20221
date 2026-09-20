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
fig_hist.update_traces(hovertemplate="관객 수 구간: %{x}<br>영화 수: %{y}편")

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

st.write("")
st.write("")

# ---------------------------------------------------------
# 네 번째 그래프: 개봉일 스크린 수 vs 총 관객 수 (산점도)
# ---------------------------------------------------------
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계")

# Plotly 산점도 생성
fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",  # 장르별 색상 구분
    hover_name="movieNm",  # 마우스오버 시 영화명 노출
    hover_data={
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f",
        "genre": True,
    },
    title="개봉일 스크린 수 대 총 관객 수",
    labels={
        "first_scrn": "개봉일 스크린 수 (개)",
        "total_audi": "총 관객 수 (명)",
        "genre": "장르",
    },
)

# 마우스오버(툴팁) 레이아웃 설정
fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>장르: %{customdata[0]}<br>개봉일 스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명"
)

# 그래프 출력
st.plotly_chart(fig_scatter, use_container_width=True)

# 그래프 설명 구역
st.divider()
st.markdown("💡 **이 그래프로 알 수 있는 것**")
st.info(
    "개봉일 스크린 수가 많을수록 대체로 총 관객 수도 증가하는 양의 상관관계를 보이지만, 스크린 수에 비해 이례적으로 높은 관객 수를 달성한 입소문 흥행작도 확인할 수 있습니다."
)

st.write("")
st.write("")

# ---------------------------------------------------------
# 다섯 번째 그래프: 주요 장르별 총 관객 수 분포 (박스플롯)
# ---------------------------------------------------------
st.subheader("5. 주요 장르별 총 관객 수 분포 (10편 이상 장르)")

# 영화 수 10편 이상인 장르 필터링
genre_counts_series = df["genre"].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_major = df[df["genre"].isin(major_genres)]

# Plotly 박스플롯 생성
fig_box = px.box(
    df_major,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",  # 이상치 점 노출
    hover_name="movieNm",  # 마우스오버 시 영화명 노출
    hover_data={"total_audi": ":,.0f", "genre": False},
    title="영화 수 10편 이상 주요 장르의 총 관객 수 분포",
    labels={"genre": "장르", "total_audi": "총 관객 수 (명)"},
)

# 마우스오버(툴팁) 설정 (이상치 포함 점 위에서 영화명 표기)
fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객 수: %{y:,.0f}명"
)

# 그래프 출력
st.plotly_chart(fig_box, use_container_width=True)

# 그래프 설명 구역
st.divider()
st.markdown("💡 **이 그래프로 알 수 있는 것**")
st.info(
    "주요 장르별 관객 수의 중앙값과 편차를 비교할 수 있으며, 상자 밖의 이상치 점들을 통해 각 장르 내에서 대흥행을 기록한 대표적인 대작 영화들을 식별할 수 있습니다."
)
