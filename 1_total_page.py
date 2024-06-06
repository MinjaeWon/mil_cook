import streamlit as st

import pandas as pd
import altair as alt

import plotly.graph_objects as go
import plotly.express as px

from PIL import Image

from PIL import Image
from streamlit_option_menu import option_menu
#from langchain.memory import StreamlitChatMessageHistory
#from langchain.callbacks import get_openai_callback

#import hydralit_components as hc

st.set_page_config(page_title = "지능형 군부대 AI영양사", page_icon="🍽️", layout = "wide", initial_sidebar_state = "expanded")
horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 2px; border: none; background-color: #25383C;'><br>"    # thin divider line

# 1. as sidebar menu
with st.sidebar:
    st.sidebar.image("img.png" , use_column_width=True)
    selected_menu = option_menu("주요 서비스", ["Home", '제공 식단 분석', '메뉴 영양소 AI분석', 'AI 식단 작성', '음식 AI챗봇', '급식포털'], 
        icons=['house', 'postcard-heart','tropical-storm','window','symmetry-horizontal'], menu_icon="cast", default_index=0)
    st.markdown(horizontal_bar, True)
    st.sidebar.markdown(
        """
        <style>
        .nice-font {
            font-size:17px;           /* 글자 크기 설정 */
            font-family: 'Helvetica'; /* 글꼴 설정, 시스템에 따라 변경 가능 */
            color: #4a4a4a;           /* 글자색 설정, 원하는 색상 코드로 변경 가능 */
            text-align: center;      	/* 텍스트 중앙 정렬 */
            padding: 10px;            /* 패딩 설정 */
            border-radius: 10px;      /* 테두리 둥글게 설정 */
            background-color: #f0f0f0; /* 배경색 설정 */
        }
        </style>
        <p class="nice-font">대한민국 군인 화이팅</p>
        """,
        unsafe_allow_html=True
)

# InitialPage 함수 정의
def InitialPage():
    # with st.sidebar:
    #     st.subheader("🖼️ Pix Match:")
    #     st.markdown(horizontal_bar, True)

    #     # sidebarlogo = Image.open('sidebarlogo.jpg').resize((300, 420))
    #     #sidebarlogo = Image.open('sidebarlogo.jpg').resize((300, 390))
    #     #st.image(sidebarlogo, use_column_width='auto')

    hlp_dtl = f"""<span style="font-size: 26px;">
    <ol>
    <li style="font-size:19px;"><strong>[메뉴1 : 제공 식단 분석]</strong> 
        <ul>
            <li style="font-size:19px">부대별로 제공된 병영식단 데이터에 대한 유형별 분석 및 시각화</li>
        </ul>
    </li> 
    <li style="font-size:19px;"><strong>[메뉴2 : 메뉴 영양소 AI분석]</strong> 
        <ul>
            <li style="font-size:19px">입력한 메뉴에 대한 AI기반 실시간 영양소 분석</li>
        </ul>
    </li>
    <li style="font-size:19px;"><strong>[메뉴3 : AI 식단 작성]</strong> 
        <ul>
            <li style="font-size:19px">사용자 요구사항 반영한 주간/월간 군부대 AI식단 작성 </li>
        </ul>
    </li> 
    <li style="font-size:19px;"><strong>[메뉴4 : 음식 AI챗봇]</strong> 
        <ul>
            <li style="font-size:19px">음식 영양소 전문 데이터 기반 대화형 AI챗봇 구현</li>
        </ul>
    </li> 
    <li style="font-size:19px;"><strong>[메뉴5 : 급식포털]</strong> 
        <ul>
            <li style="font-size:19px">군급식 홍보 이미지 작성 및 QR 설문조사 기능 구현</li>
        </ul>
    </li> </ol></span>"""

    sc1, sc2 = st.columns(2)
    #random.seed()
    #GameHelpImg = vpth + random.choice(["MainImg1.jpg", "MainImg2.jpg", "MainImg3.jpg", "MainImg4.jpg"]) #랜던으로 사진쓰기.
    GameHelpImg = Image.open("cook_ai.png").resize((700, 400))
    sc2.image(GameHelpImg, use_column_width='auto')
    
    sc1.subheader('[공모전 출품] | 지능형 군부대 AI 영양사 서비스')
    sc1.markdown(horizontal_bar, True)
    sc1.markdown(hlp_dtl, unsafe_allow_html=True)
    st.markdown(horizontal_bar, True)

    author_dtl = "<strong>✔ [2024년 국방 공공데이터 활용 경진대회] 👉 '서비스 개발' 부문</strong>"
    st.markdown(author_dtl, unsafe_allow_html=True)


