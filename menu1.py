import streamlit as st
import pandas as pd
from collections import Counter
import openai
# import plotly.graph_objects as go
# import plotly.express as px

# OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# # 와이드 레이아웃 설정
# st.set_page_config(layout="wide", page_title="메뉴 영양소 분석 도구")


# 특정 메뉴를 제외하는 함수
def filter_specific_menus(series):
    filtered_series = series.dropna()
    filtered_series = filtered_series[~filtered_series.isin(['밥', '우유', '조미김', '맛김', '깍두기', '생수'])]
    filtered_series = filtered_series[~filtered_series.apply(lambda x: isinstance(x, str) and x.endswith('김치'))]
    filtered_series = filtered_series[~filtered_series.apply(lambda x: isinstance(x, str) and x.endswith('밥'))]
    return filtered_series

# 가장 많이 나온 메뉴 상위 10개를 계산하는 함수
def top_15_menus(series):
    all_menus = []
    filtered_series = filter_specific_menus(series)
    for items in filtered_series:
        if isinstance(items, str):
            all_menus.append(items)
    counter = Counter(all_menus)
    return counter.most_common(7)

# ChatGPT를 사용하여 영양소 분석을 요청하는 함수
def get_nutrition_analysis(menu):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 영양 전문가입니다. 다음 메뉴의 영양소 특징을 짧은 2문장 이내로 매우 간단히 설명해 주세요."},
            {"role": "user", "content": f"{menu}의 영양소 특징을 짤은 2문장 이내로 알려주세요. 간단하게 알려주세요."}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    analysis = response.choices[0].message['content'].strip()
    return analysis

# 데이터프레임 생성 함수
def create_top_15_df(data, analysis_func, season=None):
    
    menus, counts = zip(*data)
    if season:
        analyses = [analysis_func(menu, season) for menu in menus]
    else:
        analyses = [analysis_func(menu) for menu in menus]
    df = pd.DataFrame({
        '메뉴': menus,
        '횟수': counts,
        'AI 기반 메뉴 분석': analyses
    }).sort_values(by='횟수', ascending=False).reset_index(drop=True)
    df.index += 1  # 인덱스를 1부터 시작하도록 설정
    return df

# 데이터 로드 및 전처리 함수
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    return df

# 테이블 스타일링 함수
def render_styled_table(df):
    styled_df = df.style.set_table_styles(
        [{'selector': 'thead th', 'props': [('background-color', '#f4f4f4'), ('color', '#333'), ('font-weight', 'bold'), ('text-align', 'center')]},
         {'selector': 'tbody td', 'props': [('text-align', 'center')]}]
    ).set_properties(**{'text-align': 'center'})
    return styled_df.to_html()

#-------------------col2 부분

# 계절을 구분하는 함수
def get_season(month):
    if month in [3, 4, 5]:
        return '봄'
    elif month in [6, 7, 8]:
        return '여름'
    elif month in [9, 10, 11]:
        return '가을'
    else:
        return '겨울'


# 계절별로 메뉴를 카운트하는 함수
def count_menus_by_season(df, season):
    df['월'] = pd.to_datetime(df['날짜']).dt.month
    df['계절'] = df['월'].apply(get_season)
    filtered_df = df[df['계절'] == season]
    return {
        '조식': top_15_menus(filtered_df['조식']),
        '중식': top_15_menus(filtered_df['중식']),
        '석식': top_15_menus(filtered_df['석식'])
    }


# ChatGPT를 사용하여 계절별 영양소 분석을 요청하는 함수
def get_seasonal_analysis(menu, season):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 영양 전문가입니다. 짧은 2문장 이내로 매우 간단히 분석해주세요."},
            {"role": "user", "content": f"{menu}가 {season}에 얼마나 도움이 되는지 영양소 측면에서 짧은 2문장 이내로 매우 간단히 분석해 주세요."}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    analysis = response['choices'][0]['message']['content'].strip()
    return analysis


# 파일 경로
file_path = '2식단_전체_통합.xlsx'

# 데이터 로드 및 전처리
df = load_and_process_data(file_path)

# 조식, 중식, 석식별 가장 많이 나온 메뉴 상위 15개
top_15_breakfast = top_15_menus(df['조식'])
top_15_lunch = top_15_menus(df['중식'])
top_15_dinner = top_15_menus(df['석식'])

# 조식, 중식, 석식 구분없이 전체에서 가장 많이 나온 메뉴 상위 15개
all_meals = pd.concat([df['조식'].dropna(), df['중식'].dropna(), df['석식'].dropna()])
top_15_overall = top_15_menus(all_meals)

# # 화면을 좌우로 구분
# col1, col2 = st.columns([1, 1])

# # 조식, 중식, 석식별 막대그래프 출력 및 표 표시
# with col1:

#     # Streamlit 앱 설정
#     st.subheader('✅ 병영 식단 데이터 분석')
#     with st.expander("**📖 분석 방법 안내**"):
#         st.markdown("""
#         <div style="font-size:18px; font-weight:bold; color:#4CAF50;">
#         병영 식단 '식사 유형별' 분석 개요
#         </div>
#         <p style="font-size:14px;">
#         <ol>
#             <li><b>Step 1 :</b> 식사 시기(조식, 중식, 석식, 전체)를 선택.</li>
#             <li><b>Step 2 :</b> 선택 값을 기준으로 가장 많이 나온 메뉴 검색.</li>
#             <li><b>Step 3 :</b> 메뉴별 생성형 AI기술 활용 실시간 영양소 분석.</li>
#         </ol>
#         </p>
#         <div style="font-size:16px; font-weight:bold; margin-top:20px;">
#         검색 Tips
#         </div>
#         <p style="font-size:14px;">
#         전체는 조식, 중식, 석식 구분없이 전체 메뉴에 대한 검색 실시.<br>
#         실시간 AI 분석으로 결과 도출까지 다소 시간이 걸림. <b>AND</b>.
#         </p>
#         """, unsafe_allow_html=True)

#     # 메뉴 선택
#     menu_type = st.selectbox('식사 유형 선택', ['===선택===','조식', '중식', '석식', '전체'])

#     with st.spinner('😍 AI기반 식사 유형별 분석 중...'):

#         if menu_type and menu_type != '===선택===':

#             color_map = {
#             '조식': 'rgb(57,106,177)',
#             '중식': 'rgb(107,174,214)',
#             '석식': 'rgb(214,39,40)',
#             '전체': 'rgb(44,160,44)'
#             }
#             selected_color = color_map.get(menu_type, 'rgb(57,106,177)')
#             if menu_type == '조식':
#                 df_breakfast = create_top_15_df(top_15_breakfast, get_nutrition_analysis)
#                 #st.bar_chart(df_breakfast[['메뉴', '횟수']].set_index('메뉴'))

#                 # plotly 3D bar chart
#                 fig = go.Figure(data=[
#                     go.Bar(
#                         x=df_breakfast['메뉴'], 
#                         y=df_breakfast['횟수'], 
#                         text=df_breakfast['횟수'], 
#                         textposition='auto',
#                         marker=dict(
#                             color=selected_color,  # 색상을 설정
#                             line=dict(color='rgb(8,48,107)', width=1.5)
#                         ),
#                         opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
#                     )
#                 ])
#                 fig.update_layout(
#                     title='조식 상위 15개 메뉴',
#                     xaxis=dict(title='메뉴'),
#                     yaxis=dict(title='횟수'),
#                     paper_bgcolor='rgba(0,0,0,0)',
#                     plot_bgcolor='rgba(0,0,0,0)',
#                     bargap=0.2,
#                     bargroupgap=0.1
#                 )

#                 st.markdown(render_styled_table(df_breakfast), unsafe_allow_html=True)
#             elif menu_type == '중식':
#                 df_lunch = create_top_15_df(top_15_lunch, get_nutrition_analysis)
#                 #st.bar_chart(df_lunch[['메뉴', '횟수']].set_index('메뉴'))

#                 # plotly 3D bar chart
#                 fig = go.Figure(data=[
#                     go.Bar(
#                         x=df_lunch['메뉴'], 
#                         y=df_lunch['횟수'], 
#                         text=df_lunch['횟수'], 
#                         textposition='auto',
#                         marker=dict(
#                             color=selected_color,  # 색상을 설정
#                             line=dict(color='rgb(8,48,107)', width=1.5)
#                         ),
#                         opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
#                     )
#                 ])
#                 fig.update_layout(
#                     title='중식 상위 15개 메뉴',
#                     xaxis=dict(title='메뉴'),
#                     yaxis=dict(title='횟수'),
#                     paper_bgcolor='rgba(0,0,0,0)',
#                     plot_bgcolor='rgba(0,0,0,0)',
#                     bargap=0.2,
#                     bargroupgap=0.1
#                 )
#                 st.plotly_chart(fig)

#                 st.markdown(render_styled_table(df_lunch), unsafe_allow_html=True)

#             elif menu_type == '석식':
#                 df_dinner = create_top_15_df(top_15_dinner, get_nutrition_analysis)
#                 # st.bar_chart(df_dinner[['메뉴', '횟수']].set_index('메뉴'))

