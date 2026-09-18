import streamlit as st
import requests
import pandas as pd
import datetime
import pytz
import plotly.express as px

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="날짜별 박스오피스 순위",
    page_icon="🎬",
    layout="wide"
)

# 1. 한국 시간(KST) 기준 '어제' 날짜 계산 (달력의 최대 선택 가능 날짜)
kst_tz = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst_tz)
yesterday_date = (now_kst - datetime.timedelta(days=1)).date()

# 2. 사이드바에서 날짜 선택 기능 추가
st.sidebar.header("🗓️ 날짜 선택")
selected_date = st.sidebar.date_input(
    "조회할 날짜를 선택하세요",
    value=yesterday_date,       # 기본값: 어제
    max_value=yesterday_date    # 최대 선택 날짜: 어제
)

# 선택한 날짜 변환
target_date_str = selected_date.strftime('%Y%m%d')
target_date_display = selected_date.strftime('%Y년 %m월 %d일')

st.title(f"🎬 {target_date_display} 박스오피스")

# 3. secrets에서 인증키 불러오기
if "KOBIS_KEY" not in st.secrets:
    st.error("🔑 API 인증키(KOBIS_KEY)가 설정되지 않았습니다. Streamlit Cloud Secrets 또는 .streamlit/secrets.toml 파일을 확인해 주세요.")
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# 4. KOBIS API 데이터를 캐싱(기억)하여 요청 최적화하는 함수
@st.cache_data(ttl=3600)
def fetch_daily_boxoffice(date_str, key):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": key,
        "targetDt": date_str
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None, f"서버 응답 오류 (상태 코드: {response.status_code})"
            
        data = response.json()
        
        if "faultInfo" in data:
            fault_msg = data["faultInfo"].get("message", "알 수 없는 오류")
            return None, f"KOBIS API 오류 발생: {fault_msg}"
            
        boxoffice_result = data.get("boxOfficeResult", {})
        movie_list = boxoffice_result.get("dailyBoxOfficeList", [])
        
        if not movie_list:
            return None, "그날은 아직 집계 전입니다."
            
        return movie_list, None

    except requests.exceptions.RequestException as e:
        return None, f"네트워크 통신 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return None, f"데이터 처리 중 오류가 발생했습니다: {str(e)}"

# 데이터 불러오기 실행
movie_data, error_message = fetch_daily_boxoffice(target_date_str, api_key)

# 5. 오류 및 비어있는 데이터 안내 처리
if error_message:
    if error_message == "그날은 아직 집계 전입니다.":
        st.info("ℹ️ 그날은 아직 집계 전입니다.")
    else:
        st.error("❌ 박스오피스 데이터를 불러올 수 없습니다.")
        st.warning(f"**상세 원인:** {error_message}")
        
        with st.expander("🛠️ 문제 해결 가이드 (확인할 사항)"):
            st.write("""
            1. **Secrets 키 이름 확인:** Streamlit Secrets에 `KOBIS_KEY` 이름으로 올바른 발급 키가 입력되어 있는지 확인해 주세요.
            2. **발급받은 키 상태 확인:** 영화진흥위원회(KOBIS) 오픈 API 사이트에서 키가 정상 활성화되어 있는지 확인해 주세요.
            """)
    st.stop()

# 6. 데이터 가공 (문자열 → 숫자 형변환)
df = pd.DataFrame(movie_data)

numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df = df.sort_values(by="rank", ascending=True)

# 7. 전날 대비 순위 증감(rankInten) 화살표 표시 가공
def format_rank_change(val):
    if val > 0:
        return f"🔺 {val}"
    elif val < 0:
        return f"🔷 {abs(val)}"
    else:
        return "-"

df["rank_change_display"] = df["rankInten"].apply(format_rank_change)

# 8. 누적 관객수 100만 명 이상 영화명에 트로피(🏆) 추가
df["movie_name_display"] = df.apply(
    lambda row: f"{row['movieNm']} 🏆" if row["audiAcc"] >= 1000000 else row["movieNm"],
    axis=1
)

# 9. 1위 영화 강조 (지표 카드 3장)
top_movie = df.iloc[0]

st.subheader("🥇 선택한 날짜의 Box Office 1위 영화")
st.markdown(f"### **{top_movie['movie_name_display']}**")