# Main content based on selected menu
if selected_menu == "Home":
    InitialPage()
    
elif selected_menu == "제공 식단 분석":
    #st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>반가워요! 여기는 당신을 위한 안전한 공간입니다.</h1>", unsafe_allow_html=True)
    import menu1
    
    # 화면을 좌우로 구분
    col1, col2 = st.columns([1, 1])

    # 조식, 중식, 석식별 막대그래프 출력 및 표 표시
    with col1:

        # Streamlit 앱 설정
        st.subheader('✅ 병영 식단 데이터 분석')
        with st.expander("**📖 분석 방법 안내**"):
            st.markdown("""
            <div style="font-size:18px; font-weight:bold; color:#4CAF50;">
            병영 식단 '식사 유형별' 분석 개요
            </div>
            <p style="font-size:14px;">
            <ol>
                <li><b>Step 1 :</b> 식사 시기(조식, 중식, 석식, 전체)를 선택.</li>
                <li><b>Step 2 :</b> 선택 값을 기준으로 가장 많이 나온 메뉴 검색.</li>
                <li><b>Step 3 :</b> 메뉴별 생성형 AI기술 활용 실시간 영양소 분석.</li>
            </ol>
            </p>
            <div style="font-size:16px; font-weight:bold; margin-top:20px;">
            검색 Tips
            </div>
            <p style="font-size:14px;">
            전체는 조식, 중식, 석식 구분없이 전체 메뉴에 대한 검색 실시.<br>
            실시간 AI 분석으로 결과 도출까지 다소 시간이 걸림. <b>AND</b>.
            </p>
            """, unsafe_allow_html=True)

        # 메뉴 선택
        menu_type = st.selectbox('식사 유형 선택', ['===선택===','조식', '중식', '석식', '전체'])

        with st.spinner('🔍 AI기반 식사 유형별 분석 중...'):

            if menu_type and menu_type != '===선택===':

                color_map = {
                '조식': 'rgb(57,106,177)',
                '중식': 'rgb(107,174,214)',
                '석식': 'rgb(214,39,40)',
                '전체': 'rgb(44,160,44)'
                }
                selected_color = color_map.get(menu_type, 'rgb(57,106,177)')
                if menu_type == '조식':
                    df_breakfast = menu1.create_top_15_df(menu1.top_15_breakfast, menu1.get_nutrition_analysis)
                    #st.bar_chart(df_breakfast[['메뉴', '횟수']].set_index('메뉴'))

                    # plotly 3D bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df_breakfast['메뉴'], 
                            y=df_breakfast['횟수'], 
                            text=df_breakfast['횟수'], 
                            textposition='auto',
                            marker=dict(
                                color=selected_color,  # 색상을 설정
                                line=dict(color='rgb(8,48,107)', width=1.5)
                            ),
                            opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
                        )
                    ])
                    fig.update_layout(
                        title='조식 상위 15개 메뉴',
                        xaxis=dict(title='메뉴'),
                        yaxis=dict(title='횟수'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        bargap=0.2,
                        bargroupgap=0.1
                    )

                    st.markdown(menu1.render_styled_table(df_breakfast), unsafe_allow_html=True)
                elif menu_type == '중식':
                    df_lunch = menu1.create_top_15_df(menu1.top_15_lunch, menu1.get_nutrition_analysis)
                    #st.bar_chart(df_lunch[['메뉴', '횟수']].set_index('메뉴'))

                    # plotly 3D bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df_lunch['메뉴'], 
                            y=df_lunch['횟수'], 
                            text=df_lunch['횟수'], 
                            textposition='auto',
                            marker=dict(
                                color=selected_color,  # 색상을 설정
                                line=dict(color='rgb(8,48,107)', width=1.5)
                            ),
                            opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
                        )
                    ])
                    fig.update_layout(
                        title='중식 상위 15개 메뉴',
                        xaxis=dict(title='메뉴'),
                        yaxis=dict(title='횟수'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        bargap=0.2,
                        bargroupgap=0.1
                    )
                    st.plotly_chart(fig)

                    st.markdown(menu1.render_styled_table(df_lunch), unsafe_allow_html=True)

                elif menu_type == '석식':
                    df_dinner = menu1.create_top_15_df(menu1.top_15_dinner, menu1.get_nutrition_analysis)
                    # st.bar_chart(df_dinner[['메뉴', '횟수']].set_index('메뉴'))

                    # plotly 3D bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df_dinner['메뉴'], 
                            y=df_dinner['횟수'], 
                            text=df_dinner['횟수'], 
                            textposition='auto',
                            marker=dict(
                                color=selected_color,  # 색상을 설정
                                line=dict(color='rgb(8,48,107)', width=1.5)
                            ),
                            opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
                        )
                    ])
                    fig.update_layout(
                        title='석식 상위 15개 메뉴',
                        xaxis=dict(title='메뉴'),
                        yaxis=dict(title='횟수'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        bargap=0.2,
                        bargroupgap=0.1
                    )

                    st.plotly_chart(fig)
                    st.markdown(menu1.render_styled_table(df_dinner), unsafe_allow_html=True)
                elif menu_type == '전체':
                    df_overall = menu1.create_top_15_df(menu1.top_15_overall, menu1.get_nutrition_analysis)
                    # st.bar_chart(df_overall[['메뉴', '횟수']].set_index('메뉴'))

                    # plotly 3D bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df_overall['메뉴'], 
                            y=df_overall['횟수'], 
                            text=df_overall['횟수'], 
                            textposition='auto',
                            marker=dict(
                                color=selected_color,  # 색상을 설정
                                line=dict(color='rgb(8,48,107)', width=1.5)
                            ),
                            opacity=0.8  # 막대의 투명도를 낮춰 색상을 더 짙게 설정
                        )
                    ])
                    fig.update_layout(
                        title='전체 상위 15개 메뉴',
                        xaxis=dict(title='메뉴'),
                        yaxis=dict(title='횟수'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        bargap=0.2,
                        bargroupgap=0.1
                    )


                    st.markdown(menu1.render_styled_table(df_overall), unsafe_allow_html=True)

    with col2:
        st.subheader("✅ 계절별 식단 데이터 분석")
        with st.expander("**📖 분석 방법 안내**"):
            st.markdown("""
            <div style="font-size:18px; font-weight:bold; color:#4CAF50;">
            병영 식단 '계절별' 분석 개요
            </div>
            <p style="font-size:14px;">
            <ol>
                <li><b>Step 1 :</b> 계절(봄, 여름, 가을, 겨울)을 선택.</li>
                <li><b>Step 2 :</b> 선택 값을 기준으로 가장 많이 나온 메뉴 검색.</li>
                <li><b>Step 3 :</b> 메뉴별 생성형 AI기술 활용 실시간 영양소 분석.</li>
            </ol>
            </p>
            <div style="font-size:16px; font-weight:bold; margin-top:20px;">
            검색 Tips
            </div>
            <p style="font-size:14px;">
            <b>실시간 AI 분석</b>으로 결과 도출까지 다소 시간이 걸림.
            </p>
            """, unsafe_allow_html=True)
            
        season = st.selectbox('계절 선택', ['===선택===', '봄', '여름', '가을', '겨울'])

        with st.spinner('🔍 AI기반 계절별 식단 분석 중...'):

            if season and season != '===선택===':
                season_counts = menu1.count_menus_by_season(menu1.df, season)
                for meal_type, meal_data in season_counts.items():
                    df_season = menu1.create_top_15_df(meal_data, menu1.get_seasonal_analysis, season=season)
                    #st.bar_chart(df_season[['횟수']].set_index(df_season.index))
                    # plotly 3D pie chart with enhanced visual effects
                    fig = go.Figure(data=[go.Pie(
                        labels=df_season['메뉴'],
                        values=df_season['횟수'],
                        textinfo='label+percent',
                        insidetextorientation='radial',
                        hole=0.3,
                        pull=[0.1] * len(df_season),  # Add pull effect to each slice for a more dynamic look
                        marker=dict(
                            colors=px.colors.qualitative.Plotly,  # Use Plotly's qualitative color palette
                            line=dict(color='rgba(0,0,0,0)')  # Remove the border line by setting it to transparent
                        )
                    )])

                    fig.update_traces(
                        hoverinfo='label+percent+value', 
                        textfont_size=12, 
                        marker=dict(
                            line=dict(color='rgba(0,0,0,0)')  # Ensure the border line is transparent
                        )
                    )

                    fig.update_layout(
                        title=f"{season} 메뉴 비율",
                        annotations=[dict(text=f"{season}", x=0.5, y=0.5, font_size=20, showarrow=False)],
                        showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',  # Make the background transparent for a cleaner look
                        plot_bgcolor='rgba(0,0,0,0)'    # Make the plot area background transparent
                    )
                    
                    st.plotly_chart(fig)
                    st.markdown(menu1.render_styled_table(df_season), unsafe_allow_html=True)
                    break





elif selected_menu == "메뉴 영양소 AI분석":
        
    import menu2
    
    
    # 오른쪽 화면을 col1과 col2로 구분
    col1, col2 = st.columns(2)

    # col1에 조식, 중식, 석식별로 메뉴 입력 필드를 생성
    with col1:
        st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>1️⃣ 메뉴 분석 도구</h1>", unsafe_allow_html=True)
        st.markdown(horizontal_bar, True)
        st.write("**조식, 중식, 석식 메뉴**를 각각 입력하세요 (콤마로 구분):")
        breakfast_input = st.text_input("✔ 조식 메뉴 👇")
        
        lunch_input = st.text_input("✔ 중식 메뉴 👇")
        
        dinner_input = st.text_input("✔ 석식 메뉴 👇")
        
        analyze_button = st.button("분석")

        # 모든 입력된 메뉴를 통합하여 분석에 사용
        all_menus = [menu.strip() for menu in f"{breakfast_input}, {lunch_input}, {dinner_input}".split(',') if menu.strip()]

        # 분석 결과 초기화
        analysis_result = ""
        nutrition_data = pd.DataFrame()

        # 분석 버튼을 누른 경우 GPT 분석 결과 표시
        with st.spinner('🔍 입력 메뉴 분석 중...'):
            if analyze_button and all_menus:
                analysis_result = menu2.ask_gpt_for_nutrition_analysis(all_menus, menu2.recommended_values)
                nutrition_data = menu2.parse_nutrition_data(analysis_result)
            else:
                analysis_result = "❇ 메뉴 입력 및 분석 버튼 클릭 후, 결과가 출력됩니다."

            st.text_area("😍 영양소 분석 결과", value='*[입력메뉴]'+'\n조식:'+breakfast_input+'\n중식:'+lunch_input+'\n석식:'+dinner_input+'\n\n'+analysis_result, height=400)

    # col2에 필수 영양소 7가지를 시각화 및 상태표 표시
    with col2:
        st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>2️⃣ 필수 영양소 7가지 차트 및 상태표</h1>", unsafe_allow_html=True)
        st.markdown(horizontal_bar, True)
        if not nutrition_data.empty:
            # 필수 영양소 데이터 필터링
            essential_df = nutrition_data[nutrition_data['영양소'].isin(menu2.essential_nutrients.keys())]

            # 데이터 변환 및 꺾은선 그래프 생성
            chart_data = essential_df.melt(id_vars='영양소', value_vars=['섭취량', '권장량'], var_name='종류', value_name='값')
            line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                x=alt.X('영양소:N', sort=essential_df['영양소'].tolist()),
                y='값:Q',
                color='종류:N'
            ).properties(width=600, height=400, title="필수 영양소 섭취량과 권장량 비교 꺾은선 그래프")

            st.altair_chart(line_chart)

            # 필수 영양소 상태표를 만들기 위한 함수
            def determine_status(row):
                nutrient = row['영양소']
                intake = row['섭취량']
                recommended = menu2.essential_nutrients.get(nutrient, 0)
                if intake >= recommended * 0.8 and intake <= recommended * 1.2:
                    return '적절'
                elif intake < recommended * 0.8:
                    return '부족'
                else:
                    return '과잉'

            # 상태 계산 및 추가
            essential_df['상태'] = essential_df.apply(determine_status, axis=1)


            # 필수 영양소 상태표를 표 형태로 표시
            st.table(essential_df[['영양소', '섭취량', '권장량', '상태']])
        else:
            st.write("❇ 메뉴 입력 및 분석 버튼 클릭 후, 결과가 출력됩니다.")


