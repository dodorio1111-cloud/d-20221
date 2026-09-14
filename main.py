import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- [1. 데이터 불러오기] 및 [2. 날짜 전처리] ---

# @st.cache_data를 사용하면 데이터를 한 번만 불러오고 임시 저장(캐싱)해 둡니다.
# 덕분에 앱에서 버튼을 누르거나 새로고침할 때마다 다시 불러오지 않아 앱이 빨라집니다.
@st.cache_data
def load_data():
    # 깃허브에 있는 CSV 파일 주소
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    
    # pandas를 이용해 주소에서 직접 데이터를 읽어옵니다.
    df = pd.read_csv(url)
    
    # 결측치(비어있는 데이터)가 포함된 행을 모두 삭제합니다.
    df = df.dropna()
    
    # "기준일자" 컬럼을 텍스트에서 날짜(datetime) 형식으로 바꿔줍니다. (예: 2023-01-01)
    df['기준일자'] = pd.to_datetime(df['기준일자'])
    
    # 전체 데이터를 "기준일자" 순서대로(과거에서 최신 순으로) 정렬합니다.
    df = df.sort_values(by='기준일자')
    
    return df

# 제목 설정
st.title("🎬 영화 박스오피스 데이터 분석")

# 위에서 만든 함수를 실행해 데이터를 불러옵니다.
df = load_data()


# --- [3. 영화 선택 기능] ---

# 영화명 목록을 '누적관객수' 기준으로 내림차순 정렬하여 만듭니다.
# 영화별로 가장 높은 누적관객수(최댓값)를 구한 뒤, 숫자가 큰 순서대로 정렬합니다.
movie_order = df.groupby('영화명')['누적관객수'].max().sort_values(ascending=False).index.tolist()

# 사용자가 영화를 고를 수 있도록 드롭다운(선택 상자)을 만듭니다.
selected_movie = st.selectbox("분석할 영화를 선택하세요:", movie_order)

# 사용자가 선택한 영화의 데이터만 따로 뽑아냅니다.
filtered_df = df[df['영화명'] == selected_movie]


# --- [5. 기타 (구역 나누기 및 그래프 그리기)] ---

# 탭(Tab)으로 구역을 나누어 여러 그래프를 깔끔하게 보여줍니다.
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 개별 영화 일별 관객수", 
    "📊 개별 영화 누적관객수", 
    "🏆 20일 이상 등재 Top 5 비교",
    "📉 전체 관객수 7일 이동평균",
    "📊 월별 전체 관객수 합계"
])

with tab1:
    # --- [4. 선그래프 그리기] ---
    
    # Plotly를 사용해 x축은 '기준일자', y축은 '해당일관객수'로 선 그래프를 만듭니다.
    fig1 = px.line(
        filtered_df, 
        x='기준일자', 
        y='해당일관객수', 
        markers=True, # 데이터 포인트마다 점을 찍어서 보기 쉽게 만듭니다.
        title=f"'{selected_movie}' 해당일관객수 변화"
    )
    
    # Streamlit 화면에 첫 번째 그래프를 출력합니다.
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 아래에 '이 그래프로 알 수 있는 것'을 적을 자리를 만들어 둡니다.
    st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 개봉 후 관객수 감소 추이나 주말/평일 관객수 차이 등을 적어주세요.)")

with tab2:
    # --- [영역차트] ---
    
    # Plotly를 사용해 x축은 '기준일자', y축은 '누적관객수'로 영역 차트(Area Chart)를 만듭니다.
    fig2 = px.area(
        filtered_df,
        x='기준일자',
        y='누적관객수',
        title=f"'{selected_movie}' 누적관객수 변화"
    )
    
    # 영역의 색상이나 투명도 등을 기본값보다 예쁘게 적용합니다.
    fig2.update_traces(line_color='royalblue', fillcolor='rgba(65, 105, 225, 0.5)')
    
    # Streamlit 화면에 두 번째 그래프를 출력합니다.
    st.plotly_chart(fig2, use_container_width=True)
    
    # 그래프 아래에 '이 그래프로 알 수 있는 것'을 적을 자리를 만들어 둡니다.
    st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 시간이 지남에 따라 누적관객수가 어떻게 쌓였는지, 최종 관객수가 얼마인지 등을 적어주세요.)")

