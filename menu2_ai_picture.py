from ultralytics import YOLO
import torch

from collections import Counter

import streamlit as st

#from langchain.document_loaders import PyPDFLoader
#from langchain.embeddings import HuggingFaceEmbeddings
#import tiktoken
#from langchain.vectorstores import FAISS
#from langchain.text_splitter import RecursiveCharacterTextSplitter

#from langchain.chains import ConversationalRetrievalChain
#from langchain.chat_models import ChatOpenAI
#from langchain.memory import ConversationBufferMemory

#from langchain.callbacks import get_openai_callback
import pdfplumber
import openai



# # YOLO 모델 로드 _집 학습한것!
# model = YOLO("/AIEDU/best_person.pt")

# # st.set_page_config(page_title="심리상담 프로그램", page_icon=":medal:", layout="wide")

# # st.title("그림 심리 검사 결과")

# # Run inference on an image
# results = model.predict(source='/AIEDU/4_total_test/남자사람_7_남_00026.jpg', save=True)  # results list

# # 이미지 전체 사이즈 설정
# img_width, img_height = 1280, 1280
# total_area = img_width * img_height  # 전체 이미지 면적

# # 클래스별 객체 카운트를 저장할 딕셔너리
# class_counts = Counter()

# # 클래스 이름을 가져오는 예시 (model.names 또는 유사한 리스트를 사용)
# class_names = model.names  # model은 YOLO 모델 인스턴스, names는 클래스 ID에 매핑된 이름 리스트

#------------------------------------------------
#집이 중앙에 있는지 확인
def check_house_center(xyxy, class_ids, img_width, img_height, class_names):
    center_x, center_y = img_width / 2, img_height / 2
    
    # 집의 중앙 위치 계산
    centers_x = (xyxy[:, 2] + xyxy[:, 0]) / 2
    centers_y = (xyxy[:, 3] + xyxy[:, 1]) / 2

    # 이미지 중앙으로부터의 최대 거리를 계산 (이미지의 대각선 길이의 절반)
    max_distance = ((img_width ** 2 + img_height ** 2) ** 0.5) / 2

    for center_x_obj, center_y_obj, class_id in zip(centers_x, centers_y, class_ids):
        class_name = class_names[class_id]
        if class_name == "집전체":
            # 중앙으로부터의 유클리드 거리 계산
            distance_from_center = ((center_x_obj - center_x) ** 2 + (center_y_obj - center_y) ** 2) ** 0.5
            # 거리를 퍼센트로 변환 (전체 가능 거리 대비)
            distance_percentage = (distance_from_center / max_distance) * 100
            
            # 반환 전 tensor에서 실수로 변환
            if isinstance(distance_percentage, torch.Tensor):
                return distance_percentage.item()  # tensor를 실수로 변환
            return distance_percentage  # 이미 실수 타입이면 그대로 반환
        
    # 집전체 클래스가 없는 경우, None을 반환
    return None

#집 크기를 확인하는 것
def check_house_size(xyxy, class_ids, img_width, img_height, class_names, total_area):
    for box, class_id in zip(xyxy, class_ids):
        class_name = class_names[class_id]
        if class_name == "집전체":
            # 바운딩 박스에서 가로 및 세로 길이 계산
            width = box[2] - box[0]
            height = box[3] - box[1]
            # 바운딩 박스의 면적 계산
            area = width * height
            # 전체 이미지 면적 대비 비율 계산
            area_percentage = (area / total_area) * 100

            # Check if the result is a tensor and convert it to a Python float
            if isinstance(area_percentage, torch.Tensor):
                return area_percentage.item()
            return area_percentage  # If already a float, return it directly
    
    # 집전체 클래스가 발견되지 않은 경우
    return 0.0

# 굴뚝, 울타리, 나무, 꽃, 해, 연못/강이 있는지 확인
def check_class_presence(class_ids, class_names, confidences):
    # 클래스 이름을 기반으로 확인할 클래스 리스트 설정
    target_classes = ['굴뚝', '울타리', '나무', '꽃', '태양', '연못']
    # 검출된 클래스 ID들을 이름으로 변환
    detected_classes = [class_names[id] for id in class_ids]

    # 검출된 각 클래스의 존재 여부 및 ID 확인
    high_confidence_presence = {target: [] for target in target_classes}  # 0.8 이상의 탐지 확률을 가진 객체 저장

    # 검출된 클래스 ID들과 확률을 검사
    for detected_class, detected_id, confidence in zip(detected_classes, class_ids, confidences):
        if detected_class in target_classes and confidence >= 0.8:
            high_confidence_presence[detected_class].append(detected_id)

    # 결과 저장 및 출력
    results = []
    for target in target_classes:
        if high_confidence_presence[target]:
            #print(f"{target} - 이미지 내에 존재합니다. 탐지된 ID (확률 >= 0.8): {high_confidence_presence[target]}")
            results.append(target)

    return results



