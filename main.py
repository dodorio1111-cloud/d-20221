import streamlit as st
import pandas as pd
import plotly.express as px

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
tab1, tab2 = st.tabs(["📈 일별 관객수 추이", "📊 누적관객수 변화 (영역차트)"])

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
    
    # Streamlit 화면에 만들어진 그래프를 출력합니다.
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 아래에 '이 그래프로 알 수 있는 것'을 적을 자리를 만들어 둡니다.
    st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 개봉 후 관객수 감소 추이나 주말/평일 관객수 차이 등을 적어주세요.)")

with tab2:
    # --- [새로운 차트 추가: 영역차트] ---
    
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
