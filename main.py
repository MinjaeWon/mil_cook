import requests
import streamlit as st
from streamlit_option_menu import option_menu

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote # 신문가져오기
import openai
import re
import streamlit_scrollable_textbox as stx
import pandas as pd

import matplotlib.pyplot as plt
import time
import plotly.express as px

import altair as alt
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


# OpenAPI 엔드포인트 및 인증 키 설정
BASE_API_URL = 'https://open.assembly.go.kr/portal/openapi/TVBPMBILL11'
API_KEY = 'a20dfc5cba0d4f70b0f8b0c67afbac53'

st.set_page_config(page_title="의안 분석 시스템", page_icon=":medal:", layout="wide")

# 함수: API 요청을 보내고 응답 데이터를 가져오는 부분
def fetch_api_data(bill_name):
    params = {
        'KEY': API_KEY,
        'pIndex': 1,
        'pSize': 5,
        'BILL_NAME': bill_name
    }
    try:
        response = requests.get(BASE_API_URL, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"오류 발생: {e}")
    return None



# 함수: API 응답 데이터를 파싱하여 필요한 정보를 추출하는 부분
def parse_api_response(xml_data):
    # print(xml_data) 값 출력됨
    #if xml_data is None:
    #    return []

    soup = BeautifulSoup(xml_data, "xml")
    #if soup is None:
     #   return []

    bill_list = soup.find_all('BILL_NAME')

    #검색할 의안 리스트 뿌려주기
    st.subheader(':two: 유사의안 검색 결과', divider='gray')


    # 리스트 컴프리헨션을 사용하여 모든 요소를 문자열로 변환
    string_list = [str(item) for item in bill_list]

    # 혹은 join() 메서드를 사용하여 문자열로 결합
    result_string = ", ".join(string_list)


    # 태그를 제거하여 문자열만 출력
    for index, item in enumerate(string_list, start=1):
        text_only = re.sub(r'<.*?>', '', item)
        #st.write(f'유사 의안({index}) : {text_only}')
        st.write(':point_right: 유사 의안({}) : {}'.format(index, text_only))
        #t.markdown(index, '유사 의안:', text_only)

    bill_list2 = soup.find_all('LINK_URL')

    print('---- 선택 의안 전달 -----')

    if content_Parsing(bill_list2):
      print('ss', content_Parsing(bill_list2), "+++++++")  # 제안이유 및 주요내용 가져오기 부분

      #프로세스 bar
      progress_text = "유사의안 검색 중..."
      my_b2ar = st.progress(0, text=progress_text)
      for percent_complete in range(100):
          time.sleep(0.02)
          my_b2ar.progress(percent_complete + 1, text=progress_text)
      time.sleep(1)
      my_b2ar.empty()

    else:
      print(' 다시 입력')
      st.write('찾을 수 없습니다. 다시 입력해주세요.')

    st.subheader(':three: 의안 제안이유 및 주요내용', divider='gray')
    stx.scrollableTextbox(content_Parsing(bill_list2),height = 400)

    # chatgpt 연결
    keyword = get_answer(content_Parsing(bill_list2)) # 핵심 키워드 가져오기

    st.subheader(':four: 생성형AI 활용 핵심 키워드 추출', divider='gray')

    st.metric(label='제안이유 및 주요내용 분석', help='chatGPT 모델 활용' , value=keyword, delta='연관성 매우 높음')


    making_char = search_sinmoon_donga(keyword, content_Parsing(bill_list2)) # 핵심키워드, 의안 제안이유 및 주요내용


    st.subheader(':six: 감성 분석 기반 여론 추이', divider='gray')

    #프로세스 bar
    progress_text = "전체 데이터 분석 중... 잠시만 기다려 주세요."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
      time.sleep(0.01)
      my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()

    #6번 여론 분석 그래프 그리기
    make_chart(making_char)

    return None



