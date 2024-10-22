import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 시스템 폰트 중 'NanumGothic' 폰트 자동 탐색
def find_available_font():
    font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_list:
        if "NanumGothic" in font:
            return font
    st.warning("⚠️ 'NanumGothic' 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    return None

# 폰트 설정
font_path = find_available_font()
if font_path:
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())

# Streamlit 앱 타이틀
st.title("온도 모니터링 대시보드")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요:", type="csv")

if uploaded_file is not None:
    # CSV 파일 읽기
    data = pd.read_csv(uploaded_file)

    # 날짜를 datetime 형식으로 변환
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 각 모듈번호의 평균 온도 계산
    module_avg = data.groupby('모듈번호')['온도'].mean().reset_index()

    # 가장 높은 평균 온도를 가진 모듈 찾기
    max_module = module_avg.loc[module_avg['온도'].idxmax()]

    # 일주일 전 데이터 필터링
    one_week_ago = datetime.now() - timedelta(days=7)
    week_ago_data = data[data['날짜'] >= one_week_ago]

    # 일주일 최고 및 최저 온도 계산
    max_temp = week_ago_data['온도'].max()
    min_temp = week_ago_data['온도'].min()

    # 당일 데이터 필터링 및 평균 온도 계산
    today = datetime.now().date()
    today_data = data[data['날짜'].dt.date == today]
    today_avg = today_data.groupby('모듈번호')['온도'].mean().reset_index()

    # 2주일 데이터 필터링 및 평균 온도 계산
    two_weeks_ago = datetime.now() - timedelta(days=14)
    two_weeks_data = data[data['날짜'] >= two_weeks_ago]
    two_weeks_avg = two_weeks_data.groupby(two_weeks_data['날짜'].dt.strftime('%a'))['온도'].mean()

    # 결과 출력
    st.write(f"📈 각 모듈번호의 평균 온도:")
    st.dataframe(module_avg)

    st.write(f"🔥 가장 높은 온도를 가진 모듈번호: **{max_module['모듈번호']}**")
    st.write(f"🌡️ 평균 온도: {max_module['온도']:.2f}°C")

    st.write(f"🔺 일주일 최고 온도: {max_temp}°C")
    st.write(f"🔻 일주일 최저 온도: {min_temp}°C")

    # 당일 평균 온도 그래프
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(today_avg['모듈번호'], today_avg['온도'])
    ax1.set_title('당일 모듈별 평균 온도', fontsize=15)
    ax1.set_xlabel('모듈번호', fontsize=12)
    ax1.set_ylabel('평균 온도 (°C)', fontsize=12)
    plt.grid(True)

    st.pyplot(fig1)

    # 2주일 평균 온도 그래프 (요일별)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o', linestyle='-', linewidth=2)
    ax2.set_title('2주일 요일별 평균 온도', fontsize=15)
    ax2.set_xlabel('요일', fontsize=12)
    ax2.set_ylabel('평균 온도 (°C)', fontsize=12)
    plt.grid(True)

    st.pyplot(fig2)