with tab3:
    # --- [세 번째 그래프: 조건부 다중 선그래프] ---
    
    # 1. 영화별로 TOP10에 등장한 일수(행 수)를 계산합니다.
    days_count = df.groupby('영화명')['기준일자'].count()
    
    # 2. 등장 일수가 20일 이상인 영화들의 목록만 걸러냅니다.
    long_run_movies = days_count[days_count >= 20].index
    
    # 3. 20일 이상 등장한 영화들 중 '누적관객수 최댓값'을 기준으로 내림차순 정렬하고, 상위 5개를 고릅니다.
    top5_filtered_movies = (
        df[df['영화명'].isin(long_run_movies)]
        .groupby('영화명')['누적관객수']
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index
        .tolist()
    )
    
    # 4. 상위 5개 영화의 데이터만 추출합니다.
    top5_df = df[df['영화명'].isin(top5_filtered_movies)]
    
    # 5. Plotly multi-line chart 생성
    fig3 = px.line(
        top5_df,
        x='기준일자',
        y='누적관객수',
        color='영화명',
        title="🏆 TOP10 20일 이상 등재 영화 중 누적관객수 Top 5 증가 추이 비교"
    )
    
    # 그래프 선을 약간 두껍게 설정하여 가독성을 높입니다.
    fig3.update_traces(line=dict(width=2.5))
    
    # Streamlit 화면에 세 번째 그래프를 출력합니다.
    st.plotly_chart(fig3, use_container_width=True)
    
    # 그래프 아래에 '이 그래프로 알 수 있는 것'을 적을 자리를 만들어 둡니다.
    st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 20일 이상 장기 흥행한 영화들 중 누적관객수 성장 속도 및 최종 흥행 성과 차이 등을 적어주세요.)")

with tab4:
    # --- [네 번째 그래프: 전체 관객수 7일 이동평균선] ---
    
    # 1. 기준일자별로 TOP10 영화 전체의 해당일관객수를 합산합니다.
    daily_total = df.groupby('기준일자')['해당일관객수'].sum().reset_index()
    
    # 2. 합계 데이터에 대해 7일 이동평균(Rolling Mean)을 구합니다.
    daily_total['7일_이동평균'] = daily_total['해당일관객수'].rolling(window=7).mean()
    
    # 3. graph_objects를 사용하여 원본 선과 이동평균 선을 겹쳐서 그립니다.
    fig4 = go.Figure()
    
    # 일별 일일 관객수 합계 (연한 색상)
    fig4.add_trace(go.Scatter(
        x=daily_total['기준일자'],
        y=daily_total['해당일관객수'],
        mode='lines',
        name='일별 총 관객수',
        line=dict(color='lightskyblue', width=1.5),
        opacity=0.6
    ))
    
    # 7일 이동평균선 (진한 색상)
    fig4.add_trace(go.Scatter(
        x=daily_total['기준일자'],
        y=daily_total['7일_이동평균'],
        mode='lines',
        name='7일 이동평균',
        line=dict(color='crimson', width=3)
    ))
    
    # 그래프 레이아웃 설정
    fig4.update_layout(
        title="📉 전체 박스오피스 일별 총 관객수 및 7일 이동평균 추이",
        xaxis_title="기준일자",
        yaxis_title="관객수",
        hovermode="x unified"
    )
    
    # Streamlit 화면에 네 번째 그래프를 출력합니다.
    st.plotly_chart(fig4, use_container_width=True)
    
    # 그래프 아래에 '이 그래프로 알 수 있는 것'을 적을 자리를 만들어 둡니다.
    st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 주말/평일 변동성이 제거된 전체 극장가 관객 흐름, 성수기/비성수기 트렌드 변화 등을 적어주세요.)")

with tab5:
    # --- [다섯 번째 그래프: 월별 전체 관객수 막대그래프] ---
    
    # 1. '기준일자'에서 연-월(YYYY-MM) 정보를 추출하여 새로운 컬럼을 만듭니다.
    daily_total['연월'] = daily_total['기준일자'].dt.to_period('M').astype(str)
    
    # 2. 월(연월) 단위로 그룹화하여 해당일관객수의 총합을 구합니다.
    monthly_total = daily_total.groupby('연월')['해당일관객수'].sum().reset_index()
    
    # 3. Plotly 막대그래프(Bar Chart) 생성
    fig5 = px.bar(
        monthly_total,
        x='연월',
        y='해당일관객수',
        title="📊 월별 전체 극장가 총 관객수 합계",
        labels={'연월': '월(Year-Month)', '해당일관객수': '총 관객수'},
        text_auto=True # 막대 상단에 자동으로 관객수 수치를 표시합니다.
    )
    
    # 막대 색상 및 레이아웃을 다듬습니다.
    fig5.update_traces(marker_color='mediumseagreen', textposition='outside')
    fig5.update_layout(xaxis_type='category') # 월 라벨이 뭉쳐서 생략되지 않도록 범주형으로 설정합니다.
    
    # Streamlit 화면에 다섯 번째 그래프를 출력합니다.
    st.plotly_chart(fig5, use_container_width=True)
    
    # 그래프 아래에 '이 그래프로 알 수 있는 것'을 적을 자리를 만들어 둡니다.
    st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 연중 극장가 최고 성수기 월과 비성수기 월 비교, 월별 관객 규모 패턴 등을 적어주세요.)")
