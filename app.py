import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="따릉이 데이터 대시보드", layout="wide")
st.title("🚲 서울시 공공자전거 이용현황 대시보드")
st.markdown("데이터를 통해 따릉이 이용 패턴을 분석해봅시다.")

# 2. 데이터베이스 연결 및 확인
DB_FILE = "bicycle.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

# DB 파일이 없는 경우를 위한 예외 처리
if not os.path.exists(DB_FILE):
    st.error(f"⚠️ '{DB_FILE}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

# --- 대시보드 본문 시작 ---

# 📊 차트 1: 월별 이용 패턴 (라인 차트)
st.subheader("1. 월별 따릉이 이용 패턴")
query1 = """
SELECT 대여일자, SUM(이용건수) as 총이용건수
FROM 이용정보
GROUP BY 대여일자
ORDER BY 대여일자
"""
with get_connection() as conn:
    df1 = pd.read_sql(query1, conn)

fig1 = px.line(df1, x='대여일자', y='총이용건수', markers=True, title="월별 총 이용건수 변화")
st.plotly_chart(fig1, use_container_width=True)

with st.expander("🔍 사용한 SQL 및 인사이트 보기"):
    st.code(query1, language='sql')
    st.write("- **인사이트**: 계절적 요인에 따라 이용량이 크게 변하며, 주로 야외 활동이 적합한 봄/가을에 이용량이 급증하는 패턴을 보입니다.")


# 🌡️ 차트 2: 기온별 평균 이용량 (막대 차트)
st.subheader("2. 기온에 따른 평균 이용량 분석")
# SQLite의 CAST 기능을 사용하여 5도 단위로 그룹화합니다.
query2 = """
SELECT 
    (CAST(평균기온 / 5 AS INT) * 5) as 기온구간, 
    AVG(이용건수) as 평균이용건수
FROM 이용정보 i
JOIN 기온 t ON i.대여일자 = t.년월
GROUP BY 기온구간
ORDER BY 기온구간
"""
with get_connection() as conn:
    df2 = pd.read_sql(query2, conn)
    # 차트 가독성을 위해 구간 이름 변경 (예: 5 -> "5도~10도")
    df2['기온구간'] = df2['기온구간'].apply(lambda x: f"{x} ~ {x+5}도")

fig2 = px.bar(df2, x='기온구간', y='평균이용건수', color='평균이용건수', 
             color_continuous_scale='Temps', title="5도 단위 기온별 평균 이용건수")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("🔍 사용한 SQL 및 인사이트 보기"):
    st.code(query2, language='sql')
    st.write("- **인사이트**: 너무 춥거나 더운 기온보다는 15~25도 사이의 적당한 기온에서 가장 높은 이용률을 기록합니다.")
    st.write("- 기온이 30도를 넘어가거나 영하로 떨어지면 이용량이 급격히 감소하는 것을 알 수 있습니다.")


# 🏆 차트 3: 인기 대여소 TOP 10 (가로 막대 차트)
st.subheader("3. 가장 인기 있는 대여소 TOP 10")
query3 = """
SELECT b.보관소명, SUM(a.이용건수) as 총이용건수
FROM 이용정보 a
JOIN 대여소 b ON a.대여소번호 = b.대여소번호
GROUP BY b.보관소명
ORDER BY 총이용건수 DESC
LIMIT 10
"""
with get_connection() as conn:
    df3 = pd.read_sql(query3, conn)

fig3 = px.bar(df3, x='총이용건수', y='보관소명', orientation='h', 
             color='총이용건수', color_continuous_scale='Viridis', title="이용건수 상위 10개 대여소")
# 가장 많은 곳이 위로 오도록 정렬
fig3.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3, use_container_width=True)

with st.expander("🔍 사용한 SQL 및 인사이트 보기"):
    st.code(query3, language='sql')
    st.write("- **인사이트**: 유동인구가 많은 지하철역 인근이나 대규모 주거단지 근처 대여소의 이용률이 압도적으로 높습니다.")
    st.write("- 해당 지역들에 자전거 및 거치대 배치를 집중하는 운영 전략이 필요합니다.")