#                 # plotly 3D bar chart
#                 fig = go.Figure(data=[
#                     go.Bar(
#                         x=df_dinner['메뉴'], 
#                         y=df_dinner['횟수'], 
#                         text=df_dinner['횟수'], 
#                         textposition='auto',
#                         marker=dict(
#                             color=selected_color,  # 색상을 설정
#                             line=dict(color='rgb(8,48,107)', width=1.5)
#                         ),
#                         opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
#                     )
#                 ])
#                 fig.update_layout(
#                     title='석식 상위 15개 메뉴',
#                     xaxis=dict(title='메뉴'),
#                     yaxis=dict(title='횟수'),
#                     paper_bgcolor='rgba(0,0,0,0)',
#                     plot_bgcolor='rgba(0,0,0,0)',
#                     bargap=0.2,
#                     bargroupgap=0.1
#                 )

#                 st.plotly_chart(fig)
#                 st.markdown(render_styled_table(df_dinner), unsafe_allow_html=True)
#             elif menu_type == '전체':
#                 df_overall = create_top_15_df(top_15_overall, get_nutrition_analysis)
#                 # st.bar_chart(df_overall[['메뉴', '횟수']].set_index('메뉴'))

#                 # plotly 3D bar chart
#                 fig = go.Figure(data=[
#                     go.Bar(
#                         x=df_overall['메뉴'], 
#                         y=df_overall['횟수'], 
#                         text=df_overall['횟수'], 
#                         textposition='auto',
#                         marker=dict(
#                             color=selected_color,  # 색상을 설정
#                             line=dict(color='rgb(8,48,107)', width=1.5)
#                         ),
#                         opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
#                     )
#                 ])
#                 fig.update_layout(
#                     title='전체 상위 15개 메뉴',
#                     xaxis=dict(title='메뉴'),
#                     yaxis=dict(title='횟수'),
#                     paper_bgcolor='rgba(0,0,0,0)',
#                     plot_bgcolor='rgba(0,0,0,0)',
#                     bargap=0.2,
#                     bargroupgap=0.1
#                 )


#                 st.markdown(render_styled_table(df_overall), unsafe_allow_html=True)

# with col2:
#     st.subheader("✅ 계절별 식단 데이터 분석")
#     with st.expander("**📖 분석 방법 안내**"):
#         st.markdown("""
#         <div style="font-size:18px; font-weight:bold; color:#4CAF50;">
#         병영 식단 '계절별' 분석 개요
#         </div>
#         <p style="font-size:14px;">
#         <ol>
#             <li><b>Step 1 :</b> 계절(봄, 여름, 가을, 겨울)을 선택.</li>
#             <li><b>Step 2 :</b> 선택 값을 기준으로 가장 많이 나온 메뉴 검색.</li>
#             <li><b>Step 3 :</b> 메뉴별 생성형 AI기술 활용 실시간 영양소 분석.</li>
#         </ol>
#         </p>
#         <div style="font-size:16px; font-weight:bold; margin-top:20px;">
#         검색 Tips
#         </div>
#         <p style="font-size:14px;">
#         <b>실시간 AI 분석</b>으로 결과 도출까지 다소 시간이 걸림.
#         </p>
#         """, unsafe_allow_html=True)
        
#     season = st.selectbox('계절 선택', ['===선택===', '봄', '여름', '가을', '겨울'])

#     with st.spinner('😍 AI기반 계절별 식단 분석 중...'):

#         if season and season != '===선택===':
#             season_counts = count_menus_by_season(df, season)
#             for meal_type, meal_data in season_counts.items():
#                 df_season = create_top_15_df(meal_data, get_seasonal_analysis, season=season)
#                 #st.bar_chart(df_season[['횟수']].set_index(df_season.index))
#                 # plotly 3D pie chart with enhanced visual effects
#                 fig = go.Figure(data=[go.Pie(
#                     labels=df_season['메뉴'],
#                     values=df_season['횟수'],
#                     textinfo='label+percent',
#                     insidetextorientation='radial',
#                     hole=0.3,
#                     pull=[0.1] * len(df_season),  # Add pull effect to each slice for a more dynamic look
#                     marker=dict(
#                         colors=px.colors.qualitative.Plotly,  # Use Plotly's qualitative color palette
#                         line=dict(color='rgba(0,0,0,0)')  # Remove the border line by setting it to transparent
#                     )
#                 )])

#                 fig.update_traces(
#                     hoverinfo='label+percent+value', 
#                     textfont_size=12, 
#                     marker=dict(
#                         line=dict(color='rgba(0,0,0,0)')  # Ensure the border line is transparent
#                     )
#                 )

#                 fig.update_layout(
#                     title=f"{season} 메뉴 비율",
#                     annotations=[dict(text=f"{season}", x=0.5, y=0.5, font_size=20, showarrow=False)],
#                     showlegend=False,
#                     paper_bgcolor='rgba(0,0,0,0)',  # Make the background transparent for a cleaner look
#                     plot_bgcolor='rgba(0,0,0,0)'    # Make the plot area background transparent
#                 )
                
#                 st.plotly_chart(fig)
#                 st.markdown(render_styled_table(df_season), unsafe_allow_html=True)
#                 break