# 도형 그리기
def make_chart(value_survey):


  #프로세스 bar
  progress_text = "추출 모든 기사에 대한, 감성 분석 진행중..."
  my_bar = st.progress(0, text=progress_text)
  for percent_complete in range(100):
          time.sleep(0.02)
          my_bar.progress(percent_complete + 1, text=progress_text)
  time.sleep(1)
  my_bar.empty()


  # 데이터를 Pandas DataFrame으로 변환
  df = pd.DataFrame(value_survey, columns=['label', 'score'])

  # Altair를 사용한 그래프 생성
  bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('score:Q', title='Score'),
    y=alt.Y('label:N', title='Label'),
    color=alt.Color('label:N', legend=None)
  )

  # Streamlit에서 그래프 출력
  st.altair_chart(bar, use_container_width=True)


#--------------------


# 핵심키워드로, 뉴스 검색 동향 찾기(두개 신문모두)
def search_sinmoon_donga(search_keyword, law_content):

  st.subheader(':five: 여론분석결과', divider='gray')

  #search_keyword = '도로교통법' # 여기가 값 받는 것 text
  user_value = quote(search_keyword)
  url = f"https://www.donga.com/news/search?query={user_value}"

  # html 정보가 담겨있는 변수를 bs4 라이브러리에 있는 BeautifulSoup을 이용해
  html = urlopen(url).read()
  soup = BeautifulSoup(html, 'html.parser')

  # 'class="tit"'로 검색한 첫 번째 'a' 태그를 찾고 'href' 속성 값을 가져와서 출력
  first_a_tags = soup.find_all(class_='tit')


  # 모든 <span> 태그에서 텍스트 추출하여 리스트에 저장
  text_list = [span_tag.a.text for span_tag in soup.find_all('span', class_='tit') if span_tag.a]

  # 리스트의 요소들을 한 줄로 합치고 출력
  output = "\n".join(text_list)
  print(output)
  st.write("주요기사 제목")
  stx.scrollableTextbox(output, height = 200, border=True, fontFamily='Helvetica')

  result_list = []

  #프로세스 bar
  progress_text = "추출 모든 기사에 대한, 감성 분석 진행중..."
  my_bar = st.progress(0, text=progress_text)




  #검색된 10개 세부 뉴스 가져오기
  for percent_complete in range(5): # 동일 설정
    for i in range(2, 5): # 검색 기사 갯수 설정
      a_tags = first_a_tags[i]

      for a_tag in a_tags:
        detail_news123 = a_tag.get('href')
        print('--- 해당링크로 연결중 ---', [i], detail_news123)

        if detail_news123:
          #여기에 뉴스 세부 주소 들어가 전체 크롤링
          #print(detail_news)
          html2 = urlopen(detail_news123).read()
          soup = BeautifulSoup(html2, 'html.parser')


          #time.sleep(0.02)
          my_bar.progress(percent_complete + 1, text=progress_text)



          # <br> 태그에 포함된 값을 출력
          br_tags = soup.find_all('br')
          news_contets_all = ""

          for br_tag in br_tags:
            if br_tag.next_sibling and br_tag.next_sibling.string:
              news_contets_all += br_tag.next_sibling.string.strip() + ' '
          print("--- 추출완료 ---",news_contets_all)

          # new  위의 기사 내용 넣고 결과 가져오기.(의안명, 제안내용)
          value = get_answer_result(news_contets_all, law_content)
          result_list.append(value)


  print('누적',result_list )
  time.sleep(1)
  my_bar.empty()
  return result_list





  # #검색된 10개 세부 뉴스 가져오기
  # for i in range(2, 5): # 구간 수정!! 필요
  #   a_tags = first_a_tags[i]

  #   for a_tag in a_tags:
  #     detail_news123 = a_tag.get('href')
  #     print('--- 해당링크로 연결중 ---', [i], detail_news123)

  #     if detail_news123:

  #       #여기에 뉴스 세부 주소 들어가 전체 크롤링
  #       #print(detail_news)
  #       html2 = urlopen(detail_news123).read()
  #       soup = BeautifulSoup(html2, 'html.parser')

  #       # <br> 태그에 포함된 값을 출력
  #       br_tags = soup.find_all('br')
  #       news_contets_all = ""

  #       for br_tag in br_tags:
  #         if br_tag.next_sibling and br_tag.next_sibling.string:
  #           news_contets_all += br_tag.next_sibling.string.strip() + ' '
  #       print("--- 추출완료 ---",news_contets_all)

  #       # new  위의 기사 내용 넣고 결과 가져오기.(의안명, 제안내용)
  #       value = get_answer_result(news_contets_all, law_content)
  #       result_list.append(value)

  # print('누적',result_list )
  # return result_list