#창문 갯수 세는 것(총 갯수 및 80% 이상)
def count_high_confidence_windows_by_name(class_ids, confidences, class_names, boxes):
    # '창문' 클래스와 '집벽' 클래스의 이름으로 검색
    window_class_name = '창문'
    wall_class_name = '집벽'
    
    # 클래스 ID 찾기
    window_class_id = None
    wall_class_id = None
    for key, value in class_names.items():
        if value == window_class_name:
            window_class_id = key
        if value == wall_class_name:
            wall_class_id = key
    if window_class_id is None or wall_class_id is None:
        print(f"'{window_class_name}' 또는 '{wall_class_name}' 클래스가 모델의 클래스 목록에 없습니다.")
        return None, None  # 실패 시 None 반환

    # '창문' 및 '집벽'의 크기 계산
    total_windows = 0
    high_confidence_windows = 0
    window_sizes = []
    wall_sizes = []

    for class_id, confidence, box in zip(class_ids, confidences, boxes):
        # 창문과 집벽 크기 계산
        width = box[2] - box[0]
        height = box[3] - box[1]
        if class_id == window_class_id:
            total_windows += 1
            window_sizes.append(width * height)  # 면적 저장
            if confidence >= 0.8:
                high_confidence_windows += 1
        elif class_id == wall_class_id:
            wall_sizes.append(width * height)  # 면적 저장

    # 결과 계산
    window_to_wall_ratio = []
    if wall_sizes:
        average_wall_size = sum(wall_sizes) / len(wall_sizes)
        window_to_wall_ratio = [window_size / average_wall_size for window_size in window_sizes]
    else:
        print("집벽을 찾을 수 없어 창문 대비 비율을 계산할 수 없습니다.")

    # 반환할 결과를 dict 형식으로 저장
    results = {
        '80% 이상 창문 갯수': high_confidence_windows,
        '집벽대비 창문 비율': window_to_wall_ratio
    }

    return results

#굴뚝의 연기 방향
def detect_smoke_direction(class_ids, confidences, class_names, boxes):
    chimney_class_name = '굴뚝'
    smoke_class_name = '연기'
    
    # 클래스 ID 찾기
    chimney_class_id = None
    smoke_class_id = None
    for key, value in class_names.items():
        if value == chimney_class_name:
            chimney_class_id = key
        if value == smoke_class_name:
            smoke_class_id = key

    if chimney_class_id is None or smoke_class_id is None:
        print(f"'{chimney_class_name}' 또는 '{smoke_class_name}' 클래스가 모델의 클래스 목록에 없습니다.")
        return None  # 실패 시 None 반환

    # 굴뚝과 연기의 위치 추적
    chimney_positions = []
    chimney_widths = []
    smoke_positions = []

    for class_id, box, confidence in zip(class_ids, boxes, confidences):
        if confidence >= 0.7:  # 고신뢰도 객체만 처리
            center_x = (box[0] + box[2]) / 2
            if class_id == chimney_class_id:
                chimney_positions.append(center_x)  # 굴뚝 중앙 x 좌표
                chimney_widths.append(box[2] - box[0])  # 굴뚝 너비
            elif class_id == smoke_class_id:
                smoke_positions.append(center_x)  # 연기 중앙 x 좌표

    # 굴뚝과 연기의 위치를 비교하여 방향 결정
    if not chimney_positions or not smoke_positions:
        return "굴뚝 또는 연기를 찾을 수 없습니다."

    chimney_center = sum(chimney_positions) / len(chimney_positions)
    average_chimney_width = sum(chimney_widths) / len(chimney_widths)
    smoke_center = sum(smoke_positions) / len(smoke_positions)

    threshold = average_chimney_width * 0.05  # 굴뚝 너비의 10%

    if abs(smoke_center - chimney_center) > threshold:
        if smoke_center > chimney_center:
            return "0" #화면 오른쪽으로 흐름, 심리검사에서 의미 없으니 리턴값 0 처리
        else:
            return "굴뚝 연기가 왼쪽으로 흐릅니다."
    else:
        return "0" #위로 흐름, 심리검사에서 의미 없으니 리턴값 0 처리

# 전체 면적에서 그림 위치
def analyze_object_distribution(boxes, img_height):
    # 객체 위치를 분석하여 상단, 중앙, 하단 분포를 계산
    top_count = 0
    middle_count = 0
    bottom_count = 0
    
    # 이미지 중앙값 계산
    middle_threshold = img_height / 2
    
    for box in boxes:
        # 각 객체의 중심 y 좌표 계산
        center_y = (box[1] + box[3]) / 2
        
        if center_y < middle_threshold * 0.5:
            top_count += 1
        elif center_y > middle_threshold * 1.5:
            bottom_count += 1
        else:
            middle_count += 1
    
    total = top_count + middle_count + bottom_count
    distribution = {
        "top": top_count / total * 100 if total > 0 else 0,
        "middle": middle_count / total * 100 if total > 0 else 0,
        "bottom": bottom_count / total * 100 if total > 0 else 0
    }
    
    return distribution

