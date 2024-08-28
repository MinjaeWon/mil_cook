import streamlit as st
import tempfile
from PIL import Image
from streamlit_option_menu import option_menu

import hydralit_components as hc

st.set_page_config(page_title = "AI 심리상담 서비스", page_icon="💬", layout = "wide", initial_sidebar_state = "expanded")
horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 2px; border: none; background-color: #25383C;'><br>"    # thin divider line

# 1. as sidebar menu
with st.sidebar:
    st.sidebar.image("img_2.png" , use_column_width=True)
    selected_menu = option_menu("Main Menu", ["Home", 'AI 미술심리 진단검사', '상담센터 검색'], 
    #selected_menu = option_menu("Main Menu", ["Home", '상담심리 AI챗봇', 'AI 미술심리 진단검사', '상담센터 검색'], 
        icons=['house', 'postcard-heart','tropical-storm','window','symmetry-horizontal'], menu_icon="cast", default_index=0)
    st.markdown(horizontal_bar, True)

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
    <li style="font-size:19px;"><strong>[메뉴1 : AI기반 미술심리 진단 검사]</strong> 
        <ul>
            <li style="font-size:19px">AI기반 미술심리 진단 데이터(AI허브) 활용 실시간 심리상태 분석 </li>
            <li style="font-size:19px">사용자가 그린그림을 입력하여 HTP기반 미술그림 심리분석</li>
        </ul>
    </li>
        <li style="font-size:19px;"><strong>[메뉴2 : 상담센터 검색]</strong> 
        <ul>
            <li style="font-size:19px"> 고용부 및 산하기관 공공데이터 활용 상담센터 연계 구현</li>
            <li style="font-size:19px">상담센터 정보 및 위치를 구글 MAP에 표기하여 편의성 제공</li>
            <li style="font-size:19px">선택한 상담센터 네이버 블로그 후기 실시간 검색 및 출력</li>
        </ul>
    </li>
    </ol></span>"""

    sc1, sc2 = st.columns(2)
    #random.seed()
    #GameHelpImg = vpth + random.choice(["MainImg1.jpg", "MainImg2.jpg", "MainImg3.jpg", "MainImg4.jpg"]) #랜던으로 사진쓰기.
    GameHelpImg = Image.open("simri_ai_2.png").resize((450, 450))
    sc2.image(GameHelpImg, use_column_width='auto')
    
    sc1.subheader('[공모전 출품] | AI기반 심리상담 서비스')
    sc1.markdown(horizontal_bar, True)
    sc1.markdown(hlp_dtl, unsafe_allow_html=True)
    st.markdown(horizontal_bar, True)

    author_dtl = "<strong>✔ [제3회 고용노동부 공공데이터 활용 공모전] 😍 '제품 및 서비스 개발' 부문 지원작</strong>"
    st.markdown(author_dtl, unsafe_allow_html=True)


# Main content based on selected menu
if selected_menu == "Home":
    InitialPage()
    
elif selected_menu == "상담심리 AI챗봇":
    #st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>반가워요! 여기는 당신을 위한 안전한 공간입니다.</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>😜 반가워요! 여기는 당신을 위한 안전한 공간이니, 자유롭게 얘기해요.</h1>", unsafe_allow_html=True)

    st.markdown(horizontal_bar, True)
    import menu1_chat_aibot #페이지 가져오기

    #대화 기록을 저장하기 위한 초기 설정
    if 'history' not in st.session_state:
        st.session_state.history = []

    # 대화 엔진 초기화 (가상의 함수, 실제 구현 필요)
    def initialize_conversation():
        return None  # 여기에 실제 대화 엔진 초기화 로직 구현

    if 'conversation' not in st.session_state:
        st.session_state.conversation = initialize_conversation()

    # 사용자 입력 받기
    query = st.chat_input("요즘 어떠세요. 하고 싶은말을 자유롭게 해보세요.")
    if query:
        # 사용자 입력을 대화 기록에 저장
        st.session_state.history.append({"role": "user", "content": query})

        # 스피너를 사용하여 로딩 중 표시
        #with st.spinner("잠시만 기다려주세요..."):
        # 대화 엔진 또는 챗봇 모델로부터 응답 받기
        answer = menu1_chat_aibot.generate_response(query)  # 가상의 응답 생성 함수
        

        # 응답 로직 분기
        print("--1--",answer )
        if answer['distance'] > 0.08:
            # 유사도가 낮으면 GPT 모델을 사용하여 응답 생성
            response = menu1_chat_aibot.generate_gpt_response(query)
        else:
            # 유사도가 높은 경우, 기존 챗봇 응답 사용
            response = f"{answer['챗봇']}."

            # 챗봇 응답을 대화 기록에 저장
        st.session_state.history.append({"role": "assistant", "content": response})

    # 대화 내용 순차적으로 출력
    for message in st.session_state.history:
        with st.chat_message(message['role']):
            st.markdown(message['content'])


    with st.sidebar:
        if len(st.session_state.history) >= 10:
            if st.sidebar.button("심리상태 분석"):
                texts = [msg['content'] for msg in st.session_state.history if msg['role'] == 'user']
                # bullying_results = [menu1_chat_aibot.check_bullying(text) for text in texts]
                # is_bullying_present = any(result[0] for result in bullying_results)  # 유사도 결과 검토
                # average_indices = [result[1] for result in bullying_results]
                # average_index = sum(average_indices) / len(average_indices) if average_indices else 0

                # # 평균 유사도에 따른 5단계 결과 메시지 출력
                # average_percentage = round(average_index * 100)
                # st.write(f"⏳ AI분석 학교폭력 피해 가능성: {average_percentage}%")
                # if 0 <= average_percentage <= 25:
                #     st.success("학교 폭력 피해 가능성 비교적 낮음")
                # elif 26 <= average_percentage <= 50:
                #     st.info("학교 폭력 피해 가능성이 보통이상, 추가 상담 필요")
                # elif 51 <= average_percentage <= 100:
                #     st.error("학교 폭력 피해 가능성이 비교적 높은편, 보호자의 관리가 필요")

                print("------------------------")
                # generate_detailed_feedback 함수 호출
                detailed_feedback = menu1_chat_aibot.generate_detailed_feedback(texts, menu1_chat_aibot.bullying_keywords)
                print("상세 피드백:")
                print(detailed_feedback)

                  # GPT 답변을 사용하여 폭력 피해 탐지 수행
                bullying_results = [menu1_chat_aibot.check_bullying(detailed_feedback)]
                average_index = bullying_results[0][1] if bullying_results else 0

                # 평균 유사도에 따른 5단계 결과 메시지 출력
                average_percentage = round(average_index * 1000)
                st.write(f"⏳ AI분석 우울도 분석 결과 : {average_percentage}%")
                if 0 <= average_percentage <= 9:
                    st.success("우울증 정도 비교적 낮음")
                elif 10 <= average_percentage <= 50:
                    st.info("우울증 정도 보통이상, 추가 상담 필요")
                elif 51 <= average_percentage <= 100:
                    st.error("우울증 정도 비교적 높은편, 전문 상담 연계 필요")

                st.text_area(
                "분석 세부내용",
                detailed_feedback,
                height=350,
                # help="At least two keyphrases for the classifier to work, one per line, "
                # + str(MAX_KEY_PHRASES)
                # + " keyphrases max in 'unlocked mode'. You can tweak 'MAX_KEY_PHRASES' in the code to change this",
                key="1"
            )
        else:
            st.sidebar.write("좀 더 많은 대화를 나누면, 심리상태 분석이 가능해져요.")


elif selected_menu == "AI 미술심리 진단검사":
    import menu2_ai_picture
    
    # NavBar
    HOME = '진단검사 설명'
    APPLICATION = '집 그림 분석'
    RESOURCE = '나무 그림 분석'
    CONTACT = '사람 그림 분석'

    tabs = [
        HOME,
        APPLICATION,
        RESOURCE,
        CONTACT,
    ]

    option_data = [
        {'icon': "✳️", 'label': HOME},
        {'icon': "🏠", 'label': APPLICATION},
        {'icon': "🌳", 'label': RESOURCE},
        {'icon': "👩‍🌾", 'label': CONTACT},
    ]

    over_theme = {'txc_inactive': 'black', 'menu_background': '#D6E5FA', 'txc_active': 'white', 'option_active': '#749BC2'}
    font_fmt = {'font-class': 'h3', 'font-size': '50%'}

    chosen_tab = hc.option_bar(
        option_definition=option_data,
        title='',
        key='PrimaryOptionx',
        override_theme=over_theme,
        horizontal_orientation=True)
    
    if chosen_tab == HOME:
        st.markdown(horizontal_bar, True)

            # HTP 심리검사 기법 설명
        st.markdown("""
        # HTP 심리검사 기법

        **HTP(집-나무-사람) 검사**는 심리 평가 도구로, 개인의 내면 세계와 정서 상태를 이해하는 데 사용됩니다. 이 검사는 **Projective Test(투사 검사)**의 일종으로, 피검자가 그림을 그리는 과정에서 무의식적으로 자신의 감정과 성격을 드러낸다는 가정에 기초합니다.

        ## 검사 방법

        HTP 검사는 피검자가 세 가지 주제에 대해 그림을 그리도록 요청합니다:
        1. **집(House)**: 집 그림을 통해 가정 생활과 가족 관계를 탐색합니다.
        2. **나무(Tree)**: 나무 그림을 통해 성장 과정과 자아 개념을 탐색합니다.
        3. **사람(Person)**: 사람 그림을 통해 대인 관계와 사회적 상호작용을 탐색합니다.

        피검자는 각 주제에 대해 별도의 종이에 그림을 그리고, 이후에는 그림에 대해 자유롭게 이야기하는 시간을 갖습니다.

        ## 해석

        각 그림의 요소들은 다음과 같은 측면에서 해석됩니다:
        - **집**: 가정 환경, 안정감, 소속감 등을 나타냅니다.
        - **나무**: 성장, 자아 강도, 인내 등을 상징합니다.
        - **사람**: 자신 또는 타인과의 관계, 사회적 역할 등을 반영합니다.

        그림의 크기, 위치, 세부 사항, 선의 강도 등 다양한 요소들이 종합적으로 고려됩니다. 해석은 훈련된 심리 전문가가 수행하며, 피검자의 전체적인 심리 상태와 정서적 이슈를 파악하는 데 도움이 됩니다.
        """)



        #home_page()

    elif chosen_tab == APPLICATION: #집그림
        st.markdown(horizontal_bar, True)
        #st.sidebar.markdown("파일업로드")
        st.sidebar.markdown("<p style='font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; color: #1f77b4;'>🔍 집 파일 업로드</p>", unsafe_allow_html=True)

        # 이미지 파일 업로드 기능을 사이드바에 추가합니다.
        uploaded_file = st.sidebar.file_uploader("✔ 이미지 파일 등록 후, 분석시작 버튼 클릭", type=['jpg', 'png'])
        

        # 이미지 파일이 업로드되었는지 확인합니다.
        if uploaded_file is not None:
            st.sidebar.write("⏬ 파일 업로드, 분석시작 버튼 클릭⏬")
        else:
            st.sidebar.write("<span style='font-family: Arial, sans-serif; font-size: 14px; color: #888;'>🧑🏻‍💻 파일이 업로드되지 않았습니다.</span>", unsafe_allow_html=True)

        # 분석 버튼을 생성합니다.
        # if st.sidebar.button("🏠 집 그림 분석 시작"):
        #     # 업로드된 이미지 파일을 열어서 처리합니다.
        #     if uploaded_file is not None:
        #         img = Image.open(uploaded_file)
        #         # process_house 함수를 호출하여 이미지를 분석합니다.
        #         with st.spinner('분석 중... 잠시만 기다려 주세요'):
        #             menu2_ai_picture.process_house(img)
        #     else:
        #         st.sidebar.write("이미지 파일을 업로드해해주세요.")
        if st.sidebar.button("🏠 집 그림 분석 시작"):
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    #img.save(temp_file, format="JPEG")
                    img.save(temp_file)
                    temp_file_path = temp_file.name
                with st.spinner('분석 중... 잠시만 기다려 주세요'):
                    menu2_ai_picture.process_house(temp_file_path)
            else:
                st.sidebar.write("이미지 파일을 업로드해 주세요.")


    elif chosen_tab == RESOURCE: #나무그림
        st.markdown(horizontal_bar, True)
        #st.sidebar.markdown("파일업로드")
        st.sidebar.markdown("<p style='font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; color: #1f77b4;'>🔍 나무 파일 업로드</p>", unsafe_allow_html=True)

        # 이미지 파일 업로드 기능을 사이드바에 추가합니다.
        uploaded_file = st.sidebar.file_uploader("✔ 이미지 파일 등록 후, 분석시작 버튼 클릭", type=['jpg', 'png'])
        

        # 이미지 파일이 업로드되었는지 확인합니다.
        if uploaded_file is not None:
            st.sidebar.write("⏬ 파일 업로드, 분석시작 버튼 클릭⏬")
        else:
            st.sidebar.write("<span style='font-family: Arial, sans-serif; font-size: 14px; color: #888;'>🧑🏻‍💻 파일이 업로드되지 않았습니다.</span>", unsafe_allow_html=True)

        # 분석 버튼을 생성합니다.
        if st.sidebar.button("🌳 나무 그림 분석 시작"):
            # 업로드된 이미지 파일을 열어서 처리합니다.
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                # process_house 함수를 호출하여 이미지를 분석합니다.
                with st.spinner('분석 중... 잠시만 기다려 주세요'):
                    menu2_ai_picture.process_tree(img)
            else:
                st.sidebar.write("이미지 파일을 업로드해주세요.")

    elif chosen_tab == CONTACT: #사람그림
        st.markdown(horizontal_bar, True)
        #st.sidebar.markdown("파일업로드")
        st.sidebar.markdown("<p style='font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; color: #1f77b4;'>🔍 사람 파일 업로드</p>", unsafe_allow_html=True)

        # 이미지 파일 업로드 기능을 사이드바에 추가합니다.
        uploaded_file = st.sidebar.file_uploader("✔ 이미지 파일 등록 후, 분석시작 버튼 클릭", type=['jpg', 'png'])
        

        # 이미지 파일이 업로드되었는지 확인합니다.
        if uploaded_file is not None:
            st.sidebar.write("⏬ 파일 업로드, 분석시작 버튼 클릭⏬")
        else:
            st.sidebar.write("<span style='font-family: Arial, sans-serif; font-size: 14px; color: #888;'>🧑🏻‍💻 파일이 업로드되지 않았습니다.</span>", unsafe_allow_html=True)

        # 분석 버튼을 생성합니다.
        if st.sidebar.button("👩‍🌾 사람 그림 분석 시작"):
            # 업로드된 이미지 파일을 열어서 처리합니다.
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                # process_house 함수를 호출하여 이미지를 분석합니다.
                with st.spinner('분석 중... 잠시만 기다려 주세요'):
                    menu2_ai_picture.process_person(img)
            else:
                st.sidebar.write("이미지 파일을 업로드해주세요.")




elif selected_menu == "상담센터 검색":

    st.markdown("<h1 style='color: #7F462C; font-size: 30px;'>✨ 사용자 수요 기반 상담센터 검색</h1>", unsafe_allow_html=True)
    st.markdown(horizontal_bar, True)
    import menu3_search_center
    import time

    file_path = 'total_복사.csv'
    df = menu3_search_center.load_data(file_path)
    df['지역'] = df['소재지'].apply(lambda x: x.split()[0])
    
    col1, col2 = st.columns([1, 1])  # 두 컬럼의 너비를 동일하게 설정
    
    
    with col1:
        regions = df['지역'].unique()
        selected_region = st.selectbox('지역을 선택하세요', options=["선택 안 함"] + list(regions), index=0)
    
        if selected_region != "선택 안 함":
            filtered_df = df[df['지역'] == selected_region]
            companies = filtered_df['회사명'].unique()
            selected_company = st.selectbox('회사를 선택하세요', options=["선택 안 함"] + list(companies), index=0)
        
            if selected_company != "선택 안 함":
                company_info = filtered_df[filtered_df['회사명'] == selected_company].iloc[0]
        
                with col2:
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin: 10px 0; background-color: #f9f9f9;">
                        <h3 style="color: #333;">{company_info['회사명']}</h3>
                        <p><b>소재지:</b> {company_info['소재지']}</p>
                        <p><b>전화번호:</b> {company_info['전화번호']}</p>
                        <p><b>운영 시간:</b> 평일 09:00 - 18:00, 주말 및 공휴일 휴무</p>
                    </div>
                    """, unsafe_allow_html=True)
                    menu3_search_center.display_map(company_info)

        if selected_region != "선택 안 함" and selected_company != "선택 안 함":
            with st.spinner('실시간 블로그 후기 검색 중...'):
                blog_results = menu3_search_center.crawl_blog(selected_company)
            
            st.markdown("### ✅ **실시간 블로그 검색 결과**")
            for result in blog_results:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin: 10px 0; max-width: 600px;">
                    <h4>{result['title']}</h4>
                    <p><b>날짜:</b> {result['date']}</p>
                    <p><b>주소:</b> <a href="{result['href']}" target="_blank">{result['href']}</a></p>
                    <p><b>본문:</b> {result['text']}... <a href="{result['href']}" target="_blank">더 보기</a></p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)  # 한 개씩 출력되도록 시간 지연 추가
    