#OPENAI API 연결, 최종 결과 나오기
def get_answer_result(query, law_content23):
  api_key = "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"
  openai.api_key = api_key

  #초기화 설정
  gpt_answer_res= None
  gpt_answer_res68 = None
  gpt_answer_res22 = None

  # 모델 - GPT 3.5 Turbo 선택
  model = "gpt-3.5-turbo"


  # 1. 기사 내용 요약
  mine = "앞의 뉴스 기사를 읽고 요약해줘. 쟁점사항, 핵심 키워드는 반드시 포함시켜줘."
  messages = [{ "role": "system", "content": "You are a helpful assistant."},
          { "role": "user", "content": query  + mine }]

  # ChatGPT API 호출(결과)
  response = openai.chat.completions.create(model=model, messages=messages) # 버전 업그레이드에 따른 신규코드
  gpt_answer_res = response.choices[0].message.content # 기사내용 요약
  print('기사 내용 요약', gpt_answer_res)

  # 2, 기사에 대한 감성 분석
  tokenizer = AutoTokenizer.from_pretrained('snunlp/KR-FinBert-SC')
  model = AutoModelForSequenceClassification.from_pretrained('snunlp/KR-FinBert-SC')
  senti_classifier = pipeline(task='text-classification', model=model, tokenizer=tokenizer)

  result = senti_classifier(gpt_answer_res)


  print('----------------- 감석 분석 결과--',result )
  return result




# #OPENAI API 연결, 최종 결과 나오기
# def get_answer_result(query, law_content23):
#   api_key = "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"
#   openai.api_key = api_key

#   #초기화 설정
#   gpt_answer_res= None
#   gpt_answer_res68 = None
#   gpt_answer_res22 = None

#   # 모델 - GPT 3.5 Turbo 선택
#   model = "gpt-3.5-turbo"

#   #프로세스 bar
#   progress_text = query, "관련 기사 수집중..."
#   my_bar = st.progress(0, text=progress_text)
#   for percent_complete in range(100):
#       time.sleep(0.02)
#       my_bar.progress(percent_complete + 1, text=progress_text)
#   time.sleep(1)
#   my_bar.empty()

#   # 1. 기사 내용 요약
#   mine = "앞의 뉴스 기사 내용을 핵심내용만 요약해줘. 답변은 1번 2번 3번 총 3개로 해줘. 답변할때 '1번' '2번' '3번'을 붙여주세요."
#   messages = [{ "role": "system", "content": "You are a helpful assistant."},
#           { "role": "user", "content": query  + mine }]

#   # ChatGPT API 호출(결과)
#   response = openai.chat.completions.create(model=model, messages=messages) # 버전 업그레이드에 따른 신규코드
#   gpt_answer_res = response.choices[0].message.content # 1.기사내용 요약, 2.긍정 혹은 부정 결과
#   #print('기사 내용 요약', gpt_answer_res)
#   #st.write('기사 내용 요약', gpt_answer_res)

#   # 2. 긍정 혹은 부정 송출
#   messages_add = [{ "role": "system", "content": "You are a helpful assistant."},
#           { "role": "user", "content": "앞의 기사 내용이 긍정적인지 부정적인지 대답해줘. '긍정' 혹은 '부정'으로 대답해줘. 문장으로 대답하지마." }]

#   #프로세스 bar
#   progress_text = "신문기사 기반 여론 분석 중..."
#   my_bar = st.progress(0, text=progress_text)
#   for percent_complete in range(100):
#         time.sleep(0.02)
#         my_bar.progress(percent_complete + 1, text=progress_text)
#   time.sleep(1)
#   my_bar.empty()