elif selected_menu == "AI 식단 작성":
    import menu3

    st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>😜 주간/월간 AI 식단표 생성기</h1>", unsafe_allow_html=True)
    st.markdown(horizontal_bar, True)

    # 주간, 월간 선택
    menu_duration = st.selectbox('✔ 기간을 선택하세요', ['선택하세요', '주간', '월간'])

    # 월 선택 (월간 선택 시에만 활성화)
    selected_month = None
    if menu_duration == '월간':
        selected_month = st.selectbox('✔ 월을 선택하세요.(계절 고려 식단 작성)', [f'{i:02d}' for i in range(1, 13)])

    # Streamlit 앱 설정 부분에서 식단표를 표시하는 방법 수정
    if menu_duration == '주간':
        if st.button('주간 식단표 생성'):
            with st.spinner('🔍 AI기반 주간메뉴 생성 중...'):
                weekly_menu = menu3.generate_weekly_menu()
                st.markdown("<h1 style='color: #7F462C; font-size: 20px;'>🥘 주간 식단표 </h1>", unsafe_allow_html=True)
                st.markdown(horizontal_bar, True)
                # Update here to apply styling to both headers and cells
                styled_menu = weekly_menu.style.set_properties(**{'text-align': 'center'}) \
                                                .set_table_styles([{
                                                'selector': 'th',
                                                'props': [('text-align', 'center')]
                                                }])
                st.write(styled_menu.to_html(escape=False), unsafe_allow_html=True)

    elif menu_duration == '월간' and selected_month:
        if st.button('월간 식단표 생성'):
            with st.spinner('🔍 AI기반 월간메뉴 생성 중...'):
                monthly_menu = menu3.generate_monthly_menu(selected_month)
                for col in ['조식', '중식', '석식']:
                    monthly_menu[col] = monthly_menu[col].apply(lambda x: '<br>'.join(x.split(', ')))
                st.markdown("<h1 style='color: #7F462C; font-size: 20px;'>🥘 주간 식단표 </h1>", unsafe_allow_html=True)
                #st.write(f'월간 식단표 ({selected_month}월)')
                st.write(monthly_menu.style.set_properties(subset=['조식', '중식', '석식'], **{'text-align': 'center'}).hide(axis='index').to_html(escape=False), unsafe_allow_html=True)

   


