import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 시스템에서 나눔고딕 폰트 경로 찾기
def get_font_path():
    font_dirs = ["/usr/share/fonts", "/usr/local/share/fonts", "C:/Windows/Fonts"]
    for font_dir in font_dirs:
        for root, _, files in os.walk(font_dir):
            for file in files:
                if "NanumGothic" in file:
                    return os.path.join(root, file)
    st.error("❌ 'NanumGothic' 폰트를 찾을 수 없습니다. 시스템에 폰트를 설치하세요.")
    st.stop()

# 한글 폰트 설정
font_path = get_font_path()
font_prop = fm.FontProperties(fname=font_path)
plt.rc('font', family=font_prop.get_name())

# scikit-learn 라이브러리 오류 처리
try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import CountVectorizer
except ModuleNotFoundError:
    st.error("❌ 'scikit-learn' 라이브러리가 설치되지 않았습니다. 아래 명령어로 설치하세요:\n\n`pip install scikit-learn`")
    st.stop()

# 유사한 통합국명 찾기 함수 (대소문자 구분 없이)
def find_similar_location(input_name, locations):
    input_name = input_name.lower()
    locations = [loc.lower() for loc in locations]
    vectorizer = CountVectorizer().fit_transform([input_name] + locations)
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    most_similar_index = cosine_sim.argmax()
    return locations[most_similar_index]

# Streamlit 앱 타이틀
st.title("온도 모니터링 대시보드")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요:", type="csv")

if uploaded_file is not None:
    # CSV 파일 읽기
    data = pd.read_csv(uploaded_file)

    # 통합국명 입력받기
    user_input = st.text_input("통합국명을 입력하세요:")

    if user_input:
        # 유사한 통합국명 찾기
        unique_locations = data['통합국명'].unique()
        most_similar_location = find_similar_location(user_input, unique_locations)

        # 해당 통합국명의 데이터 필터링
        filtered_data = data[data['통합국명'].str.lower() == most_similar_location]

        # 가장 최근 데이터 추출
        latest_record = filtered_data.sort_values(by='날짜', ascending=False).iloc[0]
        module_number = latest_record['모듈번호']
        latest_temp = latest_record['온도']
        latest_date = latest_record['날짜']

        # 일주일 전 데이터 필터링
        one_week_ago = datetime.now() - timedelta(days=7)
        week_ago_data = filtered_data[pd.to_datetime(filtered_data['날짜']) >= one_week_ago]

        # 일주일 최고/최저 온도 계산
        max_temp = week_ago_data['온도'].max()
        min_temp = week_ago_data['온도'].min()

        # 일주일 최고 온도 추이 계산
        max_temp_trend = week_ago_data.groupby('dt')['온도'].max()

        # 결과 출력
        st.write(f"📍 가장 유사한 통합국명: {most_similar_location}")
        st.write(f"🔢 모듈번호: {module_number}")
        st.write(f"🌡️ 가장 최근 온도: {latest_temp}°C (측정일: {latest_date})")
        st.write(f"🔺 일주일 최고 온도: {max_temp}°C")
        st.write(f"🔻 일주일 최저 온도: {min_temp}°C")

        # 일주일 최고 온도 추이 그래프 시각화
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(max_temp_trend.index.astype(str), max_temp_trend.values, marker='o', linestyle='-', linewidth=2)
        ax.set_title(f"'{most_similar_location}' 지역의 일주일 최고 온도 추이", fontsize=15)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('최고 온도 (°C)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)

        # 그래프 출력
        st.pyplot(fig)