# elif selected_menu == "학교폭력 예방지원":
#     import menu2_ai_picture

        
#     # NavBar
#     HOME = '학교폭력 예방 홍보'
#     APPLICATION = '설문조사 QR만들기'


#     tabs = [
#         HOME,
#         APPLICATION,
#      ]

#     option_data = [
#         {'icon': "✳️", 'label': HOME},
#         {'icon': "🏠", 'label': APPLICATION},
#     ]

#     over_theme = {'txc_inactive': 'black', 'menu_background': '#D6E5FA', 'txc_active': 'white', 'option_active': '#749BC2'}
#     font_fmt = {'font-class': 'h3', 'font-size': '50%'}

#     chosen_tab = hc.option_bar(
#         option_definition=option_data,
#         title='',
#         key='PrimaryOptionx',
#         override_theme=over_theme,
#         horizontal_orientation=True)
    
#     if chosen_tab == HOME: # 이미지 만들기 가져오기
#         st.markdown(horizontal_bar, True)
#         import menu4_center_call #페이지 가져오기
#         # 메인 화면 레이아웃
#         col1, col2 = st.columns(2)

#         with col1:
#             st.title("학교폭력 예방/대책 이미지 만들기!")
#             prompt = st.text_area("만들고 싶은 이미지 프롬프트(Prompt)를 작성해주세요")
#             size = st.selectbox("이미지 크기 선택:", options=["256x256", "512x512", "1024x1024", "2048x2048"])
#             text_to_add = st.text_input("이미지에 작성하고 싶은 표어(문구)를 작성해주세요")
#             font_size = st.slider("표어(문구) 크기 설정", min_value=20, max_value=100, value=60)
#             submit_button = st.button("이미지 생성")

