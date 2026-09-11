import streamlit as st
import requests
import pandas as pd
import datetime
import pytz
import plotly.express as px

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="어제 박스오피스 순위",
    page_icon="🎬",
    layout="wide"
)

# 1. 한국 시간(KST) 기준 '어제' 날짜 구하기
# Streamlit Cloud 서버는 해외 시간(UTC)을 사용하므로 한국 시간대로 명확히 변환해 주어야 합니다.
kst_tz = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst_tz)
yesterday_kst = now_kst - datetime.timedelta(days=1)
target_date_str = yesterday_kst.strftime('%Y%m%d') # YYYYMMDD 형식 문자열 변환
target_date_display = yesterday_kst.strftime('%Y년 %m월 %d일')

st.title(f"🎬 어제({target_date_display})의 박스오피스")

# 2. secrets에서 인증키 불러오기
# Streamlit Cloud의 비밀 금고(Secrets) 설정에 저장된 KOBIS_KEY 값을 읽어옵니다.
if "KOBIS_KEY" not in st.secrets:
    st.error("🔑 API 인증키(KOBIS_KEY)가 설정되지 않았습니다. Streamlit Cloud Secrets 또는 .streamlit/secrets.toml 파일을 확인해 주세요.")
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# 3. KOBIS API 데이터를 캐싱(기억)하여 요청 최적화하는 함수
# ttl=3600: 동일한 날짜로 요청이 들어올 경우 1시간(3600초) 동안 API를 다시 호출하지 않고 이전 결과를 재사용합니다.
@st.cache_data(ttl=3600)
def fetch_daily_boxoffice(date_str, key):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": key,
        "targetDt": date_str
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        # 네트워크 오류 등으로 응답 실패 시
        if response.status_code != 200:
            return None, f"서버 응답 오류 (상태 코드: {response.status_code})"
            
        data = response.json()
        
        # 1) 인증키가 틀리거나 API 오류가 있을 때 (faultInfo 확인)
        if "faultInfo" in data:
            fault_msg = data["faultInfo"].get("message", "알 수 없는 오류")
            return None, f"KOBIS API 오류 발생: {fault_msg}"
            
        # 2) 데이터 응답 구조 검증
        boxoffice_result = data.get("boxOfficeResult", {})
        movie_list = boxoffice_result.get("dailyBoxOfficeList", [])
        
        # 3) 영화 목록이 비어있는 경우
        if not movie_list:
            return None, "해당 날짜의 박스오피스 데이터가 비어 있습니다."
            
        return movie_list, None

    except requests.exceptions.RequestException as e:
        return None, f"네트워크 통신 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return None, f"데이터 처리 중 오류가 발생했습니다: {str(e)}"

# 데이터 불러오기 실행
movie_data, error_message = fetch_daily_boxoffice(target_date_str, api_key)

# 4. 오류 안내 처리 (요청 실패, 인증키 오류, 빈 데이터 등)
if error_message:
    st.error("❌ 박스오피스 데이터를 불러올 수 없습니다.")
    st.warning(f"**상세 원인:** {error_message}")
    
    # 초보자를 위한 안내 가이드 출력
    with st.expander("🛠️ 문제 해결 가이드 (확인할 사항)"):
        st.write("""
        1. **Secrets 키 이름 확인:** Streamlit Secrets에 `KOBIS_KEY` 이름으로 올바른 발급 키가 입력되어 있는지 확인해 주세요.
        2. **발급받은 키 상태 확인:** 영화진흥위원회(KOBIS) 오픈 API 사이트에서 키가 정상 활성화되어 있는지 확인해 주세요.
        3. **집계 시간 확인:** 매일 새벽 시간대에는 KOBIS 측 전날 데이터 집계 작업으로 일시적으로 데이터가 제공되지 않을 수 있습니다.
        """)
    st.stop()

# 5. 데이터 가공 (문자열 → 숫자 형변환)
df = pd.DataFrame(movie_data)

# API 응답 결과는 모든 숫자가 문자열(str) 형태이므로 연산 및 정렬을 위해 정수형(int)으로 변환합니다.
numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# 순위(rank) 기준으로 정렬
df = df.sort_values(by="rank", ascending=True)

# 6. 1위 영화 강조 (지표 카드 3장)
top_movie = df.iloc[0]

st.subheader("🥇 어제의 Box Office 1위 영화")
st.markdown(f"### **{top_movie['movieNm']}**")

col1, col2, col3 = st.columns(3)
col1.metric(label="일별 관객수", value=f"{top_movie['audiCnt']:,} 명")
col2.metric(label="누적 관객수", value=f"{top_movie['audiAcc']:,} 명")
col3.metric(label="스크린 수", value=f"{top_movie['scrnCnt']:,} 개")

st.markdown("---")

# 7. 관객수 상위 5편 막대그래프 (Plotly 활용)
st.subheader("📊 관객수 상위 5개 영화")

top_5_df = df.head(5).copy()

# 보기 좋은 그래프 생성을 위한 Plotly 차트 설정
fig = px.bar(
    top_5_df,
    x="movieNm",
    y="audiCnt",
    text="audiCnt",
    labels={"movieNm": "영화명", "audiCnt": "일별 관객수(명)"},
    color="audiCnt",
    color_continuous_scale="Blues"
)

# 그래프 내부 수치 표시 레이아웃 수정
fig.update_traces(texttemplate='%{text:,}명', textposition='outside')
fig.update_layout(xaxis_tickangle=-0, showlegend=False)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 8. 전체 박스오피스 순위 표 (Table)
st.subheader("📋 전체 박스오피스 순위")

# 표에 보여줄 필요한 컬럼 선택 및 이름 변경
display_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "영화명", "개봉일", "어제 관객수", "누적 관객수", "스크린수"]

# 데이터프레임 스타일링 (숫자에 천 단위 쉼표 추가)
st.dataframe(
    display_df.style.format({
        "어제 관객수": "{:,}명",
        "누적 관객수": "{:,}명",
        "스크린수": "{:,}개"
    }),
    use_container_width=True,
    hide_index=True
)
