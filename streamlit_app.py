import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# 폴더 생성 함수 (이미지 저장용)
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

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

# 통합국명 유사도 찾기 함수
def find_similar_locations(input_name, locations):
    input_name = input_name.lower()
    locations = [loc.lower() for loc in locations]
    vectorizer = CountVectorizer().fit_transform([input_name] + locations)
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    # 유사도가 높은 상위 10개 통합국명 선택
    similar_indices = cosine_sim.argsort()[-10:][::-1]
    return [locations[i] for i in similar_indices]

# 그래프를 이미지로 저장하고 경로 반환
def save_plot(fig, filename):
    ensure_dir("images")
    filepath = os.path.join("images", filename)
    fig.savefig(filepath, bbox_inches='tight')
    return filepath

# Streamlit 앱 타이틀
st.title("온도 모니터링 대시보드")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요:", type="csv")

if uploaded_file is not None:
    # CSV 파일 읽기 및 날짜 변환
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 결측값을 제외하고 데이터 필터링
    data = data.dropna(subset=['온도'])  # 온도 값이 없는 행 제외

    # 통합국명 입력받기
    user_input = st.text_input("통합국명을 입력하세요:")

    if user_input:
        # 유사한 통합국명 찾기
        unique_locations = data['통합국명'].unique()
        similar_locations = find_similar_locations(user_input, unique_locations)

        # 유사한 통합국명을 선택할 수 있는 폴더 형식으로 제공
        selected_location = st.selectbox("매칭된 통합국명을 선택하세요:", similar_locations)

        # 선택한 통합국명의 데이터 필터링
        filtered_data = data[data['통합국명'].str.lower() == selected_location]

        # 통합국명 결과 출력
        st.write(f"**입력한 통합국명**: {user_input}")
        st.write(f"**선택된 통합국명**: {selected_location}")

        # 각 모듈별 현재 온도 추출
        latest_data = filtered_data.sort_values(by='날짜', ascending=False).groupby('모듈번호').first().reset_index()

        # 일주일 최고 및 최저 온도 계산
        one_week_ago = datetime.now() - timedelta(days=7)
        week_data = filtered_data[filtered_data['날짜'] >= one_week_ago]
        max_temp = week_data['온도'].max()
        min_temp = week_data['온도'].min()

        # 일평균 온도 계산 (결측값 제외)
        today_data = filtered_data[filtered_data['날짜'].dt.date == datetime.now().date()]
        daily_avg_temp = today_data['온도'].mean()

        # 가장 높은 평균 온도를 가진 모듈 찾기
        max_module = latest_data.loc[latest_data['온도'].idxmax()]

        # 최근 24시간 시간대별 평균 온도 계산
        last_24_hours = datetime.now() - timedelta(hours=24)
        recent_data = filtered_data[filtered_data['날짜'] >= last_24_hours]
        hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

        # 2주 평균 온도 계산
        two_weeks_ago = datetime.now() - timedelta(days=14)
        two_weeks_data = filtered_data[filtered_data['날짜'] >= two_weeks_ago]
        two_weeks_avg = two_weeks_data.groupby(two_weeks_data['날짜'].dt.strftime('%m-%d'))['온도'].mean()

        # 하루 중 최대값을 일 단위로 계산
        daily_max = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()

        # 결과 출력
        st.write(f"📈 각 모듈번호의 현재 온도:")
        st.dataframe(latest_data[['모듈번호', '온도']])

        st.write(f"🔥 가장 높은 온도를 가진 모듈번호: **{max_module['모듈번호']}** 온도: **{max_module['온도']}°C**")
        st.write(f"🌡️ 일평균 온도: {daily_avg_temp:.2f}°C")
        st.write(f"🔺 일주일 최고 온도: {max_temp}°C")
        st.write(f"🔻 일주일 최저 온도: {min_temp}°C")

        # 최근 24시간 시간대별 평균 온도 그래프
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-', linewidth=2)
        ax1.set_title('최근 24시간 시간대별 평균 온도', fontsize=15)
        ax1.set_xlabel('시간대 (시)', fontsize=12)
        ax1.set_ylabel('평균 온도 (°C)', fontsize=12)
        plt.grid(True)
        img1_path = save_plot(fig1, "hourly_avg.png")
        st.image(img1_path)

        # 2주 평균 온도 그래프
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o', linestyle='-', linewidth=2)
        ax2.set_title('2주 평균 온도', fontsize=15)
        ax2.set_xlabel('날짜 (월-일)', fontsize=12)
        ax2.set_ylabel('평균 온도 (°C)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        img2_path = save_plot(fig2, "two_weeks_avg.png")
        st.image(img2_path)

        # 하루 중 최대값 그래프
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        ax3.plot(daily_max.index, daily_max.values, marker='o', linestyle='-', linewidth=2)
        ax3.set_title('하루 중 최대 온도', fontsize=15)
        ax3.set_xlabel('날짜 (월-일)', fontsize=12)
        ax3.set_ylabel('최대 온도 (°C)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        img3_path = save_plot(fig3, "daily_max.png")
        st.image(img3_path)