def analyze_detailed_object_distribution(boxes, img_width, img_height):
    # 객체 위치를 더 상세하게 분석하여 구역별로 분류
    region_counts = {
        "top_left": 0, "top_center": 0, "top_right": 0,
        "middle_left": 0, "middle_center": 0, "middle_right": 0,
        "bottom_left": 0, "bottom_center": 0, "bottom_right": 0
    }
    
    # 이미지를 세로와 가로로 세 등분
    vertical_thresholds = [img_height / 3, 2 * img_height / 3]
    horizontal_thresholds = [img_width / 3, 2 * img_width / 3]
    
    for box in boxes:
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2
        
        # 세로 위치 결정
        if center_y < vertical_thresholds[0]:
            vertical_position = "top"
        elif center_y < vertical_thresholds[1]:
            vertical_position = "middle"
        else:
            vertical_position = "bottom"
        
        # 가로 위치 결정
        if center_x < horizontal_thresholds[0]:
            horizontal_position = "left"
        elif center_x < horizontal_thresholds[1]:
            horizontal_position = "center"
        else:
            horizontal_position = "right"
        
        # 해당하는 구역의 카운트 증가
        region_key = f"{vertical_position}_{horizontal_position}"
        region_counts[region_key] += 1
    
    return region_counts    

#체크리스트 파일 읽어오기
def extract_pdf_content(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())
    return full_text

def prepare_query(analyzed_data, expert_content):
    """분석 데이터와 전문가 내용을 바탕으로 질의 준비"""
    query = f"그림 분석 결과: {analyzed_data}\n를 전문가 체크리스트: {expert_content}\n 와 비교해 그림의 심리적 상태를 상세하게 분석해주세요. 이해가 쉽게 분석해주세요. 이를 바탕으로 우울감 등 심리상태에 대해서도 분석해주세요."
    return query