#   # ChatGPT API 긍정 혹은 부정 결과
#   response23 = openai.chat.completions.create(model=model, messages=messages_add) # 버전 업그레이드에 따른 신규코드
#   gpt_answer_res68 = response23.choices[0].message.content
#   #print('기사 내용 요약, 여론 결과++++++++', gpt_answer_res68)
#   #st.write('분석 결과', gpt_answer_res68)

#   # 3. 개정여부 결과
#   mine2 = "앞의 뉴스기사 내용과 법안내용을 비교해, 법안 개정이 필요한지 필요한지 대답해줘. '개정필요' 혹은 '불필요'로 답변해줘.법안내용:"
#   messages_add2 = [{ "role": "system", "content": "You are a helpful assistant."},
#                     { "role": "user", "content": mine2 + law_content23  }]

#   # ChatGPT API 호출
#   response32 = openai.chat.completions.create(model=model, messages=messages_add2) # 버전 업그레이드에 따른 신규코드
#   gpt_answer_res22 = response32.choices[0].message.content
#   #print('개정 필요 여부 +++++++++++' ,gpt_answer_res22)
#   #st.write('개정 필요 여부', gpt_answer_res22)

#   last_ward = ''.join([gpt_answer_res68, gpt_answer_res22])

#   print('최종 도출 결과 ------', last_ward)


#   return last_ward





#OPENAI API 연결해서 질문-대답 가져오기
def get_answer(query):
  api_key = "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"
  openai.api_key = api_key

  # 모델 - GPT 3.5 Turbo 선택
  model = "gpt-3.5-turbo"

  # 메시지 설정하기
  messages = [{ "role": "system", "content": "You are a helpful assistant."},
          { "role": "user", "content": query + "가장 중요한 단어 오직 한개만 추천해줘. 반드시 '단어'로만 대답해줘." }
  ]

  # ChatGPT API 호출
  response = openai.chat.completions.create(model=model, messages=messages) # 버전 업그레이드에 따른 신규코드
  gpt_answer = response.choices[0].message.content
  print("핵심키워드", gpt_answer)

  return gpt_answer




# (웹크롤링) 제안이유 및 주요내용 가져오기 부분
def content_Parsing(link_datd):
  for conts in link_datd:
    read = conts.text
    real_link = urlopen(read)

    #프로세스 bar
    progress_text = "데이터 수집 및 분석 진행 중, 잠시만 기다려주세요..."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
         time.sleep(0.02)
         my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()


    soup = BeautifulSoup(real_link.read(), "html.parser")
    sum_contents = soup.select_one('div[id="summaryHiddenContentDiv"]')

    print('---- 선택 의안 제안이유 및 주요내용 가져오기 완료 ----')

    #result = []

    result =  sum_contents.text.strip()

    #for bill in bill_list:
     #   result.append(bill.text)

    return result

## ----------------------------------- 여론검색 -----

# ** 사이드바 **
with st.sidebar:
    selected_menu = option_menu("Main Menu", ["분석 서비스 소개","의정활동분석", '의안 여론검색', '챗봇'],
        icons=['house', 'gear', 'gear', 'gear'], menu_icon="cast", default_index=0)

if selected_menu == "분석 서비스 소개":
  st.header("자기 소개 제작 예정")

