import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 폰트 경로 설정 (Windows와 Linux 환경 처리)
def get_font_path():
    # 폰트 경로 설정 (Windows와 Linux 환경 처리)
    if os.name == 'nt':  # Windows
        font_path = r"C:\Users\SKTelecom\Downloads\NanumGothic.ttf"
    else:  # Linux 또는 다른 OS
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

    if not os.path.exists(font_path):
        st.error(f"❌ '{font_path}' 경로에 폰트가 없습니다. 경로를 확인하세요.")
        st.stop()
    
    return font_path

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

# 유사한 통합국명 찾기 함수
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
        week_ago_data = filtered_data[pd