#         if submit_button:
#             with col2:
#                 st.title("학교폭력 예방/대책 이미지 생성!")
#                 # 이미지 생성 및 URL 출력
#                 image_url = menu4_center_call.create_prevention_image(prompt, size)
#                 # 이미지 다운로드 및 메모리에 저장
#                 image_byte_io = menu4_center_call.download_and_save_image(image_url, text_to_add, font_size)
#                 # 원본 이미지 표시
#                 st.image(image_url, caption="Original Image")
#                 # 텍스트가 추가된 이미지 표시
#                 st.image(image_byte_io, caption="Text Overlay Image")
#                 # # 이미지 다운로드 링크 제공
#                 # st.download_button(label="이미지 다운로드",
#                 #                 data=image_byte_io.getvalue(),
#                 #                 file_name="final_image.jpg",
#                 #                 mime="image/jpeg")


#     elif chosen_tab == APPLICATION: # QR코드 만들기 가져오기
#         st.markdown(horizontal_bar, True)
#         import menu4_center_call #페이지 가져오기
#         import io
#         # 메인 화면 레이아웃
#         col1, col2 = st.columns(2)

#         with col1:
#             st.title("학교폭력 예방 설문지 만들기")
#             survey_url = st.text_input("설문지 URL을 입력하세요.", menu4_center_call.survey_url.strip())

#             if st.button("QR 코드 생성") and survey_url.strip():
#                 qr_img = menu4_center_call.create_qr_code(survey_url)

#         # QR 코드를 col2에 표시
#         with col2:
#             if survey_url.strip() and qr_img:
#                 # 이미지를 바이트로 변환
#                 img_byte_arr = io.BytesIO()
#                 qr_img.save(img_byte_arr, format='PNG')
#                 img_byte_arr = img_byte_arr.getvalue()
#                 st.image(img_byte_arr, caption="QR 코드")

#                 # QR 코드 다운로드 링크 제공
#                 qr_filename = "survey_qr_code.png"
#                 st.markdown(menu4_center_call.get_image_download_link(qr_img, qr_filename, "QR 코드 다운로드 클릭"), unsafe_allow_html=True)
 
    
# elif selected_menu == "Settings":
#     st.markdown(horizontal_bar, True)
#     st.markdown(horizontal_bar, True)
    