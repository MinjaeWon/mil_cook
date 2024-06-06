import streamlit as st
import pandas as pd
import random
import openai

#pip install xlsxwriter  설치건

# OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]  # 여기에 OpenAI API 키를 입력하세요

# # 와이드 레이아웃 설정
# st.set_page_config(layout="wide", page_title="메뉴 영양소 분석 도구")

# 엑셀 파일 경로
file_path = '2식단_전체_통합.xlsx'

# 데이터 로드
df = pd.read_excel(file_path)

# 특정 메뉴를 제외하는 함수
def filter_specific_menus(series, exclude):
    return series[~series.isin(exclude)].dropna().tolist()

# 국, 밥, 반찬, 우유/주스 메뉴 추출
all_menus = pd.concat([df['조식'], df['중식'], df['석식']])
rice_menus = filter_specific_menus(all_menus, [''])
soup_menus = filter_specific_menus(all_menus, [''])
side_dish_menus = filter_specific_menus(all_menus, [''])
drink_menus = ['우유', '주스', '요구르트']

# 새로운 반찬 추천 함수 (ChatGPT 활용)
def get_new_side_dish():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 영양사입니다."},
            {"role": "user", "content": "메뉴 하나만 추천해줘. 군대에서 식사 때 만들 음식 메뉴 하나 추천해줘. 설명 필요없이 메뉴로만 대답해줘."}
        ],
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    new_side_dish = response.choices[0]['message']['content'].strip()
    return new_side_dish

# 한 주의 식단 생성 함수
def generate_weekly_menu():
    menu = {'요일': ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일']}
    meals = ['조식', '중식', '석식']
    for meal in meals:
        menu[meal] = []
        for _ in range(7):  # 각 식사 유형에 대해 7일 간의 식단 생성
            rice = random.choice(rice_menus)
            soup = random.choice(soup_menus)
            side_dishes = random.sample(side_dish_menus, 2)
            new_side_dish = get_new_side_dish() 
            side_dishes.append(new_side_dish)
            drink = random.choice(drink_menus) if random.random() > 0.7 else ""
            # 각 메뉴 항목을 <br> 태그로 구분
            meal_items = f"{rice}<br>{soup}<br>{'<br>'.join(side_dishes)}"
            if drink:
                meal_items += f"<br>{drink}"
            menu[meal].append(meal_items)
    
    df = pd.DataFrame(menu)
    df.set_index('요일', inplace=True)  # 요일을 인덱스로 설정
    return df.T  # 행렬을 전치하여 조식, 중식, 석식을 왼쪽 열에
# 한 달의 식단 생성 함수
def generate_monthly_menu(selected_month):
    month_days = pd.date_range(start=f'2023-{selected_month}-01', end=f'2023-{selected_month}-28').days_in_month.max()
    dates = pd.date_range(start=f'2023-{selected_month}-01', periods=month_days).strftime('%m-%d').tolist()
    
    menu = {'날짜': dates, '조식': [], '중식': [], '석식': []}
    
    for _ in range(month_days):
        for meal in ['조식', '중식', '석식']:
            rice = random.choice(rice_menus)
            soup = random.choice(soup_menus)
            side_dishes = random.sample(side_dish_menus, 2)
            new_side_dish = get_new_side_dish()
            side_dishes.append(new_side_dish)
            drink = random.choice(drink_menus) if random.random() > 0.7 else ""
            menu[meal].append(f"{rice}, {soup}, {', '.join(side_dishes)}, {drink}".strip(", "))
    
    df = pd.DataFrame(menu)
    return df

# # Streamlit 앱 설정
# st.title('식단표 생성기')
# st.write('주간 또는 월간 식단표를 생성합니다.')

# # 주간, 월간 선택
# menu_duration = st.selectbox('기간을 선택하세요', ['선택하세요', '주간', '월간'])

# # 월 선택 (월간 선택 시에만 활성화)
# selected_month = None
# if menu_duration == '월간':
#     selected_month = st.selectbox('월을 선택하세요', [f'{i:02d}' for i in range(1, 13)])

# # Streamlit 앱 설정 부분에서 식단표를 표시하는 방법 수정
# if menu_duration == '주간':
#     if st.button('주간 식단표 생성'):
#         weekly_menu = generate_weekly_menu()
#         st.write('주간 식단표')
#         # Update here to apply styling to both headers and cells
#         styled_menu = weekly_menu.style.set_properties(**{'text-align': 'center'}) \
#                                         .set_table_styles([{
#                                            'selector': 'th',
#                                            'props': [('text-align', 'center')]
#                                         }])
#         st.write(styled_menu.to_html(escape=False), unsafe_allow_html=True)

# elif menu_duration == '월간' and selected_month:
#     if st.button('월간 식단표 생성'):
#         monthly_menu = generate_monthly_menu(selected_month)
#         for col in ['조식', '중식', '석식']:
#             monthly_menu[col] = monthly_menu[col].apply(lambda x: '<br>'.join(x.split(', ')))
#         st.write(f'월간 식단표 ({selected_month}월)')
#         st.write(monthly_menu.style.set_properties(subset=['조식', '중식', '석식'], **{'text-align': 'center'}).hide(axis='index').to_html(escape=False), unsafe_allow_html=True)