# gpt로 질문하기.
def ask_gpt(query, openai_api_key):
    """GPT 챗봇 모델에 질의하여 결과 받기"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 적절한 챗봇 모델 지정
            messages=[{"role": "system", "content": "I am a professional psychological assistant trained to analyze drawings and provide psychological insights based on expert checklists and drawing analysis."},
                      {"role": "user", "content": query}],
            api_key=openai_api_key
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.InvalidRequestError as e:
        print(f"오류 발생: {e}")
        return None

#여백에 잔디 그리는 것!
# def check_grass_in_margin(results, img_width, img_height):
#     # 여백을 계산할 영역의 크기
#     margin_ratio=0.1
#     margin_width = img_width * margin_ratio
#     margin_height = img_height * margin_ratio

#     # 여백 영역의 바운딩 박스 좌표
#     margin_box = [0, 0, margin_width, margin_height]

#     # 잔디 클래스의 ID 확인
#     grass_class_id = "잔디"

#     # 검출된 잔디 객체 중 여백 영역에 속하는지 여부 확인
#     for result in results:
#         boxes = result['boxes']  # 바운딩 박스 좌표
#         class_ids = result['class_ids']  # 클래스 ID
#         for box, class_id in zip(boxes, class_ids):
#             if class_id == grass_class_id:
#                 # 바운딩 박스가 여백 영역에 포함되는지 여부 확인
#                 if box[0] <= margin_box[0] and box[1] <= margin_box[1] and box[2] >= margin_box[2] and box[3] >= margin_box[3]:
#                     return "여백에 잔디가 있습니다."

#     # 여백에 잔디가 없는 경우
#     return "여백에 잔디가 없습니다."


# 입력된 파일(jpg) 집일때
def process_house(pic_path):


    # YOLO 모델 로드 _집 학습한것!
    model = YOLO("best.pt")
    # Run inference on an image
    #results = model.predict(source='/AIEDU/4_total_test/집_7_남_00060.jpg', save=True)  # results list
    results = model.predict(source=pic_path, save=True)  # results list


    # 이미지 전체 사이즈 설정
    img_width, img_height = 1280, 1280
    total_area = img_width * img_height  # 전체 이미지 면적

    # 클래스별 객체 카운트를 저장할 딕셔너리
    class_counts = Counter()

    # 클래스 이름을 가져오는 예시 (model.names 또는 유사한 리스트를 사용)
    class_names = model.names  # model은 YOLO 모델 인스턴스, names는 클래스 ID에 매핑된 이름 리스트

    for result in results:
        # 각 result 객체에서 boxes 속성에 접근
        xyxy = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표 추출
        widths = xyxy[:, 2] - xyxy[:, 0]  # x2 - x1 계산으로 가로 길이 구하기
        heights = xyxy[:, 3] - xyxy[:, 1]  # y2 - y1 계산으로 세로 길이 구하기
        areas = widths * heights  # 각 객체의 면적 계산

        # 면적 비율 계산
        total_area = widths.sum() * heights.sum()  # 전체 면적 계산 예시
        area_ratios = areas / total_area

        # 클래스 ID와 탐지 확률 추출
        class_ids = result.boxes.cls.numpy()  # .numpy()는 텐서를 numpy 배열로 변환
        confidences = result.boxes.conf.numpy()  # 탐지 확률 배열

        # 바운딩 박스 배열을 추가 처리
        boxes = xyxy  # 바운딩 박스 좌표

        # #집 중앙 여부 확인
        center_house = check_house_center(xyxy, class_ids, img_width, img_height, class_names)
        #print("- 집 위치(중앙모임 정도) -", center_house )

        # #집 크기 확인
        house_size = check_house_size(xyxy, class_ids, img_width, img_height, class_names, total_area)
        #print("- 집 크기(전체 면적대비 비율) -", house_size)

        # #굴뚝, 울타리, 나무, 꽃, 해, 연못 있는지 확인
        six_class= check_class_presence(class_ids, class_names, confidences)
        #print("- 6개 클래스 있나 여부 -", six_class ) #리스트 형식

        #창문 갯수 및 창문 크기
        windows_sum =  count_high_confidence_windows_by_name(class_ids, confidences, class_names, boxes)
        #print("- 창문갯수 및 집벽대비 면적 비율 -", windows_sum)

        #굴뚝의 연기 오른쪽인지 왼쪽인지
        chimney = detect_smoke_direction(class_ids, confidences, class_names, boxes)
        #print(" - 굴뚝 연기 방향 -", chimney)

        #그림의 위치
        distribution = analyze_detailed_object_distribution(boxes, img_width, img_height)
        #print("- 그림의 전체적인 위치 -", distribution)
        
        # #여백에 잔디 그리는 것
        # final_message = check_grass_in_margin(results, img_width, img_height)
        # print(final_message) 


        # 분석 관련 promt
        analyzed_data = (f"- 집 위치(중앙모임 정도) - {center_house}이다. 전체 면적 대비 집 크기 비율은 {house_size}이다. "
                 f"창문개수 및 창문 크기 비율은 {windows_sum}이다. 그림에는 {six_class}가 그려져 있다. ", chimney, "그림의 전체적인 위치는 ",distribution, ", ")
        
        # PDF 내용 추출
        pdf_path = "house_result.pdf"
        expert_content = extract_pdf_content(pdf_path)


        # 질의 준비
        query = prepare_query(analyzed_data, expert_content)

        # GPT에 질의
        openai_api_key = st.secrets["OPENAI_API_KEY"]  #나의 api 키 코드
        final_result = ask_gpt(query, openai_api_key)
        # 결과 출력
        print(" <집 그림 분석 결과>\n", final_result)
        # 감각적이고 전문적인 제목을 크게 표시하는 HTML 태그를 사용하여 텍스트 영역을 표시합니다.
        st.markdown("<h1 style='font-family: Arial, sans-serif; font-weight: bold; color: #1f77b4; font-size: 28px;'>✅ 입력한 그림에 대한 AI 심리분석 결과</h1>", unsafe_allow_html=True)

        with st.form(key="my_form"):

            # 텍스트 영역 표시
            st.text_area(
                "분석 세부내용",
                final_result,
                height=350,
                # help="At least two keyphrases for the classifier to work, one per line, "
                # + str(MAX_KEY_PHRASES)
                # + " keyphrases max in 'unlocked mode'. You can tweak 'MAX_KEY_PHRASES' in the code to change this",
                key="1"
            )
            st.form_submit_button(" *본 분석은 참고용입니다. 보다 자세한 상담은 전문 상담사와 상의하세요.*")
        # st.write(final_result)

#------------------------------------------------------------------------------------------------------------

# 사람 일때 사용 클래스 총7개 탐지.
def check_class_presence_person(class_ids, class_names, confidences):
    # 클래스 이름을 기반으로 확인할 클래스 리스트 설정
    target_classes = ['눈', '코', '입', '머리카락', '목', '팔', '단추']
    # 검출된 클래스 ID들을 이름으로 변환
    detected_classes = [class_names[id] for id in class_ids]

    # 검출된 각 클래스의 존재 여부 및 ID 확인
    high_confidence_presence = {target: [] for target in target_classes}  # 0.8 이상의 탐지 확률을 가진 객체 저장

    # 검출된 클래스 ID들과 확률을 검사
    for detected_class, detected_id, confidence in zip(detected_classes, class_ids, confidences):
        if detected_class in target_classes and confidence >= 0.8:
            high_confidence_presence[detected_class].append(detected_id)

    # 결과 저장 및 출력
    results = []
    for target in target_classes:
        if high_confidence_presence[target]:
            #print(f"{target} - 이미지 내에 존재합니다. 탐지된 ID (확률 >= 0.8): {high_confidence_presence[target]}")
            results.append(target)

    return results

# 사람 객체 크기 찾는것
def calculate_person_ratio(results, img_width, img_height, class_names, target_class='사람전체'):
    total_area = img_width * img_height
    person_area = 0

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        # '사람전체' 클래스의 객체들에 대한 면적 계산
        for box, class_id in zip(boxes, class_ids):
            if class_names[class_id] == target_class:
                # 각 객체의 바운딩 박스로부터 면적 계산
                width = box[2] - box[0]
                height = box[3] - box[1]
                person_area += width * height

    # 전체 면적 대비 사람전체 객체의 비율을 %로 계산
    if total_area > 0:  # 분모가 0이 아닐 때만 계산
        ratio_percent = (person_area / total_area) * 100
    else:
        ratio_percent = 0

    return ratio_percent

#코 표현(작다, 생략 등)
def calculate_nose_to_face_ratio(results, class_names, face_class='얼굴', nose_class='코'):
    face_area = 0
    nose_area = 0

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for box, class_id in zip(boxes, class_ids):
            # 각 객체의 바운딩 박스로부터 면적 계산
            width = box[2] - box[0]
            height = box[3] - box[1]
            area = width * height

            if class_names[class_id] == face_class:
                face_area += area
            elif class_names[class_id] == nose_class:
                nose_area += area

    # 얼굴 면적 대비 코 객체의 면적 비율을 계산
    if face_area > 0 and nose_area > 0:
        ratio_percent = (nose_area / face_area) * 100
    else:
        ratio_percent = 0

    return ratio_percent

#귀 몇개 있는지, 양쪽 귀 사이즈 비교
def analyze_ears(results, class_names, ear_class='귀'):
    ear_areas = []  # 귀의 면적을 저장할 리스트

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for box, class_id in zip(boxes, class_ids):
            if class_names[class_id] == ear_class:
                # 각 귀 객체의 바운딩 박스로부터 면적 계산
                width = box[2] - box[0]
                height = box[3] - box[1]
                area = width * height
                ear_areas.append(area)

    ear_count = len(ear_areas)  # 귀의 개수

    # 귀의 개수와 면적 비교를 통한 결과 분석
    if ear_count == 0:
        return "귀를 그리지 않았습니다."
    elif ear_count == 1:
        return "귀를 한쪽만 그렸습니다."
    else:
        # 두 귀의 면적이 거의 동일한지 확인 (소수점 아래 두 자리까지)
        if abs(ear_areas[0] - ear_areas[1]) < 0.01 * max(ear_areas):
            return "귀를 양쪽에 그렸으며, 양쪽 귀의 크기가 거의 동일합니다."
        else:
            return "귀를 양쪽에 그렸으며, 양쪽 귀의 크기가 다릅니다."

# 목이 굵은지 확인
def analyze_neck_thickness(results, class_names, neck_class='목', img_width=None):
    neck_widths = []  # 목의 너비를 저장할 리스트

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for box, class_id in zip(boxes, class_ids):
            if class_names[class_id] == neck_class:
                # 목 객체의 바운딩 박스 너비 계산
                width = box[2] - box[0]
                neck_widths.append(width)

    if not neck_widths:
        return "목 객체가 탐지되지 않았습니다."

    # 전체 이미지 너비 대비 목의 너비 비율 평균 계산
    if img_width:
        avg_neck_width_ratio = (sum(neck_widths) / len(neck_widths)) / img_width
        if avg_neck_width_ratio > 0.1:
            return "목이 굵다.(목을 그렸습니다.)"
        elif avg_neck_width_ratio > 0.05:
            return "목이 보통.(목을 그렸습니다.)"
        else:
            return "목이 가늘다.(목을 그렸습니다.)"
    else:
        # 전체 이미지 너비가 제공되지 않은 경우
        return "목을 그리지 않았습니다. 생략함."

#머리비율
def analyze_head_size(results, class_names, head_class='머리', img_width=None, img_height=None):
    head_areas = []  # 머리의 면적을 저장할 리스트

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for box, class_id in zip(boxes, class_ids):
            if class_names[class_id] == head_class:
                # 머리 객체의 바운딩 박스 면적 계산
                width = box[2] - box[0]
                height = box[3] - box[1]
                area = width * height
                head_areas.append(area)

    if not head_areas:
        return "머리를 그리지 않았습니다."

    # 전체 이미지 면적 대비 머리의 면적 비율 평균 계산
    if img_width and img_height:
        total_area = img_width * img_height
        avg_head_area_ratio = (sum(head_areas) / len(head_areas)) / total_area
        # 비율에 따른 머리 크기 분류
        if avg_head_area_ratio > 0.1:
            return "머리 크기가 크다"
        elif avg_head_area_ratio > 0.03:
            return "머리 크기가 보통"
        else:
            return "머리 크기가 작다"
    else:
        # 이미지 크기 정보가 필요
        return "머리를 그리지 않았습니다."

#두팔 균형 여부
def analyze_arms(results, class_names, arm_class='팔'):
    arm_lengths = []  # 팔의 길이를 저장할 리스트

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for box, class_id in zip(boxes, class_ids):
            if class_names[class_id] == arm_class:
                # 팔 객체의 바운딩 박스 길이(높이) 계산
                height = box[3] - box[1]
                arm_lengths.append(height)

    arm_count = len(arm_lengths)  # 팔의 개수

    # 팔의 개수와 길이를 통한 결과 분석
    if arm_count == 0:
        return "팔을 그리지 않았습니다."
    elif arm_count == 1:
        return "한쪽 팔만 그려졌습니다."
    else:
        # 두 팔의 길이가 거의 동일한지 확인 (소수점 아래 두 자리까지)
        if abs(arm_lengths[0] - arm_lengths[1]) < 0.05 * max(arm_lengths):
            return "양쪽 팔의 길이가 균형있게 그려졌습니다."
        else:
            return "양쪽 팔의 길이가 균형있지 않게 그려졌습니다."

# 다리 길이
def analyze_legs_length(results, class_names, leg_class='다리', img_height=None, threshold=0.15):
    leg_heights = []  # 다리의 높이를 저장할 리스트

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for box, class_id in zip(boxes, class_ids):
            if class_names[class_id] == leg_class:
                # 다리 객체의 바운딩 박스 높이 계산
                height = box[3] - box[1]
                leg_heights.append(height)

    if not leg_heights:
        return "다리를 그리지 않았습니다."

    # 전체 이미지 높이 대비 다리의 높이 비율 평균 계산
    if img_height:
        avg_leg_height_ratio = sum(leg_heights) / len(leg_heights) / img_height
        # 비율에 따른 다리 길이 분류
        if avg_leg_height_ratio < threshold:
            return "다리를 짧게 그렸습니다."
        else:
            return "다리 길이가 보통 이상입니다."
    else:
        # 이미지 높이 정보가 필요
        return "다리를 그리지 않았습니다."



# 입력된 파일(jpg) 사람일때
def process_person(pic_path):


    # YOLO 모델 로드 _집 학습한것!
    model = YOLO("best_person.pt")
    # Run inference on an image
    #results = model.predict(source='/AIEDU/4_total_test/집_7_남_00060.jpg', save=True)  # results list
    results = model.predict(source=pic_path, save=True)  # results list


    # 이미지 전체 사이즈 설정
    img_width, img_height = 1280, 1280
    total_area = img_width * img_height  # 전체 이미지 면적

    # 클래스별 객체 카운트를 저장할 딕셔너리
    class_counts = Counter()

    # 클래스 이름을 가져오는 예시 (model.names 또는 유사한 리스트를 사용)
    class_names = model.names  # model은 YOLO 모델 인스턴스, names는 클래스 ID에 매핑된 이름 리스트

    for result in results:
        # 각 result 객체에서 boxes 속성에 접근
        xyxy = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표 추출
        widths = xyxy[:, 2] - xyxy[:, 0]  # x2 - x1 계산으로 가로 길이 구하기
        heights = xyxy[:, 3] - xyxy[:, 1]  # y2 - y1 계산으로 세로 길이 구하기
        areas = widths * heights  # 각 객체의 면적 계산

        # 면적 비율 계산
        total_area = widths.sum() * heights.sum()  # 전체 면적 계산 예시
        area_ratios = areas / total_area

        # 클래스 ID와 탐지 확률 추출
        class_ids = result.boxes.cls.numpy()  # .numpy()는 텐서를 numpy 배열로 변환
        confidences = result.boxes.conf.numpy()  # 탐지 확률 배열

        # 바운딩 박스 배열을 추가 처리
        boxes = xyxy  # 바운딩 박스 좌표
        print(" --------- 여긴 person 함수입니다. --------- ")

        # 7개 클래스 포함여부 
        detected = check_class_presence_person(class_ids, class_names, confidences)
        print("감지된 클래스:", detected)

        # 사람크기 찾는것 
        person_size = calculate_person_ratio(results, img_width, img_height, class_names, target_class='사람전체')
        print("전체 면적대비 사람 객체 비율:", person_size)

        # 얼굴 대비 코 비율
        nose_ratio = calculate_nose_to_face_ratio(results, class_names)
        print("얼굴 대비 코 면적 비율: {:.2f}%".format(nose_ratio))

        # 귀 있는지, 양쪽귀 크기 비교
        ears_analysis = analyze_ears(results, class_names)
        print(ears_analysis)

        # 목 그렸는지 여부, 굵기 확인
        neck_analysis = analyze_neck_thickness(results, class_names, img_width=img_width)
        print(neck_analysis)

        # 머리 비율
        head_size_analysis = analyze_head_size(results, class_names, img_width=img_width, img_height=img_height)
        print(head_size_analysis)

        # 두팔 균형있는지 확인
        arms_analysis = analyze_arms(results, class_names)
        print(arms_analysis)

        # 두 다리 균형있는지 확인
        legs_length_analysis = analyze_legs_length(results, class_names, img_height=img_height)
        print(legs_length_analysis)

        #그림의 위치
        distribution = analyze_detailed_object_distribution(boxes, img_width, img_height)
        #print("- 그림의 전체적인 위치 -", distribution)

        # 분석 관련 promt
        analyzed_data = (f"그림에는  {detected}이 그려져 있다. 전체 면적 대비 사람 객체 비율은 {person_size}이다. "
                 f"{ears_analysis}. {neck_analysis}. {head_size_analysis}. {arms_analysis}. {legs_length_analysis}."
                 f"얼굴 대비 코 면적 비율: {nose_ratio:.2f}%","그림의 전체적인 위치는 ",distribution )

        # PDF 내용 추출
        pdf_path = "person_result.pdf"
        expert_content = extract_pdf_content(pdf_path)


        # 질의 준비
        query = prepare_query(analyzed_data, expert_content)

        # GPT에 질의
        openai_api_key = st.secrets["OPENAI_API_KEY"]  #나의 api 키 코드
        final_result = ask_gpt(query, openai_api_key)
        # 결과 출력
        print(" <사람 그림 분석 결과>\n", final_result)
        #st.write(final_result)

        # 감각적이고 전문적인 제목을 크게 표시하는 HTML 태그를 사용하여 텍스트 영역을 표시합니다.
        st.markdown("<h1 style='font-family: Arial, sans-serif; font-weight: bold; color: #1f77b4; font-size: 28px;'>✅ 입력한 그림에 대한 AI 심리분석 결과</h1>", unsafe_allow_html=True)

        with st.form(key="my_form"):
            st.text_area(
                "분석 세부내용",
                final_result,
                height=350,
                # help="At least two keyphrases for the classifier to work, one per line, "
                # + str(MAX_KEY_PHRASES)
                # + " keyphrases max in 'unlocked mode'. You can tweak 'MAX_KEY_PHRASES' in the code to change this",
                key="1"
            )
            st.form_submit_button(" *본 분석은 참고용입니다. 보다 자세한 상담은 전문 상담사와 상의하세요.*")

        
        #stx.scrollableTextbox(final_result,height = 600)

#나무 크기 재는 것!
def calculate_tree_ratio(results, img_width, img_height, class_names, target_class='나무전체'):
    total_area = img_width * img_height
    tree_area = 0

    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        # '사람전체' 클래스의 객체들에 대한 면적 계산
        for box, class_id in zip(boxes, class_ids):
            if class_names[class_id] == target_class:
                # 각 객체의 바운딩 박스로부터 면적 계산
                width = box[2] - box[0]
                height = box[3] - box[1]
                tree_area += width * height

    # 전체 면적 대비 나무전체 객체의 비율을 %로 계산
    if total_area > 0:  # 분모가 0이 아닐 때만 계산
        ratio_percent = (tree_area / total_area) * 100
    else:
        ratio_percent = 0

    return ratio_percent

#동물 유무(다람쥐, 새 등)
def check_presence_of_animals(results, class_names, target_classes=['다람쥐', '새']):
    # 타겟 클래스 이름을 클래스 ID로 변환
    target_class_ids = {name: index for index, name in enumerate(class_names)}

    # 검출된 객체들 중 타겟 클래스가 있는지 확인
    found_classes = set()
    for result in results:
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for class_id in class_ids:
            class_name = class_names[class_id]
            if class_name in target_classes:
                found_classes.add(class_name)

    # 타겟 클래스의 객체가 하나라도 있는지 여부 반환
    presence = {class_name: (class_name in found_classes) for class_name in target_classes}

    # 최종 결과 메시지 반환
    if any(presence.values()):
        return "동물이 그려져 있습니다."
    else:
        return "동물이 그려져 있지 않습니다."

#나뭇잎과 열매 둘다 있나 하나만 있나.
def check_leaves_and_fruits(results, class_names, threshold=0.8):
    # 타겟 클래스 이름을 클래스 ID로 변환
    target_classes = ['나뭇잎', '열매']
    target_class_ids = {name: index for index, name in enumerate(class_names)}

    # 검출된 객체들 중 타겟 클래스가 있는지 확인
    found_classes = set()
    for result in results:
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for class_id in class_ids:
            class_name = class_names[class_id]
            if class_name in target_classes:
                found_classes.add(class_name)

    # 타겟 클래스의 객체가 하나라도 있는지 여부 확인
    presence = {class_name: (class_name in found_classes) for class_name in target_classes}

    # 탐지된 객체의 개수 확인
    total_objects = sum(1 for result in results for _ in result.boxes)

    # 타겟 클래스의 객체가 하나라도 있는 경우
    if presence['나뭇잎'] and presence['열매']:
        return "나뭇잎과 열매를 모두 그렸습니다."
    elif presence['나뭇잎'] or presence['열매']:
        return "나뭇잎과 열매 중 하나만 그렸습니다."
    else:
        return "나뭇잎과 열매 중 하나만 그렸습니다."

#나무잎에 꽃 있는지
def check_leaves_and_flowers(results, class_names):
    # 타겟 클래스 이름을 클래스 ID로 변환
    target_classes = ['나뭇잎', '꽃']
    target_class_ids = {name: index for index, name in enumerate(class_names)}

    # 검출된 객체들 중 타겟 클래스가 있는지 확인
    found_classes = set()
    total_objects = sum(len(result.boxes) for result in results)
    for result in results:
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for class_id in class_ids:
            class_name = class_names[class_id]
            if class_name in target_classes:
                found_classes.add(class_name)

    # 타겟 클래스의 객체가 하나라도 있는지 여부 확인
    presence = {class_name: (class_name in found_classes) for class_name in target_classes}

    detection_ratios = {class_name: sum(1 for result in results for class_id in result.boxes.cls.numpy() if class_names[class_id] == class_name) / total_objects
                        for class_name in target_classes}

    # 객체 탐지 비율이 0.8 이상인 경우에만 분석
    if all(detection_ratios[class_name] >= 0.8 for class_name in target_classes):
        if presence['나뭇잎'] and presence['꽃']:
            return "나뭇잎과 꽃이 함께 그렸다."
        else:
            return "나뭇잎과 꽃을 함께 그리지 않았습니다."
    else:
        return "나뭇잎과 꽃을 함께 그리지 않았습니다."


#가지가 있나 없나 확인
def check_branch(results, class_names):
    # '가지' 클래스의 ID 확인
    branch_class_id = None
    for class_id, name in class_names.items():
        if name == '가지':
            branch_class_id = class_id
            break

    # '가지' 클래스의 ID를 찾지 못한 경우
    if branch_class_id is None:
        return "가지를 안 그렸습니다."

    # 검출된 가지 객체의 수 계산
    branch_count = 0
    for result in results:
        boxes = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표
        class_ids = result.boxes.cls.numpy()  # 클래스 ID
        for class_id in class_ids:
            if class_id == branch_class_id:
                branch_count += 1

    # 가지 객체 탐지 비율 계산
    total_objects = sum(len(result.boxes) for result in results)
    branch_detection_ratio = branch_count / total_objects

    # 가지 객체 탐지 비율이 0.8 이상인 경우에만 분석
    if branch_detection_ratio >= 0.8:
        return "가지를 그렸습니다."
    else:
        return "가지를 안 그렸습니다."

# 입력된 파일(jpg) 나무일때
def process_tree(pic_path):

    # YOLO 모델 로드 _집 학습한것!
    model = YOLO("best_tree.pt")
    # Run inference on an image
    #results = model.predict(source='/AIEDU/4_total_test/집_7_남_00060.jpg', save=True)  # results list
    results = model.predict(source=pic_path, save=True)  # results list

    # 이미지 전체 사이즈 설정
    img_width, img_height = 1280, 1280
    total_area = img_width * img_height  # 전체 이미지 면적

    # 클래스별 객체 카운트를 저장할 딕셔너리
    class_counts = Counter()

    # 클래스 이름을 가져오는 예시 (model.names 또는 유사한 리스트를 사용)
    class_names = model.names  # model은 YOLO 모델 인스턴스, names는 클래스 ID에 매핑된 이름 리스트

    for result in results:
        # 각 result 객체에서 boxes 속성에 접근
        xyxy = result.boxes.xyxy.numpy()  # 바운딩 박스 좌표 추출
        widths = xyxy[:, 2] - xyxy[:, 0]  # x2 - x1 계산으로 가로 길이 구하기
        heights = xyxy[:, 3] - xyxy[:, 1]  # y2 - y1 계산으로 세로 길이 구하기
        areas = widths * heights  # 각 객체의 면적 계산

        # 면적 비율 계산
        total_area = widths.sum() * heights.sum()  # 전체 면적 계산 예시
        area_ratios = areas / total_area

        # 클래스 ID와 탐지 확률 추출
        class_ids = result.boxes.cls.numpy()  # .numpy()는 텐서를 numpy 배열로 변환
        confidences = result.boxes.conf.numpy()  # 탐지 확률 배열

        # 바운딩 박스 배열을 추가 처리
        boxes = xyxy  # 바운딩 박스 좌표
        print(" --------- 여긴 tree 함수입니다. --------- ")

        # 나무 크기 상태를 구하는 것
        tree_size = calculate_tree_ratio(results, img_width, img_height, class_names)
        print("나무 크기 ",tree_size )

        # 동물(다람쥐, 새) 있나
        presence = check_presence_of_animals(results, class_names)
        print(presence)  

        # 나뭇잎, 열매 있나 확인
        final_message = check_leaves_and_fruits(results, class_names)
        print(final_message)

        #나뭇잎, 꽃 있나 확인
        tree_flo_final_message = check_leaves_and_flowers(results, class_names)
        print(tree_flo_final_message)

        #가지 있나 없나
        branch_result = check_branch(results, class_names)
        print(branch_result)

        #그림의 위치
        distribution = analyze_detailed_object_distribution(boxes, img_width, img_height)
        #print("- 그림의 전체적인 위치 -", distribution)


        # 분석 관련 promt
        analyzed_data = (f"나무 크기는 전체 면적의  {tree_size}이다. {presence}, {final_message}, {tree_flo_final_message}, {branch_result}"
                 f"그림의 전체적인 위치는 ", distribution)

        # PDF 내용 추출
        pdf_path = "tree_result.pdf"
        expert_content = extract_pdf_content(pdf_path)


        # 질의 준비
        query = prepare_query(analyzed_data, expert_content)

        # GPT에 질의
        openai_api_key = st.secrets["OPENAI_API_KEY"]  #나의 api 키 코드
        final_result = ask_gpt(query, openai_api_key)
        # 결과 출력
        print(" <나무 그림 분석 결과>\n", final_result)
        #st.write(final_result)

        # 감각적이고 전문적인 제목을 크게 표시하는 HTML 태그를 사용하여 텍스트 영역을 표시합니다.
        st.markdown("<h1 style='font-family: Arial, sans-serif; font-weight: bold; color: #1f77b4; font-size: 28px;'>✅ 입력한 그림에 대한 AI 심리분석 결과</h1>", unsafe_allow_html=True)

        with st.form(key="my_form"):
            st.text_area(
                "분석 세부내용",
                final_result,
                height=350,
                # help="At least two keyphrases for the classifier to work, one per line, "
                # + str(MAX_KEY_PHRASES)
                # + " keyphrases max in 'unlocked mode'. You can tweak 'MAX_KEY_PHRASES' in the code to change this",
                key="1"
            )
            st.form_submit_button(" *본 분석은 참고용입니다. 보다 자세한 상담은 전문 상담사와 상의하세요.*")

        #stx.scrollableTextbox(final_result,height = 600)


# # Streamlit을 사용한 사용자 입력 인터페이스
# def main():
#     st.title("AI기반 그림심리 검사")
#     option = st.selectbox(
#         '분석 객체 유형 선택:',
#         ('집', '사람', '나무')
#     )
#     if st.button('분석 시작'):
#         # 여기서 results는 각 객체의 탐지 결과를 포함하는 가정된 데이터 구조
#         #results = fetch_results()  # fetch_results()는 결과를 불러오는 함수로 가정
#         if option == '집':

#             process_house() # 함수 이름 확인!!
#         # elif option == '사람':
#         #     process_person()
#         # elif option == '나무':
#         #     process_tree()
#         st.success(f"{option} 분석 완료!")

# if __name__ == "__main__":
#     main()