elif selected_menu == "음식 AI챗봇":
    import menu4

    st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>🧑‍💻 재료 및 영양소 전문 AI챗봇</h1>", unsafe_allow_html=True)
    with st.expander("**📖 (필독) 지능형 AI챗봇 사용법**"):
            st.markdown("""
            <div style="font-size:18px; font-weight:bold; color:#4CAF50;">
            chatGPT와 같은 대화형 AI챗봇
            </div>
            <p style="font-size:14px;">
            <ol>
                <li><b>특징 1 :</b> 사전 전문DB 학습기반 대화형 챗봇(속도, 용량 문제로 제한적 학습)</li>
                <li><b>특징 2 :</b> 음식 재료(어묵김말이, 고구마그라탕 등) 및 영양소(호박죽, 산채비빔밥 등)에 대한 질문 가능</li>
                <li><b>특징 3 :</b> 사전 학습되지 않은 정보는 미출력(할루시네이션 최소화)</li>
            </ol>
            </p>
            <div style="font-size:16px; font-weight:bold; margin-top:20px;">
            검색 Tips
            </div>
            <p style="font-size:14px;">
            레시피, 조리법 등은 제공하지 않지만, 향후 전문 데이터 추가 학습 가능<br>
            AI 분석으로 결과 도출까지 다소 시간이 걸릴 수 있음<b>AND</b>.
            </p>
            """, unsafe_allow_html=True)
    st.markdown(horizontal_bar, True)
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None
        local_file_paths = ['영양DB.pdf','음식재료.pdf'] #챗봇 사전 학습 데이터
        openai_api_key = st.secrets["OPENAI_API_KEY"] # 개인 API 번호

        files_text = menu4.get_text(local_file_paths)
        text_chunks = menu4.get_text_chunks(files_text)
        vetorestore = menu4.get_vectorstore(text_chunks)

        st.session_state.conversation = menu4.get_conversation_chain(vetorestore,openai_api_key)

        st.session_state.processComplete = True

    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{"role": "assistant",
                                      "content": "안녕하세요!  AI 영양사에요. 궁금한것을 물어봐 주세요!"}]

    for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    
    # history = StreamlitChatMessageHistory(key="chat_messages")

    # Chat logic
    if query := st.chat_input("질문(재료 및 영양소)을 입력해주세요."):
          st.session_state.messages.append({"role": "user", "content": query})

          with st.chat_message("user"):
                st.markdown(query)

          with st.chat_message("assistant"):
                chain = st.session_state.conversation

                with st.spinner("잠시만 기다려주세요..."):
                    result = chain({"question": query})
                    # with get_openai_callback() as cb:
                    #     st.session_state.chat_history = result['chat_history']
                    response = result['answer']
                    #빅source_documents = result['source_documents']

                    st.markdown(response)
                    # with st.expander("출처확인"):
                    #     st.markdown(source_documents[0].metadata['source'], help = source_documents[0].page_content)

          # Add assistant message to chat history
          st.session_state.messages.append({"role": "assistant", "content": response})