col1, col2, col3 = st.columns(3)
col1.metric(label="일별 관객수", value=f"{top_movie['audiCnt']:,} 명")
col2.metric(label="누적 관객수", value=f"{top_movie['audiAcc']:,} 명")
col3.metric(label="스크린 수", value=f"{top_movie['scrnCnt']:,} 개")

st.markdown("---")

# 10. 관객수 상위 5편 막대그래프
st.subheader("📊 관객수 상위 5개 영화")

top_5_df = df.head(5).copy()

fig = px.bar(
    top_5_df,
    x="movieNm",
    y="audiCnt",
    text="audiCnt",
    labels={"movieNm": "영화명", "audiCnt": "일별 관객수(명)"},
    color="audiCnt",
    color_continuous_scale="Blues"
)

fig.update_traces(texttemplate='%{text:,}명', textposition='outside')
fig.update_layout(xaxis_tickangle=-0, showlegend=False)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 11. 여섯 번째: 캘린더 히트맵 (월/주차별 x 요일별)
st.subheader("🗓️ 캘린더 히트맵 (월/주차 × 요일별 관객 수)")

# 선택한 날짜 기준 데이터프레임 생성
heatmap_df = df.copy()
heatmap_df["date"] = pd.to_datetime(selected_date)

# 요일 및 주차 추출
# 요일 순서 지정 (월요일 ~ 일요일)
day_names_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
heatmap_df["day_name"] = heatmap_df["date"].dt.dayofweek.map(lambda x: day_names_kr[x])
heatmap_df["day_name"] = pd.Categorical(heatmap_df["day_name"], categories=day_names_kr, ordered=True)

# 월 및 월별 주차 계산 (예: 9월 3주차)
heatmap_df["month"] = heatmap_df["date"].dt.month
heatmap_df["week_of_month"] = (heatmap_df["date"].dt.day - 1) // 7 + 1
heatmap_df["month_week"] = heatmap_df.apply(lambda row: f"{row['month']}월 {row['week_of_month']}주차", axis=1)

# 마우스 오버용 yyyy-mm-dd 포맷 문자열
heatmap_df["formatted_date"] = heatmap_df["date"].dt.strftime("%Y-%m-%d")

# 요일별 x 월/주차별 그룹화 및 집계 (일관객 합계)
pivot_agg = heatmap_df.groupby(["month_week", "day_name"], observed=False).agg(
    total_audi=("audiCnt", "sum"),
    formatted_date=("formatted_date", "first")
).reset_index()

# 피벗 테이블 작성 (행: 요일, 열: 월/주차)
pivot_audi = pivot_agg.pivot(index="day_name", columns="month_week", values="total_audi").fillna(0)
pivot_date = pivot_agg.pivot(index="day_name", columns="month_week", values="formatted_date").fillna("-")

# 히트맵 생성 (Plotly px.imshow)
fig_heatmap = px.imshow(
    pivot_audi,
    labels=dict(x="월 / 주차", y="요일", color="총 관객수"),
    x=pivot_audi.columns,
    y=pivot_audi.index,
    color_continuous_scale="Reds", # 관객수가 많을수록 진한 빨간색
    text_auto=False
)

# Customdata로 yyyy-mm-dd 날짜 전달 및 툴팁(Hover) 설정
fig_heatmap.update_traces(
    customdata=pivot_date.values,
    hovertemplate="<b>날짜: %{customdata}</b><br>요일: %{y}<br>총 관객수: %{z:,}명<extra></extra>"
)

fig_heatmap.update_layout(
    height=400,
    xaxis_title="월 / 주차",
    yaxis_title="요일",
    coloraxis_colorbar=dict(title="관객수")
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# 12. 전체 박스오피스 순위 표 (Table)
st.subheader("📋 전체 박스오피스 순위")

display_df = df[[
    "rank", 
    "rank_change_display", 
    "movie_name_display", 
    "openDt", 
    "audiCnt", 
    "audiAcc", 
    "scrnCnt"
]].copy()

display_df.columns = ["순위", "순위 증감", "영화명", "개봉일", "당일 관객수", "누적 관객수", "스크린수"]

st.dataframe(
    display_df.style.format({
        "당일 관객수": "{:,}명",
        "누적 관객수": "{:,}명",
        "스크린수": "{:,}개"
    }),
    use_container_width=True,
    hide_index=True
)