if selected_menu == "의정활동분석":

  #프로세스 bar
  progress_text = "세부법안 데이터 추출 중..."
  my_bar = st.progress(0, text=progress_text)
  for percent_complete in range(100):
        time.sleep(0.02)
        my_bar.progress(percent_complete + 1, text=progress_text)
  time.sleep(1)
  my_bar.empty()


  ## 국회의원 의안 벌률 리스트
  raw_data = pd.read_excel('/content/member_law_21.xlsx')
  print("1번꺼---", raw_data)

  # 21대 국회의원 의안 벌률 리스트
  raw_data_info = pd.read_excel('/content/member_list.xlsx')
  #print(raw_data_info)

  # 탭 생성 : 첫번째 탭의 이름은 Tab A 로, Tab B로 표시합니다.

  tab1, tab2= st.tabs(['국회의원 정보 분석' , '의안 분석'])
  col1, col2 = st.columns((2))

  #국회의원 정보 분석
  with tab1:

    # ---- SIDEBAR ----#---------------------------------------------------------------------------------
    st.sidebar.header("조건을 선택해주세요")

    # 21대 국회의원 의안 벌률 리스트
    raw_data_info = pd.read_excel('/content/member_list.xlsx')
    #print(raw_data_info)

    search_name = st.sidebar.selectbox(
        "국회의원 선택",
        index=None,
        options=raw_data_info["의원명"].unique()
        #default=raw_data["법률안명"].unique()
    )

    search_button = st.sidebar.button('검색하기', key="button1")

    # 선택된 연도의 대표발의건수와 공동발의건수 가져오기
    if search_name in raw_data_info['의원명'].tolist():
      #프로세스 bar
      progress_text = "국회의원 명단 검색 중..."
      my_bar = st.progress(0, text=progress_text)
      for percent_complete in range(100):
        time.sleep(0.02)
        my_bar.progress(percent_complete + 1, text=progress_text)
      time.sleep(1)
      my_bar.empty()

      with st.sidebar:
        part = raw_data_info[raw_data_info['의원명'] == search_name]['정당'].values[0]
        committee_aff = raw_data_info[raw_data_info['의원명'] == search_name]['소속위원회'].values[0]
        constituency = raw_data_info[raw_data_info['의원명'] == search_name]['지역'].values[0]
        gender = raw_data_info[raw_data_info['의원명'] == search_name]['성별'].values[0]
        re_election = raw_data_info[raw_data_info['의원명'] == search_name]['지역'].values[0]
        num_of_terms = raw_data_info[raw_data_info['의원명'] == search_name]['당선횟수'].values[0]
        elec_method = raw_data_info[raw_data_info['의원명'] == search_name]['당선방법'].values[0]

      # 의원 세부 정보 확인
      with st.sidebar:
           cho = option_menu("의원 세부 정보", [f':정당: {part}', f'소속위원회: {committee_aff}', f'지역: {constituency}',
                           f'성별: {gender}', f'지역: {re_election}', f'당선횟수: {num_of_terms}', f'당선방법: {elec_method}'],
                         icons=['1-square', '2-square', '3-square','4-square','5-square','6-square','7-square'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
                         "container": {"padding": "4!important", "background-color": "#fafafa"},
                         "icon": {"color": "black", "font-size": "20px"},
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
                        "nav-link-selected": {"white-color": "#08c7b4"},}
           )

  #tab1의 col1 안에 표시 내용
  with col1:

    st.subheader(":smiley: :blue[유형별] 법안발의 분석 결과", divider='gray')

    if search_button:

      # 입력받은 대표발의자 데이터 필터링
      filtered_representative_data = raw_data[raw_data['대표발의자'] == search_name]
      print('검색어',search_name )

      # 입력받은 공동발의자 데이터 필터링
      filtered_joint_data = raw_data[raw_data['공동발의자'].str.contains(search_name, na=False)]

      #프로세스 bar
      progress_text = "전체 데이터 분석 중... 잠시만 기다려 주세요."
      my_bar = st.progress(0, text=progress_text)
      for percent_complete in range(100):
          time.sleep(0.02)
          my_bar.progress(percent_complete + 1, text=progress_text)
      time.sleep(1)
      my_bar.empty()


      # 데이터 개수 계산
      count_representative = len(filtered_representative_data)
      count_joint = len(filtered_joint_data)

      # 데이터 프레임 생성
      count_df = pd.DataFrame({'Category': [f'대표발의건수', f'공동발의건수'], 'Count': [count_representative, count_joint]})

      # 데이터 출력
      st.info(f'국회의원 {search_name} :point_right: [총 발의 : {count_representative+count_joint} 건], [대표발의 : {count_representative} 건], [공동발의 : {count_joint} 건]')


      # 원그래프
      fig = px.pie(count_df, names='Category', values='Count',  hole=.3, color_discrete_sequence=px.colors.qualitative.Vivid) #title=' ',
      fig.update_traces(textposition='inside', textinfo='percent+label+value')
      fig.update_layout(font=dict(size=14))
      fig.update(layout_showlegend=False) # 범례표시 여부
      st.plotly_chart(fig)

      st.subheader(":smiley: :red[대표발의] 법안 세부정보", divider='gray')

      #프로세스 bar
      progress_text = "세부법안 데이터 추출 중..."
      my_bar = st.progress(0, text=progress_text)
      for percent_complete in range(100):
          time.sleep(0.02)
          my_bar.progress(percent_complete + 1, text=progress_text)
      time.sleep(1)
      my_bar.empty()

      # 모든 연도에 대한 데이터 출력
      st.dataframe(filtered_representative_data[['연도', '대표발의자', '법률안명', '본회의심의결과', '소관위처리결과', '법사위처리결과']].fillna('진행중'), use_container_width=True)


  with col2:
        st.subheader(":smiley: :blue[연도별] 법안발의 분석 결과", divider='gray')
        if search_button:

          #프로세스 bar
          progress_text = "연도별 법안발의 데이터 분석 중..."
          my_bar = st.progress(0, text=progress_text)
          for percent_complete in range(100):
               time.sleep(0.01)
               my_bar.progress(percent_complete + 1, text=progress_text)
          time.sleep(1)
          my_bar.empty()

          # 연도별로 대표발의자 몇 번 등장하는지 계산
          count_representative_data = raw_data[raw_data['대표발의자'] == search_name].groupby('연도').size().reset_index(name='대표발의건수')

          # 연도별로 공동발의자 몇 번 등장하는지 계산
          count_joint_data = raw_data[raw_data['공동발의자'].str.contains(search_name, na=False, regex=False)].groupby('연도').size().reset_index(name='공동발의건수')

          # 데이터 병합
          count_data = pd.merge(count_representative_data, count_joint_data, on='연도', how='outer').fillna(0)

          # 데이터 출력
          output = '\\n'.join([f':thumbsup: {year}년, 대표발의:{data_value}건, 공동발의:{mu_value}건' for year, data_value, mu_value in zip(count_data['연도'], count_data['대표발의건수'], count_data['공동발의건수'])])

          st.success(output)


          # 누적 막대 그래프 생성
          fig2 = px.bar(count_data, x='연도', y=['대표발의건수', '공동발의건수'],
                     labels={'연도': '연도', 'value': '발의건수'},
                     barmode='relative', category_orders={'연도': sorted(count_data['연도'].unique())}, height=450, width=550)

          st.plotly_chart(fig2)

          #프로세스 bar
          progress_text = "세부법안 데이터 분석 중..."
          my_bar = st.progress(0, text=progress_text)
          for percent_complete in range(100):
               time.sleep(0.01)
               my_bar.progress(percent_complete + 1, text=progress_text)
          time.sleep(1)
          my_bar.empty()


          st.subheader(":smiley: :red[공동발의] 법안 세부정보", divider='gray')

          # 모든 연도에 대한 데이터 출력
          df = filtered_representative_data[['연도', '법률안명', '공동발의자', '본회의심의결과', '소관위처리결과', '법사위처리결과']].fillna(' ')
          st.dataframe(df, use_container_width=True)

  with tab2:
    #tab B를 누르면 표시될 내용
    st.write('hi')

left_column, right_column = st.columns(2)


#여론검색 파트
if selected_menu == "의안 여론검색":

  #프로세스 bar
  progress_text = "창전환, 프로세스 세팅 중..."
  my_bar = st.progress(0, text=progress_text)
  for percent_complete in range(100):
       time.sleep(0.001)
       my_bar.progress(percent_complete + 1, text=progress_text)
  time.sleep(1)
  my_bar.empty()

  st.subheader(':one: 의안명 입력', divider='gray')
  search_bill_name = st.text_input("찾으려는 의안 입력")

  if st.button("검색하기"):
    if search_bill_name:
      # API 데이터 가져오기
      search_bill_name_xml = fetch_api_data(search_bill_name)
      #print(api_data)

      parse_api_response(search_bill_name_xml)














if selected_menu == "챗봇":
    st.header("챗봇_제작중")