elif selected_menu == "급식포털":
    import menu5
    import hydralit_components as hc

      
    # NavBar
    HOME = '군급식 홍보 이미지 생성'
    APPLICATION = '설문조사 QR 자동생성'


    tabs = [
        HOME,
        APPLICATION,
     ]

    option_data = [
        {'icon': "✳️", 'label': HOME},
        {'icon': "🏠", 'label': APPLICATION},
    ]

    over_theme = {'txc_inactive': 'black', 'menu_background': '#D6E5FA', 'txc_active': 'white', 'option_active': '#749BC2'}
    font_fmt = {'font-class': 'h3', 'font-size': '50%'}

    chosen_tab = hc.option_bar(
        option_definition=option_data,
        title='',
        key='PrimaryOptionx',
        override_theme=over_theme,
        horizontal_orientation=True)
    
    if chosen_tab == HOME: # 이미지 만들기 가져오기
        st.markdown(horizontal_bar, True)
        import menu5 #페이지 가져오기
        # 메인 화면 레이아웃
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>🌄 군급식 홍보 AI 이미지 만들기</h1>", unsafe_allow_html=True)
            prompt = st.text_area("만들고 싶은 이미지에 대한 설명Prompt)을 자세히 작성해주세요")
            size = "512x512"
            # size = st.selectbox("이미지 크기 선택:", options=["256x256", "512x512", "1024x1024", "2048x2048"])
            text_to_add = st.text_input("이미지 위에 넣고 싶은 표어(문구)를 작성해주세요(선택사항)")
            font_size = st.slider("표어(문구) 크기 설정", min_value=20, max_value=100, value=60)
            submit_button = st.button("이미지 생성")

        if submit_button:
            with st.spinner('🔍 입력 조건 반영 AI이미지 생성 중...'):
                with col2:
                    st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>🆗 군급식 홍보 이미지</h1>", unsafe_allow_html=True)
                    # 이미지 생성 및 URL 출력
                    image_url = menu5.create_prevention_image(prompt, size)
                    # 이미지 다운로드 및 메모리에 저장
                    image_byte_io = menu5.download_and_save_image(image_url, text_to_add, font_size)
                    # 원본 이미지 표시
                    st.image(image_url, caption="원본 이미지!")
                    # 텍스트가 추가된 이미지 표시
                    st.image(image_byte_io, caption="문구가 들어간 이미지")
                    # # 이미지 다운로드 링크 제공
                    # st.download_button(label="이미지 다운로드",
                    #                 data=image_byte_io.getvalue(),
                    #                 file_name="final_image.jpg",
                    #                 mime="image/jpeg")



        #home_page()

    elif chosen_tab == APPLICATION: # QR코드 만들기 가져오기
        st.markdown(horizontal_bar, True)
        import menu5 #페이지 가져오기
        import io
        # 메인 화면 레이아웃
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>🏁 급식 설문조사 QR생성</h1>", unsafe_allow_html=True)
            survey_url = st.text_input("설문지 URL을 입력하세요.", menu5.survey_url.strip())

            if st.button("QR 코드 생성") and survey_url.strip():
                qr_img = menu5.create_qr_code(survey_url)

        # QR 코드를 col2에 표시
        with col2:
            if survey_url.strip() and qr_img:
                st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>🆗 QR생성 완료</h1>", unsafe_allow_html=True)
                # 이미지를 바이트로 변환
                
                img_byte_arr = io.BytesIO()
                qr_img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                st.image(img_byte_arr, caption="QR 코드")

                # QR 코드 다운로드 링크 제공
                qr_filename = "survey_qr_code.png"
                st.markdown(menu5.get_image_download_link(qr_img, qr_filename, "QR 코드 다운로드 클릭"), unsafe_allow_html=True)
 


   
 
    
# elif selected_menu == "Settings":
#     st.markdown(horizontal_bar, True)
#     st.markdown(horizontal_bar, True)
    