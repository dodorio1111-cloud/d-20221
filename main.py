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

st.subheader("1. 장르별 영화 편수 비율")

# 장르별 영화 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화 편수"]

# Plotly 도넛 차트 생성
fig = px.pie(
    genre_counts,
    values="영화 편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 편수 분포",
)

# 마우스오버(툴팁) 시 편수와 비율 표기 설정
fig.update_traces(hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}")

# 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# 그래프 설명 구역
st.divider()
st.markdown("💡 **이 그래프로 알 수 있는 것**")
st.info(
    "박스오피스 상위권 영화 중 특정 장르가 차지하는 비중을 한눈에 파악할 수 있으며, 가장 비중이 높은 주력 장르를 확인해 볼 수 있습니다."
)
